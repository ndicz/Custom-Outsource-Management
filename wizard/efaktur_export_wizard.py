import base64
import csv
import io
from odoo import models, fields
from odoo.exceptions import UserError


class EfakturExportWizard(models.TransientModel):
    _name = 'outsource.efaktur.export.wizard'
    _description = 'Export e-Faktur ke CSV DJP Online'

    date_from = fields.Date(
        string='Dari tanggal', required=True,
        default=lambda self: fields.Date.today().replace(day=1)
    )
    date_to   = fields.Date(
        string='Sampai tanggal', required=True,
        default=fields.Date.today
    )
    file_data = fields.Binary(string='File CSV', readonly=True)
    filename  = fields.Char(readonly=True)
    state = fields.Selection(
        [('draft', 'Form'), ('done', 'Selesai')], default='draft')

    def action_export(self):
        self.ensure_one()
        invoices = self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('invoice_date', '>=', self.date_from),
            ('invoice_date', '<=', self.date_to),
            ('state', '=', 'posted'),
        ])
        if not invoices:
            raise UserError('Tidak ada invoice untuk periode ini.')

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'No. Invoice', 'Tanggal', 'Klien', 'NPWP Klien',
            'DPP', 'PPN 11%', 'No. Faktur Pajak', 'Status',
        ])
        for inv in invoices:
            ppn = inv.amount_tax
            writer.writerow([
                inv.name or '',
                str(inv.invoice_date) if inv.invoice_date else '',
                inv.partner_id.name or '',
                inv.partner_id.npwp if hasattr(inv.partner_id, 'npwp') else '',
                int(inv.amount_untaxed),
                int(ppn),
                inv.efaktur_number if hasattr(inv, 'efaktur_number') else '',
                inv.efaktur_status if hasattr(inv, 'efaktur_status') else 'draft',
            ])

        filename = 'efaktur_%s_%s.csv' % (self.date_from, self.date_to)
        self.write({
            'file_data': base64.b64encode(
                output.getvalue().encode('utf-8')),
            'filename': filename,
            'state': 'done',
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }
