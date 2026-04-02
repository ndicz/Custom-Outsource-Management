# Real Case End-to-End (Semua Modul)

Dokumen ini adalah simulasi bisnis nyata dari awal sampai akhir untuk module Outsource Custom.

## 1. Profil Kasus
- Nama perusahaan: PT Sumber Daya Nusantara
- Bulan simulasi: April 2026
- Klien:
  - PT Maju Retail
  - PT Cipta Logistik
- Project:
  - Project Security Maju Retail (20 orang)
  - Project Warehouse Cipta Logistik (15 orang)

## 2. Tujuan Simulasi
- Menjalankan workflow lengkap dari setup, operasional, payroll, pajak, pembayaran, sampai audit closing.
- Memastikan semua modul terintegrasi dan angka laporan konsisten.

## 3. Prasyarat Sistem
- Module `outsource_custom` sudah ter-install dan upgrade terakhir sukses.
- Chart of account dasar sudah siap.
- User role minimal:
  - HR Officer
  - HR Manager
  - Finance/Accounting
  - Admin

## 4. Setup Master (Hari 1)
### 4.1 Setup Klien
- Klik menu: `Outsource > Klien > Daftar klien` (atau `Contacts` jika user lebih nyaman dari app Contacts).
- Buat partner perusahaan:
  - PT Maju Retail (dengan NPWP)
  - PT Cipta Logistik (dengan NPWP)
- Isi flag PKP jika relevan.

### 4.2 Setup Project & Analytic
- Klik menu: `Outsource > Klien > Project` (atau app `Project`).
- Buat 2 project dan analytic account terkait:
  - PRJ-MR-SEC
  - PRJ-CL-WHS
- Hubungkan project ke klien masing-masing.

### 4.3 Setup Payroll Components
- Klik menu: `Outsource > Setup Payroll > Komponen Gaji`.
- Verifikasi komponen gaji default sudah tersedia:
  - Gaji Pokok
  - Tunjangan
  - Overtime
  - Potongan Lain
  - PPh21
  - BPJS

### 4.4 Setup Accounting Parameters
- Klik menu: `Accounting > Configuration > Settings`.
- Isi akun konfigurasi outsource:
  - Salary Expense
  - Salary Payable
  - Tax Payable
  - BPJS Payable
- Isi akun expense operasional per kategori.

## 5. Setup Karyawan (Hari 1-2)
- Klik menu: `Outsource > Payroll > Gaji Karyawan`.
Buat minimal 5 karyawan per project dulu untuk pilot test.

Contoh data per karyawan:
- Nama: Budi Santoso
- Klien penempatan: PT Maju Retail
- Project: PRJ-MR-SEC
- PTKP: TK0
- Gaji Pokok: 5,000,000
- Tunjangan Manual: 500,000
- Potongan Manual: 0
- Tarif Overtime: 150

Tambahkan juga 1 contoh pinjaman aktif untuk 1 karyawan agar cicilan otomatis teruji.

## 6. Operasional Harian (Hari 2-25)
### 6.1 Purchase & Costing
- Klik menu: `Purchases > Orders > Requests for Quotation` lalu konfirmasi menjadi PO.
- Buat 3 Purchase Order:
  - Seragam satpam (billable ke klien)
  - HT/radio komunikasi (internal)
  - Jasa maintenance (billable)
- Pastikan cost category dan billable flag terisi.
- Validasi jurnal/invoice terkait terbentuk normal.

### 6.2 Operational Expense
- Klik menu: `Outsource > Financial & Operations > Operational Expense`.
- Input minimal 5 expense:
  - Transport supervisor
  - Utilities pos security
  - Supplies kebersihan
  - Makan lembur
  - Professional fee training
- Jalankan approval flow sampai `Approved/Post`.
- Pastikan bukti lampiran terisi untuk audit sample.

### 6.3 Sales & Invoicing
- Klik menu: `Sales > Orders > Quotations` lalu `Accounting > Customers > Invoices`.
- Buat SO bulanan ke kedua klien.
- Buat invoice dan validasi posting.
- Jika ada PPh23, pastikan field tax-withholding terisi.

## 7. Payroll + Absensi Import (Tanggal 26-28)
### 7.1 Buat Periode Payroll
- Klik menu: `Outsource > Payroll > Periode Payroll`.
- Periode: 01 Apr 2026 - 30 Apr 2026
- Status: Open
- Klik Auto-Generate Slips

### 7.2 Import Absensi dari Sistem Eksternal
- Klik menu: `Outsource > Payroll > Periode Payroll > (pilih periode) > Import Absensi`.
- Dari form Periode Payroll klik `Import Absensi`.
- Upload file CSV/XLSX.
- Field minimum yang dipakai sistem:
  - employee_name (atau employee_id/barcode/work_email)
  - days_worked
  - absent_days
  - public_holiday_days
  - holiday_work_days
  - overtime_hours
- Opsional:
  - absence_deduction_rate
  - holiday_work_rate

