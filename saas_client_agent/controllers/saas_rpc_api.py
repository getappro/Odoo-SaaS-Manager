# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
RPC API endpoints for master server to send commands to client instance
"""

from odoo import http, fields
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class SaasRPCAPI(http.Controller):
    """
    RPC API endpoints for master server to send commands to client instance.
    
    SECURITY WARNING:
    -----------------
    These endpoints use auth='public' to allow master-to-client communication.
    
    In production environments, you should:
    1. Implement API key authentication
    2. Add IP whitelist for master server
    3. Use HTTPS/TLS for all communications
    4. Implement rate limiting
    5. Add request signature verification
    
    Current implementation is suitable for POC/testing only.
    """
    
    @http.route('/saas/set_user_limit', type='json', auth='public', methods=['POST'], csrf=False)
    def set_user_limit(self, instance_uuid, user_limit, **kwargs):
        """
        Set user limit for this instance (called by master).
        
        SECURITY: This endpoint is publicly accessible for POC.
        In production, implement proper authentication.
        
        Args:
            instance_uuid: Unique identifier of instance
            user_limit: New user limit value
        
        Returns:
            dict: Success status and current user count
        """
        try:
            config = request.env['saas.client.config'].sudo().search([
                ('instance_uuid', '=', instance_uuid)
            ], limit=1)
            
            if not config:
                return {
                    'success': False,
                    'error': 'Instance UUID not found'
                }
            
            config.write({
                'user_limit': user_limit,
                'last_sync_date': fields.Datetime.now(),
                'sync_status': 'success',
            })
            
            _logger.info(f"User limit updated to {user_limit} by master")
            
            return {
                'success': True,
                'user_limit': user_limit,
                'current_users': config.current_users,
                'users_percentage': config.users_percentage,
            }
            
        except Exception as e:
            _logger.error(f"Error setting user limit: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/saas/get_users_count', type='json', auth='public', methods=['POST'], csrf=False)
    def get_users_count(self, instance_uuid, **kwargs):
        """
        Get current user count (called by master).
        
        SECURITY: This endpoint is publicly accessible for POC.
        In production, implement proper authentication.
        
        Args:
            instance_uuid: Unique identifier of instance
        
        Returns:
            dict: Current user count and limit info
        """
        try:
            config = request.env['saas.client.config'].sudo().search([
                ('instance_uuid', '=', instance_uuid)
            ], limit=1)
            
            if not config:
                return {
                    'success': False,
                    'error': 'Instance UUID not found'
                }
            
            return {
                'success': True,
                'current_users': config.current_users,
                'user_limit': config.user_limit,
                'users_percentage': config.users_percentage,
                'is_limit_enforced': config.is_limit_enforced,
            }
            
        except Exception as e:
            _logger.error(f"Error getting user count: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @http.route('/saas/get_status', type='json', auth='public', methods=['POST'], csrf=False)
    def get_status(self, instance_uuid, **kwargs):
        """
        Get instance status and health info (called by master).
        
        SECURITY: This endpoint is publicly accessible for POC.
        In production, implement proper authentication to prevent
        information disclosure.
        
        Args:
            instance_uuid: Unique identifier of instance
        
        Returns:
            dict: Instance status information
        """
        try:
            config = request.env['saas.client.config'].sudo().search([
                ('instance_uuid', '=', instance_uuid)
            ], limit=1)
            
            if not config:
                return {
                    'success': False,
                    'error': 'Instance UUID not found'
                }
            
            return {
                'success': True,
                'instance_uuid': config.instance_uuid,
                'current_users': config.current_users,
                'user_limit': config.user_limit,
                'users_percentage': config.users_percentage,
                'last_sync_date': config.last_sync_date.isoformat() if config.last_sync_date else None,
                'sync_status': config.sync_status,
                'is_limit_enforced': config.is_limit_enforced,
            }
            
        except Exception as e:
            _logger.error(f"Error getting status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
