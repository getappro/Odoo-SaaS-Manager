# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
SaaS Client Configuration Model
================================
Local configuration for SaaS client instance.
Stores limits and settings received from master.
"""

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SaasClientConfig(models.Model):
    """
    Local configuration for SaaS client instance.
    Stores limits and settings received from master.
    """
    _name = 'saas.client.config'
    _description = 'SaaS Client Configuration'
    _rec_name = 'instance_uuid'

    instance_uuid = fields.Char(
        string='Instance UUID',
        required=True,
        default=lambda self: self._generate_uuid(),
        readonly=True,
        help="Unique identifier for this instance"
    )
    
    master_url = fields.Char(
        string='Master Server URL',
        help="URL of the master SaaS manager (e.g., http://master.example.com:8069)"
    )
    
    master_database = fields.Char(
        string='Master Database Name',
        help="Database name of the master"
    )
    
    # User Limits
    user_limit = fields.Integer(
        string='User Limit',
        default=5,
        help="Maximum number of active users allowed"
    )
    
    current_users = fields.Integer(
        string='Current Active Users',
        compute='_compute_current_users',
        help="Number of currently active users"
    )
    
    users_percentage = fields.Float(
        string='Usage Percentage',
        compute='_compute_users_percentage',
        help="Percentage of user limit used"
    )
    
    # Status
    is_limit_enforced = fields.Boolean(
        string='Enforce User Limit',
        default=True,
        help="Block user creation when limit is reached"
    )
    
    last_sync_date = fields.Datetime(
        string='Last Sync with Master',
        readonly=True,
        help="Last successful sync with master server"
    )
    
    sync_status = fields.Selection([
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('never', 'Never Synced'),
    ], string='Sync Status', default='never', readonly=True)
    
    sync_message = fields.Text(
        string='Last Sync Message',
        readonly=True
    )
    
    # Metadata
    active = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('instance_uuid_unique', 'UNIQUE(instance_uuid)', 
         'Instance UUID must be unique!'),
    ]
    
    @api.model
    def _generate_uuid(self):
        """Generate unique instance identifier"""
        import uuid
        return str(uuid.uuid4())
    
    @api.depends('user_limit')
    def _compute_current_users(self):
        """Count active users (excluding admin and internal users)"""
        for record in self:
            active_users = self.env['res.users'].search_count([
                ('active', '=', True),
                ('share', '=', False),  # Exclude portal users
                ('id', '!=', 1),  # Exclude OdooBot
            ])
            record.current_users = active_users
    
    @api.depends('current_users', 'user_limit')
    def _compute_users_percentage(self):
        """Calculate usage percentage"""
        for record in self:
            if record.user_limit > 0:
                record.users_percentage = (record.current_users / record.user_limit) * 100
            else:
                record.users_percentage = 0.0
    
    @api.model
    def get_config(self):
        """Get or create singleton config record"""
        config = self.search([], limit=1)
        if not config:
            config = self.create({
                'master_url': self.env['ir.config_parameter'].sudo().get_param(
                    'saas_client.master_url', ''
                ),
                'master_database': self.env['ir.config_parameter'].sudo().get_param(
                    'saas_client.master_database', ''
                ),
            })
        return config
    
    def check_user_limit(self):
        """
        Check if user limit allows creation of new user.
        Returns: (allowed: bool, message: str)
        """
        self.ensure_one()
        
        if not self.is_limit_enforced:
            return True, ""
        
        if self.current_users >= self.user_limit:
            return False, _(
                "User limit reached (%d/%d). Please contact your administrator to upgrade your plan."
            ) % (self.current_users, self.user_limit)
        
        return True, ""
    
    def action_sync_with_master(self):
        """Manually trigger sync with master"""
        self.ensure_one()
        return self._sync_with_master()
    
    def _sync_with_master(self):
        """
        Sync configuration with master server.
        Master will update user_limit and other settings.
        
        TODO: Implement proper authentication mechanism
        - Use API key authentication
        - Store secure credentials in ir.config_parameter
        - Implement token-based authentication
        """
        self.ensure_one()
        
        if not self.master_url or not self.master_database:
            self.write({
                'sync_status': 'error',
                'sync_message': 'Master URL or database not configured',
            })
            return False
        
        try:
            import requests
            import json
            
            # TODO: Replace with proper API authentication
            # Current implementation uses hard-coded credentials for POC
            # Production should use secure token-based auth
            
            # Call master RPC endpoint
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'object',
                    'method': 'execute_kw',
                    'args': [
                        self.master_database,
                        1,  # TODO: Replace with proper user ID
                        'admin',  # TODO: Replace with secure API token
                        'saas.instance',
                        'sync_client_config',
                        [self.instance_uuid],
                    ]
                },
                'id': 1
            }
            
            response = requests.post(
                f"{self.master_url}/jsonrpc",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json().get('result', {})
                
                # Update local config with master's values
                if result:
                    self.write({
                        'user_limit': result.get('user_limit', self.user_limit),
                        'last_sync_date': fields.Datetime.now(),
                        'sync_status': 'success',
                        'sync_message': 'Successfully synced with master',
                    })
                    _logger.info(f"Client config synced with master. User limit: {self.user_limit}")
                    return True
            
            self.write({
                'sync_status': 'error',
                'sync_message': f'HTTP {response.status_code}: {response.text[:200]}',
            })
            return False
            
        except Exception as e:
            _logger.error(f"Failed to sync with master: {str(e)}")
            self.write({
                'sync_status': 'error',
                'sync_message': str(e),
                'last_sync_date': fields.Datetime.now(),
            })
            return False
    
    @api.model
    def cron_sync_with_master(self):
        """CRON: Periodic sync with master"""
        _logger.info("Running client config sync with master...")
        config = self.get_config()
        config._sync_with_master()
