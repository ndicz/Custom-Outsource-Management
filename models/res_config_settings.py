from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Coretax Configuration
    coretax_api_url = fields.Char(
        string='Coretax API URL',
        default='https://api.coretax.co.id/v1/efaktur',
        config_parameter='outsource_custom.coretax_api_url',
    )
    coretax_api_key = fields.Char(
        string='Coretax API Key',
        config_parameter='outsource_custom.coretax_api_key',
        invisible=False,
    )
    
    # Accounting Accounts for Payroll
    salary_expense_account_id = fields.Many2one(
        'account.account',
        string='Rekening Beban Gaji',
        config_parameter='outsource_custom.salary_expense_account_id',
        domain=[('deprecated', '=', False)],
    )
    salary_payable_account_id = fields.Many2one(
        'account.account',
        string='Rekening Hutang Gaji',
        config_parameter='outsource_custom.salary_payable_account_id',
        domain=[('deprecated', '=', False)],
    )
    tax_payable_account_id = fields.Many2one(
        'account.account',
        string='Rekening Hutang Pajak',
        config_parameter='outsource_custom.tax_payable_account_id',
        domain=[('deprecated', '=', False)],
    )
    bpjs_payable_account_id = fields.Many2one(
        'account.account',
        string='Rekening Hutang BPJS',
        config_parameter='outsource_custom.bpjs_payable_account_id',
        domain=[('deprecated', '=', False)],
    )

    # Operational Expense Accounts
    expense_rent_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Sewa',
        config_parameter='outsource_custom.expense_rent_account_id'
    )
    expense_utilities_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Utilitas (Listrik, Air)',
        config_parameter='outsource_custom.expense_utilities_account_id'
    )
    expense_transport_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Transportasi',
        config_parameter='outsource_custom.expense_transport_account_id'
    )
    expense_communication_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Komunikasi',
        config_parameter='outsource_custom.expense_communication_account_id'
    )
    expense_maintenance_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Perawatan & Perbaikan',
        config_parameter='outsource_custom.expense_maintenance_account_id'
    )
    expense_equipment_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Peralatan',
        config_parameter='outsource_custom.expense_equipment_account_id'
    )
    expense_supplies_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Perlengkapan/ATK',
        config_parameter='outsource_custom.expense_supplies_account_id'
    )
    expense_meals_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Makan/Minuman',
        config_parameter='outsource_custom.expense_meals_account_id'
    )
    expense_travel_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Perjalanan',
        config_parameter='outsource_custom.expense_travel_account_id'
    )
    expense_professional_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Profesional/Konsultan',
        config_parameter='outsource_custom.expense_professional_account_id'
    )
    expense_insurance_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Asuransi',
        config_parameter='outsource_custom.expense_insurance_account_id'
    )
    expense_other_account_id = fields.Many2one(
        'account.account',
        string='Akun Biaya Lainnya',
        config_parameter='outsource_custom.expense_other_account_id'
    )

    # Bank/Cash Account for Expense Payments
    expense_payment_account_id = fields.Many2one(
        'account.account',
        string='Akun Bank/Kas untuk Pembayaran',
        config_parameter='outsource_custom.expense_payment_account_id'
    )

    # Journal for Expense Entries
    expense_journal_id = fields.Many2one(
        'account.journal',
        string='Jurnal untuk Posting Pengeluaran',
        config_parameter='outsource_custom.expense_journal_id',
        domain="[('type', '=', 'general')]"
    )

    # Financial Report Settings
    corporate_tax_rate = fields.Float(
        string='Tarif Pajak Korporat (%)',
        config_parameter='outsource_custom.corporate_tax_rate',
        default=21.0
    )
    
    overhead_allocation_rate = fields.Float(
        string='Tingkat Alokasi Overhead (% dari COGS)',
        config_parameter='outsource_custom.overhead_allocation_rate',
        default=10.0
    )
