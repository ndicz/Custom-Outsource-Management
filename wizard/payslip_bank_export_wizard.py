from odoo import models, fields, api
from datetime import datetime
import base64
from io import StringIO
import csv


class PayslipBankExportWizard(models.TransientModel):
    _name = 'payslip.bank.export.wizard'
    _description = 'Export Payslip untuk Pembayaran Bank'

    payroll_period_id = fields.Many2one('hr.payroll.period', string='Periode Payroll', required=True)
    
    export_format = fields.Selection([
        ('csv', 'CSV Standard'),
        ('mandiri', 'Mandiri'),
        ('bca', 'BCA'),
        ('bri', 'BRI'),
    ], string='Format Bank', default='csv')
    
    include_approved_only = fields.Boolean('Hanya Approved Slips', default=True)
    
    file_content = fields.Binary(string='File', readonly=True)
    file_name = fields.Char(string='Nama File', readonly=True)

    def action_export(self):
        """Generate export file"""
        slips = self.payroll_period_id.payslip_ids
        
        if self.include_approved_only:
            slips = slips.filtered(lambda s: s.state == 'finance_approved')
        
        if not slips:
            raise ValueError('Tidak ada slip gaji untuk diekspor di periode ini')
        
        if self.export_format == 'csv':
            content = self._export_csv(slips)
            filename = f'payroll_export_{self.payroll_period_id.year}_{self.payroll_period_id.month}.csv'
        else:
            content = self._export_bank_format(slips)
            filename = f'payroll_{self.export_format}_{self.payroll_period_id.year}_{self.payroll_period_id.month}.txt'
        
        self.write({
            'file_content': base64.b64encode(content.encode('utf-8')),
            'file_name': filename,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'payslip.bank.export.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    def _export_csv(self, slips):
        """Export CSV standard format"""
        output = StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'No. Slip', 'Nama Karyawan', 'Rekening Bank', 'Jenis Rekening',
            'Gaji Bersih', 'Tanggal', 'Catatan'
        ])
        
        for slip in slips:
            emp = slip.employee_id
            writer.writerow([
                slip.name,
                emp.name,
                getattr(emp, 'bank_account_id', '').acc_number or '',
                getattr(emp, 'bank_account_id', '').bank_id.name or '',
                slip.net_salary,
                slip.date_to,
                f"Gaji {slip.date_from} - {slip.date_to}",
            ])
        
        return output.getvalue()

    def _export_bank_format(self, slips):
        """Export per format bank specifik"""
        if self.export_format == 'mandiri':
            return self._export_mandiri(slips)
        elif self.export_format == 'bca':
            return self._export_bca(slips)
        elif self.export_format == 'bri':
            return self._export_bri(slips)
        return ''

    def _export_mandiri(self, slips):
        """Format export Bank Mandiri"""
        # Mandiri format: nama|rek|jumlah
        output = []
        for slip in slips:
            emp = slip.employee_id
            rek = getattr(emp, 'bank_account_id', '').acc_number or ''
            output.append(f"{emp.name}|{rek}|{int(slip.net_salary)}")
        return '\n'.join(output)

    def _export_bca(self, slips):
        """Format export BCA"""
        # BCA format: KLIRING dengan header
        output = ["CLRG", "HEADER", "001", "GAJI"]
        for idx, slip in enumerate(slips, 1):
            emp = slip.employee_id
            rek = getattr(emp, 'bank_account_id', '').acc_number or ''
            output.append(f"{idx:06d}|{emp.name}|{rek}|{int(slip.net_salary)}")
        return '\n'.join(output)

    def _export_bri(self, slips):
        """Format export BRI"""
        # BRI format
        output = []
        for slip in slips:
            emp = slip.employee_id
            rek = getattr(emp, 'bank_account_id', '').acc_number or ''
            output.append(f"{emp.name}={rek}={int(slip.net_salary)}")
        return '\n'.join(output)
