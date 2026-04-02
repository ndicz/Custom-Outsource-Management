from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class GenerateClientProfitabilityWizard(models.TransientModel):
    _name = 'generate.client.profitability.wizard'
    _description = 'Wizard untuk Generate Laporan Profitabilitas Client'

    partner_id = fields.Many2one(
        'res.partner',
        string='Client',
        required=True,
    )
    
    project_id = fields.Many2one(
        'project.project',
        string='Project (Optional)',
        domain="[('partner_id', '=', partner_id)]"
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

    def action_generate_profitability(self):
        self.ensure_one()
        
        # Create client profitability record
        profitability_obj = self.env['client.profitability'].create({
            'name': f"{self.partner_id.name} - Profitabilitas - {self.period_start} s/d {self.period_end}",
            'partner_id': self.partner_id.id,
            'project_id': self.project_id.id if self.project_id else False,
            'period_start': self.period_start,
            'period_end': self.period_end,
        })
        
        # Return the created profitability record
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'model': 'client.profitability',
            'res_id': profitability_obj.id,
        }
