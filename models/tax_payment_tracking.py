from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TaxPaymentTracking(models.Model):
    _name = 'tax.payment.tracking'
    _description = 'Tracking Pembayaran Pajak'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'tax_period desc, id desc'

    name = fields.Char(string='Referensi', required=True, copy=False, default='New')
    
    tax_type = fields.Selection([
        ('pph21', 'PPh 21 (Karyawan)'),
        ('pph23', 'PPh 23 (Jasa/Bunga)'),
        ('pph25', 'PPh 25 (Badan Usaha)'),
        ('ppn', 'PPN'),
        ('bpjs_kesehatan', 'BPJS Kesehatan'),
        ('bpjs_jht', 'BPJS JHT'),
        ('bpjs_jp', 'BPJS JP'),
        ('bpjs_jkk', 'BPJS JKK'),
        ('bpjs_jkm', 'BPJS JKM'),
    ], string='Jenis Pajak', required=True, tracking=True)
    
    tax_period = fields.Date(string='Periode Pajak', required=True, tracking=True)
    
    # Calculated amounts
    total_withheld = fields.Monetary(
        string='Total Dipotong',
        currency_field='company_currency_id',
        compute='_compute_total_withheld',
        store=False
    )
    
    # Payment tracking
    payment_amount = fields.Monetary(
        string='Jumlah Dibayar',
        currency_field='company_currency_id'
    )
    
    payment_date = fields.Date(string='Tanggal Pembayaran', tracking=True)
    
    payment_method = fields.Selection([
        ('bank_transfer', 'Transfer Bank'),
        ('cash', 'Tunai'),
        ('check', 'Cek'),
        ('other', 'Lainnya'),
    ], string='Metode Pembayaran')
    
    payment_reference = fields.Char(
        string='Nomor Referensi Pembayaran',
        help='Nomor transfer, nomor cek, atau referensi pembayaran lainnya'
    )
    
    # Reconciliation
    gl_account_id = fields.Many2one(
        'account.account',
        string='GL Account (Liabilitas)',
        required=True,
        domain="[('account_type', '=', 'liability_current')]"
    )
    
    move_id = fields.Many2one(
        'account.move',
        string='Payment Journal Entry',
        readonly=True
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('verified', 'Terverifikasi'),
        ('paid', 'Sudah Dibayar'),
        ('reconciled', 'Sudah Direkonsiliasi'),
    ], string='Status', default='draft', tracking=True)
    
    # Details
    calculation_notes = fields.Text(string='Catatan Kalkulasi')
    payment_notes = fields.Text(string='Catatan Pembayaran')
    
    # Approval
    prepared_by = fields.Many2one('res.users', string='Disiapkan Oleh', readonly=True, default=lambda self: self.env.user)
    verified_by = fields.Many2one('res.users', string='Diverifikasi Oleh', readonly=True, tracking=True)
    verified_date = fields.Datetime(string='Tanggal Verifikasi', readonly=True)
    
    paid_by = fields.Many2one('res.users', string='Dibayar Oleh', readonly=True, tracking=True)
    paid_datetime = fields.Datetime(string='Tanggal/Waktu Pembayaran', readonly=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    company_currency_id = fields.Many2one(
        'res.currency',
        related='company_id.currency_id',
        store=True,
        readonly=True
    )
    
    # Tax detail lines
    tax_detail_ids = fields.One2many(
        'tax.payment.detail',
        'tax_tracking_id',
        string='Detail Pajak'
    )
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('tax.payment.tracking') or 'New'
        return super().create(vals)
    
    @api.depends('tax_type', 'tax_period')
    def _compute_total_withheld(self):
        for rec in self:
            if rec.tax_type == 'pph21':
                rec.total_withheld = self._compute_pph21_total(rec.tax_period)
            elif rec.tax_type == 'pph23':
                rec.total_withheld = self._compute_pph23_total(rec.tax_period)
            elif rec.tax_type.startswith('bpjs'):
                rec.total_withheld = self._compute_bpjs_total(rec.tax_type, rec.tax_period)
            else:
                rec.total_withheld = 0.0
    
    def _compute_pph21_total(self, period):
        """Compute total PPh21 withheld in period"""
        period_start = period.replace(day=1)
        period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
        
        payslips = self.env['outsource.payslip'].search([
            ('date_from', '>=', period_start),
            ('date_to', '<=', period_end),
            ('state', 'in', ['finance_approved', 'posted', 'done']),
            ('company_id', '=', self.company_id.id),
        ])
        
        return sum(payslips.mapped('pph21_amount'))
    
    def _compute_pph23_total(self, period):
        """Compute total PPh23 invoices in period"""
        period_start = period.replace(day=1)
        period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
        
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', period_start),
            ('invoice_date', '<=', period_end),
            ('state', '=', 'posted'),
            ('company_id', '=', self.company_id.id),
            ('pph23_applicable', '=', True),
        ])
        
        return sum(invoices.mapped('pph23_amount'))
    
    def _compute_bpjs_total(self, bpjs_type, period):
        """Compute total BPJS contributions in period"""
        period_start = period.replace(day=1)
        period_end = (period_start + relativedelta(months=1)) - timedelta(days=1)
        
        payslips = self.env['outsource.payslip'].search([
            ('date_from', '>=', period_start),
            ('date_to', '<=', period_end),
            ('state', 'in', ['finance_approved', 'posted', 'done']),
            ('company_id', '=', self.company_id.id),
        ])
        
        bpjs_field_map = {
            'bpjs_kesehatan': 'bpjs_employee_amount',  # Or employer amount
            'bpjs_jht': 'bpjs_employer_amount',
            'bpjs_jp': 'bpjs_employer_amount',
            'bpjs_jkk': 'bpjs_employer_amount',
            'bpjs_jkm': 'bpjs_employer_amount',
        }
        
        field = bpjs_field_map.get(bpjs_type)
        if field:
            return sum(payslips.mapped(field))
        return 0.0
    
    def action_verify(self):
        """Verify tax calculation"""
        self.ensure_one()
        self.write({
            'state': 'verified',
            'verified_by': self.env.user.id,
            'verified_date': fields.Datetime.now(),
        })
        
        self.message_post(
            body=f"Tax tracking untuk {self.get_tax_type_display()} - {self.tax_period} terverifikasi. Total: Rp {self.total_withheld:,.2f}",
            message_type='notification'
        )
    
    def action_record_payment(self):
        """Record tax payment"""
        self.ensure_one()
        
        if not self.payment_amount or not self.payment_date or not self.payment_method:
            raise ValidationError('Harap isi Jumlah Dibayar, Tanggal Pembayaran, dan Metode Pembayaran.')
        
        if self.payment_amount > self.total_withheld * 1.05:  # Allow 5% overpayment
            if not self.payment_notes:
                raise ValidationError(
                    f'Jumlah dibayar (Rp {self.payment_amount:,.2f}) '
                    f'melebihi total dipotong (Rp {self.total_withheld:,.2f}). '
                    'Harap jelaskan dalam Catatan Pembayaran.'
                )
        
        # Create GL entry untuk payment
        self._create_payment_journal_entry()
        
        self.write({
            'state': 'paid',
            'paid_by': self.env.user.id,
            'paid_datetime': fields.Datetime.now(),
        })
        
        self.message_post(
            body=f"Pembayaran {self.get_tax_type_display()} dicatat: Rp {self.payment_amount:,.2f} pada {self.payment_date}",
            message_type='notification'
        )
    
    def action_reconcile_payment(self):
        """Mark as reconciled"""
        self.ensure_one()
        self.write({'state': 'reconciled'})
        
        self.message_post(
            body=f"Pembayaran {self.get_tax_type_display()} sudah direkonsiliasi dengan GL",
            message_type='notification'
        )
    
    def _create_payment_journal_entry(self):
        """Create GL entry untuk tax payment"""
        if self.move_id:
            return  # Already created
        
        lines = [
            (0, 0, {
                'account_id': self.gl_account_id.id,
                'debit': 0.0,
                'credit': self.payment_amount,
                'name': f"Pembayaran {self.get_tax_type_display()} - {self.tax_period}",
            }),
            (0, 0, {
                'account_id': self.env['ir.config_parameter'].sudo().get_param(
                    'outsource_custom.expense_payment_account_id'),
                'debit': self.payment_amount,
                'credit': 0.0,
                'name': f"Pembayaran {self.get_tax_type_display()}",
            }),
        ]
        
        move = self.env['account.move'].create({
            'move_type': 'entry',
            'date': self.payment_date,
            'ref': self.name,
            'line_ids': lines,
        })
        
        self.move_id = move.id
        move.action_post()
    
    def action_reset_draft(self):
        """Reset ke draft"""
        self.ensure_one()
        if self.move_id:
            self.move_id.button_draft()
            self.move_id.unlink()
            self.move_id = False
        
        self.write({'state': 'draft'})


