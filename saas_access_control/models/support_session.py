# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from datetime import datetime, timedelta
import jwt
import logging
import secrets
import string

_logger = logging.getLogger(__name__)


class SupportSession(models.Model):
    """
    Manages secure support access to SaaS instances.
    Creates temporary JWT tokens for support staff.
    """
    _name = 'support.session'
    _description = 'Support Access Session'
    _order = 'create_date desc'

    instance_id = fields.Many2one(
        'saas.instance',
        string='Instance',
        required=True,
        ondelete='cascade',
        index=True,
    )

    support_user_id = fields.Many2one(
        'res.users',
        string='Support User',
        required=True,
        default=lambda self: self.env.user,
    )

    reason = fields.Selection([
        ('troubleshooting', 'Troubleshooting'),
        ('maintenance', 'Maintenance'),
        ('customization', 'Customization'),
        ('training', 'Training'),
        ('emergency', 'Emergency'),
    ], string='Access Reason', required=True)

    description = fields.Text(string='Description')

    jwt_token = fields.Char(
        string='JWT Token',
        readonly=True,
        copy=False,
        groups='saas_access_control.group_saas_admin',
    )

    token_hash = fields.Char(
        string='Token Hash',
        readonly=True,
        copy=False,
    )

    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True,
    )

    expires_at = fields.Datetime(
        string='Expires At',
        required=True,
    )

    accessed_at = fields.Datetime(
        string='Last Accessed At',
    )

    access_count = fields.Integer(
        string='Access Count',
        default=0,
        readonly=True,
    )

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ], string='State', default='active', compute='_compute_state', store=True)

    allowed_actions = fields.Selection([
        ('view', 'View Only'),
        ('edit', 'Edit'),
        ('full', 'Full Access'),
    ], string='Allowed Actions', default='view', required=True)

    allowed_ip = fields.Char(
        string='Allowed IP Address',
        help='Leave empty to allow any IP',
    )

    created_by_id = fields.Many2one(
        'res.users',
        string='Created By',
        readonly=True,
        default=lambda self: self.env.user,
    )

    revoked_by_id = fields.Many2one(
        'res.users',
        string='Revoked By',
        readonly=True,
    )

    revoked_date = fields.Datetime(string='Revoked Date', readonly=True)

    is_revoked = fields.Boolean(
        string='Is Revoked',
        default=False,
        readonly=True,
    )

    @api.depends('expires_at', 'is_revoked')
    def _compute_state(self):
        """Compute session state based on expiration and revocation"""
        now = datetime.now()
        for record in self:
            if record.is_revoked:
                record.state = 'revoked'
            elif record.expires_at <= now:
                record.state = 'expired'
            else:
                record.state = 'active'

    def create(self, vals):
        """Create support session and generate JWT token"""
        # Set default expiration (24 hours from now)
        if 'expires_at' not in vals:
            vals['expires_at'] = fields.Datetime.to_string(
                datetime.now() + timedelta(hours=24)
            )

        record = super().create(vals)

        # Generate JWT token
        token = self._generate_jwt_token(record)
        record.jwt_token = token

        _logger.info(
            f"Support session created for {record.instance_id.name} "
            f"by {record.created_by_id.name}"
        )

        return record

    def _generate_jwt_token(self, record):
        """Generate JWT token for support access"""
        secret_key = self.env['ir.config_parameter'].sudo().get_param(
            'saas_access_control.jwt_secret_key'
        ) or 'default-secret-key-change-in-prod'

        payload = {
            'session_id': record.id,
            'instance_id': record.instance_id.id,
            'instance_db': record.instance_id.db_name,
            'support_user_id': record.support_user_id.id,
            'support_user': record.support_user_id.login,
            'reason': record.reason,
            'allowed_actions': record.allowed_actions,
            'iat': datetime.now(),
            'exp': datetime.fromisoformat(record.expires_at),
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')

        # Store token hash for validation
        record.token_hash = self._hash_token(token)

        return token

    def _hash_token(self, token):
        """Hash token for secure storage"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    def verify_token(self, token):
        """Verify JWT token validity"""
        secret_key = self.env['ir.config_parameter'].sudo().get_param(
            'saas_access_control.jwt_secret_key'
        ) or 'default-secret-key-change-in-prod'

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])

            # Check if session exists and is still valid
            session = self.search([
                ('id', '=', payload['session_id']),
                ('state', '=', 'active'),
            ])

            if not session:
                return False, "Session not found or expired"

            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "Token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid token"

    def action_revoke(self):
        """Revoke a support session"""
        for record in self:
            record.write({
                'is_revoked': True,
                'revoked_date': fields.Datetime.now(),
                'revoked_by_id': self.env.user.id,
            })

            _logger.info(
                f"Support session {record.id} revoked by {self.env.user.name}"
            )

    def action_extend(self, hours=24):
        """Extend session expiration"""
        for record in self:
            if record.is_revoked:
                raise ValueError("Cannot extend revoked session")

            new_expiry = datetime.fromisoformat(record.expires_at) + timedelta(
                hours=hours
            )
            record.expires_at = new_expiry

            _logger.info(
                f"Support session {record.id} extended until {new_expiry}"
            )

    def log_access(self, ip_address=None):
        """Log access to support session"""
        for record in self:
            record.write({
                'accessed_at': fields.Datetime.now(),
                'access_count': record.access_count + 1,
            })

            # Create access log entry
            self.env['access.log'].create({
                'session_id': record.id,
                'instance_id': record.instance_id.id,
                'user_id': record.support_user_id.id,
                'ip_address': ip_address,
                'timestamp': fields.Datetime.now(),
                'action': 'access',
            })

