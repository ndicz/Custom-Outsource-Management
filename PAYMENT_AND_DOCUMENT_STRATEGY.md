# PAYMENT & DOCUMENT MANAGEMENT STRATEGY
## outsource_custom v18.0.4.0.0+

---

## 🎯 EXECUTIVE SUMMARY

Anda menanyakan **6 workflow penting** yang belum di-automate penuh:

| Workflow | Current Status | Recommendation | Effort | Impact |
|----------|----------------|-----------------|--------|--------|
| **1. Salary Payment Distribution** | ⚠️ Manual export | ✅ **Automate bank file** | 2-3 hari | HIGH |
| **2. Vendor Payment** | ❌ Not integrated | ✅ **Create PO→Invoice→Payment flow** | 1 minggu | HIGH |
| **3. Invoice/Billing Letters** | ❌ Not in system | ✅ **Auto-generate from system** | 3-4 hari | MEDIUM |
| **4. Work Order (SPK) per Person** | ❌ Not in system | ✅ **Create SPK model + auto-print** | 5-7 hari | MEDIUM |
| **5. BPJS Payment** | ⚠️ Tracked only | ✅ **Automate GL posting** | 1-2 hari | HIGH |
| **6. Tax Payment** | ⚠️ Tracked only | ✅ **Auto GL posting + export** | 1-2 hari | HIGH |

**Total effort: 2-3 minggu untuk semua automated**

**Overall recommendation: 🎯 PRIORITIZE IN THIS ORDER**

```
PHASE 1 (WEEK 1): Bank payment automation + BPJS/Tax GL posting
  └─ Biggest impact, least complex

PHASE 2 (WEEK 2): PO → Invoice → Payment flow for vendors
  └─ Medium impact, medium complexity

PHASE 3 (WEEK 3): Document generation (Invoices, SPK, Work Orders)
  └─ Nice-to-have, medium complexity
```

---

## 📋 KEBUTUHAN ANDA SAAT INI

### Current State Analysis:

**SUDAH ADA ✅:**
- Payroll calculation (complete)
- BPJS contribution calculation
- Tax (PPh21) calculation
- GL posting untuk payroll
- Approval workflow
- Audit trail
- Bank export wizard (4 formats)

**BELUM ADA ❌:**
- Automated salary payment routing
- Vendor payment management system
- Invoice generation & tracking
- Work Order (SPK) management
- BPJS payment automation
- Tax payment automation
- Document/letter generation system

---

## 🏦 WORKFLOW 1: SALARY PAYMENT DISTRIBUTION

### CURRENT SITUATION:
```
Step 1: HR creates payslip (✅ dalam sistem)
Step 2: Finance approves (✅ dalam sistem)
Step 3: GL posted (✅ dalam sistem)
Step 4: Finance exports payroll data (⚠️ manual)
Step 5: Finance prepare bank transfer ❌ MANUAL
Step 6: Bank transfer executed ❌ MANUAL
Step 7: Distribute payslips to employees ❌ MANUAL
Step 8: Reconcile payments ❌ MANUAL
```

### RECOMMENDED SOLUTION:

**Option A: SEMI-AUTOMATIC (Recommended for now)**
```python
# Create new model: hr.payroll.payment.run

class HrPayrollPaymentRun(models.Model):
    _name = 'hr.payroll.payment.run'
    _inherit = ['mail.thread']
    
    # Fields
    name = fields.Char(compute='_compute_name')
    period_id = fields.Many2one('hr.payroll.period')
    payslips = fields.One2many('outsource.payslip', related='period_id.payslips')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready for Payment'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('reconciled', 'Reconciled')
    ], default='draft')
    
    # Payment Details
    total_amount = fields.Monetary(compute='_compute_total')
    payment_date = fields.Date()
    payment_method = fields.Selection([
        ('bank_transfer', 'Bank Transfer'),
        ('check', 'Check'),
        ('cash', 'Cash'),
        ('digital_wallet', 'Digital Wallet')
    ])
    bank_account_id = fields.Many2one('res.bank')
    
    # Files
    bank_file = fields.Binary('Bank File', readonly=True)
    bank_file_name = fields.Char()
    payment_proof = fields.Binary('Payment Proof', readonly=True)
    
    # Methods
    def action_prepare_for_payment(self):
        """Validate & prepare payment file"""
        # Check all payslips approved
        # Check no pending approvals
        # Generate bank file (ABC format, SWIFT, CAMT.053, etc)
        # Set state to 'ready'
        pass
    
    def action_generate_bank_file(self):
        """Generate bank transfer file (auto download)"""
        # Format: ABC format (most common in Indonesia)
        # Structure:
        # - Header: Bank code, date, time
        # - Detail: Employee bank account, amount, ref
        # - Footer: Total, record count, checksum
        # Result: File ready for upload to bank
        pass
    
    def action_upload_to_bank(self):
        """Mark as uploaded (payment_proof upload)"""
        # Manual step: Upload file to bank portal
        # System: User upload proof/receipt
        # State: Processing
        pass
    
    def action_validate_reconciliation(self):
        """Validate bank statement vs payslip"""
        # Check each payslip has matching bank posting
        # Flag any discrepancies
        # State: Reconciled
        pass
    
    def _compute_total(self):
        for run in self:
            run.total_amount = sum(run.payslips.mapped('net_salary'))
    
    # Button: Generate bank file
    # Button: Mark as paid
    # Button: Reconcile with bank statement
```

