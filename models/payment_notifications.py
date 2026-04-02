# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class PaymentNotificationTemplate(models.Model):
    """Email notification templates for payment events"""
    _name = 'payment.notification.template'
    _description = 'Payment Notification Template'
    _inherit = 'mail.thread'

    name = fields.Char('Template Name', required=True)
    notification_type = fields.Selection([
        ('payment_ready', 'Payment Ready to Upload'),
        ('payment_overdue', 'Payment Overdue'),
        ('payment_reconciled', 'Payment Reconciled'),
        ('3way_match_failed', '3-Way Match Failed'),
        ('payment_proof_received', 'Payment Proof Received'),
    ], string='Notification Type', required=True)

    # Template content
    subject = fields.Char('Subject', required=True)
    body_html = fields.Html('Body', required=True)
    
    # Trigger rules
    auto_send = fields.Boolean('Auto Send', default=True)
    send_to_roles = fields.Many2many('res.groups', string='Send To Groups',
        help='Groups that will receive this notification')
    
    # For overdue reminder
    overdue_days = fields.Integer('Days After Due', default=0,
        help='Send notification X days after due date')


class PaymentNotificationLog(models.Model):
    """Log of all payment notifications sent"""
    _name = 'payment.notification.log'
    _description = 'Payment Notification Log'
    _inherit = 'mail.thread'

    notification_type = fields.Selection([
        ('payment_ready', 'Payment Ready to Upload'),
        ('payment_overdue', 'Payment Overdue'),
        ('payment_reconciled', 'Payment Reconciled'),
        ('3way_match_failed', '3-Way Match Failed'),
        ('payment_proof_received', 'Payment Proof Received'),
    ], string='Notification Type', required=True)
    
    subject = fields.Char('Subject', required=True)
    body = fields.Html('Body')
    
    # Who sent
    sent_by = fields.Many2one('res.users', string='Sent By', readonly=True)
    sent_date = fields.Datetime('Sent Date', readonly=True, default=lambda self: fields.Datetime.now())
    
    # Who received
    recipient_ids = fields.Many2many('res.partner', string='Recipients')
    
    # Related document
    payment_run_id = fields.Many2one('hr.payroll.payment.run', string='Salary Payment Run')
    vendor_invoice_id = fields.Many2one('account.invoice.incoming', string='Vendor Invoice')
    payment_run_vendor_id = fields.Many2one('account.payment.run', string='Vendor Payment Run')
    
    # Status
    state = fields.Selection([
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ], string='Status', default='draft')
    
    error_message = fields.Text('Error Message')
    
    @api.model
    def create(self, vals):
        vals['sent_by'] = self.env.user.id
        vals['sent_date'] = fields.Datetime.now()
        return super().create(vals)


class PaymentReadyNotification(models.AbstractModel):
    """Mixin for payment ready notifications"""
    _name = 'payment.ready.notification'
    
    # Notification settings
    notify_when_ready = fields.Boolean('Notify on Ready', default=True)
    notification_recipients = fields.Many2many('res.partner', 
        string='Notification Recipients', 
        help='Partners to notify when payment is ready')
    
    def _notify_payment_ready(self):
        """Send notification that payment is ready to upload to bank"""
        template = self.env['payment.notification.template'].search([
            ('notification_type', '=', 'payment_ready')
        ], limit=1)
        
        if not template or not self.notify_when_ready:
            return False
        
        recipients = self.notification_recipients or self._get_default_recipients()
        
        log_vals = {
            'notification_type': 'payment_ready',
            'subject': template.subject,
            'body': template.body_html,
            'state': 'sent',
        }
        
        # Add payment reference based on model
        if self._name == 'hr.payroll.payment.run':
            log_vals['payment_run_id'] = self.id
        elif self._name == 'account.payment.run':
            log_vals['payment_run_vendor_id'] = self.id
        
        log = self.env['payment.notification.log'].create(log_vals)
        
        # Send email
        try:
            for recipient in recipients:
                email = recipient.email if hasattr(recipient, 'email') else recipient.email_normalized
                if email:
                    self.env['mail.mail'].create({
                        'subject': template.subject,
                        'body_html': template.body_html,
                        'email_to': email,
                        'email_from': self.env.user.partner_id.email,
                        'message_type': 'notification',
                    }).send()
            log.state = 'sent'
        except Exception as e:
            log.state = 'failed'
            log.error_message = str(e)
            _logger.error(f"Failed to send payment ready notification: {e}")
        
        return log
    
    def _get_default_recipients(self):
        """Get default recipients (accounting team)"""
        accounting_group = self.env.ref('account.group_account_manager')
        return accounting_group.users.mapped('partner_id')


