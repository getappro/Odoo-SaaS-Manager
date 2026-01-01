# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http, fields
from odoo.http import request
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class SupportPortal(http.Controller):
    """
    Portal for secure remote support access using JWT tokens.
    """

    @http.route('/support/portal', auth='public', type='http')
    def support_portal_index(self, **kwargs):
        """Support portal landing page"""
        return request.render('saas_access_control.support_portal_template', {
            'page_title': 'Support Portal',
        })

    @http.route('/support/verify-token', auth='public', type='json', csrf=False)
    def verify_support_token(self, token, **kwargs):
        """
        Verify JWT token and return access information.
        This endpoint can be called from instances to validate tokens.
        """
        try:
            support_session_model = request.env['support.session'].sudo()
            is_valid, payload = support_session_model.verify_token(token)

            if is_valid:
                # Log access
                support_session = request.env['support.session'].browse(
                    payload['session_id']
                )
                support_session.log_access(
                    ip_address=self._get_client_ip()
                )

                return {
                    'valid': True,
                    'payload': payload,
                }
            else:
                # Log failed access
                self._log_failed_access('Invalid token', token)
                return {
                    'valid': False,
                    'error': payload,
                }
        except Exception as e:
            _logger.error(f"Token verification error: {e}")
            return {
                'valid': False,
                'error': str(e),
            }

    @http.route(
        '/support/request-access',
        auth='user',
        type='json',
        methods=['POST']
    )
    def request_support_access(self, instance_id, reason, description=None, **kwargs):
        """
        Request support access (used by instance to request access from master).
        This creates a support session in the master.
        """
        try:
            # Verify user has permission to request
            if not request.env.user.has_group('base.group_user'):
                return {'error': 'Insufficient permissions'}

            # Create support session
            session = request.env['support.session'].create({
                'instance_id': instance_id,
                'support_user_id': request.env.user.id,
                'reason': reason,
                'description': description,
                'expires_at': fields.Datetime.to_string(
                    datetime.now() + timedelta(hours=24)
                ),
            })

            _logger.info(
                f"Support access requested for instance {instance_id} "
                f"by {request.env.user.name}"
            )

            return {
                'success': True,
                'session_id': session.id,
                'token': session.jwt_token,
            }
        except Exception as e:
            _logger.error(f"Error creating support session: {e}")
            return {'error': str(e)}

    @http.route(
        '/support/access-list',
        auth='user',
        type='json',
        methods=['GET']
    )
    def get_support_sessions(self, instance_id=None, **kwargs):
        """Get list of support sessions for current user"""
        try:
            domain = [('support_user_id', '=', request.env.user.id)]
            if instance_id:
                domain.append(('instance_id', '=', instance_id))

            sessions = request.env['support.session'].search(domain, order='create_date desc')

            return {
                'sessions': [{
                    'id': s.id,
                    'instance': s.instance_id.name,
                    'reason': s.reason,
                    'state': s.state,
                    'created': s.created_date,
                    'expires': s.expires_at,
                    'access_count': s.access_count,
                } for s in sessions]
            }
        except Exception as e:
            _logger.error(f"Error fetching support sessions: {e}")
            return {'error': str(e)}

    @http.route(
        '/support/revoke-session/<int:session_id>',
        auth='user',
        type='json',
        methods=['POST']
    )
    def revoke_support_session(self, session_id, **kwargs):
        """Revoke a support session"""
        try:
            session = request.env['support.session'].browse(session_id)

            # Check permission
            if session.support_user_id != request.env.user:
                if not request.env.user.has_group('saas_access_control.group_saas_admin'):
                    return {'error': 'Permission denied'}

            session.action_revoke()

            _logger.info(f"Support session {session_id} revoked")

            return {'success': True}
        except Exception as e:
            _logger.error(f"Error revoking session: {e}")
            return {'error': str(e)}

    @http.route(
        '/support/access-logs/<int:instance_id>',
        auth='user',
        type='json',
        methods=['GET']
    )
    def get_access_logs(self, instance_id, limit=100, **kwargs):
        """Get access logs for an instance"""
        try:
            # Check permission
            instance = request.env['saas.instance'].browse(instance_id)
            if not request.env.user.has_group('saas_access_control.group_saas_admin'):
                return {'error': 'Permission denied'}

            logs = request.env['access.log'].get_instance_logs(
                instance_id,
                limit=limit
            )

            return {
                'logs': [{
                    'id': l.id,
                    'action': l.action,
                    'user': l.user_id.name,
                    'timestamp': l.timestamp,
                    'ip': l.ip_address,
                    'status': l.status,
                } for l in logs]
            }
        except Exception as e:
            _logger.error(f"Error fetching access logs: {e}")
            return {'error': str(e)}

    def _get_client_ip(self):
        """Get client IP address from request"""
        try:
            if 'X-Forwarded-For' in request.httprequest.headers:
                return request.httprequest.headers['X-Forwarded-For'].split(',')[0].strip()
            return request.httprequest.remote_addr
        except:
            return None

    def _log_failed_access(self, reason, token=None):
        """Log failed access attempt"""
        try:
            request.env['access.log'].sudo().create({
                'instance_id': None,
                'user_id': request.env.user.id if request.env.user else 1,
                'action': 'failed_access',
                'timestamp': fields.Datetime.now(),
                'ip_address': self._get_client_ip(),
                'status': 'denied',
                'error_message': reason,
            })
        except Exception as e:
            _logger.warning(f"Could not log failed access: {e}")