**Implementation steps:**
```
1. Create model hr.payroll.payment.run
2. Create form view (with download bank file button)
3. Link from payroll period (after approval)
4. Generate bank files in multiple formats:
   ├── ABC Format (common for Indonesian banks)
   ├── SWIFT MT101 (for international)
   ├── CAMT.053 (ISO format)
   └── CSV (for manual import)
5. Example ABC format:
   ```
   101CODEFRS0ECODEDOM1001111101200405BANK1BNK  0000000050
   5CODEDOMFRSNAME000000000BIC0000000DOMAIN   TESTGEN       
   6000000000001000000050EUR0INVOICE   UNSE
   61...
   62...
   ```

Time: 2-3 days
Result: Automatic bank file generation → Download & upload to bank portal
```

**Benefit untuk AUDIT:**
- ✅ Proof of payment (bank file + upload confirmation)
- ✅ Segregation of duties (HR creates, Finance approves, System generates)
- ✅ Reconciliation (compare bank statement vs system)
- ✅ Audit trail (who downloaded, when, file verification)

---

## 🏪 WORKFLOW 2: VENDOR PAYMENT MANAGEMENT

### PROBLEM STATEMENT:
Current system tidak integrate vendor payment. Anda perlu:
- PO (Purchase Order)
- Invoice from vendor
- Payment tracking
- GL posting
- Payment proof

### RECOMMENDED SOLUTION:

**Create complete PO→Invoice→Payment flow:**

```python
# Model 1: purchase_order_line → Extend existing
# (sudah ada di v18.0.3.0.0, kita enhance)

# Model 2: account.invoice.incoming (or extend)
class AccountInvoiceIncoming(models.Model):
    _name = 'account.invoice.incoming'
    _inherit = ['mail.thread']
    
    # Reference
    name = fields.Char()
    vendor_id = fields.Many2one('res.partner', domain=[('supplier', '=', True)])
    po_id = fields.Many2one('purchase_order_extended')
    invoice_number = fields.Char('Vendor Invoice Number')
    
    # Amounts
    total_amount = fields.Monetary()
    paid_amount = fields.Monetary()
    balance_due = fields.Monetary(compute='_compute_balance')
    
    # Dates
    invoice_date = fields.Date()
    due_date = fields.Date()
    payment_date = fields.Date()
    
    # State
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted'),
        ('verified', 'Verified'),
        ('approved', 'Approved'),
        ('scheduled', 'Scheduled for Payment'),
        ('paid', 'Paid'),
        ('reconciled', 'Reconciled')
    ], default='draft')
    
    # GL
    move_id = fields.Many2one('account.move')
    
    # Methods
    def action_verify_with_po(self):
        """3-way match: PO → GRN → Invoice"""
        # Validate: Amount matches PO
        # Validate: Items match GRN (Goods Receipt Note)
        # Validate: Terms match PO
        # Flag any discrepancy
        # Set state to 'verified'
        pass
    
    def action_approve_for_payment(self):
        """Approve by Finance Manager"""
        # Check verification complete
        # Check budget approved
        # Set state to 'approved'
        pass
    
    def action_post_journal_entry(self):
        """Create GL entry"""
        # Dr: Expense account (per line item)
        # Cr: Accounts Payable (vendor payable)
        # Ref: Invoice number
        # Post to GL
        pass
    
    def action_schedule_payment(self):
        """Schedule for bulk payment"""
        # Check due date
        # Check payment term (net 30, net 60, etc)
        # Add to payment run
        # State: Scheduled
        pass
    
    def action_record_payment(self):
        """Record payment made"""
        # Record payment date
        # Record payment amount
        # Record payment method
        # Update GL (Dr: AP, Cr: Bank)
        pass

# Model 3: account.payment.run (Vendor payments)
class AccountPaymentRun(models.Model):
    _name = 'account.payment.run'
    _inherit = ['mail.thread']
    
    name = fields.Char('Payment Run')
    payment_date = fields.Date()
    invoices = fields.Many2many('account.invoice.incoming')
    total_amount = fields.Monetary(compute='_compute_total')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('ready', 'Ready'),
        ('processing', 'Processing'),
        ('completed', 'Completed')
    ])
    
    # Generate payment file (similar to payroll)
    def action_generate_bank_file(self):
        # Generate ABC format for bulk payment
        pass
```

