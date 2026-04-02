from odoo import models, fields, api
from datetime import datetime, timedelta


class HrEmployeeLoan(models.Model):
    _name = 'hr.employee.loan'
    _description = 'Pinjaman Karyawan'
    
    name = fields.Char(string='Nomor Pinjaman', required=True, copy=False, default='New')
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True, ondelete='cascade')
    
    loan_type = fields.Selection([
        ('koperasi', 'Koperasi'),
        ('vehicle', 'Kendaraan'),
        ('housing', 'Perumahan'),
        ('emergency', 'Darurat'),
        ('other', 'Lainnya'),
    ], string='Tipe Pinjaman', required=True)
    
    loan_amount = fields.Float(string='Jumlah Pinjaman', required=True)
    interest_rate = fields.Float(string='Bunga (%)', default=0.0)
    
    loan_date = fields.Date(string='Tanggal Pinjaman', default=fields.Date.today)
    tenure_months = fields.Integer(string='Masa Bayar (bulan)', required=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Disetujui'),
        ('disbursed', 'Dicairkan'),
        ('active', 'Cicilan Berjalan'),
        ('completed', 'Lunas'),
        ('cancelled', 'Dibatalkan'),
    ], string='Status', default='draft', tracking=True)
    
    # Calculated fields
    total_amount_with_interest = fields.Float(
        compute='_compute_total_with_interest', store=True)
    monthly_installment = fields.Float(
        compute='_compute_monthly_installment', store=True)
    
    total_paid = fields.Float(compute='_compute_total_paid', store=True)
    remaining_balance = fields.Float(compute='_compute_remaining_balance', store=True)
    
    # Relations
    loan_installment_ids = fields.One2many('hr.employee.loan.installment', 'loan_id', 
        string='Cicilan', readonly=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.depends('loan_amount', 'interest_rate')
    def _compute_total_with_interest(self):
        for rec in self:
            interest = rec.loan_amount * (rec.interest_rate / 100)
            rec.total_amount_with_interest = rec.loan_amount + interest

    @api.depends('total_amount_with_interest', 'tenure_months')
    def _compute_monthly_installment(self):
        for rec in self:
            if rec.tenure_months > 0:
                rec.monthly_installment = rec.total_amount_with_interest / rec.tenure_months
            else:
                rec.monthly_installment = 0

    @api.depends('loan_installment_ids.amount', 'loan_installment_ids.state')
    def _compute_total_paid(self):
        for rec in self:
            rec.total_paid = sum(rec.loan_installment_ids.filtered(
                lambda x: x.state == 'paid').mapped('amount'))

    @api.depends('total_amount_with_interest', 'total_paid')
    def _compute_remaining_balance(self):
        for rec in self:
            rec.remaining_balance = rec.total_amount_with_interest - rec.total_paid

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.employee.loan') or 'New'
        return super().create(vals)

    def action_approve(self):
        self.write({'state': 'approved'})

    def action_disburse(self):
        """Cairkan pinjaman dan buat installment schedule"""
        self.write({'state': 'active'})
        self._generate_installments()

    def _generate_installments(self):
        """Generate monthly installment schedule"""
        from dateutil.relativedelta import relativedelta
        
        installment_model = self.env['hr.employee.loan.installment']
        current_date = self.loan_date
        
        for i in range(self.tenure_months):
            current_date += relativedelta(months=1)
            installment_model.create({
                'loan_id': self.id,
                'installment_number': i + 1,
                'due_date': current_date,
                'amount': self.monthly_installment,
            })


class HrEmployeeLoanInstallment(models.Model):
    _name = 'hr.employee.loan.installment'
    _description = 'Cicilan Pinjaman'
    
    loan_id = fields.Many2one('hr.employee.loan', string='Pinjaman', required=True, ondelete='cascade')
    installment_number = fields.Integer(string='Cicilan ke-')
    due_date = fields.Date(string='Jatuh Tempo')
    amount = fields.Float(string='Jumlah Cicilan')
    
    state = fields.Selection([
        ('pending', 'Belum Dibayar'),
        ('paid', 'Lunas'),
        ('partial', 'Sebagian'),
        ('overdue', 'Jauh Tempo'),
    ], string='Status', default='pending')
    
    paid_date = fields.Date(string='Tanggal Bayar')
    paid_amount = fields.Float(string='Jumlah Dibayar', default=0.0)
    
    _order = 'loan_id, installment_number'
