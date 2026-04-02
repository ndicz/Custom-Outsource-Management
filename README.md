# outsource_custom — Odoo 18 Custom Module

Modul kustom lengkap untuk perusahaan outsource Indonesia dengan integrasi Payroll, Purchasing, Expense Tracking, dan Financial Reporting.

## Fitur Utama

### 1. PAYROLL & HR (v18.0.2.0.0)
- **PPh 21 Progresif**: Kalkulasi otomatis sesuai PTKP terbaru
- **BPJS Integration**: Kesehatan, JHT, JP, JKK, JKM otomatis per payslip
- **Multi-Level Approval**: Draft → Submit → Verify → Approve
- **Salary Structure & Components**: Gaji pokok, tunjangan, potongan, bonus
- **Salary History**: Audit trail lengkap perubahan gaji
- **Employee Loans**: Pengelolaan pinjaman dengan cicilan otomatis
- **Bank Export Wizard**: Export ke Mandiri, BCA, BRI, generic CSV

### 2. PURCHASING & COST TRACKING (NEW v18.0.3.0.0)
- **Extended Purchase Order**: Link ke project/client untuk tracking biaya
- **Cost Categories**: Material, Service, Operational, Equipment
- **Billable Tracking**: Flag untuk memisahkan biaya charging vs internal
- **Analytic Account Integration**: Auto-assign cost center dari project

### 3. OPERATIONAL EXPENSE MANAGEMENT (NEW v18.0.3.0.0)
- **12 Expense Types**: 
  - Sewa, Listrik/Air/Gas, Transport, Komunikasi
  - Maintenance, Equipment, Supplies, Makanan
  - Perjalanan, Professional Fees, Asuransi, Lainnya
- **Budget Workflow**: Draft → Submit → Verify → Approve → Post
- **GL Auto-Posting**: Automatic journal entry saat approve
- **Receipt Management**: Attachment untuk bukti pengeluaran
- **Project Tracking**: Klien cost allocation

### 4. FINANCIAL REPORTING (NEW v18.0.3.0.0)
- **P&L Report**: Revenue, COGS, Gross Profit, Expenses, Tax, Net Income
- **Revenue Breakdown**: Per-client revenue analysis
- **Client Profitability**: Margin analysis per klien
- **Financial Insights**: 
  - Gross Margin %
  - Per-Invoice Metrics
  - Profitability Ratio
- **Multi-Period Comparison**: Flexible date range selection

### 5. TAX & COMPLIANCE (v18.0.2.0.0)
- **e-Faktur Export**: Format DJP Online dengan validation
- **PPh 23 Withholding**: 2% / 4% auto-detection
- **PPh 21 Reporting**: Monthly tax reconciliation
- **BPJS Reporting**: Export format untuk pelaporannya BPJS

## Models (Extended & New)

### Extended Models
| Model | Field tambahan | Keterangan |
|---|---|---|
| `res.partner` | npwp, is_pkp, client_type | Info klien |
| `purchase.order` | project_id, cost_category, billable | Tracking biaya ke klien |
| `purchase.order.line` | cost_category, billable | Kategori & flag billable |
| `hr.employee` | ptkp_status, bpjs_*_number, outsource_client | PTKP & BPJS |
| `account.move` | efaktur_*, pph23_* | e-Faktur & PPh 23 |

### New Models (v18.0.3.0.0)
| Model | Deskripsi | Fitur |
|---|---|---|
| `operational.expense` | Pengeluaran operasional | Approval workflow, GL posting |
| `financial.report` | Laporan keuangan (P&L, BS, CF) | Auto-compute, HTML report |
| `client.profitability` | Analisis profitabilitas per klien | Margin, cost breakdown, per-invoice metrics |

## Wizard & Tools

### Existing Wizards
- **Export e-Faktur CSV**: Filter periode & klien
- **Laporan BPJS Bulanan**: CSV format untuk BPJS
- **Payslip Bank Export**: Mandiri, BCA, BRI, CSV

### New Wizards (v18.0.3.0.0)
- **Generate Financial Report**: Pilih tipe, periode → otomatis compute
- **Generate Client Profitability**: Pilih klien, periode → analysis

## Setup & Konfigurasi

### 1. Mandatory Setup (First Time)
```
Accounting Settings → Outsource Custom Configuration
├── Payroll Accounts
│   ├── Salary Expense Account
│   ├── Salary Payable Account
│   ├── Tax Payable Account
│   └── BPJS Payable Account
│
├── Operational Expense Accounts (12 types)
│   ├── Rent, Utilities, Transport, Communication
│   ├── Maintenance, Equipment, Supplies, Meals
│   ├── Travel, Professional, Insurance, Other
│   └── Bank/Cash Account for Payments
│
└── Financial Report Settings
    ├── Corporate Tax Rate (%)
    ├── Overhead Allocation Rate (%)
    └── Reporting Journal
```

