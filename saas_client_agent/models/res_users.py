# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to check user limit with professional, helpful messages
        """
        config = self.env['saas.client.config'].sudo().get_config()
        
        # Count new internal users being created
        new_internal_users = sum(
            1 for vals in vals_list 
            if not vals.get('share', False)  # Internal user
        )
        
        if new_internal_users > 0 and config.is_limit_enforced:
            allowed, message = config.check_user_limit()
            
            if not allowed:
                # ✅ Professional, actionable error message
                raise ValidationError(_(
                    "User Limit Reached\n\n"
                    "Your subscription plan allows %d active users, and you currently have %d.\n\n"
                    "To add more users, you can:\n"
                    "• Upgrade to a higher plan (Settings → Subscription → Request Upgrade)\n"
                    "• Deactivate unused user accounts\n"
                    "• Contact your account manager\n\n"
                    "Need immediate assistance? Email: support@yourcompany.com\n"
                    "Instance ID: %s"
                ) % (config.user_limit, config.current_users, config.instance_uuid))
            
            # ✅ Warning when approaching limit (>= 90%)
            if config.users_percentage >= 90:
                _logger.warning(
                    f"User limit critical: {config.current_users}/{config.user_limit} "
                    f"({config.users_percentage:.1f}%) - Instance: {config.instance_uuid}"
                )
        
        return super().create(vals_list)
