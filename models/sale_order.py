from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    contract_number  = fields.Char('No. kontrak', copy=False)
    contract_type    = fields.Selection([
        ('fixed',        'Fixed price'),
        ('timesheet',    'Per jam'),
        ('milestone',    'Per milestone'),
        ('subscription', 'Langganan bulanan'),
    ], string='Tipe billing', default='fixed')
    po_number_client = fields.Char('No. PO klien')
    pph23_applicable = fields.Boolean('Kenakan PPh 23?', default=True)
    pph23_rate = fields.Selection([
        ('0.02', '2% — punya NPWP'),
        ('0.04', '4% — tanpa NPWP'),
    ], string='Tarif PPh 23', default='0.02')
    pph23_amount = fields.Float(
        'Estimasi PPh 23',
        compute='_compute_pph23_amount', store=True)

    outsource_lead_id = fields.Many2one(
        'crm.lead', 'CRM Lead', copy=False, readonly=True)
    outsource_project_id = fields.Many2one(
        'project.project', 'Proyek', copy=False, readonly=True)

    @api.depends('amount_untaxed', 'pph23_applicable', 'pph23_rate')
    def _compute_pph23_amount(self):
        for o in self:
            if o.pph23_applicable and o.pph23_rate:
                o.pph23_amount = o.amount_untaxed * float(o.pph23_rate)
            else:
                o.pph23_amount = 0.0

    def action_confirm(self):
        for o in self:
            if not o.contract_number:
                o.contract_number = (
                    self.env['ir.sequence'].next_by_code('outsource.contract') or '/')
        return super().action_confirm()

    def action_create_outsource_project(self):
        """Create a project from this Sales Order and link both ways."""
        self.ensure_one()
        if self.outsource_project_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'project.project',
                'res_id': self.outsource_project_id.id,
                'view_mode': 'form',
                'target': 'current',
            }
        project = self.env['project.project'].create({
            'name': self.name or self.contract_number or self.partner_id.name,
            'partner_id': self.partner_id.id,
            'outsource_sale_order_id': self.id,
            'outsource_lead_id': self.outsource_lead_id.id or False,
            'contract_number': self.contract_number,
            'billing_type': self.contract_type,
            'po_number_client': self.po_number_client,
        })
        self.outsource_project_id = project
        if self.outsource_lead_id:
            self.outsource_lead_id.outsource_project_id = project
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'project.project',
            'res_id': project.id,
            'view_mode': 'form',
            'target': 'current',
        }