**Implementation steps:**
```
1. Create account.invoice.incoming model (3-way match)
2. Create account.payment.run model (bulk vendor payment)
3. Create views & workflows
4. Add 3-way match logic (PO amount vs GRN qty vs Invoice amount)
5. Generate bank files for vendor payments
6. Create reconciliation workflow

Flow:
  PO → Goods Received → Invoice Received → Verification → Approval 
  → Scheduled → Payment → Reconciliation
```

**Form view features:**
```
Tab 1: Invoice Details
  - Vendor name, invoice #, date, amount
  - PO link
  - Status (not matched / matched / verified)

Tab 2: Line Items
  - Item description, qty, unit price
  - GL account (expense category)
  - Cost center (project/department)

Tab 3: Matching Results (3-way match)
  - PO amount: Rp X
  - GRN amount: Rp X
  - Invoice amount: Rp X
  - ✅ MATCHED / ⚠️ DISCREPANCY (list differences)

Tab 4: Approval History
  - Verified by: [name] [date]
  - Approved by: [name] [date]

Tab 5: Payment History
  - Scheduled date: [date]
  - Payment date: [date]
  - Payment method: [bank transfer]
  - Reconciled: Yes/No
```

**Benefit untuk AUDIT:**
- ✅ Complete audit trail (PO → Invoice → Payment)
- ✅ 3-way match (fraud prevention)
- ✅ GL posting (reconcilable)
- ✅ Segregation of duties (verify ≠ approve ≠ pay)
- ✅ Payment proof (bank file + statement)

**Time: 1 minggu (3 hari design, 3 hari implement, 1 hari test)**

---

## 📄 WORKFLOW 3: INVOICE & BILLING LETTER GENERATION

### REQUIREMENT:
Anda butuh generate:
- Surat penagihan (Customer invoice/billing letter)
- Surat SPK kerja (Work Order contract)
- Payment receipt
- Payslip (sudah ada, tapi bisa enhance)

### RECOMMENDED SOLUTION:

**Create document generation engine:**

