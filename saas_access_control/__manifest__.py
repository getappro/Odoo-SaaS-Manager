# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SaaS Access Control',
    'version': '18.0.1.0.0',
    'category': 'Administration',
    'summary': 'Control suspension and remote support access for SaaS instances',
    'description': '''
        SaaS Access Control
        ===================
        
        Manage instance suspension and secure remote support access.
        
        Features:
        * Instance suspension with middleware blocking
        * Temporary support tokens with JWT authentication
        * Secure remote access portal
        * Audit logging and compliance tracking
        * IP-based access restrictions
        * Action-based permission control
        * Master-Instance synchronization
        
        Security:
        * JWT token expiration
        * Rate limiting
        * Audit trail for all access
        * Support token rotation
        * Session isolation
    ''',
    'author': 'Your Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
        'saas_manager',
    ],
    'external_dependencies': {
        'python': ['jwt', 'requests'],
    },
    'data': [
        # Security
        'security/access_control_security.xml',
        'security/ir.model.access.csv',

        # Views
        'views/saas_suspension_views.xml',
        'views/support_session_views.xml',
        'views/access_logs_views.xml',
        'views/saas_instance_extended.xml',

        # Data
        'data/ir_config_parameter.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}

