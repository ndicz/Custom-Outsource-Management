# QUICK START - AUDIT & COMPLIANCE FEATURES
## Panduan Penggunaan Cepat untuk Kepala Accounting

---

## 📋 CHECKLIST TUTUP BUKU (Period Closing)

### Sebelum tutup periode, gunakan:
```
Menu: Accounting → Audit & Compliance → Periode & Tutup Buku
```

### Step-by-step:
```
1. Create New Period:
   ├── Periode: January 2024 → otomatis generate nama
   ├── Tanggal Mulai: 1-Jan-2024
   ├── Tanggal Akhir: 31-Jan-2024
   └── Save

2. System auto-check (read-only):
   ├── ✅ Semua payslip posted? → dicek otomatis
   ├── ✅ Semua expense approved? → dicek otomatis
   ├── ✅ Semua invoice posted? → dicek otomatis
   ├── ✅ Semua PO sudah diinvoice? → dicek otomatis
   └── Jika ada yang belum:
       └── ERROR: "Ada X payslips belum posted"
           → Fix dulu, baru bisa close

3. Manual Checks (check boxes):
   ├── Bank reconciled? ☑ YES
   ├── GL reconciled? ☑ YES
   └── Catatan: "All checked"

4. Click "Close Period":
   ├── System validate semua checklist
   ├── If OK → Period CLOSED
   ├── Status berubah: Open → Closed
   └── Tercatat: Closed by Anda, on 1-Feb-2024 10:30 AM

5. Result:
   └── Periode sekarang LOCKED
       ├── GL posting untuk Jan tidak bisa dientry lagi
       ├── Tapi data masih bisa dilihat (read-only)
       └── Audit trail tercatat semua perubahan

6. Jika perlu reopen (untuk audit):
   └── Hanya Account Manager bisa
       ├── Click "Reopen Period"
       ├── Tercatat: Reopened by XXX on YYY (reason for audit)
       └── Bisa edit lagi
```

**Contoh Scenario:**
```
Kepala Accounting: "Tutup Januari"
  ↓
Create Period Januari
  ↓
System check:
├── Payslips: 40 posted, 2 masih draft
│   → ERROR! "Ada payslip draft"
├── → Fix: Approve 2 payslips yang draft
├── → Cek lagi: "All 42 posted? YES"
│
├── Expenses: 15 posted
│   → OK
│
├── Invoices: 50 posted
│   → OK
│
├── PO billed: 80 billed
│   → OK
│
├── Bank reconciled: YES ☑
├── GL reconciled: YES ☑
│
└── NOW Click "Close Period"
    → CLOSED! ✅

Result:
  Periode Januari sesaat terkunci
  Semua perubahan tercatat
  Ready untuk audit!
```

---

## 🔍 REKONSILIASI GL (GL Reconciliation)

### Gunakan untuk:
```
- Verify A/R balance vs customer statement
- Verify A/P balance vs vendor invoice
- Verify bank balance vs bank statement
- Verify general accounts
```

### Cara pakai:
```
Menu: Accounting → Audit & Compliance → Rekonsiliasi GL
```

### Step-by-step:
```
1. Create GL Reconciliation:
   ├── Account: A/R (Accounts Receivable)
   ├── Type: Receivable
   ├── As of Date: 31-Jan-2024
   ├── Period: 1-Jan-2024 to 31-Jan-2024
   └── Save

2. System auto-calculate (read-only):
   ├── Expected Balance (from GL): Rp 500.000.000
   │   (Ini calculated dari GL entry di Jan)
   │
   └── Status: WAIT for reconciliation

3. Enter reconciled balance:
   ├── Terima customer statement: Rp 480.000.000
   ├── Input di field "Saldo Direkonsiliasi"
   └── Save

4. System auto-calculate variance:
   ├── Variance = 500jt - 480jt = Rp 20.000.000
   ├── Status: VARIANCE DETECTED
   └── Require explanation → MANDATORY FIELD

5. Investigate variance:
   ├── Cari di GL: Posting mana yang belum?
   ├── Contoh: Invoice #XYZ Rp 20jt posted tapi klien belum terima
   ├── Input: "Invoice ABC-123 belum diterima klien (pending)"
   └── Save

6. Add detail lines (optional):
   ├── Ini untuk tracking per-item reconciliation
   ├── Bisa direct dari GL or manual entry
   └── Contoh:
       Invoice #XYZ, Rp 20jt, Status: Pending

7. Complete reconciliation:
   ├── Click "Complete"
   ├── System validate: Variance explained? YES
   └── Status: Completed

8. Review & Approve:
   ├── Kepala Accounting review
   ├── Click "Approve"
   ├── Status: Approved ✅
   ├── Tercatat: Approved by Kepala, on 5-Feb-2024
   └── Mail thread shows all changes

Result:
  Full reconciliation record
  Aging analysis (if A/R or A/P):
  ├── 0-30 days: Rp 300jt
  ├── 31-60 days: Rp 150jt
  ├── 61-90 days: Rp 30jt
  └── >90 days: Rp 0jt

Ready untuk audit!
```