```python
# Model: account.document.template
class AccountDocumentTemplate(models.Model):
    _name = 'account.document.template'
    
    name = fields.Char('Template Name')
    doc_type = fields.Selection([
        ('invoice', 'Invoice/Billing Letter'),
        ('spk', 'Work Order (SPK)'),
        ('receipt', 'Payment Receipt'),
        ('payslip', 'Payslip'),
        ('contract', 'Employment Contract')
    ])
    
    # Template content (HTML)
    template_html = fields.Html('Template Content')
    
    # Variables placeholders
    variables = fields.Text('Available Variables', readonly=True)
    # Example: {{ company_name }}, {{ invoice_date }}, {{ customer_name }}, {{ total_amount }}
    
    # Footer
    footer = fields.Html('Footer (Signature block, notes)')
    
    def generate_document(self, context_dict):
        """Generate PDF from template"""
        # Use Jinja2 to populate variables
        # Convert HTML to PDF (using wkhtmltopdf or similar)
        # Return PDF bytes
        pass

# Model: sale.invoice (or extend account.move)
class SaleInvoice(models.Model):
    _name = 'sale.invoice'
    _inherit = ['mail.thread']
    
    name = fields.Char('Invoice #')
    sale_id = fields.Many2one('sale.order', domain=[('client_id', '=', True)])
    # (Link to outsourced client, not internal)
    
    customer_id = fields.Many2one('res.partner')
    invoice_date = fields.Date()
    due_date = fields.Date()
    
    # Lines
    lines = fields.One2many('sale.invoice.line', 'invoice_id')
    total_amount = fields.Monetary(compute='_compute_total')
    
    # Document
    pdf_content = fields.Binary('PDF Invoice', readonly=True)
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent to Customer'),
        ('received', 'Received'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue')
    ], default='draft')
    
    def action_generate_invoice_pdf(self):
        """Generate professional invoice PDF"""
        # Load template
        # Populate with data
        # Generate PDF
        # Save as attachment
        # Set state to 'sent'
        pass
    
    def action_send_to_customer(self):
        """Email invoice to customer"""
        # Generate PDF (if not done)
        # Compose email
        # Attach PDF & payment terms
        # Send
        pass

# Model: hr.work_order (SPK Kerja)
class HrWorkOrder(models.Model):
    _name = 'hr.work.order'
    _inherit = ['mail.thread']
    
    name = fields.Char('SPK Number', readonly=True)
    employee_id = fields.Many2one('hr.employee')
    outsource_client_id = fields.Many2one('res.partner', domain=[('outsource_client', '=', True)])
    
    # Work details
    job_title = fields.Char()
    job_description = fields.Text()
    location = fields.Char()
    
    # Dates
    start_date = fields.Date()
    end_date = fields.Date()
    
    # Compensation
    daily_rate = fields.Monetary()
    total_days = fields.Integer(compute='_compute_total_days')
    total_amount = fields.Monetary(compute='_compute_total_amount')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived')
    ], default='draft')
    
    # Document
    pdf_content = fields.Binary('SPK PDF', readonly=True)
    signed_copy = fields.Binary('Signed Copy')
    
    def action_generate_spk_pdf(self):
        """Generate SPK (Work Order) PDF"""
        # Load template
        # Populate with employee & work details
        # Generate PDF
        # Make available for printing & signing
        pass
    
    def action_send_for_signature(self):
        """Send to employee for signature"""
        # Email PDF to employee
        # Request signature (print, sign, scan back)
        # Or: Use digital signature system
        pass
    
    def action_mark_signed(self):
        """Mark as signed when copy received"""
        # Upload signed copy
        # Validate signature
        # State: Signed
        pass
```

**Implementation:**

**Step 1: Create Invoice Template (HTML + CSS)**
```html
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .header { text-align: center; border-bottom: 2px solid #333; }
        .invoice-number { float: right; }
        .invoice-date { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .total { background-color: #f2f2f2; font-weight: bold; }
        .terbilang { margin-top: 20px; }
        .signature { margin-top: 40px; display: flex; justify-content: space-around; }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
        <p>{{ company_address }}</p>
        <div class="invoice-number">Invoice #: {{ invoice_number }}</div>
    </div>
    
    <div class="invoice-date">
        <p><strong>Invoice Date:</strong> {{ invoice_date }}</p>
        <p><strong>Due Date:</strong> {{ due_date }}</p>
    </div>
    
    <div>
        <h3>BILL TO:</h3>
        <p>{{ customer_name }}<br>
        {{ customer_address }}<br>
        {{ customer_city }}<br>
        {{ customer_phone }}</p>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Amount</th>
            </tr>
        </thead>
        <tbody>
            {% for line in lines %}
            <tr>
                <td>{{ line.description }}</td>
                <td>{{ line.quantity }}</td>
                <td>Rp {{ line.unit_price | currency }}</td>
                <td>Rp {{ line.subtotal | currency }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <table>
        <tr class="total">
            <td colspan="3">TOTAL</td>
            <td>Rp {{ total_amount | currency }}</td>
        </tr>
    </table>
    
    <div class="terbilang">
        <p><strong>Terbilang:</strong> {{ total_amount_words }}</p>
    </div>
    
    <div class="signature">
        <div>
            <p>Prepared by:</p>
            <p>_________________</p>
            <p>{{ prepared_by_name }}</p>
        </div>
        <div>
            <p>Approved by:</p>
            <p>_________________</p>
            <p>{{ approved_by_name }}</p>
        </div>
        <div>
            <p>Customer Signature:</p>
            <p>_________________</p>
            <p>Date: ____________</p>
        </div>
    </div>
</body>
</html>
```

