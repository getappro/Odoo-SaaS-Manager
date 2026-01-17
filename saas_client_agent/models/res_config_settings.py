# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # SaaS Usage Fields (read-only, for display)
    saas_current_users = fields.Integer(
        string='Current Active Users',
        readonly=True,
    )
    saas_user_limit = fields.Integer(
        string='User Limit',
        readonly=True,
    )
    saas_users_percentage = fields.Float(
        string='Usage Percentage',
        readonly=True,
    )
    saas_instance_uuid = fields.Char(
        string='Instance ID',
        readonly=True,
    )

    @api.model
    def default_get(self, fields_list):
        """
        Populate SaaS usage data when opening settings form.
        Called automatically by Odoo when creating the transient record.
        """
        res = super().default_get(fields_list)

        # ✅ CORRIGÉ : Pas d'espace dans le nom du modèle
        try:
            config = self.env['saas.client.config'].sudo().get_config()

            res.update({
                'saas_current_users': config.current_users,
                'saas_user_limit': config.user_limit,
                'saas_users_percentage': config.users_percentage,
                'saas_instance_uuid': config.instance_uuid,
            })
        except Exception as e:
            # Fallback si pas de config
            import logging
            _logger = logging.getLogger(__name__)
            _logger.warning(f"Could not load SaaS config: {e}")

            res.update({
                'saas_current_users': 0,
                'saas_user_limit': 0,
                'saas_users_percentage': 0.0,
                'saas_instance_uuid': 'Not configured',
            })

        return res

    def action_request_upgrade(self):
        """Open upgrade request wizard or redirect to contact form"""
        self.ensure_one()

        # ✅ CORRIGÉ : Pas d'espace
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
                    'or email support@yourcompany.com with your Instance ID:  %s'
                ) % config.instance_uuid,
                'type': 'info',
                'sticky': True,
            }
        }