**Aging Analysis (Otomatis untuk A/R & A/P):**
```
Contoh A/R aging dari reconciliation:
┌─────────────────────────────────────┐
│ 0-30 Hari:     Rp 300.000.000      │  Current
│ 31-60 Hari:    Rp 150.000.000      │  Current-1
│ 61-90 Hari:    Rp 30.000.000       │  Current-2
│ >90 Hari:      Rp 0                │  Overdue!
├─────────────────────────────────────┤
│ TOTAL A/R:     Rp 480.000.000      │
└─────────────────────────────────────┘

Jika ada >90 hari, perlu investigate:
- Sudah follow-up ke klien?
- Sudah buat provision for doubtful debt?
- Sudah escalate ke legal/collector?
```

---

## 💰 TRACKING PEMBAYARAN PAJAK (Tax Payment Tracking)

### Gunakan untuk:
```
- Track PPh 21 (payroll withholding)
- Track PPh 23 (service/interest withholding)
- Track BPJS contributions (JHT, Kesehatan, JP, JKK, JKM)
- Track PPN (jika applicable)
```

### Cara pakai:
```
Menu: Accounting → Audit & Compliance → Tracking Pembayaran Pajak
```

### Step-by-step (Example: PPh 21):
```
1. Create Tax Payment Tracking:
   ├── Jenis Pajak: PPh 21
   ├── Periode Pajak: January 2024
   └── Save

2. System auto-calculate (read-only):
   ├── Query semua payslips di Jan yang posted
   ├── Sum field "pph21_amount" di semua payslips
   ├── Total Dipotong: Rp 15.000.000
   │   (Contoh hasil aggregasi)
   └── Status: VERIFIED?

3. Verify calculation:
   ├── Cek: "Benar total PPh 21 = Rp 15jt?"
   ├── If YES → click "Verify"
   ├── Status: Verified
   └── tercatat: verified_by, verified_date

4. Record payment:
   ├── Jumlah Dibayar: Rp 15.000.000
   ├── Tanggal Pembayaran: 5-Feb-2024
   ├── Metode: Transfer Bank
   ├── Nomor Referensi: BCA-TRF-123456789
   ├── GL Account: 2102 (Tax Payable - PPh21)
   └── Click "Record Payment"

5. System auto GL posting:
   ├── CREATE journal entry:
   │   Dr: 1101 Bank Account Rp 15.000.000
   │   Cr: 2102 Tax Payable Rp 15.000.000
   │
   ├── Reference: TAX-2024/01-0001
   ├── Posted: Automatically
   └── Status: Paid

6. Reconcile (optional):
   ├── Verify di bank statement: Rp 15jt cleared
   ├── Click "Reconcile Payment"
   ├── Status: Reconciled ✅
   └── Tercatat lengkap: who/when/ref number

Result:
  ├── PPh 21 payment documented
  ├── GL posting automatic
  ├── GL balance updated (Tax Payable = 0)
  ├── Bank balance updated (-Rp 15jt)
  └── Full audit trail: proof of payment

Detail breakdown (optional):
  Payslip #SLP-001: Rp 400.000
  Payslip #SLP-002: Rp 450.000
  Payslip #SLP-003: Rp 500.000
  ... (38 more)
  Total: Rp 15.000.000
```