**Step 2: Create SPK Template**
```html
<html>
<head>
    <style>
        /* Similar to invoice template */
    </style>
</head>
<body>
    <h1 style="text-align: center;">SURAT PERINTAH KERJA (WORK ORDER)</h1>
    <p style="text-align: center;">SPK No: {{ spk_number }} / {{ month }} / {{ year }}</p>
    
    <table>
        <tr>
            <td style="width: 50%;">
                <strong>PT/CV:</strong> {{ company_name }}<br>
                <strong>Address:</strong> {{ company_address }}
            </td>
            <td>
                <strong>Date:</strong> {{ spk_date }}<br>
                <strong>Effective:</strong> {{ start_date }} s/d {{ end_date }}
            </td>
        </tr>
    </table>
    
    <h3>WORK ASSIGNMENT</h3>
    <table>
        <tr>
            <td><strong>Employee Name:</strong> {{ employee_name }}</td>
            <td><strong>NPWP:</strong> {{ employee_npwp }}</td>
        </tr>
        <tr>
            <td><strong>Position:</strong> {{ job_title }}</td>
            <td><strong>Client:</strong> {{ client_name }}</td>
        </tr>
    </table>
    
    <h3>JOB DESCRIPTION:</h3>
    <p>{{ job_description }}</p>
    
    <h3>COMPENSATION:</h3>
    <table>
        <tr>
            <td><strong>Daily Rate:</strong></td>
            <td>Rp {{ daily_rate | currency }}</td>
        </tr>
        <tr>
            <td><strong>Period:</strong></td>
            <td>{{ start_date }} to {{ end_date }} ({{ total_days }} days)</td>
        </tr>
        <tr class="total">
            <td><strong>Total Amount:</strong></td>
            <td>Rp {{ total_amount | currency }}</td>
        </tr>
    </table>
    
    <h3>TERMS & CONDITIONS:</h3>
    <ol>
        <li>Assignment is effective from {{ start_date }} to {{ end_date }}</li>
        <li>Payment will be made upon completion and submission of timesheets</li>
        <li>Cancellation must be notified 5 days in advance</li>
        <li>All company rules & regulations apply</li>
    </ol>
    
    <div class="signature">
        <p>Authorized by:</p>
        <p>_________________</p>
        <p>{{ authorized_by_name }}</p>
        <p>Date: ____________</p>
    </div>
</body>
```

**Step 3: Generate PDF**
```python
# In your model:
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from jinja2 import Template

def action_generate_invoice_pdf(self):
    # 1. Load template
    template = self.env['account.document.template'].search(
        [('doc_type', '=', 'invoice'), ('active', '=', True)], limit=1
    )
    if not template:
        raise ValidationError("Invoice template not configured")
    
    # 2. Prepare context
    context = {
        'company_name': self.env.company.name,
        'invoice_number': self.name,
        'invoice_date': self.invoice_date.strftime('%d/%m/%Y'),
        'due_date': self.due_date.strftime('%d/%m/%Y'),
        'customer_name': self.customer_id.name,
        'customer_address': self.customer_id.street,
        'total_amount': self.total_amount,
        'lines': self.lines,
        # ... more context
    }
    
    # 3. Render template
    j2_template = Template(template.template_html)
    html_content = j2_template.render(context)
    
    # 4. Convert to PDF (using wkhtmltopdf or weasyprint)
    # Option A: Using wkhtmltopdf (command line)
    import subprocess
    pdf = subprocess.run([
        'wkhtmltopdf', '-', '-'
    ], input=html_content.encode(), capture_output=True, check=True).stdout
    
    # Option B: Using weasyprint (Python library)
    from weasyprint import HTML, CSS
    pdf = HTML(string=html_content).write_pdf()
    
    # 5. Save to model
    self.pdf_content = base64.b64encode(pdf)
    self.state = 'sent'
```

**Time: 3-4 days**
- Day 1: Design templates (HTML structure)
- Day 2: Implement model & PDF generation
- Day 3: Create views & workflows
- Day 4: Testing & refinement

---

## 💳 WORKFLOW 4: BPJS PAYMENT AUTOMATION

### CURRENT STATE:
```
✅ BPJS calculated & tracked in payslip
⚠️ But: Manual GL posting for BPJS payment
⚠️ But: No payment workflow
❌ No automatic reconciliation
```

### RECOMMENDED SOLUTION:

**Enhance tax_payment_tracking model (already created in v18.0.4.0.0):**

