from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class AccountingPeriod(models.Model):
    _name = 'accounting.period'
    _description = 'Periode Akuntansi'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc'

    name = fields.Char(string='Periode', required=True, compute='_compute_name', store=True)
    
    date_from = fields.Date(string='Tanggal Mulai', required=True)
    date_to = fields.Date(string='Tanggal Akhir', required=True)
    
    state = fields.Selection([
        ('open', 'Open'),
        ('locked', 'Locked'),
        ('closed', 'Closed'),
    ], string='Status', default='open', tracking=True)
    
    # Closing checklist
    payslips_all_posted = fields.Boolean(
        string='Semua Payslip Posted?',
        compute='_check_payslips_posted',
        store=False
    )
    expenses_all_approved = fields.Boolean(
        string='Semua Expense Approved?',
        compute='_check_expenses_approved',
        store=False
    )
    invoices_all_posted = fields.Boolean(
        string='Semua Invoice Posted?',
        compute='_check_invoices_posted',
        store=False
    )
    purchase_orders_billed = fields.Boolean(
        string='Semua PO Sudah Diinvoice?',
        compute='_check_po_billed',
        store=False
    )
    
    bank_reconciled = fields.Boolean(
        string='Bank Reconciled?',
        tracking=True
    )
    gl_reconciled = fields.Boolean(
        string='GL Reconciled?',
        tracking=True
    )
    
    closing_notes = fields.Text(string='Catatan Penutupan')
    
    # Closing details
    closed_by = fields.Many2one('res.users', string='Ditutup Oleh', readonly=True, tracking=True)
    closed_date = fields.Datetime(string='Tanggal Penutupan', readonly=True, tracking=True)
    
    reopened_by = fields.Many2one('res.users', string='Dibuka Kembali Oleh', readonly=True)
    reopened_date = fields.Datetime(string='Tanggal Dibuka Kembali', readonly=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    @api.depends('date_from', 'date_to')
    def _compute_name(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                month_names = {
                    1: 'Januari', 2: 'Februari', 3: 'Maret', 4: 'April',
                    5: 'Mei', 6: 'Juni', 7: 'Juli', 8: 'Agustus',
                    9: 'September', 10: 'Oktober', 11: 'November', 12: 'Desember'
                }
                month_name = month_names.get(rec.date_from.month, '')
                year = rec.date_from.year
                rec.name = f"{month_name} {year}"
            else:
                rec.name = "Period"
    
    @api.depends('date_from', 'date_to')
    def _check_payslips_posted(self):
        for rec in self:
            payslips = self.env['outsource.payslip'].search([
                ('date_from', '>=', rec.date_from),
                ('date_to', '<=', rec.date_to),
                ('company_id', '=', rec.company_id.id),
                ('state', 'not in', ['posted', 'done']),
            ])
            rec.payslips_all_posted = len(payslips) == 0
    
    @api.depends('date_from', 'date_to')
    def _check_expenses_approved(self):
        for rec in self:
            expenses = self.env['operational.expense'].search([
                ('expense_date', '>=', rec.date_from),
                ('expense_date', '<=', rec.date_to),
                ('company_id', '=', rec.company_id.id),
                ('state', 'not in', ['approved', 'posted']),
            ])
            rec.expenses_all_approved = len(expenses) == 0
    
    @api.depends('date_from', 'date_to')
    def _check_invoices_posted(self):
        for rec in self:
            invoices = self.env['account.move'].search([
                ('move_type', 'in', ['out_invoice', 'in_invoice']),
                ('invoice_date', '>=', rec.date_from),
                ('invoice_date', '<=', rec.date_to),
                ('company_id', '=', rec.company_id.id),
                ('state', '!=', 'posted'),
            ])
            rec.invoices_all_posted = len(invoices) == 0
    
    @api.depends('date_from', 'date_to')
    def _check_po_billed(self):
        for rec in self:
            # Check if all received PO have vendor bill
            po_lines = self.env['purchase.order.line'].search([
                ('order_id.date_order', '>=', rec.date_from),
                ('order_id.date_order', '<=', rec.date_to),
                ('order_id.company_id', '=', rec.company_id.id),
                ('order_id.state', 'in', ['purchase', 'done']),
                ('qty_received', '>', 0),
                ('qty_invoiced', '<', 'qty_received'),
            ])
            rec.purchase_orders_billed = len(po_lines) == 0
    
    def action_close_period(self):
        """Close period dengan checklist verification"""
        self.ensure_one()
        
        if not self.payslips_all_posted:
            raise ValidationError('Ada payslip yang belum posted. Pastikan semua payslip sudah finance approved.')
        
        if not self.expenses_all_approved:
            raise ValidationError('Ada operational expense yang belum approved. Pastikan semua expense sudah diapprove.')
        
        if not self.invoices_all_posted:
            raise ValidationError('Ada invoice yang belum posted. Pastikan semua invoice sudah dipost.')
        
        if not self.bank_reconciled:
            raise ValidationError('Bank belum direconcile. Pastikan bank reconciliation sudah completed.')
        
        if not self.gl_reconciled:
            raise ValidationError('GL belum direconcile. Pastikan GL reconciliation sudah completed.')
        
        self.write({
            'state': 'closed',
            'closed_by': self.env.user.id,
            'closed_date': fields.Datetime.now(),
        })
        
        # Send notification
        self.message_post(
            body=f"Periode {self.name} ditutup oleh {self.env.user.name}",
            message_type='notification'
        )
    
    def action_lock_period(self):
        """Lock period (soft lock) - prevent GL posting tapi data bisa diubah"""
        self.ensure_one()
        self.write({'state': 'locked'})
        
        self.message_post(
            body=f"Periode {self.name} dikunci oleh {self.env.user.name}. GL posting tidak diizinkan.",
            message_type='notification'
        )
    
    def action_reopen_period(self):
        """Reopen period (hanya untuk auditor/finance manager)"""
        if not self.env.user.has_group('account.group_account_manager'):
            raise ValidationError('Hanya Account Manager yang bisa reopen period.')
        
        self.ensure_one()
        self.write({
            'state': 'open',
            'reopened_by': self.env.user.id,
            'reopened_date': fields.Datetime.now(),
        })
        
        self.message_post(
            body=f"Periode {self.name} dibuka kembali oleh {self.env.user.name} untuk audit/adjustment.",
            message_type='notification'
        )
    
    @api.constrains('date_from', 'date_to')
    def _check_date_range(self):
        for rec in self:
            if rec.date_from > rec.date_to:
                raise ValidationError('Tanggal mulai harus lebih awal dari tanggal akhir!')
    
    @api.model
    def create(self, vals):
        # Check overlapping periods
        existing = self.search([
            ('company_id', '=', vals.get('company_id', self.env.company.id)),
            ('date_from', '<=', vals['date_to']),
            ('date_to', '>=', vals['date_from']),
        ])
        if existing:
            raise ValidationError('Sudah ada periode yang overlap!')
        
        return super().create(vals)
