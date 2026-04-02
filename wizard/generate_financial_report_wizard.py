from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class GenerateFinancialReportWizard(models.TransientModel):
    _name = 'generate.financial.report.wizard'
    _description = 'Wizard untuk Generate Laporan Keuangan'

    report_type = fields.Selection(
        [
            ('profit_loss', 'Profit & Loss (P&L)'),
            ('balance_sheet', 'Balance Sheet'),
            ('cash_flow', 'Cash Flow'),
            ('trial_balance', 'Trial Balance'),
        ],
        string='Tipe Laporan',
        default='profit_loss',
        required=True
    )
    
    period_start = fields.Date(
        string='Tanggal Mulai',
        default=lambda self: datetime(datetime.now().year, datetime.now().month, 1).date(),
        required=True
    )
    
    period_end = fields.Date(
        string='Tanggal Akhir',
        default=lambda self: datetime.now().date(),
        required=True
    )

    @api.constrains('period_start', 'period_end')
    def _check_date_range(self):
        for rec in self:
            if rec.period_start > rec.period_end:
                raise ValidationError('Tanggal mulai harus lebih awal dari tanggal akhir!')

    def action_generate_report(self):
        self.ensure_one()
        
        # Create financial report record
        report_obj = self.env['financial.report'].create({
            'name': f"Laporan {self.get_report_type_display()} - {self.period_start} s/d {self.period_end}",
            'report_type': self.report_type,
            'period_start': self.period_start,
            'period_end': self.period_end,
        })
        
        # Return the created report
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'model': 'financial.report',
            'res_id': report_obj.id,
        }
