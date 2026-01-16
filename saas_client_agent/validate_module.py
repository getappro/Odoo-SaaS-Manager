#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation script for saas_client_agent module
Checks that all required files are present and properly structured
"""

import os
import sys

# Required files and directories
REQUIRED_STRUCTURE = {
    'files': [
        '__init__.py',
        '__manifest__.py',
        'README.md',
        'models/__init__.py',
        'models/saas_client_config.py',
        'models/res_users.py',
        'models/res_users_dashboard.py',
        'models/res_config_settings.py',
        'models/saas_heartbeat.py',
        'security/ir.model.access.csv',
        'views/saas_client_config_views.xml',
        'views/res_config_settings_views.xml',
        'static/src/js/usage_banner.js',
        'static/src/xml/usage_banner.xml',
    ],
    'directories': [
        'models',
        'views',
        'security',
        'static',
        'static/src',
        'static/src/js',
        'static/src/xml',
    ]
}

def check_module_structure(module_path):
    """Check if all required files and directories exist"""
    
    print(f"Validating module at: {module_path}\n")
    
    errors = []
    warnings = []
    
    # Check directories
    print("📁 Checking directories...")
    for directory in REQUIRED_STRUCTURE['directories']:
        path = os.path.join(module_path, directory)
        if os.path.isdir(path):
            print(f"  ✓ {directory}")
        else:
            errors.append(f"Missing directory: {directory}")
            print(f"  ✗ {directory}")
    
    print()
    
    # Check files
    print("📄 Checking files...")
    for file in REQUIRED_STRUCTURE['files']:
        path = os.path.join(module_path, file)
        if os.path.isfile(path):
            print(f"  ✓ {file}")
        else:
            errors.append(f"Missing file: {file}")
            print(f"  ✗ {file}")
    
    print()
    
    # Print summary
    if errors:
        print("❌ VALIDATION FAILED\n")
        for error in errors:
            print(f"  • {error}")
        return False
    else:
        print("✅ VALIDATION PASSED")
        print("\nModule structure is complete and ready for installation!")
        return True

if __name__ == '__main__':
    module_path = os.path.dirname(os.path.abspath(__file__))
    success = check_module_structure(module_path)
    sys.exit(0 if success else 1)
