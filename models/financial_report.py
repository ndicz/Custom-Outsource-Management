from odoo import models, fields, api
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class FinancialReport(models.Model):
    _name = 'financial.report'
    _description = 'Laporan Keuangan (P&L, Balance Sheet)'
    
    name = fields.Char(string='Nama Laporan', compute='_compute_name', store=True)
    
    report_type = fields.Selection([
        ('profit_loss', 'Profit & Loss'),
        ('balance_sheet', 'Balance Sheet'),
        ('cash_flow', 'Cash Flow'),
        ('trial_balance', 'Trial Balance'),
    ], string='Tipe Laporan', required=True)
    
    period_start = fields.Date(string='Periode Mulai', required=True)
    period_end = fields.Date(string='Periode Akhir', required=True)
    
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    # Computed fields for P&L
    revenue_total = fields.Float(compute='_compute_revenue', store=False)
    revenue_by_client = fields.Text(compute='_compute_revenue_detail', store=False)
    
    cogs_total = fields.Float(compute='_compute_cogs', store=False)
    gross_profit = fields.Float(compute='_compute_gross_profit', store=False)
    gross_margin_pct = fields.Float(compute='_compute_gross_margin', store=False)
    
    salary_expense = fields.Float(compute='_compute_expenses', store=False)
    other_expenses = fields.Float(compute='_compute_expenses', store=False)
    total_expenses = fields.Float(compute='_compute_expenses', store=False)
    
    ebit = fields.Float(compute='_compute_ebit', store=False)
    tax_expense = fields.Float(compute='_compute_tax', store=False)
    net_income = fields.Float(compute='_compute_net_income', store=False)
    
    # Generated report
    report_html = fields.Html(compute='_compute_report_html', store=False)
    
    @api.depends('report_type', 'period_start', 'period_end')
    def _compute_name(self):
        for rec in self:
            period = rec.period_start.strftime('%B %Y') if rec.period_start else 'N/A'
            report_name = dict(self._fields['report_type'].selection).get(rec.report_type, 'Report')
            rec.name = f"{report_name} - {period}"
    
    @api.depends('period_start', 'period_end')
    def _compute_revenue(self):
        for rec in self:
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', rec.period_start),
                ('invoice_date', '<=', rec.period_end),
                ('company_id', '=', rec.company_id.id),
            ])
            rec.revenue_total = sum(invoices.mapped('amount_untaxed'))
    
    def _compute_revenue_detail(self):
        for rec in self:
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', rec.period_start),
                ('invoice_date', '<=', rec.period_end),
                ('company_id', '=', rec.company_id.id),
            ])
            
            revenue_by_partner = {}
            for inv in invoices:
                partner_name = inv.partner_id.name
                revenue_by_partner[partner_name] = revenue_by_partner.get(partner_name, 0) + inv.amount_untaxed
            
            html = "<ul>"
            for partner, amount in revenue_by_partner.items():
                html += f"<li>{partner}: Rp {amount:,.0f}</li>"
            html += "</ul>"
            
            rec.revenue_by_client = html
    
    @api.depends('period_start', 'period_end')
    def _compute_cogs(self):
        for rec in self:
            # Cost of Goods Sold = Purchase of billable items
            purchases = self.env['purchase.order'].search([
                ('state', '=', 'done'),
                ('date_order', '>=', rec.period_start),
                ('date_order', '<=', rec.period_end),
                ('billable', '=', True),
                ('company_id', '=', rec.company_id.id),
            ])
            rec.cogs_total = sum(purchases.mapped('amount_untaxed'))
    
    @api.depends('revenue_total', 'cogs_total')
    def _compute_gross_profit(self):
        for rec in self:
            rec.gross_profit = rec.revenue_total - rec.cogs_total
    
    @api.depends('revenue_total', 'cogs_total')
    def _compute_gross_margin(self):
        for rec in self:
            if rec.revenue_total > 0:
                rec.gross_margin_pct = (rec.gross_profit / rec.revenue_total) * 100
            else:
                rec.gross_margin_pct = 0
    
    @api.depends('period_start', 'period_end')
    def _compute_expenses(self):
        for rec in self:
            # Salary expenses from payroll
            payslips = self.env['outsource.payslip'].search([
                ('state', '=', 'done'),
                ('date_from', '>=', rec.period_start),
                ('date_to', '<=', rec.period_end),
            ])
            rec.salary_expense = sum(payslips.mapped('gross_salary'))
            
            # Other operational expenses
            exp_account = self.env['ir.config_parameter'].sudo().get_param(
                'outsource_custom.other_expense_account')
            if exp_account:
                moves = self.env['account.move.line'].search([
                    ('account_id', '=', int(exp_account)),
                    ('move_id.date', '>=', rec.period_start),
                    ('move_id.date', '<=', rec.period_end),
                    ('move_id.state', '=', 'posted'),
                ])
                rec.other_expenses = sum(m.debit for m in moves)
            else:
                rec.other_expenses = 0
            
            rec.total_expenses = rec.salary_expense + rec.other_expenses
    
    @api.depends('gross_profit', 'total_expenses')
    def _compute_ebit(self):
        for rec in self:
            rec.ebit = rec.gross_profit - rec.total_expenses
    
    @api.depends('ebit')
    def _compute_tax(self):
        for rec in self:
            # PPh badan (simplified): 21% EBIT - excluding PPh21 sudah ada
            if rec.ebit > 50000000:  # Corporate tax threshold
                rec.tax_expense = rec.ebit * 0.21
            else:
                rec.tax_expense = 0
    
    @api.depends('ebit', 'tax_expense')
    def _compute_net_income(self):
        for rec in self:
            rec.net_income = rec.ebit - rec.tax_expense
    
    def _compute_report_html(self):
        for rec in self:
            if rec.report_type == 'profit_loss':
                rec.report_html = rec._generate_pl_report()
            elif rec.report_type == 'balance_sheet':
                rec.report_html = rec._generate_bs_report()
    
    def _generate_pl_report(self):
        """Generate P&L HTML report"""
        html = f"""
        <div style="font-family: Arial; padding: 20px;">
            <h2>LAPORAN LABA RUGI (P&L)</h2>
            <h4>Periode: {self.period_start} s/d {self.period_end}</h4>
            
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f0f0f0;">
                    <td style="border: 1px solid #ccc; padding: 8px;">PENDAPATAN</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Total Revenue</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.revenue_total:,.0f}</td>
                </tr>
                
                <tr style="background-color: #f9f9f9;">
                    <td style="border: 1px solid #ccc; padding: 8px;"><b>BEBAN POKOK PENJUALAN</b></td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  COGS (Purchase)</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.cogs_total:,.0f}</td>
                </tr>
                
                <tr style="background-color: #e8f4f8;">
                    <td style="border: 1px solid #ccc; padding: 8px;"><b>LABA BRUTO</b></td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold;">{self.gross_profit:,.0f}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Margin %</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.gross_margin_pct:.2f}%</td>
                </tr>
                
                <tr style="background-color: #ffe8e8;">
                    <td style="border: 1px solid #ccc; padding: 8px;"><b>BEBAN OPERASIONAL</b></td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">Rp</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Beban Gaji</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.salary_expense:,.0f}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Beban Operasional Lain</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.other_expenses:,.0f}</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Total Beban</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.total_expenses:,.0f}</td>
                </tr>
                
                <tr style="background-color: #e8e8f8;">
                    <td style="border: 1px solid #ccc; padding: 8px;"><b>EBIT (Operating Income)</b></td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right; font-weight: bold;">{self.ebit:,.0f}</td>
                </tr>
                
                <tr>
                    <td style="border: 1px solid #ccc; padding: 8px;">  Pajak Penghasilan (21%)</td>
                    <td style="border: 1px solid #ccc; padding: 8px; text-align: right;">{self.tax_expense:,.0f}</td>
                </tr>
                
                <tr style="background-color: #d4f1d4; font-weight: bold; font-size: 16px;">
                    <td style="border: 2px solid #333; padding: 8px;">LABA BERSIH</td>
                    <td style="border: 2px solid #333; padding: 8px; text-align: right;">{self.net_income:,.0f}</td>
                </tr>
            </table>
        </div>
        """
        return html
    
    def _generate_bs_report(self):
        """Generate Balance Sheet HTML report"""
        html = """
        <div style="font-family: Arial; padding: 20px;">
            <h2>NERACA (Balance Sheet)</h2>
            <p><em>Coming Soon</em> - Membutuhkan account balances calculation</p>
        </div>
        """
        return html
