import base64
import csv
import io
from odoo import models, fields
from odoo.exceptions import UserError


class BpjsReportWizard(models.TransientModel):
    _name = 'outsource.bpjs.report.wizard'
    _description = 'Laporan BPJS Bulanan'

    year = fields.Integer(
        string='Tahun', required=True,
        default=lambda self: fields.Date.today().year)
    month = fields.Selection([
        ('1','Januari'), ('2','Februari'), ('3','Maret'),
        ('4','April'),   ('5','Mei'),      ('6','Juni'),
        ('7','Juli'),    ('8','Agustus'),  ('9','September'),
        ('10','Oktober'),('11','November'),('12','Desember'),
    ], string='Bulan', required=True,
       default=lambda self: str(fields.Date.today().month))

    file_data = fields.Binary(string='File CSV', readonly=True)
    filename  = fields.Char(readonly=True)
    state = fields.Selection(
        [('draft', 'Form'), ('done', 'Selesai')], default='draft')

    def action_export_bpjs(self):
        self.ensure_one()
        employees = self.env['hr.employee'].search([('active', '=', True)])
        if not employees:
            raise UserError('Tidak ada karyawan aktif.')

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'NIK', 'Nama', 'Klien penempatan',
            'No. BPJS Kesehatan', 'No. BPJS TK',
            'JHT', 'JP', 'JKK', 'JKM',
            'Status PTKP', 'Nilai PTKP',
        ])
        for emp in employees:
            writer.writerow([
                emp.identification_id or '',
                emp.name,
                emp.outsource_client_id.name if hasattr(emp, 'outsource_client_id') and emp.outsource_client_id else '',
                emp.bpjs_kesehatan_number if hasattr(emp, 'bpjs_kesehatan_number') else '',
                emp.bpjs_tk_number if hasattr(emp, 'bpjs_tk_number') else '',
                'Ya' if hasattr(emp, 'bpjs_tk_jht') and emp.bpjs_tk_jht else 'Tidak',
                'Ya' if hasattr(emp, 'bpjs_tk_jp')  and emp.bpjs_tk_jp  else 'Tidak',
                'Ya' if hasattr(emp, 'bpjs_tk_jkk') and emp.bpjs_tk_jkk else 'Tidak',
                'Ya' if hasattr(emp, 'bpjs_tk_jkm') and emp.bpjs_tk_jkm else 'Tidak',
                emp.ptkp_status if hasattr(emp, 'ptkp_status') else '',
                int(emp.ptkp_amount) if hasattr(emp, 'ptkp_amount') else 0,
            ])

        filename = 'bpjs_%s_%02d.csv' % (self.year, int(self.month))
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
