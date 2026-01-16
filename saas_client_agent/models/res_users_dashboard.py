# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model
    def get_saas_usage_info(self):
        """
        Get SaaS usage information for dashboard widget.
        Visible to all users - provides transparency without complexity.
        
        Returns:
            dict: Usage metrics and plan information
        """
        config = self.env['saas.client.config'].sudo().get_config()
        
        # Determine warning level based on usage
        warning_level = 'success'
        if config.users_percentage >= 95:
            warning_level = 'danger'
        elif config.users_percentage >= 80:
            warning_level = 'warning'
        
        return {
            'current_users': config.current_users,
            'user_limit': config.user_limit,
            'users_percentage': round(config.users_percentage, 1),
            'warning_level': warning_level,
            'show_warning': config.users_percentage >= 80,
            'can_create_users': config.current_users < config.user_limit,
            'users_remaining': max(0, config.user_limit - config.current_users),
        }
