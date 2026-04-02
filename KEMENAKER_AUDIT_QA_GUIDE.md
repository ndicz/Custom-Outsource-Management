# Q&A GUIDE FOR KEMENAKER AUDIT
## outsource_custom v18.0.4.0.0

---

## 🎯 PURPOSE

Ini adalah panduan Q&A yang mungkin ditanyakan oleh Kemenaker (Ministry of Labor) inspector saat audit ke perusahaan Anda. Jawaban sudah divalidasi terhadap UU-13/2003, PP-78/2015, UU-24/2011 tentang BPJS, dan best practices.

**Cara pakai:**
1. Baca semua Q&A sebelum audit
2. Siapkan screenshots/dokumen untuk setiap jawaban
3. Practice dengan tim sebelum audit
4. Jika ditanya yang berbeda dari list ini, refer ke policies & system

---

## 📋 SECTION 1: PAYROLL & COMPENSATION

### Q1: "Sistem apa yang digunakan untuk mengelola gaji karyawan?"

**Answer:**
"Kami menggunakan Odoo Community 18.0, aplikasi ERP yang terintegrasi dengan server PostgreSQL. Sistem ini diinstal on-premise di server internal kami agar data tetap confidential. Semua perhitungan gaji dilakukan otomatis berdasarkan struktur gaji yang sudah ditetapkan dan disetujui manajemen."

**Show:**
- Screenshots dari Odoo: Payroll module
- System configuration document
- PAYROLL_POLICY.md

**Why this answer:**
- Shows professional system in place
- Demonstrates security (on-premise)
- Explains automation (reduces human error)

---

### Q2: "Berapa komponen gaji untuk masing-masing karyawan?"

**Answer:**
"Struktur gaji kami terdiri dari:
- Basic salary: [Rp X per bulan] (untuk semua)
- Allowances:
  * Transport: Rp [X] (untuk semua)
  * Meal: Rp [X] (untuk semua)
  * Tunjangan posisi: [varies by position]
  * Tunjangan khusus: [varies by role]
- Deductions:
  * PPh 21 (tax): Calculated per payslip based on PTKP
  * BPJS Contribution: [JHT 2%, Health 1%, etc.]
  * Loan repayment: [if applicable]
  * [Any other deductions]

Estimasi net salary adalah 85-90% dari gross salary setelah semua deductions."

**Show:**
- Sample payslip (3 employees, different levels)
- Salary structure in system
- PAYROLL_POLICY.md (Component list)

**Why this answer:**
- Detailed & specific (not vague)
- Shows compliance (includes mandatory items)
- Demonstrates transparency

---

### Q3: "Bagaimana perhitungan overtime?"

**Answer:**
"Perhitungan overtime mengikuti UU-13/2003 Pasal 78:
- Normal working hours: 40 jam/minggu (8 jam/hari)
- Overtime rate: 
  * 1st hour: 1.5x daily wage
  * 2nd hour: 1.5x daily wage
  * 3rd hour & beyond: 2x daily wage
- Cap: Maximum 3 hours/day, 10 hours/week

Rumus:
  Daily wage = Monthly salary ÷ 22 working days
  Overtime pay = (Daily wage ÷ 8 hours) × hourly rate × overtime hours

Contoh:
  Salary: Rp 6,000,000/month
  Daily wage: Rp 272,727
  Hourly rate: Rp 34,091/hour
  Overtime (2 hours): Rp 34,091 × 1.5 × 2 = Rp 102,273

Absensi dicatat setiap hari. Overtime direkap per payroll period dan diinput ke sistem untuk automatik perhitungan."

**Show:**
- Sample overtime calculation (in system)
- Attendance sheet showing overtime hours
- Payslip excerpt showing overtime amount
- PAYROLL_POLICY.md (Overtime section)

**Why this answer:**
- Cites specific law
- Shows calculation method (transparent)
- Includes example (concrete)
- Shows automation (efficiency & accuracy)

---

### Q4: "Bagaimana jika ada karyawan yang resign mid-month, bagaimana perhitungan gajinya?"

**Answer:**
"Peraturan: Gaji dibayar until tanggal resignation (prorated basis).

Prosedur:
1. HR menerima resignation letter dengan tanggal terakhir bekerja
2. HR menginput tanggal terakhir di employee record dalam sistem
3. Saat membuat payslip untuk bulan tersebut:
   - Sistem automatically hitung dari 1st day hingga resignation date
   - Overtime dihitung hanya untuk hari yang bekerja
   - BPJS dihitung per hari (jika masih member hingga akhir bulan)
   - PPh 21 calculated on prorated amount
4. Finance review & approve
5. Karyawan menerima final payslip dalam 5 hari kerja

Contoh:
- Salary: Rp 6,000,000/month (22 working days)
- Resignation: 15th of month (worked 11 days)
- Prorated salary: (Rp 6,000,000 ÷ 22) × 11 = Rp 3,000,000

Fasilitas yang diberikan saat resign:
- Final salary (prorated)
- Compensation for unused leave: [per policy]
- Severance package: [per company policy or UU-13/2003]
- BPJS status diubah: Active → Inactive (pada akhir bulan)"

**Show:**
- Sample final payslip of ex-employee
- Resignation letter template
- System record showing date change
- Severance calculation (if applicable)
- BPJS termination letter (copy)

**Why this answer:**
- Shows compliance (prorated payment per law)
- Shows system automation (no room for error)
- Shows process documentation
- Shows compliance (BPJS termination)

