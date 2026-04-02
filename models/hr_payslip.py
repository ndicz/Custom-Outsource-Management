from odoo import api, fields, models
from datetime import datetime, timedelta


class OutsourcePayslipAllowanceLine(models.Model):
    _name = 'outsource.payslip.allowance.line'
    _description = 'Rincian Tunjangan Slip Gaji'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Urutan', default=10)
    payslip_id = fields.Many2one('outsource.payslip', string='Slip Gaji', required=True, ondelete='cascade')
    name = fields.Char(string='Nama Tunjangan', required=True)
    amount = fields.Monetary(string='Nominal', currency_field='company_currency_id', required=True, default=0.0)
    note = fields.Char(string='Catatan')
    company_currency_id = fields.Many2one('res.currency', related='payslip_id.company_currency_id', store=True, readonly=True)


class OutsourcePayslipDeductionLine(models.Model):
    _name = 'outsource.payslip.deduction.line'
    _description = 'Rincian Potongan Slip Gaji'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Urutan', default=10)
    payslip_id = fields.Many2one('outsource.payslip', string='Slip Gaji', required=True, ondelete='cascade')
    name = fields.Char(string='Nama Potongan', required=True)
    amount = fields.Monetary(string='Nominal', currency_field='company_currency_id', required=True, default=0.0)
    note = fields.Char(string='Catatan')
    company_currency_id = fields.Many2one('res.currency', related='payslip_id.company_currency_id', store=True, readonly=True)