### 7.3 Rule Bisnis yang Diuji
- Alfa: dipotong otomatis (`absent_days x absence_deduction_rate`).
- Cuti bersama/tanggal merah: tidak dipotong otomatis.
- Masuk saat hari libur: dapat insentif (`holiday_work_days x holiday_work_rate`).
- Overtime tetap dihitung sesuai jam lembur.

### 7.4 Validasi Slip
- Klik menu: `Outsource > Payroll > Slip Gaji`.
Periksa 3 contoh kondisi:
- Karyawan A: hadir penuh, overtime 10 jam.
- Karyawan B: alfa 2 hari.
- Karyawan C: masuk 1 hari saat tanggal merah + overtime.

Pastikan nilai:
- Gross Salary benar
- Attendance Deduction benar
- Holiday Work Amount benar
- Net Salary benar

## 8. Approval & Payment (Tanggal 28-30)
### 8.1 Workflow Approval
- Klik menu: `Outsource > Payroll > Slip Gaji`.
- Slip: Draft -> Submitted -> HR Verified -> Finance Approved -> Posted -> Done

### 8.2 Ekspor Payroll ke Bank
- Klik menu: `Outsource > Payroll > Export Payroll`.
- Jalankan wizard `Export Payroll`.
- Coba format:
  - CSV generic
  - salah satu format bank (Mandiri/BCA/BRI)
- Cocokkan total file export vs total net salary pada periode.

## 9. Pajak & Compliance (Akhir Bulan)
### 9.1 e-Faktur Export
- Klik menu: `Outsource > Pajak & laporan > Export e-Faktur`.
- Jalankan wizard export e-Faktur untuk invoice periode April.
- Verifikasi format file dan nilai DPP/PPN.

### 9.2 BPJS Report
- Klik menu: `Outsource > Pajak & laporan > Laporan BPJS bulanan`.
- Jalankan wizard BPJS bulanan.
- Verifikasi jumlah peserta dan total iuran.

### 9.3 PPh21/PPh23 Check
- Klik menu: `Outsource > Payroll > Slip Gaji` (PPh21) dan `Accounting > Customers > Invoices` (PPh23).
- Cek total PPh21 dari payslip periode.
- Cek posting PPh23 dari invoice terkait.

## 10. Financial Reporting & Profitability
### 10.1 Generate Financial Report
- Klik menu: `Outsource > Financial & Operations > Financial Report > Generate`.
- Periode: 01 Apr 2026 - 30 Apr 2026
- Output yang dicek:
  - Revenue
  - COGS
  - Operational Expense
  - Net Profit

### 10.2 Generate Client Profitability
- Klik menu: `Outsource > Financial & Operations > Client Profitability > Generate`.
- Jalankan per klien.
- Bandingkan margin PT Maju Retail vs PT Cipta Logistik.
- Tentukan 1 keputusan bisnis:
  - Pertahankan pricing
  - Negosiasi ulang
  - Optimasi biaya

## 11. Audit Trail & Closing
### 11.1 Audit Sampling
- Klik menu: 
  - `Outsource > Payroll > Slip Gaji`
  - `Outsource > Financial & Operations > Operational Expense`
  - `Purchases > Orders > Purchase Orders`
  - `Accounting > Customers > Invoices`
Ambil sampel 5 transaksi:
- 2 payslip
- 1 operational expense
- 1 purchase
- 1 invoice

Pastikan tiap transaksi punya:
- Approval trail
- Nilai yang konsisten antar dokumen
- Bukti/attachment jika wajib

### 11.2 Monthly Closing Checklist
- Semua slip payroll status `Done`
- Semua expense bulan April diposting
- Semua invoice bulan April sudah tervalidasi
- Laporan finansial final sudah di-generate
- Export pajak/BPJS sudah dilakukan

## 12. KPI Acceptance (Lulus UAT)
Skenario dianggap lulus jika:
- Tidak ada error saat workflow utama berjalan.
- Seluruh approval flow berhasil tanpa manual SQL fix.
- Selisih total payroll export vs total net salary = 0.
- Laporan profitabilitas menampilkan data untuk 2 klien.
- Dokumen audit sample lengkap.

## 13. Timeline Implementasi Nyata (Rekomendasi)
- Minggu 1: Master data + training user
- Minggu 2: Pilot payroll 1 project
- Minggu 3: Full payroll seluruh project
- Minggu 4: Hardening + SOP final + handover

## 14. SOP Operasional Bulanan (Ringkas)
Referensi menu utama:
- Payroll: `Outsource > Payroll`
- Pajak/BPJS: `Outsource > Pajak & laporan`
- Expense/Report: `Outsource > Financial & Operations`

1. Buka periode payroll
2. Auto-generate payslip
3. Import absensi eksternal
4. Review exception (alfa/lembur/libur)
5. Approval berjenjang
6. Export bank dan posting
7. Export pajak/BPJS
8. Generate laporan finansial dan profitability
9. Audit sample dan closing