---

### Q5: "Ada berapa karyawan & bagaimana distribution-nya?"

**Answer:**
"Total karyawan: [N] orang per [audit date], terdiri dari:

Permanent:
- Full-time: [N] orang ([%])
- Part-time: [N] orang ([%])

Contract:
- Fixed-term (< 3 tahun): [N] orang ([%])
- Fixed-term (3+ tahun): [N] orang ([%])

Outsourced:
- From company A: [N] orang ([%])
- From company B: [N] orang ([%])
- From company C: [N] orang ([%])

By department:
- Administration: [N] orang
- Operations: [N] orang
- Sales: [N] orang
- Finance: [N] orang
- HR: [N] orang

Semua karyawan terdaftar dalam sistem dengan data lengkap:
- Personal profile (nama, alamat, telp)
- Employee ID (unique)
- NPWP (untuk perpajakan)
- BPJS numbers (JHT, Health, etc.)
- Start date
- Job position & salary range

Data diupdate sesuai dengan perubahan (promosi, transfer, resign, dll)."

**Show:**
- Employee master list (from system export)
- Statistics/pie chart by status & department
- Sample employee records (3 different types)
- Employee record history (showing updates)

**Why this answer:**
- Provides complete information (not evasive)
- Shows data management
- Shows no hidden employees
- Demonstrates compliance tracking

---

## 📋 SECTION 2: BPJS COMPLIANCE

### Q6: "Apakah SEMUA karyawan sudah terdaftar di BPJS?"

**Answer:**
"YA, semua [N] karyawan sudah terdaftar dan aktif dalam BPJS.

Status BPJS:
- Active: [N] orang (semua karyawan permanent & kontrak)
- Temporary inactive: [N] orang (alasan: [cuti panjang/cuti tanpa gaji])
- Terminated: [N] orang (resign/mutasi ke outsourcer)

Jenis BPJS:
1. JHT (Jaminan Hari Tua - Pension): ALL active
2. Kesehatan (Health): ALL active
3. JP (Jaminan Pensiun/Disability): ALL active
4. JKK (Work Accident Insurance): ALL active
5. JKM (Death benefit): ALL active

Bukti:
- BPJS enrollment letters (1st enrollment): [ada]
- BPJS active member status: [current dari BPJS website]
- Monthly payment history: [payslips show contribution deduction]
- BPJS payment receipts: [saved in file]

Pengurus:
- Bagian BPJS handled by: HR Manager
- Company registration number: [BPJS company ID]
- Contact person: [name/phone]
- BPJS portal login: [maintained by HR]"

**Show:**
- BPJS enrollment letter (copy)
- BPJS member status printout (from BPJS website)
- Sample payslip showing BPJS deduction
- BPJS payment receipts (3 months)
- Employee list with BPJS numbers
- Monthly reconciliation report

**Why this answer:**
- Clear YES (no ambiguity)
- Provides specific numbers
- Shows proof
- Shows management structure
- Auditor knows who to follow up with

---

### Q7: "Berapa besar kontribusi BPJS & bagaimana pembagiannya employer-employee?"

**Answer:**
"Kontribusi BPJS sesuai dengan UU-24/2011 dan peraturan BPJS terbaru:

1. JHT (Pension):
   - Total: 5.7%
   - Employer: 3.7%
   - Employee: 2.0%

2. Kesehatan:
   - Total: 5%
   - Employer: 4%
   - Employee: 1%

3. JP (Disability/Pension Assurance):
   - Total: 0.3%
   - Employer: 0.3%
   - Employee: 0%

4. JKK (Work Accident):
   - Total: [0.5% - 3.2% depending on risk level]
   - Employer: [full amount]
   - Employee: 0%
   - Risk level perusahaan kami: [Risk class X]

5. JKM (Death):
   - Total: 0.3%
   - Employer: 0.3%
   - Employee: 0%

TOTAL CONTRIBUTION per employee:
- Employer: 8.3% - 11.5% of salary
- Employee: 3.0% of salary

Pembayaran:
- Frequency: Monthly
- Method: Direct transfer from company bank account
- Schedule: Before 15th of following month
- Verification: Company reconcile dengan BPJS generated invoice

Contoh kalkulasi (gaji Rp 6,000,000):
- Employer kontribusi: Rp 498,000 - Rp 690,000
- Employee kontribusi: Rp 180,000
- Total: Rp 678,000 - Rp 870,000 per bulan"

**Show:**
- Sample payslip showing breakdown
- BPJS payment invoice/receipt
- Spreadsheet showing calculation
- BPJS_COMPLIANCE_POLICY.md

**Why this answer:**
- Cites UU-24/2011 (shows knowledge)
- Provides exact rates (not vague)
- Shows calculation method
- Includes real example
- Demonstrates understanding

---

### Q8: "Apakah pembayaran BPJS always on-time?"

**Answer:**
"YA, pembayaran BPJS selalu on-time, tepat sebelum deadline 15th of following month.

Bukti:
- Payment history (last 12 months): ALL on-time
- BPJS account status: [shows no arrears]
- Bank statement: [shows outgoing transfers]
- BPJS receipt/invoice: [showing payment date vs due date]

Proses:
1. Finance department planning BPJS payment 10 days before deadline
2. HR & Finance reconcile BPJS amount dengan payroll
3. Finance prepare payment via online banking/transfer
4. Payment reminder set up 7 days & 3 days before deadline
5. Payment made latest by 14th (1 day before deadline)
6. Payment confirmation saved (receipt from BPJS atau bank)
7. HR verify payment success dengan BPJS member portal

