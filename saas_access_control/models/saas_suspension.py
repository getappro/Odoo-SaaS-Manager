# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaasSuspension(models.Model):
    """
    Manages suspension of SaaS instances.
    When suspended, instances cannot be accessed except by admins.
    """
    _name = 'saas.suspension'
    _description = 'SaaS Instance Suspension'
    _order = 'create_date desc'

    instance_id = fields.Many2one(
        'saas.instance',
        string='Instance',
        required=True,
        ondelete='cascade',
        index=True,
    )

    reason = fields.Selection([
        ('expired', 'Subscription Expired'),
        ('payment', 'Payment Failed'),
        ('abuse', 'Terms of Service Violation'),
        ('request', 'User Request'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ], string='Suspension Reason', required=True)

    description = fields.Text(string='Description')

    suspended_date = fields.Datetime(
        string='Suspension Date',
        default=fields.Datetime.now,
        readonly=True,
    )

    resumed_date = fields.Datetime(
        string='Resume Date',
        readonly=True,
    )

    state = fields.Selection([
        ('active', 'Active'),
        ('resolved', 'Resolved'),
    ], string='State', default='active', readonly=True)

    is_active = fields.Boolean(
        string='Is Currently Suspended',
        compute='_compute_is_active',
        store=True,
    )

    notes = fields.Text(string='Internal Notes')

    created_by_id = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True,
    )

    resumed_by_id = fields.Many2one(
        'res.users',
        string='Resumed By',
        readonly=True,
    )

    @api.depends('state')
    def _compute_is_active(self):
        """Compute if suspension is currently active"""
        for record in self:
            record.is_active = record.state == 'active'

    def action_resume(self):
        """Resume a suspended instance"""
        for record in self:
            if record.state == 'resolved':
                raise ValueError("Suspension already resolved")

            record.write({
                'state': 'resolved',
                'resumed_date': fields.Datetime.now(),
                'resumed_by_id': self.env.user.id,
            })

            # Update instance state
            if record.instance_id.state == 'suspended':
                record.instance_id.state = 'active'

            # Sync with remote instance if needed
            self._sync_suspension_state_to_instance(
                record.instance_id,
                is_suspended=False
            )

            _logger.info(f"Instance {record.instance_id.name} resumed")

    def _sync_suspension_state_to_instance(self, instance, is_suspended=True):
        """
        Sync suspension state to remote instance via RPC.
        This allows the instance to block access if needed.
        """
        try:
            rpc_client = instance.get_rpc_client()

            # Call method on remote instance to update suspension state
            rpc_client.call({
                'service': 'object',
                'method': 'execute_kw',
                'args': [
                    instance.server_id.db_name,
                    self.env.user.id,
                    'saas.access.local',
                    'set_suspension_state',
                    [instance.db_name],
                    {'is_suspended': is_suspended},
                ]
            })

            _logger.info(
                f"Synced suspension state to {instance.name}: "
                f"is_suspended={is_suspended}"
            )
        except Exception as e:
            _logger.warning(
                f"Failed to sync suspension state to {instance.name}: {e}"
            )

    def create(self, vals):
        """Create suspension and update instance state"""
        record = super().create(vals)

        if record.instance_id:
            # Update instance state to suspended
            if record.instance_id.state != 'suspended':
                record.instance_id.state = 'suspended'

            # Sync suspension to instance
            self._sync_suspension_state_to_instance(
                record.instance_id,
                is_suspended=True
            )

        return record

