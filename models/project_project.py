from odoo import models, fields, api
from datetime import date


class ProjectProject(models.Model):
    _inherit = 'project.project'

    sla_start_date = fields.Date('Mulai SLA')
    sla_end_date   = fields.Date('Berakhir SLA')
    sla_status = fields.Selection([
        ('on_track', 'On track'),
        ('at_risk',  'At risk'),
        ('breached', 'Breached'),
    ], string='Status SLA', compute='_compute_sla_status', store=True)

    contract_number  = fields.Char('No. kontrak')
    billing_type     = fields.Char('Tipe billing')
    po_number_client = fields.Char('No. PO klien')

    placed_employee_ids = fields.One2many(
        'hr.employee', 'outsource_project_id', 'Karyawan ditempatkan')

    @api.depends('sla_end_date')
    def _compute_sla_status(self):
        today = date.today()
        for p in self:
            if not p.sla_end_date:
                p.sla_status = 'on_track'
            elif (p.sla_end_date - today).days > 7:
                p.sla_status = 'on_track'
            elif (p.sla_end_date - today).days >= 0:
                p.sla_status = 'at_risk'
            else:
                p.sla_status = 'breached'
