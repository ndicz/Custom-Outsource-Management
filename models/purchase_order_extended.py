from odoo import models, fields, api
from datetime import datetime


class PurchaseOrderEnhanced(models.Model):
    _inherit = 'purchase.order'
    
    project_id = fields.Many2one('project.project', string='Project/Client', 
        help='Link ke project untuk cost center tracking')
    analytic_account_id = fields.Many2one('account.analytic.account', 
        string='Cost Center', compute='_compute_analytic', store=True)
    
    cost_category = fields.Selection([
        ('material', 'Bahan Baku'),
        ('service', 'Jasa/Subkon'),
        ('operational', 'Operasional'),
        ('equipment', 'Peralatan'),
    ], string='Kategori Biaya', default='material')
    
    billable = fields.Boolean(string='Bagian dari Tagihan Client?', help='Jika YES, akan di-charge ke client')
    
    @api.depends('project_id')
    def _compute_analytic(self):
        for rec in self:
            if rec.project_id:
                rec.analytic_account_id = rec.project_id.analytic_account_id
            else:
                rec.analytic_account_id = False


class PurchaseOrderLineEnhanced(models.Model):
    _inherit = 'purchase.order.line'
    
    project_id = fields.Many2one('project.project', string='Project', 
        related='order_id.project_id', store=True)
    is_billable = fields.Boolean('Billable', related='order_id.billable', store=True)
    cost_category = fields.Selection(selection=[
        ('material', 'Bahan Baku'),
        ('service', 'Jasa/Subkon'),
        ('operational', 'Operasional'),
        ('equipment', 'Peralatan'),
    ], related='order_id.cost_category', store=True)
