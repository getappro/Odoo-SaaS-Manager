#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SaaS Access Control - Module Verification Script

This script verifies that the module is properly structured
and all dependencies are available.
"""

import os
import sys
import ast
from pathlib import Path

def check_file_exists(path, required=True):
    """Check if a file exists"""
    if os.path.exists(path):
        return True, f"✓ {path}"
    else:
        status = "✗" if required else "⚠"
        return not required, f"{status} {path} (MISSING)"

def check_python_syntax(filepath):
    """Check Python file syntax"""
    try:
        with open(filepath, 'r') as f:
            ast.parse(f.read())
        return True, f"✓ {filepath}"
    except SyntaxError as e:
        return False, f"✗ {filepath}: {e}"

def check_imports():
    """Check if required Python packages are available"""
    missing = []

    try:
        import jwt
    except ImportError:
        missing.append('PyJWT')

    return len(missing) == 0, missing

def main():
    """Main verification function"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    print(f"Verifying SaaS Access Control module at: {base_path}\n")

    all_ok = True

    # Check directory structure
    print("=" * 60)
    print("1. Directory Structure")
    print("=" * 60)

    required_dirs = [
        'models',
        'controllers',
        'security',
        'views',
        'data',
        'tests',
    ]

    for dir_name in required_dirs:
        dir_path = os.path.join(base_path, dir_name)
        ok, msg = check_file_exists(dir_path)
        print(msg)
        all_ok = all_ok and ok

    # Check required files
    print("\n" + "=" * 60)
    print("2. Required Files")
    print("=" * 60)

    required_files = [
        '__init__.py',
        '__manifest__.py',
        'README.md',
        'INSTALLATION.md',
        'USAGE_EXAMPLES.md',
        'DEPLOYMENT_NOTES.md',
        'models/__init__.py',
        'models/saas_suspension.py',
        'models/support_session.py',
        'models/access_logs.py',
        'models/saas_instance_access.py',
        'controllers/__init__.py',
        'controllers/access_middleware.py',
        'controllers/support_portal.py',
        'security/access_control_security.xml',
        'security/ir.model.access.csv',
        'views/saas_suspension_views.xml',
        'views/support_session_views.xml',
        'views/access_logs_views.xml',
        'views/saas_instance_extended.xml',
        'data/ir_config_parameter.xml',
        'tests/__init__.py',
        'tests/test_saas_access_control.py',
    ]

    for file_name in required_files:
        file_path = os.path.join(base_path, file_name)
        ok, msg = check_file_exists(file_path)
        print(msg)
        all_ok = all_ok and ok

    # Check Python syntax
    print("\n" + "=" * 60)
    print("3. Python Syntax Validation")
    print("=" * 60)

    python_files = [
        '__init__.py',
        '__manifest__.py',
        'models/__init__.py',
        'models/saas_suspension.py',
        'models/support_session.py',
        'models/access_logs.py',
        'models/saas_instance_access.py',
        'controllers/__init__.py',
        'controllers/access_middleware.py',
        'controllers/support_portal.py',
        'tests/__init__.py',
        'tests/test_saas_access_control.py',
    ]

    for file_name in python_files:
        file_path = os.path.join(base_path, file_name)
        if os.path.exists(file_path):
            ok, msg = check_python_syntax(file_path)
            print(msg)
            all_ok = all_ok and ok

    # Check Python dependencies
    print("\n" + "=" * 60)
    print("4. Python Dependencies")
    print("=" * 60)

    ok, missing = check_imports()
    if ok:
        print("✓ PyJWT is installed")
    else:
        print(f"✗ Missing: {', '.join(missing)}")
        print("  Install with: pip install PyJWT")
        all_ok = False

    # Check manifest
    print("\n" + "=" * 60)
    print("5. Manifest Validation")
    print("=" * 60)

    manifest_path = os.path.join(base_path, '__manifest__.py')
    try:
        with open(manifest_path, 'r') as f:
            manifest = ast.literal_eval(f.read())

        required_keys = ['name', 'version', 'category', 'author', 'depends', 'data']
        for key in required_keys:
            if key in manifest:
                print(f"✓ Manifest has '{key}'")
            else:
                print(f"✗ Manifest missing '{key}'")
                all_ok = False

        print(f"✓ Version: {manifest.get('version')}")
        print(f"✓ Dependencies: {', '.join(manifest.get('depends', []))}")
    except Exception as e:
        print(f"✗ Error reading manifest: {e}")
        all_ok = False

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    if all_ok:
        print("✓ All checks passed! Module is ready for installation.")
        return 0
    else:
        print("✗ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