### 2. Company Setup
- Add salary expense account untuk payroll postings
- Add expense accounts (12 types) untuk operational expenses
- Create project/analytic accounts untuk client cost tracking

### 3. Data Initialization
- Create salary components (salary_component_data.xml)
- Setup payment methods (cash, bank)
- Create project-client linkages

## Workflow & Usage

### Payroll Workflow
1. Create employees → link ke klien (outsource_client_id)
2. Setup salary structure per employee/klien
3. Override payroll period jika ada perubahan
4. Generate & approve payslips (multi-level approval)
5. Export ke bank → post journal entries
6. Monthly: export e-Faktur & BPJS reports

### Purchasing & Costing Workflow
1. Create purchase order
2. Link ke project (klien)
3. Set cost_category & billable flag
4. Analytic account auto-populate dari project
5. Post PO → track COGS per klien

### Expense Management Workflow
1. Create operational expense
2. Pilih expense_type (12 options)
3. Optional: link ke project (cost allocation)
4. Attach Receipt PDF/Image
5. Submit → Verify → Approve workflow
6. On Approve: automatic GL posting
7. View in GL & Financial Reports

### Financial Reporting Workflow
1. Menu → Generate Financial Report Baru
2. Pilih tipe laporan (P&L, Balance Sheet, dll)
3. Set periode (start_date - end_date)
4. Click Generate → auto-compute semua metrics
5. View P&L table dengan breakdown per klien
6. Export/Share untuk stakeholder

### Client Profitability Workflow
1. Menu → Generate Laporan Profitabilitas
2. Pilih klien + optional project
3. Set periode
4. Click Generate → auto-analyze
5. View: Revenue, Costs, Margin %, Per-Invoice Metrics
6. Decision: Scale up / adjust pricing / reduce cost

## Accounting Integration

### GL Account Requirements
```
Chart of Accounts minimum:
├── 1. Income / Revenue
│   └── Sales (default Odoo sale.order posting)
│
├── 4. Expenses (12 categories)
│   ├── Salary Expense (211)
│   ├── Rent (214)
│   ├── Utilities (215)
│   ├── Transport (216)
│   ├── Communication (217)
│   ├── Maintenance (218)
│   ├── Equipment (219)
│   ├── Supplies (220)
│   ├── Meals (221)
│   ├── Travel (222)
│   ├── Professional (223)
│   ├── Insurance (224)
│   └── Other (225)
│
└── 1. Assets / Bank
    ├── Cash (101)
    └── Bank Accounts (102-110)
```

### Automatic GL Postings
1. **Payslip Approval**: Dr Salary Exp / Cr Salary Payable
2. **Tax Withholding**: Dr Tax Payable / Cr Bank (on payment)
3. **Expense Approval**: Dr Expense Type / Cr Bank
4. **Purchase Invoice**: Dr COGS/Inventory / Cr AP (standard)

## Tax Compliance

### PPh 21 (Personal Income Tax)
- Progressive rate: 5%, 15%, 25%, 30%, 35%
- PTKP: TK0, K0, K1, K2, K3, K/I, K/I/0-2 tiers
- Formula: Income > PTKP → Calculate PPh 21
- Monthly: Withhold from salary & post GL

### PPh 23 (Service Tax)
- Rate: 2% (NPWP) / 4% (Non-NPWP)
- Auto-detection: Check NPWP during invoice creation
- On PPh 23 invoice: Dr PPh expense / Cr PPh payable

### BPJS Contributions
- **JHT** (Old Age): Company 3.7% + Employee 2%
- **Kesehatan** (Health): Company 4% + Employee 1%
- **JP** (Disability): Company 0.3%
- **JKK/JKM** (Insurance): Company rate based on risk class
- Monthly: Submit to BPJS via wizard export

## Reporting & Analytics

### Reports Available
1. **Payroll Reports**
   - Monthly payslip summary
   - Tax withholding summary (PPh 21)
   - BPJS contribution summary

2. **Financial Reports**
   - Profit & Loss (P&L)
   - Balance Sheet
   - Cash Flow
   - Trial Balance

3. **Client Analytics**
   - Revenue per client
   - Cost allocation per client
   - Margin % per client
   - Profitability ranking

4. **Tax Reports**
   - e-Faktur ready export (DJP format)
   - PPh 21 monthly report
   - PPh 23 withholding summary
   - BPJS monthly submission

## Security & Access Control

