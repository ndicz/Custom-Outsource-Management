from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime


class OperationalExpense(models.Model):
    _name = 'operational.expense'
    _description = 'Pengeluaran Operasional'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    name = fields.Char(string='Deskripsi', required=True)
    reference = fields.Char(string='Nomor Referensi', copy=False, default='New')
    
    expense_date = fields.Date(string='Tanggal Pengeluaran', required=True, default=fields.Date.today)
    
    expense_type = fields.Selection([
        ('rent', 'Sewa Office/Tempat'),
        ('utilities', 'Listrik/Air/Gas'),
        ('transport', 'Transport/BBM'),
        ('communication', 'Komunikasi/Internet'),
        ('maintenance', 'Maintenance/Perbaikan'),
        ('equipment', 'Peralatan Kantor'),
        ('supplies', 'Supplies/ATK'),
        ('meals', 'Makanan/Minuman'),
        ('travel', 'Perjalanan Dinas'),
        ('professional', 'Fee Profesional'),
        ('insurance', 'Asuransi'),
        ('other', 'Lainnya'),
    ], string='Tipe Pengeluaran', required=True)
    
    amount = fields.Float(string='Jumlah', required=True)
    
    project_id = fields.Many2one('project.project', string='Project/Client', 
        help='Jika ada, expense di-charge ke project')
    
    employee_id = fields.Many2one('hr.employee', string='Karyawan', 
        help='Jika reimbursement')
    
    vendor_id = fields.Many2one('res.partner', string='Vendor/Supplier')
    
    description = fields.Text(string='Catatan')
    
    attachment_ids = fields.Many2many('ir.attachment', string='Bukti/Receipt')
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('posted', 'Posted'),
    ], string='Status', default='draft', tracking=True)
    
    move_id = fields.Many2one('account.move', string='Journal Entry', readonly=True)
    
    posted_date = fields.Datetime(string='Tanggal Posted')
    approved_by = fields.Many2one('res.users', string='Approved By')
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    _order = 'expense_date desc'
    
    @api.model
    def create(self, vals):
        if vals.get('reference', 'New') == 'New':
            vals['reference'] = self.env['ir.sequence'].next_by_code('operational.expense') or 'New'
        return super().create(vals)
    
    def action_submit(self):
        self.write({'state': 'submitted'})
    
    def action_verify(self):
        self.write({'state': 'verified'})
    
    def action_approve(self):
        self.write({
            'state': 'approved',
            'approved_by': self.env.user.id,
        })
        self._create_journal_entry()
    
    def action_post(self):
        self.write({
            'state': 'posted',
            'posted_date': fields.Datetime.now(),
        })
    
    def _create_journal_entry(self):
        """Create accounting entry untuk expense"""
        for rec in self:
            if rec.move_id:
                continue
            
            # Get expense account berdasarkan type
            expense_account_map = {
                'rent': 'expense_rent_account_id',
                'utilities': 'expense_utilities_account_id',
                'transport': 'expense_transport_account_id',
                'communication': 'expense_communication_account_id',
                'maintenance': 'expense_maintenance_account_id',
                'equipment': 'expense_equipment_account_id',
                'supplies': 'expense_supplies_account_id',
                'meals': 'expense_meals_account_id',
                'travel': 'expense_travel_account_id',
                'professional': 'expense_professional_account_id',
                'insurance': 'expense_insurance_account_id',
                'other': 'expense_other_account_id',
            }
            
            account_param = expense_account_map.get(rec.expense_type, 'expense_other_account_id')
            expense_account_id = self.env['ir.config_parameter'].sudo().get_param(
                f'outsource_custom.{account_param}')
            
            if not expense_account_id:
                raise ValueError(f'Expense account untuk {rec.expense_type} tidak dikonfigurasi')
            
            # Debit: Expense Account
            debit_lines = [(0, 0, {
                'account_id': int(expense_account_id),
                'debit': rec.amount,
                'credit': 0,
                'name': rec.name,
                'analytic_account_id': rec.project_id.analytic_account_id.id if rec.project_id else False,
            })]
            
            # Credit: Cash/Bank Account
            bank_account_id = self.env['ir.config_parameter'].sudo().get_param(
                'outsource_custom.expense_payment_account_id')
            
            if not bank_account_id:
                raise ValueError('Bank/Cash account tidak dikonfigurasi')
            
            debit_lines.append((0, 0, {
                'account_id': int(bank_account_id),
                'debit': 0,
                'credit': rec.amount,
                'name': f"Pembayaran {rec.name}",
            }))
            
            move = self.env['account.move'].create({
                'move_type': 'entry',
                'date': rec.expense_date,
                'line_ids': debit_lines,
                'ref': rec.reference,
            })
            
            rec.move_id = move.id
            move.action_post()


class EmployeeReimbursement(models.Model):
    _name = 'employee.reimbursement'
    _description = 'Penggantian Dana Karyawan'
    _inherit = 'operational.expense'
    
    employee_id = fields.Many2one('hr.employee', string='Karyawan', required=True)
    
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not args:
            args = []
        return self._search(args, offset=0, limit=limit, order=self._order, access_rights_uid=name_get_uid), True
