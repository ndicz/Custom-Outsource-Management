from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class AccountReconciliation(models.Model):
    _name = 'account.reconciliation'
    _description = 'Rekonsiliasi GL'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_reconciliation desc'

    name = fields.Char(string='Referensi Rekonsiliasi', required=True, copy=False, default='New')
    
    account_id = fields.Many2one(
        'account.account',
        string='GL Account',
        required=True,
        domain="[('deprecated', '=', False)]"
    )
    
    reconciliation_type = fields.Selection([
        ('receivable', 'Receivable (A/R)'),
        ('payable', 'Payable (A/P)'),
        ('bank', 'Bank Account'),
        ('general', 'General Account'),
    ], string='Tipe Rekonsiliasi', required=True)
    
    date_reconciliation = fields.Date(
        string='Tanggal Rekonsiliasi',
        required=True,
        default=fields.Date.today
    )
    
    period_start = fields.Date(string='Periode Mulai', required=True)
    period_end = fields.Date(string='Periode Akhir', required=True)
    
    # Balance Summary
    expected_balance = fields.Monetary(
        string='Saldo Diharapkan (Ledger)',
        currency_field='company_currency_id',
        compute='_compute_expected_balance',
        store=False
    )
    
    reconciled_balance = fields.Monetary(
        string='Saldo Direkonsiliasi',
        currency_field='company_currency_id'
    )
    
    variance = fields.Monetary(
        string='Selisih',
        currency_field='company_currency_id',
        compute='_compute_variance',
        store=False
    )
    
    variance_explanation = fields.Text(string='Penjelasan Selisih')
    
    # Aging Analysis
    aging_0_30_days = fields.Monetary(
        string='0-30 Hari',
        currency_field='company_currency_id',
        compute='_compute_aging',
        store=False
    )
    aging_31_60_days = fields.Monetary(
        string='31-60 Hari',
        currency_field='company_currency_id',
        compute='_compute_aging',
        store=False
    )
    aging_61_90_days = fields.Monetary(
        string='61-90 Hari',
        currency_field='company_currency_id',
        compute='_compute_aging',
        store=False
    )
    aging_over_90_days = fields.Monetary(
        string='>90 Hari',
        currency_field='company_currency_id',
        compute='_compute_aging',
        store=False
    )
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('approved', 'Approved'),
    ], string='Status', default='draft', tracking=True)
    
    reconciliation_notes = fields.Text(string='Catatan Rekonsiliasi')
    
    # Approval
    prepared_by = fields.Many2one('res.users', string='Disiapkan Oleh', readonly=True, default=lambda self: self.env.user)
    approved_by = fields.Many2one('res.users', string='Disetujui Oleh', readonly=True, tracking=True)
    approved_date = fields.Datetime(string='Tanggal Approval', readonly=True, tracking=True)
    
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
    
    # Detailed lines (for showing reconciling items)
    reconciliation_line_ids = fields.One2many(
        'account.reconciliation.line',
        'reconciliation_id',
        string='Detail Rekonsiliasi'
    )
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.reconciliation') or 'New'
        return super().create(vals)
    
    @api.depends('account_id', 'period_start', 'period_end', 'reconciliation_type')
    def _compute_expected_balance(self):
        for rec in self:
            if not rec.account_id:
                rec.expected_balance = 0.0
                continue
            
            # Get GL lines untuk account in period
            move_lines = self.env['account.move.line'].search([
                ('account_id', '=', rec.account_id.id),
                ('date', '>=', rec.period_start),
                ('date', '<=', rec.period_end),
                ('parent_state', '=', 'posted'),
            ])
            
            balance = sum(move_lines.mapped('balance'))
            rec.expected_balance = balance
    
    @api.depends('expected_balance', 'reconciled_balance')
    def _compute_variance(self):
        for rec in self:
            rec.variance = rec.expected_balance - rec.reconciled_balance
    
    @api.depends('account_id', 'reconciliation_type', 'date_reconciliation')
    def _compute_aging(self):
        for rec in self:
            if rec.reconciliation_type not in ['receivable', 'payable']:
                rec.aging_0_30_days = 0.0
                rec.aging_31_60_days = 0.0
                rec.aging_61_90_days = 0.0
                rec.aging_over_90_days = 0.0
                continue
            
            # Get partner from account (A/R or A/P)
            if rec.reconciliation_type == 'receivable':
                domain = [
                    ('account_id.user_type_id.type', '=', 'receivable'),
                    ('parent_state', '=', 'posted'),
                    ('full_reconcile_id', '=', False),  # Unreconciled only
                    ('date', '<=', rec.date_reconciliation),
                ]
            else:  # payable
                domain = [
                    ('account_id.user_type_id.type', '=', 'payable'),
                    ('parent_state', '=', 'posted'),
                    ('full_reconcile_id', '=', False),
                    ('date', '<=', rec.date_reconciliation),
                ]
            
            move_lines = self.env['account.move.line'].search(domain)
            
            # Calculate aging buckets
            today = rec.date_reconciliation
            aging_0_30 = aging_31_60 = aging_61_90 = aging_over_90 = 0.0
            
            for line in move_lines:
                age = (today - line.date).days
                amount = line.balance
                
                if age <= 30:
                    aging_0_30 += amount
                elif age <= 60:
                    aging_31_60 += amount
                elif age <= 90:
                    aging_61_90 += amount
                else:
                    aging_over_90 += amount
            
            rec.aging_0_30_days = aging_0_30
            rec.aging_31_60_days = aging_31_60
            rec.aging_61_90_days = aging_61_90
            rec.aging_over_90_days = aging_over_90
    
    def action_start_reconciliation(self):
        """Start reconciliation process"""
        self.ensure_one()
        self.write({'state': 'in_progress'})
    
    def action_complete_reconciliation(self):
        """Mark reconciliation as completed"""
        self.ensure_one()
        
        if self.variance and abs(self.variance) > 0.01:  # Allow for rounding
            if not self.variance_explanation:
                raise ValidationError(
                    f'Ada selisih Rp {self.variance:,.2f}. '
                    'Harap jelaskan dalam field "Penjelasan Selisih".'
                )
        
        self.write({'state': 'completed'})
        
        self.message_post(
            body=f"Rekonsiliasi {self.account_id.name} selesai dengan variance: Rp {self.variance:,.2f}",
            message_type='notification'
        )
    
    def action_approve_reconciliation(self):
        """Approve reconciliation"""
        if not self.env.user.has_group('account.group_account_manager'):
            raise ValidationError('Hanya Account Manager yang bisa approve rekonsiliasi.')
        
        self.ensure_one()
        
        if self.state != 'completed':
            raise ValidationError('Rekonsiliasi belum completed. Harap complete terlebih dahulu.')
        
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        
        self.message_post(
            body=f"Rekonsiliasi {self.account_id.name} diapprove oleh {self.env.user.name}",
            message_type='notification'
        )
    
    def action_reset_draft(self):
        """Reset ke draft"""
        self.ensure_one()
        self.write({'state': 'draft'})