### Roles
- **User**: Read operational data, create submissions
- **Manager**: Approve workflows, view analytics
- **Accounting**: Post GL, manage financial reports
- **Admin**: Full access, configuration

### Record Rules (if needed)
- Operational Expense: visible only to own allocation or approved
- Financial Report: visible to accounting group
- Client Profitability: visible to managers + accounting

## Support & Troubleshooting

### Common Issues

1. **GL Account not found when approving expense**
   - Check: Accounting Settings → Operational Expense configurations
   - Ensure all 12 expense account types are configured
   - Check: Bank/Cash account is set

2. **Payslip not posting GL entries**
   - Verify: Salary expense account configured in settings
   - Check: Journal configuration for accounting entries
   - Manual posting: Re-approve payslip

3. **Financial reports showing 0 revenue**
   - Check: Invoices are 'Paid' status (not draft)
   - Verify: Invoice period matches report period_start/period_end
   - Check: Partner linked to invoices

4. **Client profitability not calculating**
   - Ensure: Purchase orders linked to project
   - Check: Project linked to correct client (partner)
   - Verify: Invoices have correct client (partner)

## Version History

- **v18.0.1.0.0**: Initial payroll module
- **v18.0.2.0.0**: Enhanced payroll + e-Faktur + BPJS
- **v18.0.3.0.0**: Add purchasing, expenses, financial reporting
- **Invoice outsource** — dengan breakdown PPh 23 dan instruksi pembayaran
- **Slip gaji** — dengan rincian PPh 21 dan BPJS lengkap
- **Ringkasan project** — daftar karyawan ditempatkan per project

### API Integration
- **e-Faktur DJP Online** — upload programatik via OAuth2
- **BPJS Kesehatan** — verifikasi nomor peserta
- **Bank statement** — fetch mutasi BCA/Mandiri/BRI untuk rekonsiliasi

## Instalasi

```bash
# 1. Copy folder ke addons path
cp -r outsource_custom /opt/odoo/custom_addons/

# 2. Update addons list
./odoo-bin -c /etc/odoo/odoo.conf --update-list

# 3. Install via CLI
./odoo-bin -c /etc/odoo/odoo.conf -d NAMA_DB -i outsource_custom --stop-after-init

# Atau install via UI: Settings → Apps → search "Outsource Custom" → Install
```

## Konfigurasi API (System Parameters)

Tambahkan di Settings → Technical → System Parameters:

| Key | Keterangan |
|---|---|
| `outsource.djp_client_id` | Client ID DJP e-Faktur |
| `outsource.djp_client_secret` | Client Secret DJP |
| `outsource.company_npwp` | NPWP perusahaan (15 digit) |
| `outsource.bpjs_cons_id` | Consumer ID BPJS Kesehatan API |
| `outsource.bpjs_secret_key` | Secret key BPJS API |
| `outsource.bca_token` | Bearer token BCA API |
| `outsource.bca_account` | Nomor rekening BCA |

## Struktur file

```
outsource_custom/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── res_partner.py        # Extend partner — NPWP, klien outsource
│   ├── sale_order.py         # Extend SO — kontrak, PPh 23
│   ├── project_project.py    # Extend project — SLA, karyawan
│   ├── hr_payslip.py         # PPh 21 progresif + BPJS calculator
│   └── account_move.py       # e-Faktur + PPh 23 withholding
├── wizard/
│   ├── efaktur_export_wizard.py      # Generate CSV e-Faktur
│   ├── efaktur_export_wizard_views.xml
│   ├── bpjs_report_wizard.py         # Generate CSV BPJS
│   └── bpjs_report_wizard_views.xml
├── controllers/
│   └── api_integration.py    # DJP, BPJS, Bank API endpoints
├── views/
│   ├── res_partner_views.xml
│   ├── sale_order_views.xml
│   ├── project_views.xml
│   ├── hr_payslip_views.xml
│   ├── account_move_views.xml
│   └── menu_views.xml
├── report/
│   ├── invoice_report.xml    # QWeb invoice kustom
│   ├── payslip_report.xml    # QWeb slip gaji + PPh 21 + BPJS
│   └── project_summary_report.xml
├── data/
│   ├── tax_data.xml          # Sequence nomor kontrak
│   └── analytic_plan_data.xml
└── security/
    └── ir.model.access.csv
```

## Pengembangan lanjutan

Tambahkan custom module baru yang depends ke `outsource_custom` untuk:
- Dashboard real-time profitabilitas per klien
- Notifikasi WhatsApp/email otomatis saat invoice jatuh tempo
- Integrasi e-SPT PPh 21 masa
- Mobile app absensi karyawan outsource
