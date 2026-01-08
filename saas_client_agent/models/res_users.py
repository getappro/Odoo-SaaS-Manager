# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
Extend res.users to enforce user creation limits
"""

from odoo import api, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    """
    Extend res.users to enforce user creation limits
    """
    _inherit = 'res.users'
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to check user limit before creating new users
        """
        # Get client config
        config = self.env['saas.client.config'].sudo().get_config()
        
        # Count new internal users being created
        new_internal_users = sum(
            1 for vals in vals_list 
            if not vals.get('share', False)  # Internal user
        )
        
        if new_internal_users > 0 and config.is_limit_enforced:
            # Check if limit allows creation
            allowed, message = config.check_user_limit()
            
            if not allowed:
                _logger.warning(
                    f"User creation blocked: limit reached ({config.current_users}/{config.user_limit})"
                )
                raise ValidationError(message)
            
            # Warn if approaching limit (80%)
            if config.users_percentage >= 80:
                _logger.warning(
                    f"Approaching user limit: {config.current_users}/{config.user_limit} "
                    f"({config.users_percentage:.1f}%)"
                )
        
        return super().create(vals_list)
