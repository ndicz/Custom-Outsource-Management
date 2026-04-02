from odoo import models, fields, api
from datetime import datetime


class HrSalaryHistory(models.Model):
    _name = 'hr.salary.history'
    _description = 'Riwayat Gaji'
    
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    
    effective_date = fields.Date(string='Berlaku Sejak', required=True)
    
    basic_salary = fields.Float(string='Gaji Pokok')
    allowance = fields.Float(string='Tunjangan')
    
    reason = fields.Selection([
        ('initial', 'Gaji Awal'),
        ('increment', 'Kenaikan Gaji'),
        ('promotion', 'Promosi'),
        ('adjustment', 'Penyesuaian'),
        ('termination', 'Berakhir Kontrak'),
    ], string='Alasan', required=True)
    
    description = fields.Text(string='Deskripsi')
    
    created_by = fields.Many2one('res.users', string='Dibuat oleh', default=lambda self: self.env.user)
    created_date = fields.Datetime(string='Tanggal Dibuat', default=fields.Datetime.now)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    _order = 'employee_id, effective_date desc'

    @api.model
    def track_salary_change(self, employee_id, basic_salary, allowance, reason, description=''):
        """Log salary change"""
        old_history = self.search([
            ('employee_id', '=', employee_id),
        ], order='effective_date desc', limit=1)
        
        # Only create if actually different
        if old_history and old_history.basic_salary == basic_salary and old_history.allowance == allowance:
            return False
        
        return self.create({
            'employee_id': employee_id,
            'basic_salary': basic_salary,
            'allowance': allowance,
            'effective_date': fields.Date.today(),
            'reason': reason,
            'description': description,
        })
