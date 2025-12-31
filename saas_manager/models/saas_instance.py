# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
SaaS Instance Model
===================
Instance client avec provisioning automatisé.
Client instance with automated provisioning.
"""

import logging
import secrets
import string
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class SaaSInstance(models.Model):
    """
    SaaS Instance - Core Provisioning System
    
    Représente une instance client avec provisioning automatisé via
    clonage PostgreSQL des templates.
    
    Represents a client instance with automated provisioning via
    PostgreSQL template cloning.
    """
    _name = 'saas.instance'
    _description = 'SaaS Instance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'

    name = fields.Char(
        string='Instance Name',
        required=True,
        tracking=True,
        help="Name of the instance"
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        tracking=True,
        ondelete='restrict',
        help="Customer owning this instance"
    )
    database_name = fields.Char(
        string='Database Name',
        required=True,
        tracking=True,
        help="PostgreSQL database name"
    )
    subdomain = fields.Char(
        string='Subdomain',
        required=True,
        tracking=True,
        help="Subdomain (e.g., 'client1')"
    )
    domain = fields.Char(
        string='Full Domain',
        compute='_compute_domain',
        store=True,
        help="Full domain (e.g., 'client1.example.com')"
    )
    template_id = fields.Many2one(
        'saas.template',
        string='Template',
        required=True,
        tracking=True,
        ondelete='restrict',
        help="Template used for this instance"
    )
    plan_id = fields.Many2one(
        'saas.plan',
        string='Plan',
        required=True,
        tracking=True,
        ondelete='restrict',
        help="Subscription plan"
    )
    server_id = fields.Many2one(
        'saas.server',
        string='Server',
        required=True,
        tracking=True,
        ondelete='restrict',
        help="Server hosting this instance"
    )
    state = fields.Selection([
        ('draft', 'Draft'),
        ('provisioning', 'Provisioning'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
    ], string='State', default='draft', required=True, tracking=True)
    
    admin_login = fields.Char(
        string='Admin Login',
        tracking=True,
        help="Administrator login"
    )
    admin_password = fields.Char(
        string='Admin Password',
        help="Administrator password (stored encrypted in production)"
    )
    current_users = fields.Integer(
        string='Current Users',
        compute='_compute_current_users',
        help="Number of active users"
    )
    storage_used = fields.Float(
        string='Storage Used (GB)',
        compute='_compute_storage_used',
        help="Storage used in GB"
    )
    activation_date = fields.Datetime(
        string='Activation Date',
        tracking=True,
        help="Date when instance was activated"
    )
    expiration_date = fields.Datetime(
        string='Expiration Date',
        tracking=True,
        help="Date when instance will expire"
    )
    version = fields.Char(
        string='Odoo Version',
        default='18.0',
        help="Odoo version"
    )
    subscription_id = fields.Many2one(
        'saas.subscription',
        string='Active Subscription',
        help="Current active subscription"
    )
    notes = fields.Text(
        string='Notes',
        help="Internal notes"
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )
    color = fields.Integer(
        string='Color Index',
        help="Color for kanban view"
    )

    _sql_constraints = [
        ('database_name_unique', 'UNIQUE(database_name)', 'Database name must be unique!'),
        ('subdomain_unique', 'UNIQUE(subdomain)', 'Subdomain must be unique!'),
    ]

    @api.depends('subdomain')
    def _compute_domain(self):
        """
        Calcule le domaine complet depuis le sous-domaine.
        Compute full domain from subdomain.
        """
        base_domain = self.env['ir.config_parameter'].sudo().get_param(
            'saas.base_domain', 'example.com'
        )
        for instance in self:
            if instance.subdomain:
                instance.domain = f"{instance.subdomain}.{base_domain}"
            else:
                instance.domain = False

    def _compute_current_users(self):
        """
        Calcule le nombre d'utilisateurs actifs.
        Compute number of active users.
        
        TODO Phase 2: Connect to instance database and count users
        """
        for instance in self:
            # Placeholder - TODO Phase 2: Query instance database
            instance.current_users = 0

    def _compute_storage_used(self):
        """
        Calcule l'espace disque utilisé.
        Compute storage used.
        
        TODO Phase 2: Query PostgreSQL database size
        """
        for instance in self:
            # Placeholder - TODO Phase 2: Query database size
            instance.storage_used = 0.0

    @api.model
    def _generate_random_password(self, length=16):
        """
        Génère un mot de passe aléatoire sécurisé.
        Generate a secure random password.
        
        Args:
            length (int): Password length
            
        Returns:
            str: Random password
        """
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(secrets.choice(alphabet) for _ in range(length))
        return password

    @api.constrains('subdomain')
    def _check_subdomain(self):
        """
        Valider le format du sous-domaine.
        Validate subdomain format.
        """
        for instance in self:
            if instance.subdomain:
                # Only lowercase alphanumeric and hyphens
                if not all(c.isalnum() or c == '-' for c in instance.subdomain):
                    raise ValidationError(_(
                        'Subdomain can only contain lowercase letters, numbers, and hyphens.'
                    ))
                if not instance.subdomain[0].isalnum() or not instance.subdomain[-1].isalnum():
                    raise ValidationError(_(
                        'Subdomain must start and end with a letter or number.'
                    ))

    def action_provision_instance(self):
        """
        Provisionner l'instance complète (orchestration).
        Provision the complete instance (orchestration).
        
        Workflow:
        1. Valider les prérequis
        2. Cloner la base de données template
        3. Neutraliser les données sensibles
        4. Personnaliser l'instance
        5. Créer l'administrateur client
        6. Configurer le sous-domaine
        7. Activer l'instance
        """
        self.ensure_one()
        
        if self.state != 'draft':
            raise UserError(_('Only draft instances can be provisioned.'))
        
        if not self.template_id.is_template_ready:
            raise UserError(_('Template %s is not ready for cloning.') % self.template_id.name)
        
        try:
            # Update state to provisioning
            self.write({'state': 'provisioning'})
            self.env.cr.commit()  # Commit state change
            
            _logger.info(f"Starting provisioning for instance: {self.name}")
            
            # Step 1: Clone template database (~5s)
            self._clone_template_database()
            
            # Step 2: Neutralize sensitive data (~2s)
            self._neutralize_database()
            
            # Step 3: Customize instance (~2s)
            self._customize_instance()
            
            # Step 4: Create client admin (~1s)
            self._create_client_admin()
            
            # Step 5: Configure subdomain (~1s)
            self._configure_subdomain()
            
            # Step 6: Activate instance
            self.write({
                'state': 'active',
                'activation_date': fields.Datetime.now(),
            })
            
            _logger.info(f"Instance {self.name} provisioned successfully")
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Instance Provisioned'),
                    'message': _('Instance %s is now active at %s') % (self.name, self.domain),
                    'type': 'success',
                    'sticky': False,
                }
            }
            
        except Exception as e:
            _logger.error(f"Provisioning failed for {self.name}: {str(e)}")
            self.write({'state': 'draft'})
            raise UserError(_('Provisioning failed: %s') % str(e))

    def _clone_template_database(self):
        """
        Cloner la base de données template PostgreSQL.
        Clone the PostgreSQL template database.
        
        TODO Phase 2: Implement with psycopg2
        
        Example implementation:
            import psycopg2
            
            # Connect to PostgreSQL
            conn = psycopg2.connect(
                dbname='postgres',
                user=config.get('db_user'),
                password=config.get('db_password'),
                host=config.get('db_host'),
                port=config.get('db_port')
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Clone template
            template_db = self.template_id.template_db
            target_db = self.database_name
            
            cursor.execute(f"CREATE DATABASE {target_db} WITH TEMPLATE {template_db}")
            cursor.close()
            conn.close()
            
            _logger.info(f"Database {target_db} cloned from {template_db}")
        """
        _logger.info(f"TODO Phase 2: Clone {self.template_id.template_db} to {self.database_name}")
        # Placeholder - actual implementation in Phase 2

    def _neutralize_database(self):
        """
        Neutraliser les données sensibles du template cloné.
        Neutralize sensitive data from cloned template.
        
        TODO Phase 2: Implement with odoorpc
        
        Example implementation:
            import odoorpc
            
            # Connect to instance database
            odoo = odoorpc.ODOO(
                host=config.get('odoo_host'),
                port=config.get('odoo_port'),
                protocol='jsonrpc+ssl'
            )
            
            # Login as superuser
            odoo.login(self.database_name, 'admin', 'admin')
            
            # Neutralize data
            User = odoo.env['res.users']
            Partner = odoo.env['res.partner']
            Company = odoo.env['res.company']
            
            # Reset admin password
            admin_user = User.browse(2)
            User.write([admin_user], {'password': 'admin'})
            
            # Clear sensitive company data
            companies = Company.search([])
            Company.write(companies, {
                'vat': False,
                'company_registry': False,
                'email': False,
                'phone': False,
            })
            
            # Anonymize demo users
            demo_users = User.search([('id', '>', 2)])
            for user_id in demo_users:
                User.write([user_id], {
                    'email': f'demo.user{user_id}@example.com',
                    'password': 'demo',
                })
            
            _logger.info(f"Database {self.database_name} neutralized")
        """
        _logger.info(f"TODO Phase 2: Neutralize database {self.database_name}")
        # Placeholder - actual implementation in Phase 2

    def _customize_instance(self):
        """
        Personnaliser l'instance avec les données client.
        Customize instance with client data.
        
        TODO Phase 2: Implement with odoorpc
        
        Example implementation:
            import odoorpc
            
            odoo = odoorpc.ODOO(host, port, protocol='jsonrpc+ssl')
            odoo.login(self.database_name, 'admin', 'admin')
            
            Company = odoo.env['res.company']
            
            # Update main company
            company = Company.browse(1)
            Company.write([company], {
                'name': self.partner_id.name,
                'email': self.partner_id.email,
                'phone': self.partner_id.phone,
                'website': self.domain,
            })
            
            # Upload logo if available
            if self.partner_id.image_1920:
                Company.write([company], {
                    'logo': self.partner_id.image_1920,
                })
            
            _logger.info(f"Instance {self.database_name} customized")
        """
        _logger.info(f"TODO Phase 2: Customize instance {self.database_name}")
        # Placeholder - actual implementation in Phase 2

    def _create_client_admin(self):
        """
        Créer le compte administrateur client.
        Create client administrator account.
        
        TODO Phase 2: Implement with odoorpc
        
        Example implementation:
            import odoorpc
            
            odoo = odoorpc.ODOO(host, port, protocol='jsonrpc+ssl')
            odoo.login(self.database_name, 'admin', 'admin')
            
            User = odoo.env['res.users']
            
            # Generate credentials
            admin_login = self.admin_login or self.partner_id.email
            admin_password = self.admin_password or self._generate_random_password()
            
            # Update admin user
            admin_user = User.browse(2)
            User.write([admin_user], {
                'name': self.partner_id.name,
                'login': admin_login,
                'password': admin_password,
                'email': self.partner_id.email,
            })
            
            # Store credentials
            self.write({
                'admin_login': admin_login,
                'admin_password': admin_password,  # Should be encrypted in production
            })
            
            _logger.info(f"Admin user created for {self.database_name}")
        """
        _logger.info(f"TODO Phase 2: Create admin for {self.database_name}")
        
        # Generate credentials now for later use
        if not self.admin_login:
            self.admin_login = self.partner_id.email or f"admin@{self.subdomain}"
        if not self.admin_password:
            self.admin_password = self._generate_random_password()

    def _configure_subdomain(self):
        """
        Configurer le sous-domaine DNS et reverse proxy.
        Configure subdomain DNS and reverse proxy.
        
        TODO Phase 2: Implement DNS/reverse proxy configuration
        
        Example implementation for Traefik:
            # Add labels to Traefik configuration
            # Or update nginx configuration
            # Or configure Cloudflare DNS via API
            
            import requests
            
            # Example: Cloudflare API
            cloudflare_api_key = config.get('cloudflare_api_key')
            zone_id = config.get('cloudflare_zone_id')
            
            headers = {
                'Authorization': f'Bearer {cloudflare_api_key}',
                'Content-Type': 'application/json',
            }
            
            data = {
                'type': 'A',
                'name': self.subdomain,
                'content': config.get('server_ip'),
                'proxied': True,
            }
            
            response = requests.post(
                f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records',
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                _logger.info(f"DNS record created for {self.domain}")
            else:
                _logger.error(f"DNS creation failed: {response.text}")
        """
        _logger.info(f"TODO Phase 2: Configure DNS for {self.domain}")
        # Placeholder - actual implementation in Phase 2

    def action_suspend(self):
        """
        Suspendre l'instance (non-paiement, expiration).
        Suspend the instance (non-payment, expiration).
        """
        self.ensure_one()
        
        if self.state not in ['active']:
            raise UserError(_('Only active instances can be suspended.'))
        
        self.write({'state': 'suspended'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Instance Suspended'),
                'message': _('Instance %s has been suspended') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_reactivate(self):
        """
        Réactiver une instance suspendue.
        Reactivate a suspended instance.
        """
        self.ensure_one()
        
        if self.state not in ['suspended', 'expired']:
            raise UserError(_('Only suspended or expired instances can be reactivated.'))
        
        self.write({'state': 'active'})
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Instance Reactivated'),
                'message': _('Instance %s is now active') % self.name,
                'type': 'success',
                'sticky': False,
            }
        }

    def action_terminate(self):
        """
        Terminer définitivement l'instance (supprime la DB).
        Terminate the instance permanently (deletes DB).
        
        TODO Phase 2: Implement database deletion
        """
        self.ensure_one()
        
        if self.state == 'terminated':
            raise UserError(_('Instance is already terminated.'))
        
        # TODO Phase 2: Delete PostgreSQL database
        _logger.warning(f"TODO Phase 2: Delete database {self.database_name}")
        
        self.write({
            'state': 'terminated',
            'active': False,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Instance Terminated'),
                'message': _('Instance %s has been terminated') % self.name,
                'type': 'warning',
                'sticky': False,
            }
        }

    def action_access_instance(self):
        """
        Ouvrir l'instance dans un nouvel onglet.
        Open instance in a new tab.
        
        Returns:
            dict: Action to open instance URL
        """
        self.ensure_one()
        
        if self.state not in ['active', 'suspended']:
            raise UserError(_('Instance must be active to access it.'))
        
        instance_url = f"https://{self.domain}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': instance_url,
            'target': 'new',
        }

    @api.model
    def cron_check_subscription_expiry(self):
        """
        CRON: Vérifier les abonnements expirés et suspendre les instances.
        CRON: Check expired subscriptions and suspend instances.
        """
        _logger.info("Running subscription expiry check...")
        
        # Find instances with expired subscriptions
        expired_instances = self.search([
            ('state', '=', 'active'),
            ('expiration_date', '<=', fields.Datetime.now()),
        ])
        
        for instance in expired_instances:
            try:
                instance.write({'state': 'expired'})
                _logger.info(f"Instance {instance.name} marked as expired")
                
                # TODO Phase 2: Send expiration email
                
            except Exception as e:
                _logger.error(f"Failed to expire instance {instance.name}: {str(e)}")

    @api.model
    def cron_monitor_instances(self):
        """
        CRON: Monitorer les instances (usage, santé).
        CRON: Monitor instances (usage, health).
        
        TODO Phase 2: Implement monitoring
        """
        _logger.info("Running instance monitoring...")
        
        active_instances = self.search([('state', '=', 'active')])
        
        for instance in active_instances:
            try:
                # TODO Phase 2: Check database health, disk usage, etc.
                _logger.debug(f"Monitoring instance {instance.name}")
                
            except Exception as e:
                _logger.error(f"Monitoring failed for {instance.name}: {str(e)}")

    @api.model
    def cron_check_user_limits(self):
        """
        CRON: Vérifier les limites d'utilisateurs et alerter.
        CRON: Check user limits and alert.
        
        TODO Phase 2: Implement limit checking
        """
        _logger.info("Running user limit check...")
        
        active_instances = self.search([('state', '=', 'active')])
        
        for instance in active_instances:
            try:
                # TODO Phase 2: Query instance database for user count
                # Compare with plan.user_limit
                # Send alert if limit exceeded
                pass
                
            except Exception as e:
                _logger.error(f"Limit check failed for {instance.name}: {str(e)}")
