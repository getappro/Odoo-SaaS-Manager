# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaaSClientConfig(models.Model):
    """
    SaaS Client Configuration
    Stores instance configuration and usage limits
    """
    _name = 'saas.client.config'
    _description = 'SaaS Client Configuration'
    _rec_name = 'instance_uuid'
    
    # Instance Identity
    instance_uuid = fields.Char(
        string='Instance UUID',
        required=True,
        default=lambda self: self._generate_uuid(),
        help='Unique identifier for this instance',
    )
    
    # Master Server Connection
    master_url = fields.Char(
        string='Master Server URL',
        help='URL of the master SaaS server',
    )
    master_api_key = fields.Char(
        string='API Key',
        help='API key for authentication with master server',
    )
    
    # Subscription Limits
    user_limit = fields.Integer(
        string='User Limit',
        default=10,
        required=True,
        help='Maximum number of active users allowed',
    )
    storage_limit_gb = fields.Float(
        string='Storage Limit (GB)',
        default=10.0,
        help='Maximum storage allowed in GB',
    )
    
    # Current Usage (computed)
    current_users = fields.Integer(
        string='Current Active Users',
        compute='_compute_current_usage',
        store=False,
    )
    current_storage_gb = fields.Float(
        string='Current Storage (GB)',
        compute='_compute_current_usage',
        store=False,
    )
    
    # Usage Percentages
    users_percentage = fields.Float(
        string='Users Usage %',
        compute='_compute_percentages',
        store=False,
    )
    storage_percentage = fields.Float(
        string='Storage Usage %',
        compute='_compute_percentages',
        store=False,
    )
    
    # Enforcement Settings
    is_limit_enforced = fields.Boolean(
        string='Enforce Limits',
        default=True,
        help='If checked, user creation will be blocked when limit is reached',
    )
    
    # Heartbeat
    last_heartbeat = fields.Datetime(
        string='Last Heartbeat',
        readonly=True,
        help='Last successful sync with master server',
    )
    heartbeat_interval = fields.Integer(
        string='Heartbeat Interval (minutes)',
        default=60,
        help='How often to sync with master server',
    )
    
    @api.model
    def _generate_uuid(self):
        """Generate a unique UUID for the instance"""
        import uuid
        return str(uuid.uuid4())
    
    @api.depends('user_limit')
    def _compute_current_usage(self):
        """Compute current usage metrics"""
        for record in self:
            # Count internal users (non-share users)
            record.current_users = self.env['res.users'].search_count([
                ('share', '=', False),
                ('active', '=', True),
            ])
            
            # TODO: Implement storage calculation
            record.current_storage_gb = 0.0
    
    @api.depends('current_users', 'user_limit', 'current_storage_gb', 'storage_limit_gb')
    def _compute_percentages(self):
        """Compute usage percentages"""
        for record in self:
            # Users percentage
            if record.user_limit > 0:
                record.users_percentage = (record.current_users / record.user_limit) * 100
            else:
                record.users_percentage = 0.0
            
            # Storage percentage
            if record.storage_limit_gb > 0:
                record.storage_percentage = (record.current_storage_gb / record.storage_limit_gb) * 100
            else:
                record.storage_percentage = 0.0
    
    @api.model
    def get_config(self):
        """
        Get or create singleton configuration record
        Returns the configuration record
        """
        config = self.search([], limit=1)
        if not config:
            config = self.create({
                'user_limit': 10,
                'storage_limit_gb': 10.0,
                'is_limit_enforced': True,
            })
        return config
    
    def check_user_limit(self):
        """
        Check if new users can be created
        Returns: (allowed: bool, message: str)
        """
        self.ensure_one()
        
        if not self.is_limit_enforced:
            return True, _("User limit enforcement is disabled")
        
        if self.current_users >= self.user_limit:
            return False, _(
                "User limit reached: %d/%d users. "
                "Please upgrade your subscription to add more users."
            ) % (self.current_users, self.user_limit)
        
        return True, _("Users: %d/%d") % (self.current_users, self.user_limit)
    
    def action_sync_with_master(self):
        """
        Manual sync with master server
        Called from UI button
        """
        self.ensure_one()
        
        if not self.master_url:
            raise ValidationError(_("Master server URL is not configured"))
        
        # TODO: Implement RPC sync with master
        _logger.info(
            f"Manual sync triggered for instance {self.instance_uuid}"
        )
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Sync Initiated'),
                'message': _('Synchronization with master server has been initiated.'),
                'type': 'success',
                'sticky': False,
            }
        }
