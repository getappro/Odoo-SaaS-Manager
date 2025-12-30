# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
SaaS Template Model
===================
Base de données PostgreSQL master servant de modèle à cloner.
PostgreSQL master database serving as a template for cloning.
"""

import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

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

    def action_create_template_db(self):
        """
        Créer la base de données template PostgreSQL.
        Create the PostgreSQL template database.
        
        TODO Phase 2: Implement actual database creation with psycopg2
        Example:
            import psycopg2
            conn = psycopg2.connect(dbname='postgres', user='odoo', password='...')
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {self.template_db}")
            conn.commit()
        """
        self.ensure_one()
        
        # Placeholder implementation
        _logger.info(f"Creating template database: {self.template_db}")
        
        # TODO Phase 2: Actual implementation
        raise UserError(_(
            "Template database creation is not yet implemented.\n\n"
            "Phase 2 TODO:\n"
            "1. Connect to PostgreSQL using psycopg2\n"
            "2. CREATE DATABASE %s\n"
            "3. Initialize Odoo database\n"
            "4. Install base modules\n"
            "5. Mark template as ready"
        ) % self.template_db)

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