class OutsourcePayslip(models.Model):
    _name = 'outsource.payslip'
    _description = 'Slip Gaji Outsource'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date_from desc, id desc'

    name = fields.Char(string='Nomor Slip', required=True, copy=False, default='New')
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    payroll_period_id = fields.Many2one('hr.payroll.period', string='Periode Payroll')
    
    date_from = fields.Date(string='Mulai', required=True)
    date_to = fields.Date(string='Sampai', required=True)

    # Salary components breakdown
    basic_salary = fields.Monetary(string='Gaji Pokok', currency_field='company_currency_id', default=0.0)
    manual_allowance = fields.Monetary(string='Tunjangan Manual', currency_field='company_currency_id', default=0.0)
    allowance_line_ids = fields.One2many('outsource.payslip.allowance.line', 'payslip_id', string='Rincian Tunjangan')
    allowance = fields.Monetary(string='Tunjangan', currency_field='company_currency_id', compute='_compute_allowance_total', store=True)
    manual_deduction = fields.Monetary(string='Potongan Manual', currency_field='company_currency_id', default=0.0)
    deduction_line_ids = fields.One2many('outsource.payslip.deduction.line', 'payslip_id', string='Rincian Potongan')
    deduction = fields.Monetary(string='Potongan Lain', currency_field='company_currency_id', compute='_compute_deduction_total', store=True)
    
    # Overtime
    overtime_hours = fields.Float(string='Jam Overtime')
    overtime_amount = fields.Monetary(string='Bayar Overtime', currency_field='company_currency_id',
        compute='_compute_overtime', store=True)

    gross_salary = fields.Monetary(string='Gaji Kotor', currency_field='company_currency_id', 
        compute='_compute_amount', store=True)
    
    # Tax & withholding  
    pph21_amount = fields.Monetary(string='PPh 21', currency_field='company_currency_id', 
        compute='_compute_amount', store=True)
    bpjs_employee_amount = fields.Monetary(string='BPJS Karyawan', currency_field='company_currency_id',
        compute='_compute_amount', store=True)
    bpjs_employer_amount = fields.Monetary(string='BPJS Perusahaan', currency_field='company_currency_id',
        compute='_compute_amount', store=True)
    
    # Loans deduction
    loan_deduction = fields.Monetary(string='Cicilan Pinjaman', currency_field='company_currency_id',
        compute='_compute_loan_deduction', store=False)
    
    net_salary = fields.Monetary(string='Gaji Bersih', currency_field='company_currency_id', 
        compute='_compute_amount', store=True)

    days_worked = fields.Integer(string='Hari Kerja', default=20)
    absent_days = fields.Integer(string='Hari Tidak Masuk', default=0)
    public_holiday_days = fields.Integer(string='Tanggal Merah/Cuti Bersama', default=0)
    holiday_work_days = fields.Float(string='Masuk di Hari Libur', default=0.0)
    absence_deduction_rate = fields.Monetary(
        string='Potongan Alfa per Hari',
        currency_field='company_currency_id',
        default=0.0,
        help='Nominal potongan untuk setiap hari tidak masuk/alfa.'
    )
    holiday_work_rate = fields.Monetary(
        string='Insentif Masuk Hari Libur per Hari',
        currency_field='company_currency_id',
        default=0.0,
        help='Nominal tambahan per hari jika karyawan masuk saat tanggal merah/cuti bersama.'
    )
    attendance_deduction = fields.Monetary(
        string='Potongan Absensi',
        currency_field='company_currency_id',
        compute='_compute_attendance_amounts',
        store=True
    )
    holiday_work_amount = fields.Monetary(
        string='Insentif Masuk Hari Libur',
        currency_field='company_currency_id',
        compute='_compute_attendance_amounts',
        store=True
    )
    attendance_source = fields.Selection([
        ('manual', 'Manual'),
        ('import', 'Import CSV/XLSX'),
    ], string='Sumber Absensi', default='manual')
    attendance_notes = fields.Text(string='Catatan Absensi')
    
    # Workflow & Approval
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('hr_verified', 'HR Verified'),
        ('finance_approved', 'Finance Approved'),
        ('posted', 'Posted'),
        ('done', 'Done'),
    ], string='Status', default='draft', tracking=True, required=True)
    
    submitted_date = fields.Datetime(string='Tanggal Submit')
    submitted_by = fields.Many2one('res.users', string='Disubmit oleh')
    
    verified_date = fields.Datetime(string='Tanggal Verifikasi')
    verified_by = fields.Many2one('res.users', string='Diverifikasi oleh')
    
    approved_date = fields.Datetime(string='Tanggal Approval')
    approved_by = fields.Many2one('res.users', string='Diapprove oleh')
    
    rejection_reason = fields.Text(string='Alasan Penolakan')
    
    # Notes field for deduction details
    deduction_notes = fields.Text(string='Catatan Potongan')

    # Accounting
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True, readonly=True)

    @api.depends('manual_allowance', 'allowance_line_ids.amount')
    def _compute_allowance_total(self):
        for rec in self:
            rec.allowance = rec.manual_allowance + sum(rec.allowance_line_ids.mapped('amount'))

    @api.depends('manual_deduction', 'deduction_line_ids.amount')
    def _compute_deduction_total(self):
        for rec in self:
            rec.deduction = rec.manual_deduction + sum(rec.deduction_line_ids.mapped('amount'))

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('outsource.payslip') or 'New'

        rec = super().create(vals)

        if rec.employee_id:
            # Copy baseline monthly values from employee master if not explicitly filled.
            if 'basic_salary' not in vals:
                rec.basic_salary = rec.employee_id.basic_salary
            if 'manual_allowance' not in vals:
                rec.manual_allowance = rec.employee_id.manual_allowance
            if 'manual_deduction' not in vals:
                rec.manual_deduction = rec.employee_id.manual_deduction
            if 'absence_deduction_rate' not in vals:
                rec.absence_deduction_rate = rec.basic_salary / 20 if rec.basic_salary else 0.0
            if 'holiday_work_rate' not in vals:
                rec.holiday_work_rate = rec.basic_salary / 20 if rec.basic_salary else 0.0

            if not rec.allowance_line_ids and rec.employee_id.allowance_line_ids:
                rec.allowance_line_ids = [
                    (0, 0, {
                        'sequence': line.sequence,
                        'name': line.name,
                        'amount': line.amount,
                        'note': line.note,
                    })
                    for line in rec.employee_id.allowance_line_ids
                ]

            if not rec.deduction_line_ids and rec.employee_id.deduction_line_ids:
                rec.deduction_line_ids = [
                    (0, 0, {
                        'sequence': line.sequence,
                        'name': line.name,
                        'amount': line.amount,
                        'note': line.note,
                    })
                    for line in rec.employee_id.deduction_line_ids
                ]

        return rec

    @api.depends('absent_days', 'absence_deduction_rate', 'holiday_work_days', 'holiday_work_rate')
    def _compute_attendance_amounts(self):
        for rec in self:
            rec.attendance_deduction = max(rec.absent_days, 0) * max(rec.absence_deduction_rate, 0.0)
            rec.holiday_work_amount = max(rec.holiday_work_days, 0.0) * max(rec.holiday_work_rate, 0.0)

    @api.depends('basic_salary', 'allowance', 'overtime_hours', 'employee_id')
    def _compute_overtime(self):
        for rec in self:
            if rec.overtime_hours and rec.employee_id:
                hourly_rate = (rec.basic_salary / 20) / 8  # daily rate / 8 hours
                ot_rate = 1 + (rec.employee_id.overtime_rate / 100)
                rec.overtime_amount = hourly_rate * rec.overtime_hours * ot_rate
            else:
                rec.overtime_amount = 0.0

    @api.depends(
        'basic_salary',
        'allowance',
        'deduction',
        'overtime_amount',
        'holiday_work_amount',
        'attendance_deduction',
        'employee_id',
        'pph21_amount',
        'bpjs_employee_amount'
    )
    def _compute_amount(self):
        for rec in self:
            # Gross salary
            rec.gross_salary = rec.basic_salary + rec.allowance + rec.overtime_amount + rec.holiday_work_amount
            
            # PPh 21 based on PTKP status
            if rec.employee_id:
                ptkp_values = {
                    'TK0': 54000000, 'TK1': 58500000, 'TK2': 63000000, 'TK3': 67500000,
                    'K0': 58500000, 'K1': 63000000, 'K2': 67500000, 'K3': 72000000,
                }
                ptkp_threshold = ptkp_values.get(rec.employee_id.ptkp_status, 54000000) / 12
                
                if rec.gross_salary > ptkp_threshold:
                    taxable = rec.gross_salary - ptkp_threshold
                    rec.pph21_amount = taxable * 0.05
                else:
                    rec.pph21_amount = 0.0
                
                # BPJS
                rec.bpjs_employee_amount = rec.gross_salary * 0.08
                rec.bpjs_employer_amount = rec.gross_salary * 0.092
            else:
                rec.pph21_amount = 0.0
                rec.bpjs_employee_amount = 0.0
                rec.bpjs_employer_amount = 0.0
            
            # Net salary
            total_deductions = (
                rec.deduction
                + rec.attendance_deduction
                + rec.pph21_amount
                + rec.bpjs_employee_amount
                + rec.loan_deduction
            )
            rec.net_salary = rec.gross_salary - total_deductions

    @api.depends('employee_id')
    def _compute_loan_deduction(self):
        for rec in self:
            if rec.employee_id:
                active_loans = rec.employee_id.loan_ids.filtered(
                    lambda x: x.state in ['active', 'disbursed'])
                rec.loan_deduction = sum(active_loans.mapped('monthly_installment'))
            else:
                rec.loan_deduction = 0.0

    def action_submit(self):
        """Submit payslip untuk verifikasi HR"""
        self.write({
            'state': 'submitted',
            'submitted_date': fields.Datetime.now(),
            'submitted_by': self.env.user.id,
        })

    def action_hr_verify(self):
        """HR verify payslip"""
        self.write({
            'state': 'hr_verified',
            'verified_date': fields.Datetime.now(),
            'verified_by': self.env.user.id,
        })

    def action_finance_approve(self):
        """Finance approve dan create journal entry"""
        self.write({
            'state': 'finance_approved',
            'approved_date': fields.Datetime.now(),
            'approved_by': self.env.user.id,
        })
        self._create_journal_entry()

    def action_post(self):
        """Post to accounting"""
        self.write({'state': 'posted'})

    def action_done(self):
        """Mark payslip as done"""
        self.write({'state': 'done'})

    def action_set_draft(self):
        """Reset to draft"""
        self.write({'state': 'draft', 'rejection_reason': False})

    def action_reject(self, reason=''):
        """Reject payslip"""
        self.write({
            'state': 'draft',
            'rejection_reason': reason,
        })

    def _create_journal_entry(self):
        """Create accounting journal entry untuk salary posting"""
        move_lines = []
        
        for rec in self:
            if rec.move_id:
                continue  # Already created
            
            emp = rec.employee_id
            date_entry = rec.date_to
            
            # Debit: Salary Expense
            move_lines.append((0, 0, {
                'account_id': self.env['ir.config_parameter'].sudo().get_param(
                    'outsource_custom.salary_expense_account_id'),
                'debit': rec.gross_salary,
                'credit': 0,
                'name': f'Gaji {emp.name} - {rec.name}',
                'analytic_account_id': emp.outsource_project_id.analytic_account_id.id,
            })),
            
            # Credit: Salary Payable
            move_lines.append((0, 0, {
                'account_id': self.env['ir.config_parameter'].sudo().get_param(
                    'outsource_custom.salary_payable_account_id'),
                'debit': 0,
                'credit': rec.net_salary,
                'name': f'Gaji ke {emp.name}',
            })),
            
            # Credit: Tax payable
            if rec.pph21_amount:
                move_lines.append((0, 0, {
                    'account_id': self.env['ir.config_parameter'].sudo().get_param(
                        'outsource_custom.tax_payable_account_id'),
                    'debit': 0,
                    'credit': rec.pph21_amount,
                    'name': f'PPh 21 {emp.name}',
                }))
            
            # Create move
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'date': date_entry,
                'line_ids': move_lines,
                'ref': rec.name,
            })
            
            rec.move_id = move.id
            move.action_post()

