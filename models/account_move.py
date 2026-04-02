from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    efaktur_number = fields.Char('No. faktur pajak', copy=False)
    efaktur_status = fields.Selection([
        ('draft',     'Belum'),
        ('generated', 'Sudah generate'),
        ('uploaded',  'Sudah upload DJP'),
    ], string='Status e-Faktur', default='draft', copy=False)

    contract_number  = fields.Char('No. kontrak', copy=False)
    po_number_client = fields.Char('No. PO klien')

    pph23_withheld = fields.Boolean('PPh 23 dipotong klien?', default=False)
    pph23_rate = fields.Selection([
        ('0.02', '2%'), ('0.04', '4%'),
    ], string='Tarif PPh 23', default='0.02')
    pph23_amount   = fields.Float('PPh 23', compute='_compute_pph23', store=True)
    amount_received = fields.Float('Diterima (net)', compute='_compute_pph23', store=True)

    coretax_status = fields.Selection([
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('uploaded', 'Uploaded'),
        ('failed', 'Failed'),
    ], string='Coretax Status', default='draft', copy=False, readonly=True)
    coretax_response = fields.Text('Coretax Response', readonly=True)
    coretax_uploaded_at = fields.Datetime('Coretax Uploaded At', readonly=True)

    @api.depends('amount_untaxed', 'amount_total', 'pph23_withheld', 'pph23_rate')
    def _compute_pph23(self):
        for m in self:
            if m.pph23_withheld and m.pph23_rate:
                m.pph23_amount   = m.amount_untaxed * float(m.pph23_rate)
                m.amount_received = m.amount_total - m.pph23_amount
            else:
                m.pph23_amount   = 0.0
                m.amount_received = m.amount_total

    def action_generate_efaktur(self):
        for m in self:
            m.efaktur_status = 'generated'
            m.coretax_status = 'generated'
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'e-Faktur',
                'message': 'Berhasil. Download CSV dari menu Outsource → Export e-Faktur.',
                'type': 'success',
            }
        }

    def _prepare_coretax_payload(self):
        self.ensure_one()
        partner = self.partner_id
        return {
            'invoice_number': self.name,
            'invoice_date': str(self.invoice_date) if self.invoice_date else False,
            'partner_name': partner.name,
            'partner_npwp': partner.npwp,
            'amount_untaxed': float(self.amount_untaxed or 0.0),
            'amount_tax': float(self.amount_tax or 0.0),
            'amount_total': float(self.amount_total or 0.0),
            'pph23_amount': float(self.pph23_amount or 0.0),
            'efaktur_number': self.efaktur_number or '',
            'efaktur_status': self.efaktur_status or '',
            'contract_number': self.contract_number or '',
            'po_number_client': self.po_number_client or '',
        }

    def action_upload_coretax(self):
        import requests
        config = self.env['ir.config_parameter'].sudo()
        api_url = config.get_param('outsource_custom.coretax_api_url', default='https://api.coretax.co.id/v1/efaktur')
        api_key = config.get_param('outsource_custom.coretax_api_key')

        if not api_key:
            raise ValueError('Silakan konfigurasi Coretax API Key di Settings > General Settings.')

        for move in self:
            if move.move_type not in ('out_invoice', 'out_refund'):
                raise ValueError('Hanya invoice keluar yang dapat di-upload ke Coretax.')
            if move.efaktur_status != 'generated':
                raise ValueError('Generate e-Faktur terlebih dahulu sebelum upload ke Coretax.')

            payload = move._prepare_coretax_payload()
            headers = {
                'Authorization': 'Bearer %s' % api_key,
                'Content-Type': 'application/json',
            }

            try:
                res = requests.post(api_url, json=payload, headers=headers, timeout=60)
                text = res.text
                if res.status_code in (200, 201):
                    move.coretax_status = 'uploaded'
                    move.coretax_uploaded_at = fields.Datetime.now()
                    move.coretax_response = text
                    move.efaktur_status = 'uploaded'
                else:
                    move.coretax_status = 'failed'
                    move.coretax_response = '%s\n%s' % (res.status_code, text)
                    raise ValueError('Upload Coretax gagal: %s' % text)
            except Exception as e:
                move.coretax_status = 'failed'
                move.coretax_response = str(e)
                raise

