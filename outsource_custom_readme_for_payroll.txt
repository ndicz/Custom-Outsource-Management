Outsource Custom - Payroll (Odoo Community)
===========================================

1. Tujuan
--------
Modul ini menambahkan fitur payroll sederhana untuk karyawan di Odoo Community (tanpa Enterprise), termasuk:
- model slip gaji (outsource.payslip)
- perhitungan otomatis gaji kotor/net
- workflow status (draft, confirmed, done)
- menu dan halaman di Employee
- report PDF "Slip Gaji"

2. File-file baru / diubah
------------------------
- models/hr_payslip.py
- models/hr_employee.py (payslip_ids One2many)
- models/__init__.py (import hr_payslip)
- views/hr_payslip_views.xml
- views/hr_employee_views.xml (tab Outsource)
- views/menu_views.xml (menu Payroll)
- data/payslip_sequence.xml
- security/ir.model.access.csv
- report/payslip_report.xml
- __manifest__.py (depends + data)

3. Dependency
-------------
__manifest__.py includes:
- hr_payroll
- hr
- account
- l10n_id + l10n_id_efaktur + l10n_id_efaktur_coretax

4. Model outsource.payslip
-------------------------
Fields:
- name (sequence)
- employee_id (hr.employee)
- date_from / date_to
- basic_salary, allowance, deduction
- gross_salary = basic_salary + allowance
- net_salary = gross_salary - deduction
- state = draft/confirmed/done

On create:
- auto set name dari ir.sequence code=outsource.payslip

5. View
-------
Form:
- field basic_salary, allowance, deduction
- field gross_salary, net_salary (readonly)
- buttons: Draft / Confirm / Done
- header: Print Slip

Tree:
- name, employee, tanggal, net_salary, state

6. Menu
-------
Outsource > Payroll > Slip Gaji

7. Security
-----------
ir.model.access:
- access_outsource_payslip_user (group_user CRUD)
- access_outsource_payslip_manager (group_system CRUD)

8. Report
---------
report/payslip_report.xml:
- action_report_outsource_payslip
- template print slip gaji

9. Cara pakai (User)
-------------------
1. Restart Odoo
2. Update Apps List
3. Install module Outsource Custom
4. Buka menu: Outsource > Payroll > Slip Gaji
5. Click Create -> masukkan data -> Save
6. Klik Confirm -> Done
7. Klik Print Slip untuk generate PDF
8. Cek di Employee > tab Outsource > Slip Gaji

10. Catatan debugging
---------------------
- Editor/detektor static mungkin laporkan `odoo` tidak ditemukan (environment VS Code). Ini false positive ketika module dijalankan di Odoo server sebenanrnya.
- Jika mengalami error di runtime, lihat log odoo-server.log.

11. Pengembangan lanjut
----------------------
- Tambahkan field: BPJS, PPh 21, tunjangan detail.
- Integrasi dengan timesheet / contract.
- Otomatisasi posting ke `account.move` saat slip `done`.