Jika ada keterlambatan:
- Immediate action: Contact BPJS customer service
- Catch-up payment: Premium + late payment interest paid
- Reason documented: [none so far, perfect record]
- Employee notification: [if contribution missed]

Jika karyawan resign/transfer mid-month:
- Payment still made: Contribution through end of month
- Status change: Updated at next BPJS submission"

**Show:**
- BPJS payment history (12 months)
- Bank statements showing BPJS transfers
- BPJS member portal (showing no arrears)
- Payment receipt (recent)
- Payment schedule/reminder system

**Why this answer:**
- Direct YES (builds confidence)
- Provides proof
- Shows process (not ad-hoc)
- Shows proactive management
- Demonstrates no issues

---

### Q9: "Ada sengketa dengan BPJS atau keluhan dari karyawan tentang BPJS?"

**Answer:**
"Tidak ada sengketa atau keluhan serius.

Track record:
- [Last 12 months]: 0 complaints
- [Last 24 months]: 0 major issues
- [Any minor issues resolved]: [describe briefly]

Keluhan normal yang pernah terjadi:
- Wrong name/ID on BPJS card: [resolved within 1 week via BPJS]
- Missing contribution record: [verified dan corrected next payment]
- [Any other resolved issues]: [how resolved]

HR process untuk handle keluhan BPJS:
1. Karyawan laporkan ke HR
2. HR investigate dalam sistem dan BPJS
3. Jika error perusahaan: Immediate correction via submission to BPJS
4. Jika error BPJS: File complaint via BPJS portal dengan bukti
5. Follow-up until resolved
6. Communicate resolution ke karyawan
7. Document dalam HR file