**Contoh untuk BPJS:**
```
1. Create Tax Payment Tracking:
   ├── Jenis Pajak: BPJS JHT
   ├── Periode: January 2024
   └── Save

2. System auto-calculate:
   ├── Query payslips di Jan
   ├── Sum BPJS contribution (employer portion)
   ├── Total Dipotong: Rp 8.000.000
   └── (Ini company portion untuk JHT)

3. Verify & Record payment
   └── (sama seperti di atas)

4. Hasil:
   ├── BPJS JHT liability: Rp 0 (paid)
   ├── GL posting tercatat
   └── Ready untuk submit ke BPJS
```

---

## 📊 MONTHLY WORKFLOW (Setelah ketiga fitur ini)

### Week 1: CLOSE PERIODE
```
Monday:
  → Check period closing checklist
  → Verify all payslips, expenses, invoices posted
  → Bank & GL reconciliation: mark YES
  → Click "Close Period"
  
Result: Periode locked, ready for reconciliation detail
```

### Week 2: RECONCILIATION
```
Wednesday:
  → Receive customer statements (A/R balance)
  → Create GL reconciliation for A/R
  → Compare expected vs received
  → Investigate & explain any variance
  → Approve reconciliation
  
Thursday:
  → Create GL reconciliation for A/P
  → Receive vendor statements
  → Same process
  
Friday:
  → Create GL reconciliation for Bank
  → Match GL vs bank statement
  → Investigate NSF checks, timing differences
```

### Week 3: TAX PAYMENT
```
Monday-Tuesday:
  → Create tax payment tracking untuk:
     ├── PPh 21 (gaji)
     ├── BPJS JHT
     ├── BPJS Kesehatan
     ├── (Other liabilities)
  → Verify calculations
  → Record payments
  → GL auto-posts

Wednesday:
  → Verify bank posting
  → Reconcile payment tracking
```

### Week 4: AUDIT PACKAGE
```
Friday:
  → Generate reports:
     ├── Period closing summary
     ├── GL reconciliation by account
     ├── Aging analysis (A/R & A/P)
     ├── Tax payment reconciliation
     └── Mail thread audit trail
     
  → Package untuk auditor
```

---

## 🎯 COMMON QUESTIONS

**Q: Bagaimana kalau harus reopen periode karena ada koreksi?"**
```
A: No problem!
   1. Click "Reopen Period"
   2. Make corrections
   3. Re-verify checklist
   4. Click "Close Period" lagi
   5. Audit trail shows: closed → reopened → closed (for reason X)
```

**Q: Variance di A/R sangat besar, apa yang harus dilakukan?"**
```
A: Investigate step-by-step:
   1. Check GL posting: Invoice #? Amount? Date?
   2. Check customer statement: Apakah invoice tercatat?
   3. Contact customer: "Apakah sudah terima invoice?"
   4. Record finding di reconciliation detail
   5. Explanation: "Waiting for customer acknowledgement"
   6. Follow up next week
```

**Q: Tax payment tracking shows overpayment, apa maksudnya?"**
```
A: Means: Amount dibayar > amount dipotong
   Reasons:
   1. Prior period settlement
   2. Penalty/interest payment
   3. Additional voluntary contribution
   4. Overwitholding (payment correction)
   
   Solution: Explain di "Catatan Pembayaran" field
```

---

## ✅ AUDIT READINESS CHECKLIST

```
Before audit review, ensure:

☑️ Semua periode tutup dan locked
☑️ Semua GL reconciliation approved
☑️ Semua tax payment recorded & GL posted
☑️ Aging analysis reviewed & explained
☑️ Period closing checklist completed
☑️ Bank reconciliation documented
☑️ Mail thread shows all approval trails
☑️ Supporting documents (statements, receipts) filed

Ready untuk auditor!
```

---

**UNTUK PERTANYAAN:** Lihat AUDIT_READINESS_CHECKLIST.md atau AUDIT_IMPLEMENTATION_COMPLETE.md untuk detail lengkap.

**VERSION:** outsource_custom v18.0.4.0.0
