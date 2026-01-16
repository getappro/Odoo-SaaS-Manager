# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'SaaS Client Agent',
    'version': '18.0.1.0.0',
    'category': 'Administration',
    'summary': 'Client-side agent for SaaS instance management',
    'description': '''
        SaaS Client Agent
        =================
        
        Client-side module installed on SaaS instances to:
        * Track usage metrics (users, storage)
        * Enforce subscription limits
        * Communicate with master server
        * Provide professional dashboard and settings
        
        Features:
        * User limit enforcement with helpful messages
        * Professional Settings integration (Subscription tab)
        * Usage warning banners (>80% capacity)
        * Upgrade request workflow
        * Hidden technical menus for system admins only
    ''',
    'author': 'Your Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'mail',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Views
        'views/saas_client_config_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'saas_client_agent/static/src/js/usage_banner.js',
            'saas_client_agent/static/src/xml/usage_banner.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
