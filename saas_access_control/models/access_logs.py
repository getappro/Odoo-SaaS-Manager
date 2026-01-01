# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class AccessLog(models.Model):
    """
    Audit log for all access to SaaS instances.
    Tracks support sessions, suspensions, and access attempts.
    """
    _name = 'access.log'
    _description = 'Access Log'
    _order = 'timestamp desc'

    session_id = fields.Many2one(
        'support.session',
        string='Support Session',
        ondelete='set null',
        index=True,
    )

    instance_id = fields.Many2one(
        'saas.instance',
        string='Instance',
        required=True,
        ondelete='cascade',
        index=True,
    )

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        index=True,
    )

    action = fields.Selection([
        ('access', 'Access'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('write', 'Write'),
        ('unlink', 'Delete'),
        ('suspension', 'Suspension'),
        ('resume', 'Resume'),
        ('token_revoke', 'Token Revoked'),
        ('failed_access', 'Failed Access'),
        ('other', 'Other'),
    ], string='Action', required=True, index=True)

    timestamp = fields.Datetime(
        string='Timestamp',
        default=fields.Datetime.now,
        readonly=True,
        index=True,
    )

    ip_address = fields.Char(
        string='IP Address',
    )

    user_agent = fields.Text(
        string='User Agent',
    )

    description = fields.Text(
        string='Description',
    )

    status = fields.Selection([
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('denied', 'Access Denied'),
    ], string='Status', default='success')

    error_message = fields.Text(
        string='Error Message',
    )

    model_name = fields.Char(
        string='Model',
    )

    record_id = fields.Integer(
        string='Record ID',
    )

    duration_ms = fields.Float(
        string='Duration (ms)',
    )

    details = fields.Json(
        string='Additional Details',
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Log creation with automatic timestamp"""
        for vals in vals_list:
            if 'timestamp' not in vals:
                vals['timestamp'] = fields.Datetime.now()

        records = super().create(vals_list)

        # Log suspension actions
        for record in records:
            if record.action in ['suspension', 'resume']:
                _logger.info(
                    f"Access Log: {record.action} on {record.instance_id.name} "
                    f"by {record.user_id.name}"
                )

        return records

    def get_instance_logs(self, instance_id, limit=100):
        """Get access logs for a specific instance"""
        return self.search([
            ('instance_id', '=', instance_id),
        ], limit=limit, order='timestamp desc')

    def get_user_logs(self, user_id, limit=100):
        """Get access logs for a specific user"""
        return self.search([
            ('user_id', '=', user_id),
        ], limit=limit, order='timestamp desc')

    def get_session_logs(self, session_id):
        """Get all logs for a specific support session"""
        return self.search([
            ('session_id', '=', session_id),
        ], order='timestamp desc')

    def get_failed_access_logs(self, instance_id=None):
        """Get failed access attempts"""
        domain = [('status', '!=', 'success')]
        if instance_id:
            domain.append(('instance_id', '=', instance_id))

        return self.search(domain, order='timestamp desc', limit=100)

    def cleanup_old_logs(self, days=90):
        """Remove logs older than specified days"""
        from datetime import timedelta
        cutoff_date = datetime.now() - timedelta(days=days)

        old_logs = self.search([
            ('timestamp', '<', cutoff_date),
        ])

        count = len(old_logs)
        old_logs.unlink()

        _logger.info(f"Cleaned up {count} old access logs")
        return count

