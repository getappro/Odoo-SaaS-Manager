# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AccessMiddleware(http.Controller):
    """
    Middleware controller that intercepts requests to check
    if instance is suspended and blocks access accordingly.
    """

    @http.route('/web', auth='user', type='http')
    def web_index(self, **kwargs):
        """Check suspension status before serving web interface"""
        try:
            # Get current instance info from request
            instance_id = self._get_current_instance_id()

            if instance_id:
                # Check if instance is suspended
                suspension = request.env['saas.suspension'].search([
                    ('instance_id', '=', instance_id),
                    ('state', '=', 'active'),
                ], limit=1)

                if suspension:
                    # Check if user is admin (bypass suspension)
                    if not request.env.user.has_group('saas_access_control.group_saas_admin'):
                        return self._return_suspension_page(suspension)
        except Exception as e:
            _logger.warning(f"Error checking suspension: {e}")

        # Continue with normal request
        return super().web_index(**kwargs)

    @http.route('/jsonrpc', auth='none', type='json', csrf=False)
    def jsonrpc(self, service, method, args, **kwargs):
        """Intercept JSON-RPC calls to check suspension"""
        try:
            # Check if this is database-specific call
            if service == 'object' and len(args) > 0:
                db_name = args[0]
                instance = request.env['saas.instance'].search([
                    ('db_name', '=', db_name),
                ], limit=1)

                if instance:
                    # Check suspension
                    suspension = request.env['saas.suspension'].search([
                        ('instance_id', '=', instance.id),
                        ('state', '=', 'active'),
                    ], limit=1)

                    if suspension:
                        # Check if user is admin
                        if not self._is_admin_user():
                            return {
                                'jsonrpc': '2.0',
                                'id': kwargs.get('id', 1),
                                'error': {
                                    'code': 403,
                                    'message': 'Instance Suspended',
                                    'data': {
                                        'name': 'AccessDenied',
                                        'debug': f"Instance is suspended: {suspension.reason}",
                                    }
                                }
                            }
        except Exception as e:
            _logger.warning(f"Error in JSON-RPC suspension check: {e}")

        # Continue with normal RPC handling
        return super().jsonrpc(service, method, args, **kwargs)

    def _get_current_instance_id(self):
        """
        Get current instance ID from request.
        Can be from hostname, cookie, or session.
        """
        try:
            # Method 1: Check hostname
            hostname = request.httprequest.host.split(':')[0]
            instance = request.env['saas.instance'].search([
                ('domain', 'ilike', hostname),
            ], limit=1)
            if instance:
                return instance.id
        except:
            pass

        return None

    def _is_admin_user(self):
        """Check if current user is SaaS admin"""
        try:
            return request.env.user.has_group('saas_access_control.group_saas_admin')
        except:
            return False

    def _return_suspension_page(self, suspension):
        """Return suspension notification page"""
        html = f"""
        <html>
            <head>
                <title>Instance Suspended</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 25px rgba(0,0,0,0.2);
                        max-width: 500px;
                        text-align: center;
                    }}
                    h1 {{
                        color: #d32f2f;
                        margin-top: 0;
                    }}
                    .reason {{
                        background: #f5f5f5;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        text-align: left;
                    }}
                    .footer {{
                        color: #999;
                        font-size: 12px;
                        margin-top: 30px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>⚠️ Instance Suspended</h1>
                    <p>Your Odoo instance has been temporarily suspended.</p>
                    <div class="reason">
                        <strong>Reason:</strong> {suspension.reason.replace('_', ' ').title()}<br>
                        <strong>Suspended:</strong> {suspension.suspended_date}
                    </div>
                    {f'<p><strong>Details:</strong> {suspension.description}</p>' if suspension.description else ''}
                    <p>Please contact support to resolve this issue.</p>
                    <div class="footer">
                        If you believe this is a mistake, contact: support@example.com
                    </div>
                </div>
            </body>
        </html>
        """
        return http.Response(html, content_type='text/html', status=403)