class PaymentOverdueNotification(models.AbstractModel):
    """Mixin for overdue payment notifications"""
    _name = 'payment.overdue.notification'
    
    def _notify_payment_overdue(self):
        """Send notification for overdue payments"""
        template = self.env['payment.notification.template'].search([
            ('notification_type', '=', 'payment_overdue')
        ], limit=1)
        
        if not template:
            return False
        
        recipients = self._get_default_recipients()
        
        log_vals = {
            'notification_type': 'payment_overdue',
            'subject': template.subject,
            'body': template.body_html,
            'state': 'sent',
        }
        
        if self._name == 'account.invoice.incoming':
            log_vals['vendor_invoice_id'] = self.id
        
        log = self.env['payment.notification.log'].create(log_vals)
        
        try:
            for recipient in recipients:
                email = recipient.email if hasattr(recipient, 'email') else recipient.email_normalized
                if email:
                    self.env['mail.mail'].create({
                        'subject': f"⚠️ {template.subject}",
                        'body_html': template.body_html,
                        'email_to': email,
                        'email_from': self.env.user.partner_id.email,
                        'message_type': 'notification',
                    }).send()
            log.state = 'sent'
        except Exception as e:
            log.state = 'failed'
            log.error_message = str(e)
            _logger.error(f"Failed to send payment overdue notification: {e}")
        
        return log
    
    def _get_default_recipients(self):
        """Get default recipients"""
        accounting_group = self.env.ref('account.group_account_manager')
        return accounting_group.users.mapped('partner_id')


class PaymentReconciledNotification(models.AbstractModel):
    """Mixin for payment reconciled notifications"""
    _name = 'payment.reconciled.notification'
    
    def _notify_payment_reconciled(self, reconciliation_notes=''):
        """Send confirmation that payment is reconciled"""
        template = self.env['payment.notification.template'].search([
            ('notification_type', '=', 'payment_reconciled')
        ], limit=1)
        
        if not template:
            return False
        
        # Build message with reconciliation details
        body = template.body_html
        if isinstance(self, self.env['hr.payroll.payment.run']):
            body = body.replace('{{amount}}', str(self.total_amount))
            body = body.replace('{{ref}}', self.name)
        elif isinstance(self, self.env['account.payment.run']):
            body = body.replace('{{amount}}', str(self.total_amount))
            body = body.replace('{{ref}}', self.name)
        
        recipients = self._get_default_recipients()
        
        log_vals = {
            'notification_type': 'payment_reconciled',
            'subject': template.subject,
            'body': body,
            'state': 'sent',
        }
        
        log = self.env['payment.notification.log'].create(log_vals)
        
        try:
            for recipient in recipients:
                email = recipient.email if hasattr(recipient, 'email') else recipient.email_normalized
                if email:
                    self.env['mail.mail'].create({
                        'subject': f"✅ {template.subject}",
                        'body_html': body,
                        'email_to': email,
                        'email_from': self.env.user.partner_id.email,
                        'message_type': 'notification',
                    }).send()
            log.state = 'sent'
        except Exception as e:
            log.state = 'failed'
            log.error_message = str(e)
            _logger.error(f"Failed to send payment reconciled notification: {e}")
        
        return log
    
    def _get_default_recipients(self):
        """Get default recipients"""
        accounting_group = self.env.ref('account.group_account_manager')
        return accounting_group.users.mapped('partner_id')


class Payment3WayMatchNotification(models.AbstractModel):
    """Mixin for 3-way match failure notifications"""
    _name = 'payment.3way.match.notification'
    
    def _notify_3way_match_failed(self, match_notes=''):
        """Send alert when 3-way match fails"""
        template = self.env['payment.notification.template'].search([
            ('notification_type', '=', '3way_match_failed')
        ], limit=1)
        
        if not template:
            return False
        
        # Build message with variance details
        body = template.body_html
        if hasattr(self, 'match_notes') and self.match_notes:
            body = body.replace('{{variance_details}}', self.match_notes)
        
        recipients = self._get_default_recipients()
        
        log_vals = {
            'notification_type': '3way_match_failed',
            'subject': template.subject,
            'body': body,
            'state': 'sent',
        }
        
        if self._name == 'account.invoice.incoming':
            log_vals['vendor_invoice_id'] = self.id
        
        log = self.env['payment.notification.log'].create(log_vals)
        
        try:
            for recipient in recipients:
                email = recipient.email if hasattr(recipient, 'email') else recipient.email_normalized
                if email:
                    self.env['mail.mail'].create({
                        'subject': f"⚠️ {template.subject}",
                        'body_html': body,
                        'email_to': email,
                        'email_from': self.env.user.partner_id.email,
                        'message_type': 'notification',
                    }).send()
            log.state = 'sent'
        except Exception as e:
            log.state = 'failed'
            log.error_message = str(e)
            _logger.error(f"Failed to send 3-way match notification: {e}")
        
        return log
    
    def _get_default_recipients(self):
        """Get default recipients"""
        accounting_group = self.env.ref('account.group_account_manager')
        return accounting_group.users.mapped('partner_id')
