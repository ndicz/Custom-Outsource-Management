# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PaymentDashboard(models.Model):
    """Payment Dashboard - Summary of all payment statuses"""
    _name = 'payment.dashboard'
    _description = 'Payment Dashboard'
    _auto = False

    # Summary counts
    salary_pending_count = fields.Integer('Salary Payments Pending', compute='_compute_dashboard')
    vendor_pending_count = fields.Integer('Vendor Invoices Pending', compute='_compute_dashboard')
    pending_proof_count = fields.Integer('Pending Payment Proofs', compute='_compute_dashboard')
    overdue_count = fields.Integer('Overdue Payments', compute='_compute_dashboard')
    reconciled_today_count = fields.Integer('Reconciled Today', compute='_compute_dashboard')
    
    # Summary amounts
    salary_pending_amount = fields.Monetary('Salary Pending Amount', compute='_compute_dashboard',
        currency_field='company_currency_id')
    vendor_pending_amount = fields.Monetary('Vendor Pending Amount', compute='_compute_dashboard',
        currency_field='company_currency_id')
    overdue_amount = fields.Monetary('Overdue Amount', compute='_compute_dashboard',
        currency_field='company_currency_id')
    
    company_currency_id = fields.Many2one('res.currency', compute='_compute_company_currency')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('company_id')
    def _compute_company_currency(self):
        for record in self:
            record.company_currency_id = record.company_id.currency_id

    @api.depends_context('company')
    def _compute_dashboard(self):
        """Compute all dashboard metrics"""
        company = self.env.company
        
        for record in self:
            # Salary payments pending (ready to pay)
            salary_ready = self.env['hr.payroll.payment.run'].search([
                ('company_id', '=', company.id),
                ('state', 'in', ['ready', 'processing']),
            ])
            record.salary_pending_count = len(salary_ready)
            record.salary_pending_amount = sum(salary_ready.mapped('total_amount'))
            
            # Vendor invoices pending payment
            vendor_pending = self.env['account.invoice.incoming'].search([
                ('company_id', '=', company.id),
                ('state', 'in', ['posted', 'verified', 'approved', 'scheduled']),
                ('balance_due', '>', 0),
            ])
            record.vendor_pending_count = len(vendor_pending)
            record.vendor_pending_amount = sum(vendor_pending.mapped('balance_due'))
            
            # Pending payment proofs (uploaded but not reconciled)
            pending_proof = self.env['hr.payroll.payment.run'].search([
                ('company_id', '=', company.id),
                ('state', '=', 'completed'),
            ])
            record.pending_proof_count = len(pending_proof)
            
            # Overdue payments
            today = fields.Date.today()
            overdue_invoices = self.env['account.invoice.incoming'].search([
                ('company_id', '=', company.id),
                ('due_date', '<', today),
                ('state', '!=', 'paid'),
                ('balance_due', '>', 0),
            ])
            record.overdue_count = len(overdue_invoices)
            record.overdue_amount = sum(overdue_invoices.mapped('balance_due'))
            
            # Reconciled today
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            reconciled_today = self.env['hr.payroll.payment.run'].search([
                ('company_id', '=', company.id),
                ('state', '=', 'reconciled'),
            ])
            # Filter by date if available
            reconciled_today = reconciled_today.filtered(lambda x: x.reconciliation_date and 
                today_start <= x.reconciliation_date <= today_end)
            record.reconciled_today_count = len(reconciled_today)

    @api.model
    def get_dashboard_data(self):
        """Return dashboard data for frontend widget"""
        dashboard = self.search([], limit=1)
        if not dashboard:
            dashboard = self.create({})
        
        return {
            'salary_pending_count': dashboard.salary_pending_count,
            'vendor_pending_count': dashboard.vendor_pending_count,
            'pending_proof_count': dashboard.pending_proof_count,
            'overdue_count': dashboard.overdue_count,
            'reconciled_today_count': dashboard.reconciled_today_count,
            'salary_pending_amount': dashboard.salary_pending_amount,
            'vendor_pending_amount': dashboard.vendor_pending_amount,
            'overdue_amount': dashboard.overdue_amount,
        }


