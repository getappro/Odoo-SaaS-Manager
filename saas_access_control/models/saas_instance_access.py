# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SaasInstanceAccessControl(models.Model):
    """
    Extend saas.instance with access control features
    """
    _inherit = 'saas.instance'

    is_suspended = fields.Boolean(
        string='Is Suspended',
        compute='_compute_is_suspended',
        store=True,
        index=True,
    )

    suspension_id = fields.Many2one(
        'saas.suspension',
        string='Active Suspension',
        compute='_compute_suspension_id',
        store=False,
    )

    suspension_reason = fields.Char(
        string='Suspension Reason',
        compute='_compute_suspension_reason',
    )

    @api.depends('id')
    def _compute_is_suspended(self):
        """Check if instance has active suspension"""
        for record in self:
            suspension = self.env['saas.suspension'].search([
                ('instance_id', '=', record.id),
                ('state', '=', 'active'),
            ], limit=1)
            record.is_suspended = bool(suspension)

    @api.depends('id')
    def _compute_suspension_id(self):
        """Get active suspension for instance"""
        for record in self:
            suspension = self.env['saas.suspension'].search([
                ('instance_id', '=', record.id),
                ('state', '=', 'active'),
            ], limit=1)
            record.suspension_id = suspension.id if suspension else False

    @api.depends('suspension_id')
    def _compute_suspension_reason(self):
        """Get suspension reason"""
        for record in self:
            if record.suspension_id:
                record.suspension_reason = f"{record.suspension_id.reason}: {record.suspension_id.description}"
            else:
                record.suspension_reason = None

    def action_suspend_instance(self):
        """Create suspension for this instance"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'saas.suspension',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_instance_id': self.id,
            },
        }

    def action_create_support_session(self):
        """Create support session for this instance"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'support.session',
            'view_mode': 'form',
            'views': [(False, 'form')],
            'target': 'new',
            'context': {
                'default_instance_id': self.id,
            },
        }

    def action_view_suspension_history(self):
        """View suspension history for this instance"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'saas.suspension',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('instance_id', '=', self.id)],
            'target': 'current',
            'context': {
                'search_default_instance_id': self.id,
            },
        }

    def action_view_access_logs(self):
        """View access logs for this instance"""
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'access.log',
            'view_mode': 'list,form',
            'views': [(False, 'list'), (False, 'form')],
            'domain': [('instance_id', '=', self.id)],
            'target': 'current',
            'context': {
                'search_default_instance_id': self.id,
            },
        }