```python
# Already in system, but enhance with:

class TaxPaymentTracking(models.Model):
    _name = 'tax.payment.tracking'
    
    # ENHANCEMENT: Add BPJS-specific workflow
    
    # If tax_type = 'bpjs_*', add BPJS-specific fields:
    bpjs_invoice_number = fields.Char('BPJS Invoice #')
    bpjs_report_id = fields.Char('BPJS Report ID')
    bpjs_member_details = fields.One2many('tax.payment.bpjs.member', 'payment_id')
    
    # Methods for BPJS:
    def action_download_bpjs_invoice(self):
        """Download invoice from BPJS portal"""
        # This is manual step, but we track it
        # User uploads invoice
        # System links invoice to payment tracking
        pass
    
    def action_validate_bpjs_members(self):
        """Validate member list vs payroll"""
        # Check: Every employee in payroll is in BPJS invoice
        # Check: No extra members in BPJS
        # Flag any differences
        pass
    
    def action_prepare_bpjs_payment(self):
        """Prepare payment to BPJS"""
        # Verify total amount matches invoice
        # Check payment method (bank transfer to BPJS account)
        # Generate payment reference (BPJS requires specific format)
        # Create GL entry: Dr Bank, Cr BPJS Payable
        pass
    
    def action_record_bpjs_payment(self):
        """Record payment made"""
        # Record payment date & confirmation
        # Post GL entry automatically
        # Move to 'reconciled' state
        pass

class TaxPaymentBpjsMember(models.Model):
    _name = 'tax.payment.bpjs.member'
    
    payment_id = fields.Many2one('tax.payment.tracking')
    employee_id = fields.Many2one('hr.employee')
    member_number = fields.Char('BPJS Member #')
    
    # Contributions
    jht_amount = fields.Monetary('JHT (Pension)')
    kes_amount = fields.Monetary('Kesehatan (Health)')
    jp_amount = fields.Monetary('JP (Disability)')
    jkk_amount = fields.Monetary('JKK (Work Accident)')
    jkm_amount = fields.Monetary('JKM (Death)')
    total_contribution = fields.Monetary(compute='_compute_total')
```

**Implementation steps:**
```
1. Create BPJS payment request form (in system)
   - Linked to tax_payment_tracking
   - Show total amount due
   - Show member breakdown
   
2. Add BPJS-specific fields:
   - BPJS invoice upload
   - Member validation
   - Payment reference generation
   
3. Workflow:
   - Verify → Validate members → Prepare payment 
   → GL posting → Record payment → Reconciled
   
4. GL entry automation:
   - When state changes to 'paid':
     * Automatically create GL entry
     * Dr: General Bank Account (Rp X)
     * Cr: BPJS Payable Liability (Rp X)
     * Ref: Payment #BPJSMM/YYYY/NNN
```

**Time: 1-2 days**

---

## 💰 WORKFLOW 5: TAX PAYMENT AUTOMATION

### CURRENT STATE:
```
✅ PPh21 calculated in payslip
✅ Tracked in tax_payment_tracking
⚠️ But: Manual GL posting for tax payment
❌ No automatic reconciliation with DJP
```

### RECOMMENDED SOLUTION:

**Enhance tax_payment_tracking for tax payments:**

```python
# Enhance existing TaxPaymentTracking model:

class TaxPaymentTracking(models.Model):
    
    # Add for PPh payments:
    ntpn_number = fields.Char('NTPN Number')  # From DJP after payment
    ntpn_date = fields.Date('NTPN Date')
    e_billing_number = fields.Char('e-Billing Number')
    
    # PPh-specific
    pph_type = fields.Selection([
        ('pph21', 'PPh 21 (Salary)'),
        ('pph23', 'PPh 23 (Service/Interest)'),
        ('pph25', 'PPh 25 (Corporate Tax)')
    ])
    
    employee_list = fields.One2many('tax.payment.pph.employee', 'payment_id')
    
    # Methods
    def action_prepare_pph_payment(self):
        """Prepare PPh payment"""
        # Verify total withheld
        # Generate e-Billing reference
        # Validate against SPT if needed
        # Create GL entry: Dr: PPh Expense, Cr: Bank
        pass
    
    def action_upload_to_e_billing(self):
        """Generate e-Billing file for DJP"""
        # Format: XML per DJP requirement
        # Include: Tax type, amount, period, NPWP
        # Generate file for upload to DJP portal
        pass
    
    def action_record_ntpn(self):
        """Record NTPN (payment confirmation)"""
        # User input NTPN from DJP
        # Verify: Amount matches
        # Post GL entry: Dr Bank (withdrawal), Cr PPh Payable
        pass

class TaxPaymentPphEmployee(models.Model):
    _name = 'tax.payment.pph.employee'
    
    payment_id = fields.Many2one('tax.payment.tracking')
    employee_id = fields.Many2one('hr.employee')
    
    gross_salary = fields.Monetary()
    ptkp_amount = fields.Monetary()
    taxable_income = fields.Monetary()
    pph_rate = fields.Float('%')
    pph_amount = fields.Monetary()
```

