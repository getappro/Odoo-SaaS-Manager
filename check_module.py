#!/usr/bin/env python3
"""
SaaS Manager Module Validation Script
Checks for common issues before installation
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if file exists"""
    exists = os.path.isfile(filepath)
    status = "✓" if exists else ("✗" if required else "⚠")
    print(f"{status} {filepath}")
    return exists or not required

def main():
    print("=" * 60)
    print("SaaS Manager Module Validation")
    print("=" * 60)
    
    module_path = Path("saas_manager")
    all_ok = True
    
    # Check essential files
    print("\n📁 Essential Files:")
    essential = [
        "__init__.py",
        "__manifest__.py",
    ]
    for f in essential:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check models
    print("\n🐍 Models:")
    models = [
        "models/__init__.py",
        "models/saas_template.py",
        "models/saas_plan.py",
        "models/saas_instance.py",
        "models/saas_subscription.py",
        "models/res_partner.py",
    ]
    for f in models:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check views
    print("\n📋 Views:")
    views = [
        "views/saas_template_views.xml",
        "views/saas_plan_views.xml",
        "views/saas_instance_views.xml",
        "views/saas_subscription_views.xml",
        "views/saas_dashboard_views.xml",
        "views/saas_menu.xml",
    ]
    for f in views:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check security
    print("\n🔒 Security:")
    security = [
        "security/saas_security.xml",
        "security/ir.model.access.csv",
    ]
    for f in security:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check data
    print("\n📊 Data:")
    data = [
        "data/ir_config_parameter.xml",
        "data/ir_sequence.xml",
        "data/saas_template_data.xml",
        "data/saas_plan_data.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
    ]
    for f in data:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check controllers
    print("\n🎮 Controllers:")
    controllers = [
        "controllers/__init__.py",
        "controllers/main.py",
        "controllers/portal.py",
    ]
    for f in controllers:
        if not check_file_exists(module_path / f):
            all_ok = False
    
    # Check documentation
    print("\n📚 Documentation:")
    docs = [
        "README.md",
        "CONFIGURATION.md",
    ]
    for f in docs:
        check_file_exists(module_path / f, required=False)
    
    # Summary
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ All essential files present!")
        print("Module structure is valid and ready for installation.")
        print("\n📋 Next Steps:")
        print("1. Copy module to Odoo addons directory")
        print("2. Update odoo.conf with dbfilter = ^%h$")
        print("3. Restart Odoo")
        print("4. Update Apps List")
        print("5. Install SaaS Manager module")
        return 0
    else:
        print("❌ Some required files are missing!")
        print("Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