class AccountReconciliationLine(models.Model):
    _name = 'account.reconciliation.line'
    _description = 'Detail Rekonsiliasi GL'
    _order = 'date desc'

    reconciliation_id = fields.Many2one(
        'account.reconciliation',
        string='Rekonsiliasi',
        required=True,
        ondelete='cascade'
    )
    
    move_line_id = fields.Many2one(
        'account.move.line',
        string='GL Entry',
        readonly=True
    )
    
    date = fields.Date(string='Tanggal', required=True)
    reference = fields.Char(string='Referensi/Invoice')
    description = fields.Char(string='Deskripsi')
    
    debit = fields.Monetary(
        string='Debit',
        currency_field='company_currency_id',
        default=0.0
    )
    credit = fields.Monetary(
        string='Kredit',
        currency_field='company_currency_id',
        default=0.0
    )
    
    balance = fields.Monetary(
        string='Saldo',
        currency_field='company_currency_id',
        compute='_compute_balance',
        store=True
    )
    
    status = fields.Selection([
        ('unreconciled', 'Belum Rekonsiliasi'),
        ('reconciled', 'Sudah Rekonsiliasi'),
        ('explained', 'Ada Penjelasan'),
    ], string='Status', default='unreconciled')
    
    explanation = fields.Text(string='Penjelasan (jika ada)')
    
    company_currency_id = fields.Many2one(
        'res.currency',
        related='reconciliation_id.company_id.currency_id',
        readonly=True)
    
    @api.depends('debit', 'credit')
    def _compute_balance(self):
        for rec in self:
            rec.balance = rec.debit - rec.credit