**GL Entry automation:**
```python
# When state = 'paid':

def _post_payment_entry(self):
    """Auto-post GL entry for payment"""
    if self.tax_type in ['pph21', 'pph23', 'pph25']:
        # Create GL entry
        move = self.env['account.move'].create({
            'date': self.payment_date,
            'ref': f'PPh-{self.name}',
            'line_ids': [
                (0, 0, {
                    'account_id': self.gl_account_id.id,  # PPh Payable
                    'debit': self.payment_amount,  # Debit: Pay the liability
                    'credit': 0,
                }),
                (0, 0, {
                    'account_id': self.env.company.bank_account_id.id,  # Bank account
                    'debit': 0,
                    'credit': self.payment_amount,  # Credit: Money from bank
                }),
            ]
        })
        move.action_post()
        self.move_id = move
        self.state = 'reconciled'
```

**Time: 1-2 days**

---

## 📊 INTEGRATION MAP (All 6 workflows)

```
PAYROLL SYSTEM
    ↓
    ├─→ [Payslip] → PPh21 Calculation → Tax Payment Tracking
    │       ↓                              ↓
    │   [Salary Payment Run]          [GL Entry: PPh Payable]
    │       ↓                              ↓
    │   [Bank File Export]             [Auto GL Posting]
    │       ↓                              ↓
    │   [Upload to Bank]              [NTPN Recording]
    │       ↓                              ↓
    │   [Payment Reconciliation]       [Tax Payment Proof]
    │
    ├─→ [Payslip] → BPJS Calculation → BPJS Payment Tracking
    │       ↓                              ↓
    │   [GL Entry: BPJS Payable]       [Auto GL Posting]
    │       ↓                              ↓
    │   [Monthly Payment]             [Payment Proof]
    │
    └─→ [SPK/Work Order]
            ↓
        [Employee Assignment]
            ↓
        [Invoice to Client]
            ↓
        [Payment from Client]

VENDOR MANAGEMENT
    ↓
    [PO]
    ↓
    [GRN - Goods Receipt]
    ↓
    [Vendor Invoice]
    ↓
    [3-way Match] → [GL Entry: Expense]
    ↓
    [Approval]
    ↓
    [Payment Run]
    ↓
    [Bank File Export]
    ↓
    [Payment + Reconciliation]
```

---

## 🎯 FINAL RECOMMENDATIONS (Priority & Sequencing)

### **IMMEDIATE (Week 1-2) - HIGHEST IMPACT:**

**1. Salary Payment Run (2-3 days)**
```
Why: Already 80% done (need bank file automation)
Impact: Reduce manual work by 80%
Effort: Low (build on existing export)
Benefit: Audit-ready payment process
```

**2. BPJS & Tax GL Automation (1-2 days each)**
```
Why: Calculations exist, just need GL posting
Impact: Auto GL entries = 50% less error
Effort: Low to medium
Benefit: Audit trail complete
```

**3. Vendor Payment Workflow (1 week)**
```
Why: Vendor management currently missing
Impact: 3-way match prevents fraud
Effort: Medium
Benefit: Compliance + control
```

### **NEXT (Week 3-4) - NICE-TO-HAVE:**

**4. Document Generation (3-4 days)**
```
Why: Professional invoices & SPK
Impact: Credibility + audit-ready docs
Effort: Medium
Benefit: Professional appearance
```

**5. SPK Work Order Model (5-7 days)**
```
Why: Explicit work assignment tracking
Impact: Clarity for employee & client
Effort: Medium
Benefit: Reduced disputes
```

---

## 📋 IMPLEMENTATION ROADMAP

### **PHASE 1: WEEK 1 (High Impact)**
```
MON: Create Salary Payment Run model
TUE: Create bank file generation (ABC format)
WED: Test with sample payroll period
THU: Add BPJS GL automation
FRI: Test BPJS posting

DELIVERABLE: 
- Salary payments can be exported to bank with 1-click
- BPJS GL entries auto-post on confirmation
- Zero manual GL entry for these 2
```

