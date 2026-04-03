{
    'name': 'Outsource Custom',
    'version': '18.0.6.0.0',
    'category': 'Custom',
    'summary': 'Sistem Payroll, Purchasing, Expense, Financial Reporting & Audit Compliance untuk Indonesia',
    'author': 'Perusahaan Anda',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'account',
        'hr',
        'l10n_id',
        'l10n_id_efaktur',
        'l10n_id_efaktur_coretax',
        'sale_management',
        'purchase',
        'project',
        'crm',
        'analytic',
    ],
    'data': [
        # Security & Data
        'security/ir.model.access.csv',
        'data/tax_data.xml',
        'data/analytic_plan_data.xml',
        'data/payslip_sequence.xml',
        'data/hr_sequences.xml',
        'data/salary_component_data.xml',
        'data/cron_jobs.xml',
        'data/expense_sequence.xml',
        'data/audit_sequence.xml',
        'data/payment_sequence.xml',
        'data/payment_notification_templates.xml',
        
        # Views - Traditional
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
        'views/project_views.xml',
        'views/account_move_views.xml',
        'views/purchase_views.xml',
        'views/res_config_settings_views.xml',
        'views/crm_lead_views.xml',
        
        # Views - Payroll & HR
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/hr_salary_views.xml',
        'views/hr_loan_views.xml',
        
        # Views - Financial & Operations
        'views/financial_views.xml',
        
        # Views - Audit & Compliance
        'views/audit_views.xml',
        
        # Views - Payments & Documents
        'views/payment_document_views.xml',
        'views/payment_dashboard_reports_views.xml',
        
        # Reports
        'report/payslip_report.xml',
        'report/invoice_report.xml',
        'report/project_summary_report.xml',
        
        # Wizards
        'wizard/efaktur_export_wizard_views.xml',
        'wizard/bpjs_report_wizard_views.xml',
        'wizard/payslip_bank_export_wizard_views.xml',
        'wizard/attendance_import_wizard_views.xml',
        'wizard/generate_financial_report_wizard_views.xml',
        'wizard/generate_client_profitability_wizard_views.xml',

        # Menu (load last so referenced actions already exist)
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