class PaymentReconciliationReport(models.Model):
    """Payment Reconciliation Report - Track payment posting to GL"""
    _name = 'payment.reconciliation.report'
    _description = 'Payment Reconciliation Report'
    _auto = False
    _order = 'payment_date desc'

    payment_date = fields.Date('Payment Date')
    payment_type = fields.Selection([
        ('salary', 'Salary Payment'),
        ('vendor', 'Vendor Payment'),
    ], string='Payment Type')
    payment_ref = fields.Char('Payment Reference')
    amount = fields.Monetary('Amount', currency_field='currency_id')
    gl_account = fields.Char('GL Account')
    debit_amount = fields.Monetary('Debit', currency_field='currency_id')
    credit_amount = fields.Monetary('Credit', currency_field='currency_id')
    posted_date = fields.Date('Posted Date')
    gl_status = fields.Selection([
        ('posted', 'Posted'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ], string='GL Status')
    proof_date = fields.Date('Proof Upload Date')
    variance = fields.Monetary('Variance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.model
    def _query(self):
        """Generate reconciliation report query"""
        query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY hpr.payment_date DESC) as id,
            hpr.payment_date,
            'salary' as payment_type,
            hpr.name as payment_ref,
            hpr.total_amount as amount,
            'Salary Expense / Bank' as gl_account,
            CASE WHEN am.id IS NOT NULL THEN hpr.total_amount ELSE 0 END as debit_amount,
            CASE WHEN am.id IS NOT NULL THEN hpr.total_amount ELSE 0 END as credit_amount,
            am.date as posted_date,
            CASE WHEN am.state = 'posted' THEN 'posted' ELSE 'pending' END as gl_status,
            hpr.payment_date_actual as proof_date,
            ABS(hpr.total_amount - hpr.payment_amount) as variance
        FROM hr_payroll_payment_run hpr
        LEFT JOIN account_move am ON am.id = hpr.invoice_id
        
        UNION ALL
        
        SELECT
            ROW_NUMBER() OVER (ORDER BY aii.invoice_date DESC) as id,
            aii.invoice_date AS payment_date,
            'vendor' as payment_type,
            aii.vendor_invoice_number as payment_ref,
            aii.total_amount as amount,
            'Expense / Accounts Payable' as gl_account,
            CASE WHEN am.id IS NOT NULL THEN aii.total_amount ELSE 0 END as debit_amount,
            CASE WHEN am.id IS NOT NULL THEN aii.total_amount ELSE 0 END as credit_amount,
            am.date as posted_date,
            CASE WHEN am.state = 'posted' THEN 'posted' ELSE 'pending' END as gl_status,
            aii.payment_date as proof_date,
            0 as variance
        FROM account_invoice_incoming aii
        LEFT JOIN account_move am ON am.id = aii.invoice_id
        """
        return query

    @api.model
    def query_get(self, domain=None, context=None):
        return self._query()


class PaymentAgingReport(models.Model):
    """Payment Aging Report - Track overdue and upcoming payments"""
    _name = 'payment.aging.report'
    _description = 'Payment Aging Report'
    _auto = False
    _order = 'due_date asc'

    invoice_ref = fields.Char('Invoice Reference')
    due_date = fields.Date('Due Date')
    days_overdue = fields.Integer('Days Overdue', compute='_compute_days_overdue')
    vendor_name = fields.Char('Vendor Name')
    amount = fields.Monetary('Amount', currency_field='currency_id')
    paid_amount = fields.Monetary('Paid Amount', currency_field='currency_id')
    balance_due = fields.Monetary('Balance Due', currency_field='currency_id')
    payment_status = fields.Char('Status')
    aging_bucket = fields.Selection([
        ('current', 'Current (Not Due)'),
        ('1-30', '1-30 Days Overdue'),
        ('31-60', '31-60 Days Overdue'),
        ('61-90', '61-90 Days Overdue'),
        ('90plus', '90+ Days Overdue'),
    ], string='Aging Bucket', compute='_compute_aging_bucket')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.depends('due_date')
    def _compute_days_overdue(self):
        """Calculate days overdue"""
        today = fields.Date.today()
        for record in self:
            if record.due_date:
                days = (today - record.due_date).days
                record.days_overdue = max(0, days)
            else:
                record.days_overdue = 0

    @api.depends('days_overdue')
    def _compute_aging_bucket(self):
        """Categorize into aging buckets"""
        for record in self:
            if record.days_overdue == 0 and record.due_date > fields.Date.today():
                record.aging_bucket = 'current'
            elif 1 <= record.days_overdue <= 30:
                record.aging_bucket = '1-30'
            elif 31 <= record.days_overdue <= 60:
                record.aging_bucket = '31-60'
            elif 61 <= record.days_overdue <= 90:
                record.aging_bucket = '61-90'
            else:
                record.aging_bucket = '90plus'

    @api.model
    def _query(self):
        """Generate aging report query"""
        query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY aii.due_date ASC) as id,
            aii.vendor_invoice_number as invoice_ref,
            aii.due_date,
            CAST((CURRENT_DATE - aii.due_date) AS INTEGER) as days_overdue,
            rp.name as vendor_name,
            aii.total_amount as amount,
            aii.paid_amount,
            aii.balance_due,
            aii.state as payment_status
        FROM account_invoice_incoming aii
        LEFT JOIN res_partner rp ON rp.id = aii.vendor_id
        WHERE aii.state NOT IN ('draft', 'cancel')
        ORDER BY aii.due_date ASC
        """
        return query

    @api.model
    def query_get(self, domain=None, context=None):
        return self._query()


class GLPostingVerificationReport(models.Model):
    """GL Posting Verification Report - Verify all GL entries"""
    _name = 'gl.posting.verification.report'
    _description = 'GL Posting Verification Report'
    _auto = False
    _order = 'posting_date desc'

    payment_ref = fields.Char('Payment Reference')
    payment_type = fields.Selection([
        ('salary', 'Salary Payment'),
        ('vendor', 'Vendor Payment'),
    ], string='Payment Type')
    posting_date = fields.Date('Posting Date')
    gl_account = fields.Char('GL Account')
    account_name = fields.Char('Account Name')
    debit = fields.Monetary('Debit', currency_field='currency_id')
    credit = fields.Monetary('Credit', currency_field='currency_id')
    posting_status = fields.Selection([
        ('balanced', 'Balanced ✓'),
        ('unbalanced', 'Unbalanced ✗'),
    ], string='Status')
    payment_amount = fields.Monetary('Payment Amount', currency_field='currency_id')
    variance = fields.Monetary('Variance', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    @api.model
    def _query(self):
        """Generate GL posting query"""
        query = """
        SELECT
            ROW_NUMBER() OVER (ORDER BY am.date DESC) as id,
            am.name as payment_ref,
            CASE WHEN hpr.id IS NOT NULL THEN 'salary' ELSE 'vendor' END as payment_type,
            am.date as posting_date,
            aa.code as gl_account,
            aa.name as account_name,
            CASE WHEN aml.debit > 0 THEN aml.debit ELSE 0 END as debit,
            CASE WHEN aml.credit > 0 THEN aml.credit ELSE 0 END as credit,
            CASE WHEN am.state = 'posted' THEN 'balanced' ELSE 'unbalanced' END as posting_status,
            COALESCE(hpr.total_amount, aii.total_amount) as payment_amount,
            0 as variance
        FROM account_move am
        LEFT JOIN account_move_line aml ON aml.move_id = am.id
        LEFT JOIN account_account aa ON aa.id = aml.account_id
        LEFT JOIN hr_payroll_payment_run hpr ON hpr.invoice_id = am.id
        LEFT JOIN account_invoice_incoming aii ON aii.invoice_id = am.id
        WHERE am.state = 'posted'
        AND (hpr.id IS NOT NULL OR aii.id IS NOT NULL)
        ORDER BY am.date DESC
        """
        return query

    @api.model
    def query_get(self, domain=None, context=None):
        return self._query()
