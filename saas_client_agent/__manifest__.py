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
        
        Lightweight agent installed in SaaS client instances.
        
        Features:
        * Receive and enforce user limits from master
        * Block user creation when limit reached
        * Report usage metrics to master
        * Local configuration storage
        * Periodic heartbeat sync
        
        This module is installed in CLIENT instances, not the master.
    ''',
    'author': 'Your Company',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'data': [
        'security/saas_client_security.xml',
        'security/ir.model.access.csv',
        'data/ir_config_parameter.xml',
        'data/ir_cron_data.xml',
        'views/saas_client_config_views.xml',
        'views/res_users_warning.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
