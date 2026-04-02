from odoo import models, fields, api


class ClientProfitabilityAnalysis(models.Model):
    _name = 'client.profitability'
    _description = 'Analisis Profitabilitas per Client'
    
    name = fields.Char(string='Nama Laporan', compute='_compute_name', store=True)
    
    partner_id = fields.Many2one('res.partner', string='Client', required=True)
    project_id = fields.Many2one('project.project', string='Project', 
        domain="[('partner_id', '=', partner_id)]")
    
    period_start = fields.Date(string='Periode Mulai', required=True)
    period_end = fields.Date(string='Periode Akhir', required=True)
    
    # Revenue
    revenue_total = fields.Float(compute='_compute_revenue', store=False)
    invoice_count = fields.Integer(compute='_compute_revenue', store=False)
    
    # Costs
    cogs_material = fields.Float(compute='_compute_costs', store=False)
    service_cost = fields.Float(compute='_compute_costs', store=False)
    allocated_salary = fields.Float(compute='_compute_costs', store=False)
    allocated_overhead = fields.Float(compute='_compute_costs', store=False)
    total_cost = fields.Float(compute='_compute_costs', store=False)
    
    # Profitability
    gross_profit = fields.Float(compute='_compute_metrics', store=False)
    gross_margin_pct = fields.Float(compute='_compute_metrics', store=False)
    net_profit = fields.Float(compute='_compute_metrics', store=False)
    net_margin_pct = fields.Float(compute='_compute_metrics', store=False)
    
    # Analysis
    avg_invoice_value = fields.Float(compute='_compute_metrics', store=False)
    cost_per_invoice = fields.Float(compute='_compute_metrics', store=False)
    profitability_ratio = fields.Float(compute='_compute_metrics', store=False)
    
    analysis_html = fields.Html(compute='_compute_analysis_html', store=False)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.depends('partner_id', 'period_start', 'period_end')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id and rec.period_start:
                period = rec.period_start.strftime('%B %Y')
                rec.name = f"{rec.partner_id.name} - {period}"
            else:
                rec.name = 'Profitability Analysis'
    
    @api.depends('period_start', 'period_end', 'partner_id', 'project_id')
    def _compute_revenue(self):
        for rec in self:
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', rec.period_start),
                ('invoice_date', '<=', rec.period_end),
                ('partner_id', '=', rec.partner_id.id),
            ]
            
            if rec.project_id:
                domain.append(('analytic_account_id', '=', rec.project_id.analytic_account_id.id))
            
            invoices = self.env['account.move'].search(domain)
            rec.revenue_total = sum(invoices.mapped('amount_untaxed'))
            rec.invoice_count = len(invoices)
    
    @api.depends('period_start', 'period_end', 'partner_id', 'project_id')
    def _compute_costs(self):
        for rec in self:
            analytic_account_id = False
            if rec.project_id:
                analytic_account_id = rec.project_id.analytic_account_id.id
            
            # COGS: Purchases yang billable untuk client
            po_domain = [
                ('state', '=', 'done'),
                ('date_order', '>=', rec.period_start),
                ('date_order', '<=', rec.period_end),
                ('partner_id', '=', rec.partner_id.id),
                ('billable', '=', True),
            ]
            
            if analytic_account_id:
                po_domain.append(('analytic_account_id', '=', analytic_account_id))
            
            pos = self.env['purchase.order'].search(po_domain)
            rec.cogs_material = sum(pos.mapped('amount_untaxed'))
            
            # Service costs
            service_pos = self.env['purchase.order'].search([
                ('state', '=', 'done'),
                ('date_order', '>=', rec.period_start),
                ('date_order', '<=', rec.period_end),
                ('partner_id', '=', rec.partner_id.id),
                ('cost_category', '=', 'service'),
            ])
            rec.service_cost = sum(service_pos.mapped('amount_untaxed'))
            
            # Allocated salary (simplified: % of project time)
            # Formula: Total Salary * (Project Hours / Total Hours) - simplified as average
            rec.allocated_salary = 0
            
            # Allocated overhead (simplified: 10% of COGS)
            rec.allocated_overhead = rec.cogs_material * 0.10
            
            rec.total_cost = rec.cogs_material + rec.service_cost + rec.allocated_salary + rec.allocated_overhead
    
    @api.depends('revenue_total', 'total_cost')
    def _compute_metrics(self):
        for rec in self:
            rec.gross_profit = rec.revenue_total - rec.total_cost
            
            if rec.revenue_total > 0:
                rec.gross_margin_pct = (rec.gross_profit / rec.revenue_total) * 100
                rec.net_margin_pct = (rec.gross_profit / rec.revenue_total) * 100
            else:
                rec.gross_margin_pct = 0
                rec.net_margin_pct = 0
            
            rec.net_profit = rec.gross_profit
            
            if rec.invoice_count > 0:
                rec.avg_invoice_value = rec.revenue_total / rec.invoice_count
                rec.cost_per_invoice = rec.total_cost / rec.invoice_count
            else:
                rec.avg_invoice_value = 0
                rec.cost_per_invoice = 0
            
            if rec.total_cost > 0:
                rec.profitability_ratio = rec.gross_profit / rec.total_cost
            else:
                rec.profitability_ratio = 0
    
    def _compute_analysis_html(self):
        for rec in self:
            html = f"""
            <div style="font-family: Arial; padding: 20px;">
                <h2>ANALISIS PROFITABILITAS CLIENT</h2>
                <h3>{rec.partner_id.name}</h3>
                <p>Periode: {rec.period_start} s/d {rec.period_end}</p>
                
                <h4>SUMMARY FINANSIAL</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f0f0f0;">
                        <td style="border: 1px solid #ccc; padding: 8px;"><b>Metrik</b></td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;"><b>Nilai</b></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Revenue Total</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.revenue_total:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">  - COGS (Material)</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.cogs_material:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">  - Service Cost</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.service_cost:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">  - Allocated Overhead</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.allocated_overhead:,.0f}</td>
                    </tr>
                    <tr style="background-color: #e8f4f8;">
                        <td style="border: 1px solid #ccc; padding: 8px;"><b>PROFIT</b></td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold;">Rp {rec.gross_profit:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Profit Margin %</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;"><b>{rec.gross_margin_pct:.2f}%</b></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Profitability Ratio</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{rec.profitability_ratio:.2f}x</td>
                    </tr>
                </table>
                
                <h4 style="margin-top: 20px;">METRIK PER INVOICE</h4>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #f0f0f0;">
                        <td style="border: 1px solid #ccc; padding: 8px;"><b>Metrik</b></td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;"><b>Nilai</b></td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Jumlah Invoice</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{rec.invoice_count}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Avg Invoice Value</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.avg_invoice_value:,.0f}</td>
                    </tr>
                    <tr>
                        <td style="border: 1px solid #ccc; padding: 8px;">Cost per Invoice</td>
                        <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp {rec.cost_per_invoice:,.0f}</td>
                    </tr>
                </table>
                
                <p style="margin-top: 20px; font-size: 12px; color: #666;">
                    Generated: {rec.create_date.strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
            """
            rec.analysis_html = html
