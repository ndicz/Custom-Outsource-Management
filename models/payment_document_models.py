"""
PAYMENT & DOCUMENT MANAGEMENT SYSTEM
outsource_custom v18.0.5.0.0

Models untuk:
1. Salary Payment Distribution
2. Vendor Payment Management (with 3-way match)
3. Document Generation (Invoices, SPK, Receipts)
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
from lxml import etree
import base64
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import num2words

# ============================================================================
# TIER 1: SALARY PAYMENT AUTOMATION
# ============================================================================

class HrPayrollPaymentRun(models.Model):
    """
    Salary Payment Run - Manages salary distribution to employees
    Handles bank file generation (ABC format) and payment reconciliation
    """
    _name = 'hr.payroll.payment.run'
    _description = 'Salary Payment Run'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== FIELDS ==========
    name = fields.Char('Reference', readonly=True)
    period_id = fields.Many2one('hr.payroll.period', required=True, string='Payroll Period')
    
    # Payment details
    payment_date = fields.Date('Payment Date', required=True)
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('digital_wallet', 'Digital Wallet')
    ], default='bank_transfer', required=True)
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account',
        domain=[('account_type', '=', 'bank')], required=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('reconciled', 'Reconciled')
    ], default='draft', string='Status', tracking=True)
    
    # Amounts
    total_amount = fields.Monetary(compute='_compute_totals', string='Total Amount')
    payment_amount = fields.Monetary('Actual Payment Amount')
    variance = fields.Monetary(compute='_compute_variance', string='Variance')
    
    # Bank file
    bank_file = fields.Binary('Bank File (ABC Format)', readonly=True)
    bank_file_name = fields.Char('File Name', readonly=True)
    bank_file_format = fields.Selection([
        ('abc', 'ABC Format'),
        ('csv', 'CSV Format'),
        ('swift', 'SWIFT MT101')
    ], default='abc', string='Bank Format')
    
    # Upload proof
    payment_proof = fields.Binary('Payment Proof/Receipt')
    payment_proof_name = fields.Char('Proof File Name')
    payment_date_actual = fields.Date('Actual Payment Date')
    payment_reference = fields.Char('Payment Reference Number')
    
    # Reconciliation
    reconciliation_status = fields.Selection([
        ('not_reconciled', 'Not Reconciled'),
        ('partial', 'Partially Reconciled'),
        ('full', 'Fully Reconciled'),
        ('error', 'Reconciliation Error')
    ], compute='_compute_reconciliation_status', string='Reconciliation Status')
    
    reconciliation_date = fields.Datetime('Reconciliation Date', readonly=True)
    reconciliation_notes = fields.Text('Reconciliation Notes')
    
    # Child records
    payslip_ids = fields.Many2many('outsource.payslip', 
        compute='_compute_payslips', string='Payslips in this Run',
        help="All payslips in the selected payroll period")
    
    payment_line_ids = fields.One2many('hr.payroll.payment.line', 'payment_run_id',
        string='Payment Details')
    
    # Invoice link (for accounting)
    invoice_id = fields.Many2one('account.move', string='GL Entry Reference')
    
    # Audit fields
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Datetime(string='Approved Date')
    bank_file_generated_date = fields.Datetime(string='Bank File Generated')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # ========== COMPUTED FIELDS ==========
    
    @api.depends('period_id')
    def _compute_payslips(self):
        for run in self:
            if run.period_id:
                run.payslip_ids = self.env['outsource.payslip'].search([
                    ('period_id', '=', run.period_id.id),
                    ('state', 'in', ['verified', 'approved', 'posted'])
                ])
            else:
                run.payslip_ids = []

    @api.depends('payslip_ids')
    def _compute_totals(self):
        for run in self:
            run.total_amount = sum(run.payslip_ids.mapped('net_salary'))

    @api.depends('total_amount', 'payment_amount')
    def _compute_variance(self):
        for run in self:
            run.variance = run.total_amount - run.payment_amount

    def _compute_reconciliation_status(self):
        for run in self:
            if run.state not in ['completed', 'reconciled']:
                run.reconciliation_status = 'not_reconciled'
            else:
                # Check how many payslips reconciled in payment_line_ids
                if not run.payment_line_ids:
                    run.reconciliation_status = 'not_reconciled'
                else:
                    reconciled_count = len(run.payment_line_ids.filtered(
                        lambda x: x.reconciliation_status == 'reconciled'))
                    total_count = len(run.payment_line_ids)
                    
                    if reconciled_count == 0:
                        run.reconciliation_status = 'not_reconciled'
                    elif reconciled_count == total_count:
                        run.reconciliation_status = 'full'
                    else:
                        run.reconciliation_status = 'partial'

    # ========== METHODS ==========
    
    @api.model
    def create(self, vals):
        """Auto-generate name for payment run"""
        if not vals.get('name'):
            period = self.env['hr.payroll.period'].browse(vals.get('period_id'))
            if period:
                vals['name'] = f"PAY-RUN-{period.name.replace(' ', '')}-{datetime.now().strftime('%d%m%Y')}"
        return super().create(vals)

    def action_prepare_for_payment(self):
        """Validate all required conditions before generating bank file"""
        for run in self:
            # Validate payroll period
            if not run.period_id:
                raise ValidationError("Payroll period is required")
            
            # Validate payslips are approved
            unverified_payslips = run.payslip_ids.filtered(lambda x: x.state != 'verified')
            if unverified_payslips:
                raise ValidationError(
                    f"Not all payslips are verified. Found {len(unverified_payslips)} unverified payslips."
                )
            
            # Validate total amount > 0
            if run.total_amount <= 0:
                raise ValidationError("Total amount must be greater than 0")
            
            # Validate payment date
            if run.payment_date < datetime.now().date():
                raise ValidationError("Payment date cannot be in the past")
            
            # Validate bank account
            if not run.bank_account_id:
                raise ValidationError("Bank account is required")
            
            # Create payment lines from payslips
            run._create_payment_lines()
            
            # Set status
            run.state = 'ready'
            run.message_post(body="Payment run prepared and ready for bank file generation")

    def _create_payment_lines(self):
        """Create payment detail lines from payslips"""
        self.ensure_one()
        
        # Delete existing lines
        self.payment_line_ids.unlink()
        
        # Create new lines from payslips
        for payslip in self.payslip_ids:
            self.env['hr.payroll.payment.line'].create({
                'payment_run_id': self.id,
                'payslip_id': payslip.id,
                'employee_id': payslip.employee_id.id,
                'bank_account_number': payslip.employee_id.bank_account_id.acc_number if payslip.employee_id.bank_account_id else '',
                'bank_account_holder': payslip.employee_id.name,
                'payment_amount': payslip.net_salary,
                'reference': payslip.name,
            })

    def action_generate_bank_file(self):
        """Generate bank file in ABC format"""
        for run in self:
            if run.state != 'ready':
                raise ValidationError("Payment run must be in 'Ready' state to generate bank file")
            
            if run.bank_file_format == 'abc':
                file_content = run._generate_abc_format()
            elif run.bank_file_format == 'csv':
                file_content = run._generate_csv_format()
            elif run.bank_file_format == 'swift':
                file_content = run._generate_swift_format()
            else:
                raise ValidationError("Invalid bank file format")
            
            # Save to model
            run.bank_file = base64.b64encode(file_content.encode('utf-8'))
            run.bank_file_name = f"PaymentRun-{run.name}-{datetime.now().strftime('%d%m%Y-%H%M%S')}.txt"
            run.bank_file_generated_date = datetime.now()
            run.state = 'processing'
            
            run.message_post(
                body=f"Bank file generated: {run.bank_file_name}",
                attachment_ids=[]
            )

    def _generate_abc_format(self):
        """
        Generate ABC format (most common Indonesian format)
        Format: Header | Detail lines | Footer
        """
        self.ensure_one()
        
        lines = []
        
        # Header record
        header_date = datetime.now().strftime('%d%m%Y')
        header_time = datetime.now().strftime('%H%M%S')
        bank_code = self.bank_account_id.bank_id.code or '0000'
        
        # Header format: RECORD_TYPE | BANK_CODE | DATE | TIME | DESTINATION_CODE
        header = f"101{bank_code:<4}PAYROLL{header_date}{header_time}SALARY{'':70}\n"
        lines.append(header)
        
        # Detail records
        detail_line_no = 0
        total_lines = 0
        total_amount = 0
        
        for i, payment_line in enumerate(self.payment_line_ids, 1):
            detail_line_no = i
            total_amount += payment_line.payment_amount
            
            # Detail record format
            detail = self._format_abc_detail_line(
                line_no=i,
                payment_line=payment_line,
                date_str=header_date
            )
            lines.append(detail + "\n")
            total_lines = i
        
        # Footer record
        footer = self._format_abc_footer(
            total_lines=total_lines,
            total_amount=total_amount
        )
        lines.append(footer)
        
        return "".join(lines)

    def _format_abc_detail_line(self, line_no, payment_line, date_str):
        """Format single detail line for ABC"""
        # Detail record: RECORD_TYPE | SEQUENCE | BANK_CODE | BRANCH_CODE | 
        #               ACCOUNT_NUMBER | AMOUNT | REFERENCE | CLIENT_ID | ADDITIONAL_INFO
        
        record_type = "110"  # Detail record
        sequence = f"{line_no:06d}"
        bank_code = self.bank_account_id.bank_id.code or '0000'
        branch_code = self.bank_account_id.bank_branch_code or '0001'
        
        # Recipient bank details (we don't know, so use 0000)
        recipient_bank_code = "0000"
        recipient_branch_code = "0001"
        
        # Account number (clean: remove spaces and special chars)
        account_number = payment_line.bank_account_number.replace(' ', '').replace('-', '')[:20]
        
        # Amount (in rupiah, right-aligned, zero-padded, no decimals)
        amount = f"{int(payment_line.payment_amount):015d}"
        
        # Reference (payslip number, max 20 chars)
        reference = payment_line.reference[:20].ljust(20)
        
        # Client ID / Customer name (max 30 chars)
        customer_name = payment_line.bank_account_holder[:30].ljust(30)
        
        # Combine all fields
        detail = f"{record_type}{sequence}{bank_code:<4}{branch_code:<4}" \
                f"{recipient_bank_code:<4}{recipient_branch_code:<4}" \
                f"{account_number:<20}{amount}{reference}{customer_name}"
        
        return detail

    def _format_abc_footer(self, total_lines, total_amount):
        """Format footer for ABC"""
        record_type = "090"  # Footer record
        total_records = f"{total_lines:06d}"
        total_amount_str = f"{int(total_amount):015d}"
        reserved = "".ljust(30)  # Reserved field
        
        footer = f"{record_type}{total_records}{total_amount_str}{reserved}"
        return footer

    def _generate_csv_format(self):
        """Generate CSV format (alternative)"""
        self.ensure_one()
        
        lines = ["No.,Employee,Account Number,Bank,Amount,Reference,Date"]
        
        for i, payment_line in enumerate(self.payment_line_ids, 1):
            line = f"{i},{payment_line.bank_account_holder}," \
                   f"{payment_line.bank_account_number}," \
                   f"{self.bank_account_id.bank_id.name}," \
                   f"{payment_line.payment_amount}," \
                   f"{payment_line.reference}," \
                   f"{self.payment_date.strftime('%d/%m/%Y')}"
            lines.append(line)
        
        return "\n".join(lines)

    def _generate_swift_format(self):
        """Generate SWIFT MT101 format (for international)"""
        self.ensure_one()
        
        # Simplified SWIFT format (MT101 is complex, simplified here)
        lines = []
        
        lines.append(":20:PAYRUN" + self.name[-10:])
        lines.append(":23B:CRED")
        lines.append(f":32A:{self.payment_date.strftime('%y%m%d')}IDR{self.total_amount:,.2f}")
        lines.append(f":50A:{self.env.company.name}")
        lines.append(f":70:{self.name}")
        
        for payment_line in self.payment_line_ids:
            lines.append(f":50K:{payment_line.bank_account_holder}")
            lines.append(f":56A:{self.bank_account_id.bank_id.code}")
            lines.append(f":57A:{self.bank_account_id.inv_acc_id}")
            lines.append(f":59:{payment_line.bank_account_number}")
            lines.append(f":32B:IDR{payment_line.payment_amount:,.2f}")
            lines.append(":70:" + payment_line.reference)
            lines.append("-")
        
        return "\n".join(lines)

    def action_upload_payment_proof(self):
        """User uploads payment proof (bank receipt/confirmation)"""
        for run in self:
            if not run.payment_proof:
                raise ValidationError("Please upload payment proof (receipt from bank)")
            
            if not run.payment_date_actual:
                raise ValidationError("Actual payment date is required")
            
            if not run.payment_reference:
                raise ValidationError("Payment reference from bank is required")
            
            run.state = 'completed'
            run.payment_amount = run.total_amount
            run.message_post(
                body=f"Payment marked as completed. Reference: {run.payment_reference}"
            )

    def action_validate_reconciliation(self):
        """Validate payment vs bank statement"""
        for run in self:
            if run.state != 'completed':
                raise ValidationError("Only completed payments can be reconciled")
            
            # Check variance
            if abs(run.variance) > 0.01:  # Allow 1 cent variance
                raise ValidationError(
                    f"Amount variance of {run.variance} found. "
                    "Please verify with bank statement."
                )
            
            run.state = 'reconciled'
            run.reconciliation_notes = "Payment successfully reconciled"
            run.message_post(body="Payment run reconciled successfully")

    def action_reset_to_draft(self):
        """Reset payment run to draft (for corrections)"""
        for run in self:
            if run.state not in ['ready', 'processing']:
                raise ValidationError("Can only reset from Ready or Processing state")
            
            run.state = 'draft'
            run.bank_file = False
            run.payment_line_ids.unlink()
            run.message_post(body="Payment run reset to draft")

    def action_post_gl_entry(self):
        """Post GL entry for salary expense"""
        for run in self:
            if run.state != 'completed':
                raise ValidationError("Only completed payments can be posted to GL")
            
            if run.invoice_id:
                raise ValidationError("GL entry already created for this payment run")
            
            # Create GL entry
            # Dr: Salary Expense
            # Cr: Salary Payable / Bank
            
            salary_expense_account = self.env['account.account'].search(
                [('code', '=', '5111')], limit=1)  # Salary expense
            bank_account = self.env['account.account'].search(
                [('code', '=', '1010')], limit=1)  # Bank account
            
            if not salary_expense_account or not bank_account:
                raise ValidationError("Required GL accounts not configured (5111 for salary, 1010 for bank)")
            
            move = self.env['account.move'].create({
                'date': run.payment_date_actual or run.payment_date,
                'ref': run.name,
                'line_ids': [
                    (0, 0, {
                        'account_id': salary_expense_account.id,
                        'debit': run.total_amount,
                        'credit': 0,
                        'name': f'Salary payment - {run.period_id.name}',
                    }),
                    (0, 0, {
                        'account_id': bank_account.id,
                        'debit': 0,
                        'credit': run.total_amount,
                        'name': f'Salary payment - {run.period_id.name}',
                    }),
                ]
            })
            
            move.action_post()
            run.invoice_id = move.id
            run.message_post(body=f"GL entry created: {move.name}")


class HrPayrollPaymentLine(models.Model):
    """Individual payment line for each employee"""
    _name = 'hr.payroll.payment.line'
    _description = 'Payroll Payment Line'
    
    payment_run_id = fields.Many2one('hr.payroll.payment.run', required=True, 
        ondelete='cascade')
    
    payslip_id = fields.Many2one('outsource.payslip', string='Payslip')
    employee_id = fields.Many2one('hr.employee', required=True)
    
    # Bank details
    bank_account_number = fields.Char('Bank Account Number')
    bank_account_holder = fields.Char('Account Holder Name')
    
    # Payment
    payment_amount = fields.Monetary('Payment Amount')
    reference = fields.Char('Reference Number')
    
    # Reconciliation
    reconciliation_status = fields.Selection([
        ('pending', 'Pending'),
        ('reconciled', 'Reconciled'),
        ('error', 'Error - Amount Mismatch')
    ], default='pending', string='Reconciliation Status')
    
    bank_posting_date = fields.Date('Posted to Bank')
    bank_posting_reference = fields.Char('Bank Reference')
    
    currency_id = fields.Many2one('res.currency', 
        default=lambda self: self.env.company.currency_id)


# ============================================================================
# TIER 2: VENDOR PAYMENT MANAGEMENT (with 3-way match)
# ============================================================================

class AccountInvoiceIncoming(models.Model):
    """Incoming vendor invoices with 3-way matching"""
    _name = 'account.invoice.incoming'
    _description = 'Incoming Vendor Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== FIELDS ==========
    
    name = fields.Char('Invoice Reference', readonly=True)
    
    # Vendor info
    vendor_id = fields.Many2one('res.partner', string='Vendor', required=True,
        domain=[('supplier', '=', True)])
    vendor_invoice_number = fields.Char('Vendor Invoice #', required=True)
    
    # Linked documents
    po_id = fields.Many2one('purchase_order_extended', string='Purchase Order')
    grn_id = fields.Many2one('stock.picking', string='GRN (Goods Receipt Note)')
    
    # Dates
    invoice_date = fields.Date('Invoice Date', required=True)
    due_date = fields.Date('Due Date')
    payment_date = fields.Date('Payment Date')
    
    # Amounts
    subtotal_amount = fields.Monetary('Subtotal')
    tax_amount = fields.Monetary('Tax Amount')
    total_amount = fields.Monetary('Total Amount', required=True)
    paid_amount = fields.Monetary('Paid Amount', compute='_compute_paid_amount')
    balance_due = fields.Monetary('Balance Due', compute='_compute_balance_due')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted in System'),
        ('verified', '3-way Match Verified'),
        ('approved', 'Approved for Payment'),
        ('scheduled', 'Scheduled for Payment'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled')
    ], default='draft', string='Status', tracking=True)
    
    # 3-way match verification
    match_po_ok = fields.Boolean('PO Amount Match', default=False, readonly=True)
    match_grn_ok = fields.Boolean('GRN Quantity Match', default=False, readonly=True)
    match_invoice_ok = fields.Boolean('Invoice Amount Match', default=False, readonly=True)
    all_matches_ok = fields.Boolean('All 3-way Match', compute='_compute_all_matches')
    
    # Match details
    po_amount = fields.Monetary('PO Amount', compute='_compute_po_amount', readonly=True)
    grn_amount = fields.Monetary('GRN Amount', compute='_compute_grn_amount', readonly=True)
    po_grn_variance = fields.Monetary('PO vs GRN Variance', 
        compute='_compute_po_grn_variance', readonly=True)
    po_invoice_variance = fields.Monetary('PO vs Invoice Variance',
        compute='_compute_po_invoice_variance', readonly=True)
    
    # GL entry
    invoice_id = fields.Many2one('account.move', string='GL Entry')
    
    # Lines
    line_ids = fields.One2many('account.invoice.incoming.line', 'invoice_id',
        string='Invoice Lines')
    
    # Notes
    match_notes = fields.Text('Match Verification Notes')
    payment_notes = fields.Text('Payment Notes')
    
    # Audit
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    verified_by = fields.Many2one('res.users', string='Verified By')
    verified_date = fields.Datetime('Verified Date')
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Datetime('Approved Date')
    
    currency_id = fields.Many2one('res.currency',
        default=lambda self: self.env.company.currency_id)

    # ========== COMPUTED FIELDS ==========
    
    @api.depends('po_id')
    def _compute_po_amount(self):
        for invoice in self:
            invoice.po_amount = invoice.po_id.amount_total if invoice.po_id else 0

    @api.depends('grn_id')
    def _compute_grn_amount(self):
        for invoice in self:
            if invoice.grn_id:
                # Calculate total GRN amount based on line items
                grn_amount = 0
                for line in invoice.grn_id.move_line_ids:
                    grn_amount += line.qty_done * line.product_id.standard_price
                invoice.grn_amount = grn_amount
            else:
                invoice.grn_amount = 0

    @api.depends('po_amount', 'grn_amount')
    def _compute_po_grn_variance(self):
        for invoice in self:
            invoice.po_grn_variance = abs(invoice.po_amount - invoice.grn_amount)

    @api.depends('po_amount', 'total_amount')
    def _compute_po_invoice_variance(self):
        for invoice in self:
            invoice.po_invoice_variance = abs(invoice.po_amount - invoice.total_amount)

    @api.depends('match_po_ok', 'match_grn_ok', 'match_invoice_ok')
    def _compute_all_matches(self):
        for invoice in self:
            invoice.all_matches_ok = (
                invoice.match_po_ok and 
                invoice.match_grn_ok and 
                invoice.match_invoice_ok
            )

    @api.depends('state')
    def _compute_paid_amount(self):
        for invoice in self:
            # In production, get from payment records
            invoice.paid_amount = invoice.total_amount if invoice.state == 'paid' else 0

    @api.depends('total_amount', 'paid_amount')
    def _compute_balance_due(self):
        for invoice in self:
            invoice.balance_due = invoice.total_amount - invoice.paid_amount

    # ========== METHODS ==========
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"VIN-{self.env['ir.sequence'].next_by_code('account.invoice.incoming') or '0000'}"
        return super().create(vals)

    def action_verify_3way_match(self):
        """Perform 3-way matching"""
        for invoice in self:
            if not invoice.po_id:
                raise ValidationError("Purchase Order is required for 3-way matching")
            
            if not invoice.grn_id:
                raise ValidationError("GRN (Goods Receipt Note) is required for 3-way matching")
            
            # Check PO amount vs Invoice amount
            po_variance = abs(invoice.po_amount - invoice.total_amount)
            if po_variance <= 100:  # Allow Rp 100 variance
                invoice.match_po_ok = True
                match_po_status = "✅ MATCHED"
            else:
                invoice.match_po_ok = False
                match_po_status = f"⚠️ VARIANCE: Rp {po_variance:,.0f}"
            
            # Check GRN vs Invoice (simplified - check amounts)
            grn_variance = abs(invoice.grn_amount - invoice.total_amount)
            if grn_variance <= 100:
                invoice.match_grn_ok = True
                match_grn_status = "✅ MATCHED"
            else:
                invoice.match_grn_ok = False
                match_grn_status = f"⚠️ VARIANCE: Rp {grn_variance:,.0f}"
            
            # Invoice line items match
            invoice.match_invoice_ok = len(invoice.line_ids) > 0
            match_invoice_status = "✅ OK" if invoice.match_invoice_ok else "❌ No lines"
            
            # Record notes
            notes = f"PO Match: {match_po_status}\n" \
                   f"GRN Match: {match_grn_status}\n" \
                   f"Invoice: {match_invoice_status}"
            invoice.match_notes = notes
            
            # Update state
            if invoice.all_matches_ok:
                invoice.state = 'verified'
                invoice.message_post(body=f"3-way match PASSED\n{notes}")
            else:
                invoice.state = 'posted'
                invoice.message_post(body=f"3-way match FAILED\n{notes}")

    def action_approve_for_payment(self):
        """Approve invoice for payment"""
        for invoice in self:
            if invoice.state != 'verified':
                raise ValidationError("Invoice must be verified before approval")
            
            if not invoice.all_matches_ok:
                raise ValidationError("3-way match must pass before approval")
            
            invoice.state = 'approved'
            invoice.approved_by = self.env.user
            invoice.approved_date = datetime.now()
            invoice.message_post(body="Invoice approved for payment")

    def action_post_gl_entry(self):
        """Post GL entry for vendor invoice"""
        for invoice in self:
            if invoice.state != 'verified':
                raise ValidationError("Invoice must be verified before GL posting")
            
            if invoice.invoice_id:
                raise ValidationError("GL entry already created for this invoice")
            
            # Create GL entry: Dr Expense, Cr Accounts Payable
            expense_account = self.env['account.account'].search(
                [('code', '=', invoice.line_ids[0].account_id.code if invoice.line_ids else '6100')],
                limit=1)
            if not expense_account:
                expense_account = self.env['account.account'].search(
                    [('code', '=', '6100')], limit=1)  # Default expense account
            
            ap_account = self.env['account.account'].search(
                [('code', '=', '2100')], limit=1)  # Accounts Payable
            
            move = self.env['account.move'].create({
                'date': invoice.invoice_date,
                'ref': invoice.vendor_invoice_number,
                'line_ids': [
                    (0, 0, {
                        'account_id': expense_account.id,
                        'debit': invoice.total_amount,
                        'credit': 0,
                        'name': f'Invoice from {invoice.vendor_id.name}',
                    }),
                    (0, 0, {
                        'account_id': ap_account.id,
                        'debit': 0,
                        'credit': invoice.total_amount,
                        'name': f'Payable to {invoice.vendor_id.name}',
                    }),
                ]
            })
            
            move.action_post()
            invoice.invoice_id = move.id
            invoice.state = 'scheduled'
            invoice.message_post(body=f"GL entry created: {move.name}")

    def action_mark_paid(self):
        """Mark invoice as paid"""
        for invoice in self:
            invoice.state = 'paid'
            invoice.paid_amount = invoice.total_amount
            invoice.payment_date = datetime.now().date()
            invoice.message_post(body="Invoice marked as paid")


class AccountInvoiceIncomingLine(models.Model):
    """Individual line items on vendor invoice"""
    _name = 'account.invoice.incoming.line'
    _description = 'Vendor Invoice Line'
    
    invoice_id = fields.Many2one('account.invoice.incoming', required=True, ondelete='cascade')
    
    # Item details
    product_id = fields.Many2one('product.product', string='Product/Service')
    description = fields.Char('Description', required=True)
    quantity = fields.Float('Quantity')
    unit = fields.Char('Unit')
    unit_price = fields.Monetary('Unit Price')
    
    line_amount = fields.Monetary('Line Amount', compute='_compute_amount')
    
    # GL account
    account_id = fields.Many2one('account.account', string='GL Account')
    
    # PO line reference
    po_line_id = fields.Many2one('purchase.order.line', string='PO Line Reference')
    
    currency_id = fields.Many2one('res.currency',
        default=lambda self: self.env.company.currency_id)
    
    @api.depends('quantity', 'unit_price')
    def _compute_amount(self):
        for line in self:
            line.line_amount = line.quantity * line.unit_price


class AccountPaymentRun(models.Model):
    """Grouped vendor payment run"""
    _name = 'account.payment.run'
    _description = 'Vendor Payment Run'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== FIELDS ==========
    
    name = fields.Char('Payment Run #', readonly=True)
    payment_date = fields.Date('Payment Date', required=True)
    
    # Linked invoices
    invoice_ids = fields.Many2many('account.invoice.incoming',
        string='Invoices in this Run')
    
    # Totals
    total_amount = fields.Monetary(compute='_compute_totals', string='Total Amount')
    invoice_count = fields.Integer(compute='_compute_totals', string='# Invoices')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed')
    ], default='draft', tracking=True)
    
    # Bank file
    bank_file = fields.Binary('Bank File')
    bank_file_name = fields.Char('File Name')
    
    currency_id = fields.Many2one('res.currency',
        default=lambda self: self.env.company.currency_id)

    # ========== METHODS ==========
    
    @api.depends('invoice_ids')
    def _compute_totals(self):
        for run in self:
            run.total_amount = sum(run.invoice_ids.mapped('balance_due'))
            run.invoice_count = len(run.invoice_ids)

    def action_generate_payment_file(self):
        """Generate bank file for batch vendor payment"""
        self.ensure_one()
        
        if self.state != 'draft':
            raise ValidationError("Payment run must be in Draft state")
        
        if not self.invoice_ids:
            raise ValidationError("Add at least one invoice to payment run")
        
        # Generate ABC format (similar to payroll)
        file_content = self._generate_payment_file_abc()
        
        self.bank_file = base64.b64encode(file_content.encode('utf-8'))
        self.bank_file_name = f"VendorPayment-{self.name}-{datetime.now().strftime('%d%m%Y')}.txt"
        self.state = 'ready'

    def _generate_payment_file_abc(self):
        """Generate ABC format for vendor payments"""
        lines = []
        
        # Header
        header_date = datetime.now().strftime('%d%m%Y')
        header_time = datetime.now().strftime('%H%M%S')
        header = f"101PAYVENDOR{header_date}{header_time}VENDOR_PAYMENT{'':60}\n"
        lines.append(header)
        
        # Detail lines
        total_amount = 0
        for i, invoice in enumerate(self.invoice_ids, 1):
            amount = int(invoice.balance_due)
            total_amount += amount
            
            # Detail record
            detail = f"110{i:06d}0000000100000000" \
                    f"{invoice.vendor_id.name[:30].ljust(30)}" \
                    f"{amount:015d}" \
                    f"{invoice.vendor_invoice_number[:20].ljust(20)}" \
                    f"{invoice.vendor_id.name[:30].ljust(30)}\n"
            lines.append(detail)
        
        # Footer
        footer = f"090{len(self.invoice_ids):06d}{total_amount:015d}{'':30}"
        lines.append(footer)
        
        return "".join(lines)


# ============================================================================
# TIER 3: DOCUMENT GENERATION (Invoices, SPK, Receipts)
# ============================================================================

class AccountDocumentTemplate(models.Model):
    """Template for document generation"""
    _name = 'account.document.template'
    _description = 'Document Template'
    
    name = fields.Char('Template Name', required=True)
    doc_type = fields.Selection([
        ('invoice', 'Customer Invoice'),
        ('spk', 'Work Order (SPK)'),
        ('receipt', 'Payment Receipt'),
        ('payslip', 'Payslip'),
        ('contract', 'Employment Contract')
    ], required=True, string='Document Type')
    
    # Template content
    template_html = fields.Html('HTML Template')
    template_css = fields.Text('CSS Styling')
    
    # Variables
    help_variables = fields.Text('Available Variables', readonly=True,
        help="Variables available for this template: "
        "{{ company_name }}, {{ company_address }}, etc.")
    
    # Configuration
    active = fields.Boolean(default=True)
    default_template = fields.Boolean('Set as Default',
        help="This template will be used for automatic generation")
    
    # Footer
    footer_text = fields.Html('Footer (Signature Block)')
    
    def get_sample_variables(self, doc_type):
        """Return sample variables for each document type"""
        samples = {
            'invoice': {
                'company_name': 'PT ABC Company',
                'invoice_number': 'INV-2024-001',
                'customer_name': 'PT Pelanggan',
                'total_amount': 'Rp 10,000,000',
            },
            'spk': {
                'employee_name': 'John Doe',
                'job_title': 'Engineer',
                'start_date': '01/04/2024',
                'daily_rate': 'Rp 500,000',
            },
            # Add more...
        }
        return samples.get(doc_type, {})


class SaleInvoiceCustomer(models.Model):
    """Customer billing/invoice"""
    _name = 'sale.invoice.customer'
    _description = 'Customer Invoice'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== FIELDS ==========
    
    name = fields.Char('Invoice #', readonly=True)
    
    # Linked documents
    sale_id = fields.Many2one('sale.order', string='Sales Order')
    
    # Customer
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    
    # Dates
    invoice_date = fields.Date('Invoice Date', default=fields.Date.today)
    due_date = fields.Date('Due Date')
    
    # Description
    description = fields.Text('Description / Services Provided')
    
    # Amounts
    subtotal = fields.Monetary('Subtotal')
    tax_amount = fields.Monetary('Tax Amount')
    total_amount = fields.Monetary('Total Amount', required=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Customer'),
        ('received', 'Received'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], default='draft', tracking=True)
    
    # PDF
    pdf_content = fields.Binary('PDF Invoice', readonly=True)
    pdf_generated_date = fields.Datetime(readonly=True)
    
    # Payment
    payment_date = fields.Date('Payment Date')
    payment_method = fields.Char('Payment Method')
    payment_proof = fields.Binary('Payment Proof')
    
    currency_id = fields.Many2one('res.currency',
        default=lambda self: self.env.company.currency_id)

    # ========== METHODS ==========
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = f"INV-{self.env['ir.sequence'].next_by_code('sale.invoice.customer') or '0000'}"
        return super().create(vals)

    def action_generate_invoice_pdf(self):
        """Generate professional invoice PDF"""
        for invoice in self:
            pdf = invoice._generate_pdf_content()
            invoice.pdf_content = base64.b64encode(pdf)
            invoice.pdf_generated_date = datetime.now()
            invoice.message_post(body="Invoice PDF generated")

    def _generate_pdf_content(self):
        """Generate PDF using ReportLab"""
        # Create file buffer
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#003366'),
            spaceAfter=30)
        
        # Title
        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Spacer(1, 0.3*inch))
        
        # Invoice details table
        invoice_data = [
            ['Invoice #:', self.name, 'Invoice Date:', self.invoice_date.strftime('%d/%m/%Y')],
            ['Customer:', self.customer_id.name, 'Due Date:', (self.due_date or '').strftime('%d/%m/%Y') if self.due_date else ''],
        ]
        
        invoice_table = Table(invoice_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        invoice_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
        ]))
        elements.append(invoice_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Description
        elements.append(Paragraph("<b>Description:</b>", styles['Heading3']))
        elements.append(Paragraph(self.description or 'Services provided', styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Amount table
        amount_data = [
            ['Subtotal:', f'Rp {self.subtotal:,.0f}'],
            ['Tax:', f'Rp {self.tax_amount:,.0f}'],
            ['<b>TOTAL</b>', f'<b>Rp {self.total_amount:,.0f}</b>'],
        ]
        
        amount_table = Table(amount_data, colWidths=[4*inch, 2*inch])
        amount_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightgrey),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        elements.append(amount_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.read()

    def action_send_to_customer(self):
        """Send invoice to customer via email"""
        for invoice in self:
            if not invoice.pdf_content:
                invoice.action_generate_invoice_pdf()
            
            # Compose email (simplified - actual implementation would use Odoo email)
            invoice.state = 'sent'
            invoice.message_post(body="Invoice sent to customer")


class HrWorkOrderSpk(models.Model):
    """Work Order / SPK (Surat Perintah Kerja)"""
    _name = 'hr.work.order.spk'
    _description = 'Work Order (SPK)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    # ========== FIELDS ==========
    
    name = fields.Char('SPK Number', readonly=True)
    
    # Employee & Assignment
    employee_id = fields.Many2one('hr.employee', required=True, string='Employee')
    outsource_client_id = fields.Many2one('res.partner', required=True,
        string='Outsource Client',
        domain=[('outsource_client', '=', True)])
    
    # Job details
    job_title = fields.Char('Job Title', required=True)
    job_description = fields.Text('Job Description')
    location = fields.Char('Work Location')
    
    # Dates
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date')
    total_days = fields.Integer('Total Days', compute='_compute_total_days')
    
    # Compensation
    daily_rate = fields.Monetary('Daily Rate', required=True)
    total_amount = fields.Monetary('Total Compensation', compute='_compute_total_amount')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('signed', 'Signed by Employee'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ], default='draft', tracking=True)
    
    # Documents
    pdf_content = fields.Binary('SPK PDF', readonly=True)
    signed_copy = fields.Binary('Signed Copy')
    signed_date = fields.Date('Signature Date')
    
    # Audit
    created_by = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved By')
    approved_date = fields.Datetime('Approved Date')
    
    currency_id = fields.Many2one('res.currency',
        default=lambda self: self.env.company.currency_id)

    # ========== METHODS ==========
    
    @api.model
    def create(self, vals):
        if not vals.get('name'):
            month = datetime.now().strftime('%m')
            year = datetime.now().strftime('%Y')
            seq = self.env['ir.sequence'].next_by_code('hr.work.order.spk') or '0001'
            vals['name'] = f"SPK-{month}-{year}-{seq}"
        return super().create(vals)

    @api.depends('start_date', 'end_date')
    def _compute_total_days(self):
        for spk in self:
            if spk.start_date and spk.end_date:
                delta = spk.end_date - spk.start_date
                spk.total_days = delta.days + 1  # Inclusive
            else:
                spk.total_days = 0

    @api.depends('daily_rate', 'total_days')
    def _compute_total_amount(self):
        for spk in self:
            spk.total_amount = spk.daily_rate * spk.total_days

    def action_approve_spk(self):
        """Approve SPK"""
        for spk in self:
            spk.state = 'approved'
            spk.approved_by = self.env.user
            spk.approved_date = datetime.now()
            spk.message_post(body="SPK approved")

    def action_generate_spk_pdf(self):
        """Generate SPK PDF for printing and signature"""
        for spk in self:
            pdf = spk._generate_spk_pdf_content()
            spk.pdf_content = base64.b64encode(pdf)
            spk.message_post(body="SPK PDF generated")

    def _generate_spk_pdf_content(self):
        """Generate SPK PDF using ReportLab"""
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        elements = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('Title', parent=styles['Heading1'],
            fontSize=14, textColor=colors.black, alignment=TA_CENTER, spaceAfter=15)
        
        # Title
        elements.append(Paragraph("SURAT PERINTAH KERJA (WORK ORDER)", title_style))
        elements.append(Paragraph(f"SPK No: {self.name}", styles['Normal']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Header info
        header_data = [
            ['Company:', self.env.company.name, 'Date:', self.create_date.strftime('%d/%m/%Y')],
            ['Client:', self.outsource_client_id.name, 'Period:', f"{self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')}"],
        ]
        
        header_table = Table(header_data, colWidths=[1.2*inch, 2.8*inch, 1*inch, 2*inch])
        header_table.setStyle(TableStyle([('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9)]))
        elements.append(header_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Employee & Job details
        elements.append(Paragraph("<b>ASSIGNMENT DETAILS:</b>", styles['Heading3']))
        
        details_data = [
            ['Employee:', self.employee_id.name],
            ['NPWP:', self.employee_id.identification_id or 'N/A'],
            ['Position:', self.job_title],
            ['Location:', self.location or 'N/A'],
            ['Job Description:', self.job_description or 'As per client requirements'],
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 5*inch])
        details_table.setStyle(TableStyle([('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('FONTSIZE', (0, 0), (-1, -1), 9), ('VALIGN', (0, 0), (-1, -1), 'TOP')]))
        elements.append(details_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Compensation
        elements.append(Paragraph("<b>COMPENSATION:</b>", styles['Heading3']))
        comp_data = [
            ['Daily Rate:', f"Rp {self.daily_rate:,.0f}", 'Total Days:', f"{self.total_days} days"],
            ['Total Amount:', f"Rp {self.total_amount:,.0f}", 'Amount in words:', num2words.num2words(int(self.total_amount), lang='id')],
        ]
        comp_table = Table(comp_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        comp_table.setStyle(TableStyle([('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'), ('BACKGROUND', (0, 1), (-1, 1), colors.lightgrey)]))
        elements.append(comp_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Terms
        elements.append(Paragraph("<b>TERMS & CONDITIONS:</b>", styles['Heading3']))
        terms_text = """1. Assignment is effective from the start date until the end date mentioned above.<br/>
        2. Payment will be made upon completion of work and submission of verified timesheets.<br/>
        3. Any cancellation must be notified 5 working days in advance.<br/>
        4. Employee must adhere to all company policies and client requirements.<br/>
        5. This agreement is subject to Indonesian Labor Law UU-13/2003."""
        elements.append(Paragraph(terms_text, styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))
        
        # Signatures
        elements.append(Paragraph("<b>AUTHORIZED BY:</b>", styles['Heading3']))
        sig_data = [
            ['HR Manager:', '', 'Client Representative:', ''],
            ['Name: _________________', '', 'Name: _________________', ''],
            ['Signature: _________________', '', 'Signature: _________________', ''],
            ['Date: _________________', '', 'Date: _________________', ''],
        ]
        sig_table = Table(sig_data, colWidths=[1.75*inch, 0.5*inch, 1.75*inch, 1*inch])
        elements.append(sig_table)
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer.read()

    def action_mark_signed(self):
        """Mark SPK as signed"""
        for spk in self:
            if not spk.signed_copy:
                raise ValidationError("Please upload signed SPK copy")
            
            spk.state = 'signed'
            spk.signed_date = datetime.now().date()
            spk.message_post(body=f"SPK marked as signed on {spk.signed_date}")

    def action_activate(self):
        """Activate SPK for work to begin"""
        for spk in self:
            if spk.state != 'signed':
                raise ValidationError("SPK must be signed before activation")
            
            spk.state = 'active'
            spk.message_post(body="SPK activated - work may now begin")


# ============================================================================
# HELPER MODELS
# ============================================================================

class ResBank(models.Model):
    """Extend res.bank with additional fields"""
    _inherit = 'res.bank'
    
    bank_code = fields.Char('Bank Code for ABC Format')


class ResBankAccount(models.Model):
    """Bank account for payment"""
    _inherit = 'res.partner.bank'
    
    bank_branch_code = fields.Char('Branch Code')
    inv_acc_id = fields.Char('International Account ID')
