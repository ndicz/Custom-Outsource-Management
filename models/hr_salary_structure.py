from odoo import models, fields, api


class HrSalaryStructure(models.Model):
    _name = 'hr.salary.structure'
    _description = 'Struktur Gaji'
    
    name = fields.Char(string='Nama Struktur', required=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    
    # Salary components for this structure
    salary_component_ids = fields.Many2many(
        'hr.salary.component',
        'hr_salary_structure_component_rel',
        'structure_id', 'component_id',
        string='Komponen Gaji'
    )
    
    # Employee category/level this structure applies to
    category = fields.Selection([
        ('staff', 'Staff'),
        ('manager', 'Manager'),
        ('executive', 'Executive'),
        ('internship', 'Magang'),
    ], string='Kategori Karyawan')
    
    is_default = fields.Boolean(string='Default')
    active = fields.Boolean(default=True)
    
    notes = fields.Text(string='Catatan')
    
    def get_components(self, category=None):
        """Get components untuk structure ini"""
        components = self.salary_component_ids
        if category:
            components = components.filtered(lambda c: c.category == category)
        return components.sorted(key=lambda c: c.sequence)
