from odoo import api, models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Compatibility field for legacy domains that still use ('customer', '=', True).
    customer = fields.Boolean(
        string='Customer (Legacy)',
        compute='_compute_customer_legacy',
        search='_search_customer_legacy',
        store=True,
    )

    npwp    = fields.Char('NPWP', size=20)
    is_pkp  = fields.Boolean('PKP?', default=False)
    client_type = fields.Selection([
        ('jasa',        'Jasa saja'),
        ('barang',      'Barang saja'),
        ('jasa_barang', 'Jasa + Barang'),
    ], string='Tipe klien', default='jasa')
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic account')

    @api.depends('customer_rank')
    def _compute_customer_legacy(self):
        for rec in self:
            rec.customer = bool(rec.customer_rank and rec.customer_rank > 0)

    def _search_customer_legacy(self, operator, value):
        if operator in ('=', '=='):
            return [('customer_rank', '>', 0)] if value else [('customer_rank', '=', 0)]
        if operator in ('!=', '<>'):
            return [('customer_rank', '=', 0)] if value else [('customer_rank', '>', 0)]
        return [('customer_rank', '>', 0)]
