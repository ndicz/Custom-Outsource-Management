from odoo import models, fields, api


class CrmLeadOutsource(models.Model):
    _inherit = 'crm.lead'

    outsource_contract_type = fields.Selection([
        ('fixed',        'Fixed price'),
        ('timesheet',    'Per jam'),
        ('milestone',    'Per milestone'),
        ('subscription', 'Langganan bulanan'),
    ], string='Tipe billing', default='fixed')

    outsource_sale_order_id = fields.Many2one(
        'sale.order', 'Sales Order', copy=False, readonly=True)

    outsource_project_id = fields.Many2one(
        'project.project', 'Proyek', copy=False, readonly=True)

    # ------------------------------------------------------------------ #
    #  Actions                                                             #
    # ------------------------------------------------------------------ #

    def action_create_outsource_sale_order(self):
        """Create a Sale Order from this lead and link it back."""
        self.ensure_one()
        if self.outsource_sale_order_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sale.order',
                'res_id': self.outsource_sale_order_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        so = self.env['sale.order'].create({
            'partner_id': self.partner_id.id,
            'contract_type': self.outsource_contract_type or 'fixed',
            'po_number_client': self.name,
            'outsource_lead_id': self.id,
        })
        self.outsource_sale_order_id = so
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'res_id': so.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_view_outsource_project(self):
        """Open the linked project."""
        self.ensure_one()
        if not self.outsource_project_id:
            return {}
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': self.outsource_project_id.id,
            'view_mode': 'form',
            'target': 'current',
        }
