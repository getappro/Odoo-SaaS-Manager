# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
SaaS Template Model
===================
Base de données PostgreSQL master servant de modèle à cloner.
PostgreSQL master database serving as a template for cloning.
"""

import logging
import json
import requests
import psycopg2
from psycopg2 import sql, OperationalError
from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
from odoo.tools import config

_logger = logging.getLogger(__name__)


class SaaSTemplate(models.Model):
    """
    SaaS Template - PostgreSQL Master Database
    
    Représente une base de données template PostgreSQL qui sert de modèle
    pour le clonage rapide d'instances client.
    
    Represents a PostgreSQL template database that serves as a model
    for rapid client instance cloning.
    """
    _name = 'saas.template'
    _description = 'SaaS Template'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence, name'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help="Display order"
    )
    name = fields.Char(
        string='Name',
        required=True,
        tracking=True,
        help="Template name (e.g., 'Restaurant', 'E-commerce')"
    )
    code = fields.Char(
        string='Code',
        required=True,
        tracking=True,
        help="Technical code (e.g., 'restaurant')"
    )
    template_db = fields.Char(
        string='Template Database',
        required=True,
        tracking=True,
        help="PostgreSQL database name (e.g., 'template_restaurant')"
    )
    is_template_ready = fields.Boolean(
        string='Template Ready',
        default=False,
        tracking=True,
        help="Template is ready to be cloned"
    )
    template_version = fields.Char(
        string='Template Version',
        default='1.0.0',
        tracking=True,
        help="Version of the template"
    )
    server_id = fields.Many2one(
        'saas.server',
        string='Server',
        required=True,
        domain="[('state', '=', 'active')]",
        help="Server where this template database is hosted"
    )
    module_ids = fields.Many2many(
        'ir.module.module',
        string='Installed Modules',
        help="Odoo modules installed in this template"
    )
    description = fields.Html(
        string='Description',
        help="Template description and features"
    )
    image = fields.Image(
        string='Image',
        help="Template image"
    )
    instance_count = fields.Integer(
        string='Instance Count',
        compute='_compute_instance_count',
        help="Number of instances created from this template"
    )
    active = fields.Boolean(
        string='Active',
        default=True
    )

    _sql_constraints = [
        ('code_unique', 'UNIQUE(code)', 'Template code must be unique!'),
        ('template_db_unique', 'UNIQUE(template_db)', 'Template database name must be unique!'),
    ]

    @api.depends('template_db')
    def _compute_instance_count(self):
        """
        Calcule le nombre d'instances créées depuis ce template.
        Compute the number of instances created from this template.
        """
        for template in self:
            template.instance_count = self.env['saas.instance'].search_count([
                ('template_id', '=', template.id)
            ])

    def _create_template_db_via_rpc(self, base_url, db_name, admin_password='admin'):
        """
        Créer une base de données template via l'API RPC jsonrpc2 d'Odoo.
        Create a template database via Odoo's jsonrpc2 RPC API.

        Args:
            base_url (str): Base URL of the Odoo instance (e.g., 'http://localhost:8069')
            db_name (str): Name of the database to create
            admin_password (str): Master password for database operations

        Returns:
            dict: Response from RPC call

        Raises:
            UserError: If RPC call fails
        """
        try:
            # Endpoint for creating database
            rpc_url = f"{base_url}/jsonrpc"

            # Payload for creating database
            payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'db',
                    'method': 'create_database',
                    'args': [
                        admin_password,  # master password
                        db_name,  # new database name
                        False,  # demo data
                        'en_US',  # language
                        'admin',  # admin password (new)
                    ]
                },
                'id': 1
            }

            _logger.info(f"Creating database via RPC: {db_name}")
            _logger.info(f"RPC URL: {rpc_url}")

            # Make RPC call
            response = requests.post(
                rpc_url,
                json=payload,
                timeout=600
            )

            response.raise_for_status()
            result = response.json()

            if 'error' in result and result['error']:
                error_msg = result['error'].get('data', {}).get('message', str(result['error']))
                raise UserError(
                    _("RPC Error while creating database.\n\nError: %s") % error_msg
                )

            _logger.info(f"Database created successfully via RPC: {db_name}")
            return result

        except requests.exceptions.RequestException as e:
            _logger.exception("Request error during RPC call")
            raise UserError(
                _("Failed to connect to Odoo RPC endpoint.\n\n"
                  "URL: %s\n\n"
                  "Error: %s") % (base_url, str(e))
            )
        except Exception as e:
            _logger.exception("Unexpected error during RPC database creation")
            raise UserError(
                _("Error creating database via RPC.\n\nError: %s") % str(e)
            )

    def _install_modules_via_rpc(self, base_url, db_name, modules_to_install, admin_login='admin', admin_password='admin'):
        """
        Installer les modules dans la base de données via l'API RPC.
        Install modules in the database via RPC API.

        Args:
            base_url (str): Base URL of the Odoo instance
            db_name (str): Database name
            modules_to_install (list): List of module names to install
            admin_login (str): Admin login username
            admin_password (str): Admin password

        Returns:
            dict: Response from RPC call

        Raises:
            UserError: If module installation fails
        """
        try:
            rpc_url = f"{base_url}/jsonrpc"

            # Step 1: Authenticate
            auth_payload = {
                'jsonrpc': '2.0',
                'method': 'call',
                'params': {
                    'service': 'common',
                    'method': 'login',
                    'args': [db_name, admin_login, admin_password]
                },
                'id': 1
            }

            _logger.info(f"Authenticating to database {db_name} via RPC")
            auth_response = requests.post(rpc_url, json=auth_payload, timeout=30)
            auth_response.raise_for_status()
            auth_result = auth_response.json()

            if 'error' in auth_result and auth_result['error']:
                raise UserError(
                    _("Authentication failed via RPC.\n\nError: %s") % str(auth_result['error'])
                )

            user_id = auth_result.get('result', False)
            if not user_id:
                raise UserError(_("Failed to authenticate to the database via RPC."))

            _logger.info(f"Authenticated successfully with user ID: {user_id}")

            # Step 2: Install modules
            for module_name in modules_to_install:
                try:
                    # First, search for the module by name
                    search_payload = {
                        'jsonrpc': '2.0',
                        'method': 'call',
                        'params': {
                            'service': 'object',
                            'method': 'execute_kw',
                            'args': [
                                db_name,
                                user_id,
                                admin_password,
                                'ir.module.module',
                                'search',
                                [[['name', '=', module_name]]]
                            ]
                        },
                        'id': 1
                    }

                    _logger.info(f"Searching for module {module_name} via RPC")
                    search_response = requests.post(rpc_url, json=search_payload, timeout=30)
                    search_response.raise_for_status()
                    search_result = search_response.json()

                    if 'error' in search_result and search_result['error']:
                        _logger.warning(f"Failed to search for module {module_name}: {search_result['error']}")
                        continue

                    module_ids = search_result.get('result', [])
                    if not module_ids:
                        _logger.warning(f"Module {module_name} not found")
                        continue

                    _logger.info(f"Found module {module_name} with IDs: {module_ids}")

                    # Now install the module
                    install_payload = {
                        'jsonrpc': '2.0',
                        'method': 'call',
                        'params': {
                            'service': 'object',
                            'method': 'execute_kw',
                            'args': [
                                db_name,
                                user_id,
                                admin_password,
                                'ir.module.module',
                                'button_install',
                                [module_ids]  # Pass the list of IDs, not a domain
                            ]
                        },
                        'id': 1
                    }

                    _logger.info(f"Installing module {module_name} via RPC")
                    install_response = requests.post(rpc_url, json=install_payload, timeout=300)
                    install_response.raise_for_status()
                    install_result = install_response.json()

                    if 'error' in install_result and install_result['error']:
                        _logger.warning(f"Failed to install module {module_name}: {install_result['error']}")
                    else:
                        _logger.info(f"Module {module_name} installed successfully")

                except Exception as e:
                    _logger.warning(f"Error installing module {module_name} via RPC: {str(e)}")

            _logger.info("All modules installation completed via RPC")
            return {'status': 'success'}

        except requests.exceptions.RequestException as e:
            _logger.exception("Request error during module installation via RPC")
            raise UserError(
                _("Failed to install modules via RPC.\n\nError: %s") % str(e)
            )
        except Exception as e:
            _logger.exception("Unexpected error during module installation via RPC")
            raise UserError(
                _("Error installing modules via RPC.\n\nError: %s") % str(e)
            )

    def action_create_template_db(self):
        """
        Créer la base de données template PostgreSQL et l'initialiser via RPC.
        Create the PostgreSQL template database and initialize it via RPC.

        Steps:
        1. Validate server is active
        2. Create database via RPC jsonrpc2 API
        3. Authenticate to the database
        4. Install base modules via RPC
        5. Mark template as ready

        Returns:
            dict: Notification action

        Raises:
            UserError: If database creation fails
        """
        self.ensure_one()

        # Validate that server is active
        if self.server_id.state != 'active':
            raise UserError(
                _("Cannot create template on server '%s'.\n\n"
                  "Server state is '%s'. Server must be 'active' to create templates.\n\n"
                  "Please activate the server first.") % (self.server_id.name, self.server_id.state)
            )

        try:
            template_db_name = self.template_db
            _logger.info(f"Starting template DB creation via RPC: {template_db_name} on server {self.server_id.name}")

            # Get base URL from server configuration
            base_url = self.server_id.server_url
            _logger.info(f"Using server URL: {base_url}")

            # Get master password from server configuration
            master_password = self.server_id.master_password

            # Step 1: Create database via RPC
            self._create_template_db_via_rpc(base_url, template_db_name, master_password)

            # Step 2: Install base modules via RPC
            modules_to_install = ['base', 'web', 'mail', 'portal']
            self._install_modules_via_rpc(
                base_url,
                template_db_name,
                modules_to_install,
                admin_login='admin',
                admin_password='admin'
            )

            # Step 3: Mark template as ready
            self.write({
                'is_template_ready': True,
            })

            _logger.info(f"Template database created and ready: {template_db_name} on server {self.server_id.name}")

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Template Created Successfully'),
                    'message': _('Template database "%s" has been created and initialized via RPC on server "%s".') % (template_db_name, self.server_id.name),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except UserError:
            raise
        except Exception as e:
            _logger.exception("Unexpected error in action_create_template_db")
            raise UserError(
                _("An unexpected error occurred while creating the template database.\n\n"
                  "Error: %s") % str(e)
            )

    def action_update_template(self):
        """
        Mettre à jour la version du template.
        Update the template version.
        """
        self.ensure_one()
        
        # Increment version (simple implementation)
        current_version = self.template_version or '1.0.0'
        parts = current_version.split('.')
        if len(parts) == 3:
            parts[2] = str(int(parts[2]) + 1)
            new_version = '.'.join(parts)
        else:
            new_version = '1.0.1'
        
        self.write({
            'template_version': new_version,
        })
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Template Updated'),
                'message': _('Template version updated to %s') % new_version,
                'type': 'success',
                'sticky': False,
            }
        }

    def clone_template_db(self, new_db_name):
        """
        Cloner la base de données template PostgreSQL.
        Clone the PostgreSQL template database.

        Phase 2: Implement ultra-fast provisioning using PostgreSQL TEMPLATE clone

        Args:
            new_db_name (str): Name of the new database to create

        Returns:
            bool: True if successful

        Raises:
            UserError: If cloning fails
        """
        self.ensure_one()

        if not self.is_template_ready:
            raise UserError(
                _("Template '%s' is not ready. Please create the template database first.") % self.name
            )

        try:
            # Get PostgreSQL connection parameters from server
            db_host = self.server_id.db_host
            db_port = self.server_id.db_port
            db_user = self.server_id.db_user
            db_password = self.server_id.db_password

            _logger.info(f"Cloning template {self.template_db} to {new_db_name} on server {self.server_id.name}")

            # Connect to PostgreSQL
            conn_params = {
                'host': db_host,
                'port': db_port,
                'user': db_user,
                'password': db_password,
                'database': 'postgres',
            }

            try:
                conn = psycopg2.connect(**conn_params)
                conn.autocommit = True
                cursor = conn.cursor()
            except OperationalError as e:
                raise UserError(
                    _("Could not connect to PostgreSQL server.\n\nError: %s") % str(e)
                )

            # Check if new database already exists
            cursor.execute(
                sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
                [new_db_name]
            )

            if cursor.fetchone():
                cursor.close()
                conn.close()
                raise UserError(
                    _("Database '%s' already exists!") % new_db_name
                )

            # Clone the template database
            # This is ultra-fast because it just creates a copy of the template
            try:
                cursor.execute(
                    sql.SQL("CREATE DATABASE {} TEMPLATE {} WITH OWNER {}").format(
                        sql.Identifier(new_db_name),
                        sql.Identifier(self.template_db),
                        sql.Identifier(db_user)
                    )
                )
                _logger.info(f"Database cloned successfully: {new_db_name}")
            except Exception as e:
                cursor.close()
                conn.close()
                raise UserError(
                    _("Failed to clone database '%s'.\n\nError: %s") % (new_db_name, str(e))
                )

            cursor.close()
            conn.close()

            _logger.info(f"Template {self.template_db} cloned to {new_db_name}")
            return True

        except UserError:
            raise
        except Exception as e:
            _logger.exception("Unexpected error in clone_template_db")
            raise UserError(
                _("An unexpected error occurred while cloning the template database.\n\nError: %s") % str(e)
            )

    def action_access_template_db(self):
        """
        Ouvrir l'URL pour accéder à la configuration du template.
        Open URL to access template configuration.
        
        Returns:
            dict: Action to open template database in new window
        """
        self.ensure_one()
        
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        template_url = f"{base_url}/web?db={self.template_db}"
        
        return {
            'type': 'ir.actions.act_url',
            'url': template_url,
            'target': 'new',
        }

    def action_view_instances(self):
        """
        Voir toutes les instances créées depuis ce template.
        View all instances created from this template.
        
        Returns:
            dict: Action to display instances
        """
        self.ensure_one()
        
        return {
            'name': _('Instances from %s') % self.name,
            'type': 'ir.actions.act_window',
            'res_model': 'saas.instance',
            'view_mode': 'list,form,kanban',
            'domain': [('template_id', '=', self.id)],
            'context': {'default_template_id': self.id},
        }

    @api.constrains('code')
    def _check_code(self):
        """
        Valider le format du code technique.
        Validate technical code format.
        """
        for template in self:
            if template.code and not template.code.islower():
                raise ValidationError(_('Template code must be lowercase.'))

    def _initialize_odoo_database(self, db_name, modules_to_install):
        """
        Initialiser une base de données Odoo via l'API plutôt que subprocess.
        Initialize an Odoo database via the API instead of subprocess.

        Args:
            db_name (str): Name of the database to initialize
            modules_to_install (str): Comma-separated module names

        Raises:
            UserError: If initialization fails
        """
        try:
            from odoo import netsvc
            from odoo.service import db as db_service

            _logger.info(f"Initializing database {db_name} with modules: {modules_to_install}")

            # Create the database
            try:
                db_service.create_database(
                    db_name,
                    demo=False,
                    lang='en_US',
                )
                _logger.info(f"Database {db_name} created successfully")
            except Exception as e:
                _logger.error(f"Failed to create database {db_name}: {str(e)}")
                raise

            # Now open the database and install modules
            with self.pool.cursor() as cr:
                # Connect to the new database
                env = self.env(cr=cr, context={'lang': 'en_US'})

                # Parse modules to install
                modules_list = [m.strip() for m in modules_to_install.split(',') if m.strip()]

                # Install modules
                for module_name in modules_list:
                    try:
                        module = env['ir.module.module'].search([('name', '=', module_name)])
                        if module:
                            module.button_install()
                            _logger.info(f"Module {module_name} installed")
                        else:
                            _logger.warning(f"Module {module_name} not found")
                    except Exception as e:
                        _logger.warning(f"Failed to install module {module_name}: {str(e)}")

            _logger.info(f"Database {db_name} initialized successfully")
            return True

        except Exception as e:
            _logger.exception(f"Error initializing database {db_name}")
            raise UserError(
                _("Failed to initialize database via API.\n\nError: %s") % str(e)
            )

