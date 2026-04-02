from odoo import models, fields, api
from datetime import datetime, timedelta


class HrEmployeeAllowance(models.Model):
    _name = 'hr.employee.allowance'
    _description = 'Rincian Tunjangan Karyawan'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Urutan', default=10)
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True, ondelete='cascade')
    name = fields.Char(string='Nama Tunjangan', required=True)
    amount = fields.Float(string='Nominal', required=True, default=0.0)
    note = fields.Char(string='Catatan')


class HrEmployeeDeduction(models.Model):
    _name = 'hr.employee.deduction'
    _description = 'Rincian Potongan Karyawan'
    _order = 'sequence, id'

    sequence = fields.Integer(string='Urutan', default=10)
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True, ondelete='cascade')
    name = fields.Char(string='Nama Potongan', required=True)
    amount = fields.Float(string='Nominal', required=True, default=0.0)
    note = fields.Char(string='Catatan')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    outsource_client_id  = fields.Many2one(
        'res.partner', 'Klien penempatan',
        domain=[('is_company', '=', True)])
    outsource_project_id = fields.Many2one(
        'project.project', 'Project penempatan')
    placement_start_date = fields.Date('Mulai penempatan')
    placement_end_date   = fields.Date('Berakhir penempatan')

    bpjs_kesehatan_number = fields.Char('No. BPJS Kesehatan')
    bpjs_tk_number        = fields.Char('No. BPJS TK')

    ptkp_status = fields.Selection([
        ('TK0', 'TK/0'), ('TK1', 'TK/1'), ('TK2', 'TK/2'), ('TK3', 'TK/3'),
        ('K0',  'K/0'),  ('K1',  'K/1'),  ('K2',  'K/2'),  ('K3',  'K/3'),
    ], string='Status PTKP', default='TK0')

    # Salary structure & components
    salary_structure_id = fields.Many2one('hr.salary.structure', string='Struktur Gaji')
    
    # Salary fields
    basic_salary = fields.Float('Gaji Pokok', default=0.0)
    manual_allowance = fields.Float('Tunjangan Manual', default=0.0)
    allowance_line_ids = fields.One2many('hr.employee.allowance', 'employee_id', string='Rincian Tunjangan')
    allowance = fields.Float('Tunjangan', compute='_compute_allowance_total', store=True)
    manual_deduction = fields.Float('Potongan Manual', default=0.0)
    deduction_line_ids = fields.One2many('hr.employee.deduction', 'employee_id', string='Rincian Potongan')
    deduction = fields.Float('Potongan', compute='_compute_deduction_total', store=True)
    gross_salary = fields.Float('Gaji Kotor', compute='_compute_gross_salary', store=True)
    net_salary = fields.Float('Gaji Bersih', compute='_compute_net_salary', store=True)

    # Overtime
    overtime_rate = fields.Float('Tarif Overtime (%)', default=150, help='1.5x = 150%')
    
    # Tax & withholding
    pph21_amount = fields.Float('PPh 21', compute='_compute_pph21', store=True)
    bpjs_employee_amount = fields.Float('BPJS Karyawan', compute='_compute_bpjs', store=True)
    bpjs_employer_amount = fields.Float('BPJS Perusahaan', compute='_compute_bpjs', store=True)
    bpjs_total = fields.Float('Total BPJS', compute='_compute_bpjs', store=True)

    # Work days tracking
    days_worked_current_month = fields.Integer('Hari Kerja Bulan Ini', default=20)
    total_days_worked_year = fields.Integer('Total Hari Kerja/Tahun', default=240)

    # Annual summary
    annual_gross = fields.Float('Gaji Kotor/Tahun', compute='_compute_annual', store=True)
    annual_net = fields.Float('Gaji Bersih/Tahun', compute='_compute_annual', store=True)
    annual_tax = fields.Float('Pajak/Tahun', compute='_compute_annual', store=True)

    # Relations
    payslip_ids = fields.One2many('outsource.payslip', 'employee_id', string='Slip Gaji')
    salary_history_ids = fields.One2many('hr.salary.history', 'employee_id', string='Riwayat Gaji')
    loan_ids = fields.One2many('hr.employee.loan', 'employee_id', string='Pinjaman')
    
    total_loan_deduction = fields.Float(compute='_compute_total_loan_deduction', store=False)

    @api.depends('manual_allowance', 'allowance_line_ids.amount')
    def _compute_allowance_total(self):
        for rec in self:
            line_total = sum(rec.allowance_line_ids.mapped('amount'))
            rec.allowance = rec.manual_allowance + line_total

    @api.depends('manual_deduction', 'deduction_line_ids.amount')
    def _compute_deduction_total(self):
        for rec in self:
            line_total = sum(rec.deduction_line_ids.mapped('amount'))
            rec.deduction = rec.manual_deduction + line_total

    @api.depends('basic_salary', 'allowance')
    def _compute_gross_salary(self):
        for rec in self:
            rec.gross_salary = rec.basic_salary + rec.allowance

    @api.depends('gross_salary', 'deduction', 'pph21_amount', 'bpjs_employee_amount')
    def _compute_net_salary(self):
        for rec in self:
            total_deductions = rec.deduction + rec.pph21_amount + rec.bpjs_employee_amount
            rec.net_salary = rec.gross_salary - total_deductions

    @api.depends('gross_salary', 'ptkp_status')
    def _compute_pph21(self):
        """
        Calculate PPh 21 based on PTKP status and gross salary
        PTKP values (Non-residents): Higher for TK (single), K (married)
        Simplified calculation: only count salary above PTKP threshold
        """
        # PTKP threshold values (yearly, simplified)
        ptkp_values = {
            'TK0': 54000000, 'TK1': 58500000, 'TK2': 63000000, 'TK3': 67500000,
            'K0': 58500000, 'K1': 63000000, 'K2': 67500000, 'K3': 72000000,
        }
        
        for rec in self:
            if rec.ptkp_status and rec.gross_salary:
                ptkp_threshold = ptkp_values.get(rec.ptkp_status, 54000000) / 12
                
                if rec.gross_salary > ptkp_threshold:
                    taxable_income = rec.gross_salary - ptkp_threshold
                    # PPh 21: 5% for income above PTKP threshold
                    rec.pph21_amount = taxable_income * 0.05
                else:
                    rec.pph21_amount = 0.0
            else:
                rec.pph21_amount = 0.0

    @api.depends('gross_salary')
    def _compute_bpjs(self):
        """
        Calculate BPJS contributions:
        - Employee: JKN 4% (Health Insurance) + JKK varies + JHT 3.7% (Pension)
        - Employer: JKN 4% + JKK varies + JHT 3.7%
        Simplified: Employee 8%, Employer varies
        """
        for rec in self:
            # Employee BPJS contribution (simplified)
            rec.bpjs_employee_amount = rec.gross_salary * 0.08  # 4% + 3.7% + selebihnya
            
            # Employer BPJS contribution (employer pays more on JKK)
            rec.bpjs_employer_amount = rec.gross_salary * 0.092  # 4% + 3.7% + higher JKK
            
            rec.bpjs_total = rec.bpjs_employee_amount + rec.bpjs_employer_amount

    @api.depends('loan_ids.remaining_balance')
    def _compute_total_loan_deduction(self):
        for rec in self:
            active_loans = rec.loan_ids.filtered(lambda x: x.state in ['active', 'disbursed'])
            rec.total_loan_deduction = sum(active_loans.mapped('monthly_installment'))

    @api.depends(
        'payslip_ids.state',
        'payslip_ids.date_to',
        'payslip_ids.gross_salary',
        'payslip_ids.net_salary',
        'payslip_ids.pph21_amount',
        'payslip_ids.bpjs_employee_amount',
    )
    def _compute_annual(self):
        today = fields.Date.today()
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)

        for rec in self:
            yearly_slips = rec.payslip_ids.filtered(
                lambda s: s.date_to
                and year_start <= s.date_to <= year_end
                and s.state in ('finance_approved', 'posted', 'done')
            )

            rec.annual_gross = sum(yearly_slips.mapped('gross_salary'))
            rec.annual_tax = sum(
                (s.pph21_amount + s.bpjs_employee_amount) for s in yearly_slips
            )
            rec.annual_net = sum(yearly_slips.mapped('net_salary'))