class TaxPaymentDetail(models.Model):
    _name = 'tax.payment.detail'
    _description = 'Detail Items untuk Tax Payment'
    _order = 'date desc'

    tax_tracking_id = fields.Many2one(
        'tax.payment.tracking',
        string='Tax Tracking',
        required=True,
        ondelete='cascade'
    )
    
    date = fields.Date(string='Tanggal', required=True)
    reference = fields.Char(string='Referensi (Slip/Invoice)')
    description = fields.Char(string='Deskripsi')
    
    amount_withheld = fields.Monetary(
        string='Jumlah Dipotong',
        currency_field='company_currency_id'
    )
    
    amount_paid = fields.Monetary(
        string='Jumlah Dibayar',
        currency_field='company_currency_id')
    
    status = fields.Selection([
        ('pending', 'Menunggu'),
        ('paid', 'Sudah Dibayar'),
        ('overpaid', 'Lebih Bayar'),
    ], string='Status', default='pending', compute='_compute_status', store=True)
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='tax_tracking_id.company_id.currency_id',
        store=True,
        readonly=True
    )
    
    @api.depends('amount_withheld', 'amount_paid')
    def _compute_status(self):
        for rec in self:
            if rec.amount_paid >= rec.amount_withheld:
                rec.status = 'paid'
            else:
                rec.status = 'pending'
