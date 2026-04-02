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