### **PHASE 2: WEEK 2 (Control & Compliance)**
```
MON-WED: Create account.invoice.incoming model (vendor invoice)
THU: Create 3-way match logic
FRI: Create payment run for vendors

DELIVERABLE:
- Vendor invoices integrated in system
- 3-way match (PO → GRN → Invoice)
- Payment run generates bank files
```

### **PHASE 3: WEEK 3-4 (Documentation)**
```
MON-WED: Create document templates (Invoice, SPK)
        Create HTML templates
        Setup PDF generation
THU-FRI: Create SPK work order model
        Test template generation

DELIVERABLE:
- Professional invoice PDFs generated from system
- SPK (Work Order) contract PDFs auto-generated
- Reduced manual document creation
```

---

## 💡 QUICK IMPLEMENTATION CHECKLIST

### If you want to start IMMEDIATELY:

**TODAY (2 hours):**
```
☑️ Task 1: Design Salary Payment Run form (mockup)
  What: Sketch form layout in notebook
  Why: Clarify requirements before coding
  
☑️ Task 2: List required bank file formats
  What: Identify what bank formats you need
  Why: Different banks need different formats
```

**TOMORROW (Full day - Day 1):**
```
☑️ Create hr.payroll.payment.run model
  Lines: 100 lines Python
  Time: 3-4 hours
  
☑️ Create form view
  Time: 1 hour
  
☑️ Test with sample payroll data
  Time: 2 hours
```

**NEXT 2 DAYS:**
```
☑️ Implement bank file generation
☑️ Test with real bank format
☑️ Add BPJS GL posting
☑️ Test deployment
```

---

## ⚖️ BEFORE YOU START - KEY DECISIONS TO MAKE

**Q1: Bank Formats?**
```
Need to know: What bank formats do you use?
- ABC Format (most common Indonesia)
- SWIFT MT101
- CAMT.053
- Custom format?
```

**Q2: Vendor Payment - 3-way match or simpler?**
```
Option A: Full 3-way match (PO → GRN → Invoice) = more complex
Option B: Simple (Invoice → Approval → Payment) = easier
Recommendation: Start with B, enhance to A later
```

**Q3: Document Generation - where stored?**
```
Option A: In system (database) = easier to track
Option B: Physical files = more familiar
Option C: Email to recipient automatically = modern
Recommendation: Store in system, email to recipient
```

**Q4: Timeline?**
```
Your urgency level?
- ASAP (start now): Go with PHASE 1 only (1-2 weeks)
- Medium (next month): Do PHASE 1 + 2 (3-4 weeks)
- Relaxed (flexibility): Do all phases (5-6 weeks)
```

---

## 🎯 SUMMARY TABLE

| Feature | Effort | Impact | Timeline | Status |
|---------|--------|--------|----------|--------|
| Salary Payment Automation | ⭐⭐ | ⭐⭐⭐⭐⭐ | 2-3d | RECOMMENDED |
| BPJS GL Posting | ⭐⭐ | ⭐⭐⭐⭐ | 1-2d | RECOMMENDED |
| Tax GL Posting | ⭐⭐ | ⭐⭐⭐⭐ | 1-2d | RECOMMENDED |
| Vendor Payment Workflow | ⭐⭐⭐ | ⭐⭐⭐⭐ | 1 week | RECOMMENDED |
| Document Generation | ⭐⭐⭐ | ⭐⭐⭐ | 3-4d | NICE-TO-HAVE |
| SPK Work Order | ⭐⭐⭐⭐ | ⭐⭐⭐ | 5-7d | NICE-TO-HAVE |

---

## 🚀 NEXT STEP

**I recommend: Start with PHASE 1 (Weeks 1-2) to get immediate value**

This gives you:
1. ✅ Automated salary payment (no more manual bank entry)
2. ✅ Auto GL posting for BPJS (compliant, audit-ready)
3. ✅ Auto GL posting for tax (compliant, audit-ready)
4. ✅ Payment reconciliation (verifiable)

**Would you like me to:**
- ✅ Create the Python models (salary payment + BPJS/Tax GL automation)?
- ✅ Create the forms & views?
- ✅ Create bank file generation for your specific format?
- ✅ Do all of the above?

**Which is highest priority for YOUR business?**
