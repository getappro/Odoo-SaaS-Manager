# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # SaaS Usage Fields (read-only, for display)
    saas_current_users = fields.Integer(
        string='Current Active Users',
        compute='_compute_saas_usage',
        readonly=True,
    )
    saas_user_limit = fields.Integer(
        string='User Limit',
        compute='_compute_saas_usage',
        readonly=True,
    )
    saas_users_percentage = fields.Float(
        string='Usage Percentage',
        compute='_compute_saas_usage',
        readonly=True,
    )
    saas_instance_uuid = fields.Char(
        string='Instance ID',
        compute='_compute_saas_usage',
        readonly=True,
    )
    
    @api.depends('id')
    def _compute_saas_usage(self):
        """Compute SaaS usage metrics for display in settings"""
        config = self.env['saas.client.config'].sudo().get_config()
        
        for record in self:
            record.saas_current_users = config.current_users
            record.saas_user_limit = config.user_limit
            record.saas_users_percentage = config.users_percentage
            record.saas_instance_uuid = config.instance_uuid
    
    def action_request_upgrade(self):
        """Open upgrade request wizard or redirect to contact form"""
        self.ensure_one()
        
        config = self.env['saas.client.config'].sudo().get_config()
        
        # TODO: Send upgrade request to master via RPC
        # For now, show a helpful message
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Upgrade Request'),
                'message': _(
                    'To upgrade your subscription plan, please contact your account manager '
                    'or email support@yourcompany.com with your Instance ID: %s'
                ) % config.instance_uuid,
                'type': 'info',
                'sticky': True,
            }
        }