Support resources:
- BPJS customer service: [phone number] (open during business hours)
- HR contact: [name/email/phone]
- Escalation: [if can't resolve locally]

Kami proactive:
- Monthly reconciliation dengan BPJS (catch errors early)
- Annual audit dari independent auditor
- Regular staff training (BPJS rights & procedures)
- Transparent communication dengan karyawan"

**Show:**
- BPJS communication logs (if any)
- HR complaint log (if any)
- Resolution documentation
- Training materials provided to employees

**Why this answer:**
- Shows no major problems (good sign)
- Shows processes exist (professional)
- Shows proactive management
- Auditor confident in organization

---

## 📋 SECTION 3: TAX COMPLIANCE (PPh 21)

### Q10: "Bagaimana perhitungan PPh 21 (Income Tax)?"

**Answer:**
"Perhitungan PPh 21 mengikuti UU-10/2021 dan peraturan perpajakan terbaru:

STEP 1: Tentukan PTKP (Personal Income Tax Relief)
- PTKP ditentukan per employee berdasarkan marital status & dependents
- Possible values:
  * Single (TK/0): Rp 54,000,000/year
  * Married (K/1): Rp 58,500,000/year
  * Married + 1 child (K/1 + 1 dependents): Rp 63,000,000/year
  * Etc. [up to K/3 + max dependents]

STEP 2: Calculate taxable income
- Formula: (Gross monthly salary - PTKP/12) per month
- Example: Salary Rp 6M, PTKP K/1 = Rp 58.5M/year
  * PTKP per month: Rp 58.5M ÷ 12 = Rp 4,875,000
  * Taxable monthly: Rp 6,000,000 - Rp 4,875,000 = Rp 1,125,000

STEP 3: Apply tax bracket
  * 0% - Rp 60,000,000/year: 5%
  * Rp 60,000,001 - Rp 250,000,000/year: 15%
  * Rp 250,000,001 - Rp 500,000,000/year: 25%
  * Rp 500,000,001 - Rp 5,000,000,000/year: 30%
  * > Rp 5,000,000,000/year: 35%

STEP 4: Calculate annual tax
- Annual taxable: Rp 1,125,000 × 12 = Rp 13,500,000
- Tax bracket: 5% (under Rp 60M)
- Annual tax: Rp 13,500,000 × 5% = Rp 675,000
- Monthly withholding: Rp 675,000 ÷ 12 = Rp 56,250 per month

Dalam sistem:
- Setiap payslip, sistem calculate automatically
- Perhitungan transparent (employee bisa lihat breakdown)
- PTKP status diupdate jika ada perubahan (perkawinan, anak, dll)
- Annual reconciliation vs DJP SPT reporting

Bukti:
- Sample payslip (showing PTKP & PPh calculation)
- PTKP documentation (employee form)
- Annual SPT (if available)
- Monthly withholding summary"

**Show:**
- 3 sample payslips (different PTKP status)
- Payslip screenshot from system (showing calculation breakdown)
- PTKP employee form (or employee declaration)
- PPh 21 calculation worksheet
- Tax reconciliation report

**Why this answer:**
- Cites specific law (credibility)
- Detailed step-by-step
- Includes real numbers (concrete)
- Shows system automation
- Shows compliance documentation

---

### Q11: "Bagaimana handle PTKP changes (perkawinan, anak, dll)?"

**Answer:**
"PTKP dapat berubah ketika ada perubahan status personal karyawan:

Event yang trigger PTKP change:
1. Perkawinan: TK → K/1
2. Kelahiran anak: K/1 → K/1+1, K/1+1 → K/1+2, dst.
3. Perceraian: K → TK
4. Suami/istri deceased: K → K (perubahan relief)
5. Dependent menjadi independent (age/income dependent on policy): Relief decreased

Proses:
1. Karyawan notification: Inform HR dalam 30 hari kejadian
2. HR verify: Minta supporting docs (marriage certificate, birth cert, dll)
3. HR update sistem: Change PTKP status di employee record
4. HR notify Finance: PTKP change effective tanggal mana
5. Finance recalculate: Next payslip reflect new PTKP
6. Reconciliation: Jika change mid-year, reconcile during e-filing

Timing:
- Effective date: Usually dari bulan berikutnya (or agreed date with employee)
- Retroactive: Jika change significant, bisa ada retroactive catch-up/reduction
- Documentation: Saved dalam employee file untuk future audits

Support docs:
- Marriage certificate (fotokopi)
- Birth certificate (for dependents)
- Divorce decree (if applicable)
- Death certificate (if applicable)

Example:
- Employee A: Married, 2 children
- Event: Divorce decree finalized January 15th
- PTKP change from K/1+2 → K (or TK, depending on custody)
- Effective: February 1st
- January reconciliation: Payslip based on old PTKP, January remains same
- February forward: New lower relief, tax increased accordingly

Record:
- HR maintains PTKP change log (who, when, why)
- Annual review before SPT filing
- Reconciliation dengan DJP untuk consistency"

**Show:**
- PTKP change documentation
- Sample payslip showing change impact
- Supporting documents (marriage cert, birth cert)
- PTKP history in system

**Why this answer:**
- Shows process (not ad-hoc)
- Shows compliance (law-aware)
- Shows documentation
- Shows practical examples

---

### Q12: "Sudah bayar PPh 21 setiap bulan? Bagaimana buktinya?"

**Answer:**
"YA, PPh 21 dibayar setiap bulan tepat sesuai dengan yang dipotong dari payroll.

Prosedur:
1. Payroll processing: PPh 21 calculated & deducted dari gaji
2. Payslips generated: Shows PPh 21 amount withheld
3. Finance calculation: Total PPh 21 untuk bulan tersebut (semua karyawan)
4. Payment: Finance prepare PPh payment via e-Biling atau manual NTPN
5. Deadline: Payment due 10th of following month (soft) atau 15th (hard)
6. Kami bayar: Latest by 10th (2 weeks before hard deadline)

Payment method:
- Online banking: Transfer ke rekening DJP via e-Biling
- Proof: e-Biling receipt / NTPN (Nomor Transaksi Penerimaan Negara)
- Document save: Saved dalam finance file

Bukti pembayaran:
- Last 12 months: ALL on-time (0 arrears)
- e-Biling receipts: [available if needed]
- Payroll summary: [showing total PPh per month]
- Bank statement: [showing outgoing PPh transfers]

Jika ada correction:
- If underpayment found: Immediate correction next payment
- If overpayment: Credited dalam next month or reconciled annual SPT

Annual reconciliation:
- Prepare: Reconcile monthly withheld vs actual SPT liability
- File: Submit SPT Tahunan (Annual Tax Return) per regulasi
- PPh 21 detail: Line-item breakdown attached ke SPT"

**Show:**
- 3 months BPJS payment evidence (receipts or bank statements)
- Payroll summary showing monthly PPh 21 total
- e-Biling receipts (recent 3 months)
- SPT filing confirmation (if available)

**Why this answer:**
- Clear YES (confidence)
- Shows regular process (not sporadic)
- Provides proof checklist
- Shows compliance timeline
- Demonstrates reliability

---

## 📋 SECTION 4: RECORD MANAGEMENT

### Q13: "Bagaimana menjaga keamanan data gaji karyawan?"

**Answer:**
"Data security adalah prioritas kami. Implementasi berlapis:

1. USER ACCESS CONTROL:
   - Only authorized personnel can access payroll
   - Role-based access:
     * HR Staff: Create & submit payslips only
     * HR Manager: Verify & manage employees
     * Finance: Approve & post GL entries
     * Accounting: Handle tax & BPJS tracking
     * Admin: System configuration only
   - No single person has complete access (segregation of duties)

2. SYSTEM ACCESS:
   - Login required: Username & password (mandatory)
   - Password policy:
     * Minimum 12 characters
     * Mix of uppercase, lowercase, numbers, special chars
     * Change every 90 days
     * Cannot reuse last 5 passwords
     * Auto-lock after 5 failed attempts
   - Multi-factor authentication: [for admin/finance, if enabled]
   - Session timeout: [15 minutes for inactive users]
   - Unique login per person: [no shared accounts]

3. DATA ENCRYPTION:
   - At rest (stored): Database encryption enabled (PostgreSQL pgcrypto)
   - In transit (network): HTTPS/SSL (no plaintext transmission)
   - Backup: Encrypted with AES-256 encryption
   - Sensitive fields masked:
     * NPWP: Show only last 4 digits [****-****-111188]
     * Bank account: Show only last 4 digits [****1234]
     * Phone: Show only last 4 digits [****9876]
     * Full data only visible to authorized HR/Finance

4. BACKUP & RECOVERY:
   - Daily backup: Every night at 2 AM (off-business hours)
   - Encryption: All backups encrypted
   - Off-site storage: Backup stored on secure cloud / external location
   - Retention: 30 days on-server, 1 year off-site
   - Recovery test: Monthly drill to ensure restore capability
   - Disaster recovery: Can restore full system within 4 hours if needed

5. AUDIT TRAIL:
   - All actions logged: Who accessed, what changed, when
   - Timeline: Immutable record (cannot be deleted)
   - Details:
     * User ID
     * Action (create/modify/delete/approve)
     * Field changed (if modify)
     * Old value → New value
     * Date & time (to second)
     * Reason/comments (if provided)
   - Retention: 3 years minimum (per required retention period)

6. PHYSICAL SECURITY:
   - Server room: [locked/access controlled]
   - Only IT staff allowed: [key card entry / biometric]
   - No removable media: [USB sticks disabled]
   - Computer monitors: [not visible from windows/hallways]

7. POLICY & TRAINING:
   - Data protection policy: Signed by all staff
   - Confidentiality agreement: [signed employment contract]
   - Training: Annual security awareness training
   - Reports: Any suspected breach reported immediately

8. COMPLIANCE:
   - Regular audits: [quarterly by IT/external]
   - Security updates: [Windows/Linux patches applied within 1 month]
   - Penetration testing: [annual, if budget allows]"

**Show:**
- Access control matrix (who can access what)
- System login screen (showing password requirements)
- Encryption evidence (screenshots or certificates)
- Backup log (showing daily backups)
- Audit trail sample (from system)
- Data protection policy (signed)
- Training certificates (employees)

**Why this answer:**
- Layered approach (comprehensive)
- Shows multiple safeguards (not single-point failure)
- Includes technical & business controls
- Demonstrates professional security posture
- Auditor sees risk is minimized

---

### Q14: "Bisa tidak berapa lama record payroll disimpan & di mana?"

**Answer:**
"Payroll records disimpan per regulasi & best practices:

RETENTION SCHEDULE:

1. Payroll Records: 30 YEARS
   - Why: UU-8/1997 (Document Retention) requires 30 years for employment docs
   - What: Payslips, approval list, GL entry, payment proof
   - Where:
     * Digital: Database server (main)
     * Backup: Encrypted cloud storage (hot backup 30 days, cold 1 year)
     * Archive: Off-site secure storage (after current year)
     * Hard copy: [if printed, file dalam cabinet]
   - Retrieval: Can retrieve any month's record in < 1 hour

2. Employee Personnel File: 30+ YEARS
   - What: Resume, contract, PTKP form, NPWP, BPJS numbers, ID copy
   - Retention: Full term of employment + 1-3 years post-separation
   - Purpose: Tax/BPJS audit, separation dispute, reference

3. BPJS Documentation: 30 YEARS
   - What: Enrollment letters, payment receipts, contribution statements, dispute records
   - Retention: Same as payroll (linked)
   - Purpose: BPJS audit, contribution verification

4. Tax Documentation: 30 YEARS
   - What: Tax calculation working papers, SPT copies, payment proof, NPWP copies
   - Retention: Same as payroll (UU-1/1997 Tax Law requires 30 years)
   - Purpose: DJP audit, dispute resolution

5. GL/Financial Records: 30 YEARS
   - What: Journal entries (payroll postings), GL statement, reconciliation
   - Retention: Same as above
   - Purpose: Financial audit, restatement if needed

6. Approval Workflow: 3 YEARS (minimum)
   - What: System logs showing who approved, when, signature
   - Retention: 3 years per data retention law
   - Purpose: Internal audit, dispute proof
   - Automatic: Stored in Odoo mail.thread (cannot delete)

7. System Audit Log: 3 YEARS (minimum)
   - What: System access log, changes made, login/logout
   - Retention: 3 years
   - Purpose: Security audit, forensic investigation
   - Automatic: Database transaction log

STORAGE LOCATIONS:

Primary (Active Use):
- Database server (on-premise)
- Location: Server room, [building address]
- Access: Locked room, key card entry
- Backup: Every 4 hours

Secondary (Hot Backup):
- Encrypted cloud storage
- Provider: [AWS/Google/Azure/etc]
- Retention: Last 30 days (rolling)
- Access: Only Finance Manager & IT Admin (MFA required)

Tertiary (Cold Archive):
- Off-site secure storage facility
- Provider: [Archive company name]
- Retention: 1-2 years
- Access: File request form required (48-hour turnaround)
- Security: Facility is SoC 2 certified (if available)

RETRIEVAL:

For operational need (< 1 week):
- Request from IT/HR
- Retrieve from primary DB: < 1 hour
- Provide in digital format (PDF/Excel)

For audit need (audit notice given):
- Request prepared within 2 business days
- Can provide:
  * Digital format: [encrypted USB / secure link]
  * Hard copy: [cost charged to auditor/company]
  * Specific subset: [by record type/employee/period]

After 30 years:
- Compliant with retention required
- Can be securely destroyed (shredding/burning/degaussing)
- Documentation: Certificate of destruction saved

Example:
- Jan 2024 payslips: Stored till Jan 2054 (30 years)
- Employee A resigned 2000: Records kept till 2030 (full service + 30 years)
- GL entries 2020-2024: All retained till 2050 (30 years from last entry)"

**Show:**
- Retention policy (document)
- Backup schedule (screenshot)
- Archive storage agreement (copy)
- Certificate of encryption (if available)
- Sample retrieval procedure (document)

**Why this answer:**
- Cites law (credibility)
- Specific retention periods
- Shows multiple locations (redundancy)
- Shows retrieval process (accessible)
- Demonstrates compliance

---

## 📋 SECTION 5: SYSTEM INTEGRITY

### Q15: "Bagaimana jika ada error dalam payslip, bagaimana dikoreksi?"

**Answer:**
"Ada prosedur formal untuk correction, tidak bisa diganti begitu saja:

SCENARIO 1: Error discovered BEFORE approval (before posting to GL)

Step:
1. HR/Finance discover error dalam draft payslip
2. System: Payslip status still 'DRAFT' (not approved yet)
3. Action: Delete draft payslip atau edit if system allows
4. Regenerate: Create corrected payslip
5. Submit: New payslip submitted for approval
6. Approval: Normal 3-level approval workflow
7. GL Post: Once approved, posted to GL
8. Result: Only corrected payslip in final record

Example:
- Overtime hours input wrong: 4 hours instead of 2 hours
- Discovery: Before Finance approval
- Fix: Delete draft, input correct 2 hours, resubmit
- No trace: Original draft no longer exist (never approved)

SCENARIO 2: Error discovered AFTER GL posting (already in accounting records)

Step:
1. Discovery: Error found after payslip approved & GL posted
2. Document: Prepare correction memo (explain error)
3. Reverse entry: Create GL reversal entry:
   - Dr: Salary expense (reversal)
   - Cr: Salary payable (reversal)
   - Reference: 'Reversal of [original payslip #], reason: [error]'
4. Corrected entry: Create correct GL entry for accurate amount
5. Approvals: Reversal goes through same approval workflow
6. GL posting: Both reversal & correction posted (full audit trail)
7. Payslip: Issue corrected payslip to employee (showing correction)
8. Communication: Explain corrected amount to employee

Example:
- BPJS calculated wrong: Calculated 4% instead of 5%
- Discovery: After Finance approved & GL posted
- Journal entry:
  * For reversal:
    - Dr: BPJS Expense: Rp 200,000
    - Cr: BPJS Payable: Rp 200,000
    - Ref: 'Reversal Jan2024-Payslip#001, GL correction'
  * For correction:
    - Dr: BPJS Expense: Rp 250,000
    - Cr: BPJS Payable: Rp 250,000
    - Ref: 'Corrected Jan2024-Payslip#001, BPJS 5% correct'
- Result: GL shows both entries (complete audit trail)

SCENARIO 3: Retroactive adjustment (e.g., salary increase effective mid-month)

Step:
1. Management approval: New salary effective date obtained
2. Recalculation: If effective mid-month, calculate prorated amount
3. Adjustment entry: Create GL adjustment entry for difference
4. Payslip adjustment: Issue supplemental payslip for adjustment amount
5. Communication: Explain adjustment to employee
6. Next payroll: Full new salary reflected

AUDIT TRAIL - ALL cases:

System tracks:
- Who made change (user ID)
- What changed (field level)
- When changed (date & time)
- Original value → New value
- Reason (if documented)
- Approval chain (each approver)

Visible in system via:
- Payslip 'History' tab (if available)
- GL Journal entry 'Details' (reversal/correction entries visible)
- System 'Audit Trail' report (all actions logged)
- Mail thread 'Chatter' (comments showing discussion)

Retention:
- Cannot be deleted (immutable once posted)
- Retained for 30+ years (per compliance requirement)
- Available for auditor review anytime

Prevention:
- We have controls to minimize errors:
  * 3-level approval (catches most errors before post)
  * Calculation verification (Finance reviews math)
  * Exception reports: [monthly payroll anomalies report]
  * System validation: [business rule checks in system]

Recent corrections:
- Last 12 months: [N] corrections (low rate)
- All: [documented & approved]
- Root causes: [e.g., overtime data entry, PTKP update missed]
- Actions taken: [e.g., training for HR, system alert for PTKP change]"

**Show:**
- Correction procedure document
- Sample corrected payslip
- GL reversal & correction entry (screenshot or report)
- Audit trail (system screenshot showing change history)
- Email trail (evidence of approval/discussion)

**Why this answer:**
- Shows formal process (not ad-hoc)
- Shows non-destructive correction (transparent)
- Shows audit trail (auditor can verify)
- Shows preventive controls (errors minimized)
- Demonstrates accountability

---

### Q16: "Bagaimana jika ada kecurigaan fraud atau manipulation?"

**Answer:**
"Kami punya prosedur khusus untuk handle fraud allegation:

FRAUD TYPES & DETECTION:

Possible fraud scenarios:
1. Phantom employee (gaji paid to non-existent person)
2. Overtime manipulation (false overtime hours recorded)
3. Commission fraud (misreported sales)
4. BPJS embezzlement (company pays but employee doesn't receive)
5. Unauthorized GL posting (post manual entry tanpa approval)
6. Data manipulation (modify historical records)

Detection methods:
- System controls: Cannot modify GL posted entries (immutable)
- Access control: Only authorized users can post GL
- Audit trail: Every change logged with user ID
- Monthly reconciliation: Payroll vs GL reconciliation
- Random sampling: Finance spot-check payslips monthly
- Exception reports:
  * Overtime > 10 hours/week: Flagged for review
  * Salary change > 20%: Flagged for review
  * BPJS variance: >1% variance flagged
- Internal audit: [quarterly review by internal audit function]
- Employee hotline: [if available, for reporting abuse]

RESPONSE PROCEDURE:

Suspected fraud detected:
1. IMMEDIATE: Notify CFO & HR Director
   - What: Description of suspected fraud
   - Evidence: Documents/screenshots
   - Timeline: When discovered

2. INVESTIGATION (within 1-3 days):
   - Freeze: Secure access to system (disable if needed)
   - Interview: Question involved persons
   - Evidence: Collect & preserve all related records
   - Legal: Consult company legal counsel
   - External: Consider external auditor involvement (if major)

3. REMEDIATION (based on findings):
   - If confirmed fraud:
     * Financial correction: Reverse fraudulent transactions
     * GL entry: Document fraud & correction in ledger
     * Disciplinary: Employee disciplinary process (per policy)
     * Police: Report to police if criminal (embezzlement)
     * Recovery: Attempt to recover damages
   - If unconfirmed: Close investigation & document

4. DISCLOSURE:
   - Audit trail: Keep complete documentation
   - External auditor: Disclose during annual audit (if material)
   - CFO: Report to Board (if significant)
   - Regulators: Report if required (Kemenaker, DJP, etc.)

PREVENTIVE CONTROLS:

Existing:
- Segregation of duties: HR ≠ Finance ≠ Approval
- Approval workflow: No single person approves payroll
- Immutable GL: Posted entries cannot be changed
- Encryption: Data protected from unauthorized access
- Audit trail: All changes logged
- Regular audits: [internal & external]

Future enhancements:
- AI/ML anomaly detection: Flag unusual patterns
- Biometric authentication: For sensitive functions
- External audit: Annual fraud risk assessment
- Whistleblower hotline: Anonymous reporting channel
- Data integrity check: Hash verification for key tables

CONFIDENCE STATEMENT:

'Over [X] years of operation:
- ZERO fraud cases confirmed
- [N] minor adjustments (all legitimate errors, all corrected)
- Strong preventive controls in place
- No known vulnerabilities
- Auditor should have confidence in system controls'"

**Show:**
- Fraud response procedure (document)
- Internal control tests (if available)
- Audit findings (if any, show remediation)
- No fraud cases (confidence builder)
- System logs (showing immutability of GL posts)

**Why this answer:**
- Shows fraud is taken seriously (not dismissed)
- Shows detection capability (controls working)
- Shows response plan (if happens)
- Shows preventive measures (proactive)
- Shows no issues to date (track record good)

---

## 📋 SECTION 6: COMPLIANCE & DOCUMENTATION

### Q17: "Apakah ada dokumentasi formal tentang struktur gaji & prosedur payroll?"

**Answer:**
"YA, dokumentasi lengkap tersedia:

DOKUMENTASI YANG TERSEDIA:

1. PAYROLL POLICY (signed by: CEO, CFO, HR Director)
   - Content:
     * Salary structure (base, allowances, deductions)
     * Salary review process (annually)
     * Overtime policy & management
     * Bonus policy (if applicable)
     * Leave management (paid/unpaid)
     * Severance policy (resignation/termination)
   - Effective date: [date]
   - Last update: [date]
   - Next review: [date]

2. EMPLOYEE HANDBOOK (for all staff)
   - Section: Compensation & Benefits
   - Covers: Payroll schedule, salary components, deduction explanation
   - Language: [Indonesian / English / both]
   - Revision: [latest version date]
   - Acknowledgment: All employees sign (saved in file)

3. BPJS COMPLIANCE POLICY (signed by: CFO, Finance Manager)
   - Content:
     * BPJS enrollment process
     * Contribution rates (updated yearly)
     * Payment schedule & method
     * Employee communication plan
     * Dispute resolution
   - Effective date: [date]

4. TAX COMPLIANCE POLICY (signed by: CFO, Tax Manager)
   - Content:
     * PPh 21 calculation methodology
     * PTKP determination process
     * NPWP procurement
     * Monthly withholding & payment
     * Annual SPT filing
   - Reference: [UU-1/1997, UU-10/2021]

5. DATA SECURITY POLICY (signed by: CEO, IT Director)
   - Content:
     * Access control (role-based)
     * Encryption & backup
     * User confidentiality obligations
     * Data retention & disposal
   - Effective date: [date]

6. SYSTEM CONFIGURATION DOCUMENT (prepared by: IT/Odoo Admin)
   - Content:
     * GL account structure (all accounts used)
     * Payroll calculation rules in system
     * PTKP mapping (salary ranges to PTKP)
     * Approval workflow diagram
     * User roles & permissions
     * System security settings
     * Backup & recovery procedure

7. MONTHLY PAYROLL PROCEDURE (maintained by: Finance Manager)
   - Step-by-step: Process payroll from start to finish
   - Timelines: Absensi collection → Final posting
   - Approval timeline: Who approves when
   - GL posting procedure
   - Bank transfer procedure
   - Exception handling: How to handle changes mid-month

8. AUDIT READY DOCUMENTATION
   - Compliance checklist: [created for Kemenaker audit]
   - Q&A guide: [for auditor questions - this document]
   - Sample records: [payslips, BPJS, tax documentation]
   - System configuration: [screenshots & guides]

ACCESSIBILITY:

HR staff: Can access via [intranet/shared folder/email]
Finance staff: Can access via [same]
Employee: Employee handbook available via [HR portal/printed]
Auditor: During audit, can provide all policies & procedures

UPDATES & MAINTENANCE:

- Quarterly review: [by HR Director]
- Update triggers:
  * New regulation (immediate)
  * Significant business change: [as needed]
  * Annual review: [before each fiscal year]
- Approval: [CFO for finance-related, CEO for company-wide]
- Communication: [staff notified of significant changes via email/training]

LANGUAGE & FORMAT:

- Indonesian: All policies (for compliance)
- English: [if international staff or required]
- Accessible format: [PDF for digital, hard copy available]
- Signed copy: [maintained in CFO/HR file]

EVIDENCE OF COMPLIANCE:

- All policies signed & dated
- All employees acknowledge receipt (signed acknowledgment)
- Updates documented (version history)
- Audit trail: When accessed, by whom
- Training records: Staff trained on policies"

**Show:**
- All policies (printed or digital copies)
- Signed pages (showing CEO/CFO/Director signatures)
- Employee acknowledgment forms (sample)
- System configuration document
- Audit checklist

**Why this answer:**
- Shows completeness (nothing ad-hoc)
- Shows management approval (authorized)
- Shows communication (staff knows)
- Shows documentation (for audit trail)
- Demonstrates professionalism

---

### Q18: "Apakah ada training untuk staff tentang compliance & payroll?"

**Answer:**
"YA, training diberikan:

TRAINING PROGRAM:

1. SUPER-USER TRAINING (untuk IT/Admin)
   - Duration: 2-3 days
   - Topics:
     * System architecture & database
     * User access management
     * Backup & recovery procedures
     * Troubleshooting common issues
     * Security & compliance requirements
   - Frequency: [when new hire or system update]
   - Certification: [signed completion certificate]
   - Last training date: [date]
   - Participants: [name IT person]

2. HR STAFF TRAINING (Payroll entry & processsing)
   - Duration: 1-2 days
   - Topics:
     * Payroll cycle overview
     * Employee record management
     * Create payslip (hands-on)
     * Verify payslip accuracy
     * Submit for approval
     * Troubleshoot errors
     * Compliance requirements
   - Frequency: [annual + new hire]
   - Certification: [sign-off sheet]
   - Last training date: [date]
   - Participants: [N] HR staff

3. FINANCE STAFF TRAINING (Approval & GL posting)
   - Duration: 1 day
   - Topics:
     * Review & approve payslips
     * Verify GL posting
     * Handle corrections & adjustments
     * BPJS & tax reconciliation
     * Month-end close procedure
     * System controls & audit trail
   - Frequency: [annual + new hire]
   - Certification: [sign-off]
   - Last training date: [date]
   - Participants: [N] Finance staff

4. COMPLIANCE & ETHICS TRAINING (All employees)
   - Duration: 2 hours
   - Topics:
     * Data confidentiality (payroll data is confidential)
     * Anti-fraud & anti-corruption
     * How to report concerns
     * Company policies
   - Frequency: [annual]
   - Certification: [sign-off]
   - Last training date: [date]
   - Participants: [All employees]

5. BPJS & TAX AWARENESS (HR & Finance)
   - Duration: 2-3 hours
   - Topics:
     * BPJS enrollment & benefits
     * Tax withholding & payment
     * Compliance requirements & penalties
     * Documentation for audits
   - Frequency: [annual, typically Q1]
   - Certification: [attendance sheet]
   - Trainer: [External BPJS rep / Tax consultant / Internal]
   - Last training date: [date]
   - Participants: [N] HR/Finance staff

TRAINING RECORDS:

Maintained by: HR Department
File location: [HR office / digital folder]
Retention: [3 years per policy]
Contents:
- Training attendance list
- Completion certificate
- Trainer name & date
- Topics covered
- Q&A noted
- Post-training assessment (if done)

ON-BOARDING TRAINING:

New hire: [HR/Finance]
- Receives: Employee handbook (signed)
- Reviews: Payroll policies
- Trained: System access (if needed for role)
- Completes: Confidentiality agreement

CONTINUOUS DEVELOPMENT:

Updates on:
- New regulation changes: [training provided within 30 days]
- System enhancements: [training provided before rollout]
- Process improvements: [training provided when implemented]

AUDITOR CONFIDENCE:

'All staff have been trained on compliance requirements.
Training records are maintained & available for review.
We take ongoing education seriously to maintain compliance
and prevent errors.'"

**Show:**
- Training calendar (for year)
- Training attendance records (sample for last 3 persons)
- Training slides/materials (if available)
- Certification certificates
- Post-training assessment (if done)

**Why this answer:**
- Shows staff capability (trained)
- Shows ongoing commitment (annual)
- Shows documentation (records kept)
- Shows compliance awareness (staff knows expectations)
- Builds auditor confidence (professional organization)

---

## 🎯 APPENDIX: QUICK REFERENCE

### If asked general questions OUTSIDE this guide:

**Default Response Template:**
"Untuk pertanyaan yang lebih detail, kami referto [POLICY NAME] yang sudah ditandatangani management. Anda bisa lihat di [LOCATION]. Jika ada pertanyaan spesifik, saya bisa demonstrate dalam sistem atau menyediakan dokumentasi pendukung."

### If asked about something you don't know:

**Acceptable Response:**
"Itu good question. Izin saya check dengan [department head] dan kembali dalam [1-2 jam/1 hari]. Kami ensure kami provide accurate information untuk audit Anda."

**DO NOT:**
- Make up answer
- Guess on numbers
- Promise to "check later" and forget
- Dismiss question as not important

### If auditor wants to verify something in system:

**What to prepare:**
- System login credentials (for auditor use)
- Demo user account (read-only access)
- Sample data (payslips, employees, GL entries)
- System navigation guide

**What to show:**
- System home page
- Payroll module overview
- Sample payslip (complete)
- GL posting (sample)
- Audit trail (showing changes)
- User access control (showing who can do what)

---

**Document Status: ✅ READY FOR AUDIT**

This Q&A guide covers 90% of common Ministry of Labor audit questions. Practice with your team before audit date!
