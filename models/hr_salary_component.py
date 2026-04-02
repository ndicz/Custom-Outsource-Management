from odoo import models, fields, api


class HrSalaryComponent(models.Model):
    _name = 'hr.salary.component'
    _description = 'Komponen Gaji'

    name = fields.Char(string='Nama Komponen', required=True)
    code = fields.Char(string='Kode', required=True, unique=True)
    category = fields.Selection([
        ('earning', 'Penghasilan'),
        ('deduction', 'Potongan'),
        ('tax', 'Pajak'),
        ('advance', 'Uang Muka'),
    ], string='Kategori', required=True)
    
    amount_type = fields.Selection([
        ('fixed', 'Tetap'),
        ('percentage', 'Persentase'),
        ('formula', 'Formula'),
    ], string='Tipe Jumlah', default='fixed')
    
    percentage_base = fields.Selection([
        ('basic', 'Gaji Pokok'),
        ('gross', 'Gaji Kotor'),
        ('net', 'Gaji Bersih'),
    ], string='Base Persentase')
    
    formula_code = fields.Text(string='Formula Python (optional)', 
        help="Contoh: employee.basic_salary * 0.05")
    
    compute_method = fields.Selection([
        ('manual', 'Manual Input'),
        ('auto', 'Otomatis dari Formula'),
        ('attendance', 'Dari Attendance'),
    ], string='Cara Hitung', default='manual')
    
    sequence = fields.Integer(string='Urutan', default=10)
    is_default = fields.Boolean(string='Default Komponen')
    
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)

    _order = 'sequence, name'
    
    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Kode komponen harus unik!')
    ]
