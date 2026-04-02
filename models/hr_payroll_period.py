from odoo import models, fields, api
from datetime import datetime


class HrPayrollPeriod(models.Model):
    _name = 'hr.payroll.period'
    _description = 'Periode Payroll'
    
    name = fields.Char(string='Nama Periode', compute='_compute_name', store=True)
    date_start = fields.Date(string='Mulai', required=True)
    date_end = fields.Date(string='Berakhir', required=True)
    
    month = fields.Selection([
        ('01', 'Januari'), ('02', 'Februari'), ('03', 'Maret'),
        ('04', 'April'), ('05', 'Mei'), ('06', 'Juni'),
        ('07', 'Juli'), ('08', 'Agustus'), ('09', 'September'),
        ('10', 'Oktober'), ('11', 'November'), ('12', 'Desember'),
    ], string='Bulan', compute='_compute_month', store=True)
    
    year = fields.Char(string='Tahun', compute='_compute_year', store=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Dibuka'),
        ('locked', 'Dikunci'),
        ('closed', 'Ditutup'),
    ], string='Status', default='draft')
    
    payslip_ids = fields.One2many('outsource.payslip', 'payroll_period_id')
    payslip_count = fields.Integer(compute='_compute_payslip_count', store=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('date_start')
    def _compute_name(self):
        for rec in self:
            if rec.date_start:
                rec.name = rec.date_start.strftime('%B %Y')
            else:
                rec.name = 'Periode'

    @api.depends('date_start')
    def _compute_month(self):
        for rec in self:
            if rec.date_start:
                rec.month = rec.date_start.strftime('%m')
            else:
                rec.month = False

    @api.depends('date_start')
    def _compute_year(self):
        for rec in self:
            if rec.date_start:
                rec.year = rec.date_start.strftime('%Y')
            else:
                rec.year = False

    @api.depends('payslip_ids')
    def _compute_payslip_count(self):
        for rec in self:
            rec.payslip_count = len(rec.payslip_ids)

    def action_open(self):
        """Buka periode untuk input payslip"""
        self.write({'state': 'open'})

    def action_lock(self):
        """Kunci periode - tidak bisa edit lagi"""
        self.write({'state': 'locked'})

    def action_close(self):
        """Tutup periode - final"""
        self.write({'state': 'closed'})

    def action_auto_generate_payslips(self):
        """Auto-generate payslips untuk semua active employees"""
        from datetime import timedelta
        
        employees = self.env['hr.employee'].search([
            ('active', '=', True),
            ('basic_salary', '>', 0)
        ])
        
        created_slips = 0
        for emp in employees:
            # Check if slip already exists for this period
            existing = self.env['outsource.payslip'].search([
                ('employee_id', '=', emp.id),
                ('payroll_period_id', '=', self.id),
            ])
            
            if not existing:
                self.env['outsource.payslip'].create({
                    'employee_id': emp.id,
                    'date_from': self.date_start,
                    'date_to': self.date_end,
                    'payroll_period_id': self.id,
                    'basic_salary': emp.basic_salary,
                    'manual_allowance': emp.manual_allowance,
                    'manual_deduction': emp.manual_deduction,
                    'days_worked': 20,  # Default
                })
                created_slips += 1
        
        self.message_post(body=f'Auto-generated {created_slips} payslips')
        return created_slips

    def action_open_attendance_import_wizard(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Absensi',
            'res_model': 'attendance.import.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_payroll_period_id': self.id,
            },
        }

    _sql_constraints = [
        ('date_range_check', 'CHECK(date_start <= date_end)', 
         'Tanggal mulai harus sebelum tanggal berakhir!'),
    ]
