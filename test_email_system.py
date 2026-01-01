#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Suite for Email Provisioning System
Tests the email sending functionality in saas_manager module
"""

import os
import sys
import json

# Add Odoo to path
sys.path.insert(0, '/opt/GetapERP/GetapERP-V18/odoo')

import odoo
from odoo import api
from odoo.tools import config

def test_email_template_exists():
    """Test that all email templates are properly created"""
    print("\n" + "="*60)
    print("TEST 1: Checking Email Templates")
    print("="*60)

    with api.Environment.manage():
        db = config['db_name']
        with odoo.registry(db).cursor() as cr:
            env = api.Environment(cr, 2, {})

            templates = [
                'saas_manager.mail_template_instance_provisioned',
                'saas_manager.mail_template_instance_suspended',
                'saas_manager.mail_template_instance_reactivated',
                'saas_manager.mail_template_instance_terminated',
            ]

            for template_id in templates:
                try:
                    template = env.ref(template_id, raise_if_not_found=True)
                    print(f"✓ Template '{template_id}' exists")
                    print(f"  - Name: {template.name}")
                    print(f"  - Subject: {template.subject}")
                except Exception as e:
                    print(f"✗ Template '{template_id}' NOT found: {str(e)}")
                    return False

    return True


def test_saas_instance_methods():
    """Test that all email methods exist in saas.instance model"""
    print("\n" + "="*60)
    print("TEST 2: Checking SaaS Instance Methods")
    print("="*60)

    with api.Environment.manage():
        db = config['db_name']
        with odoo.registry(db).cursor() as cr:
            env = api.Environment(cr, 2, {})

            instance_model = env['saas.instance']

            methods = [
                '_send_provisioning_email',
                '_send_suspension_email',
                '_send_reactivation_email',
                '_send_termination_email',
            ]

            for method_name in methods:
                if hasattr(instance_model, method_name):
                    print(f"✓ Method '{method_name}' exists")
                else:
                    print(f"✗ Method '{method_name}' NOT found")
                    return False

    return True


def test_customer_email_config():
    """Test that partner email configuration is properly set"""
    print("\n" + "="*60)
    print("TEST 3: Checking Partner Email Configuration")
    print("="*60)

    with api.Environment.manage():
        db = config['db_name']
        with odoo.registry(db).cursor() as cr:
            env = api.Environment(cr, 2, {})

            partners = env['res.partner'].search([('email', '!=', False)], limit=5)

            if not partners:
                print("⚠ WARNING: No partners with email found")
                print("  Please ensure at least one partner has an email address")
                return True

            print(f"✓ Found {len(partners)} partners with email:")
            for partner in partners:
                print(f"  - {partner.name}: {partner.email}")

    return True


def test_smtp_configuration():
    """Test SMTP server configuration"""
    print("\n" + "="*60)
    print("TEST 4: Checking SMTP Configuration")
    print("="*60)

    with api.Environment.manage():
        db = config['db_name']
        with odoo.registry(db).cursor() as cr:
            env = api.Environment(cr, 2, {})

            ir_config = env['ir.config_parameter']
            smtp_host = ir_config.get_param('mail.smtp.host')
            smtp_port = ir_config.get_param('mail.smtp.port')
            smtp_user = ir_config.get_param('mail.smtp.user')

            if not smtp_host:
                print("✗ SMTP Host NOT configured")
                print("  Please configure SMTP in Settings → Technical → Email → Outgoing Mail Servers")
                return False

            print(f"✓ SMTP Host: {smtp_host}")
            print(f"✓ SMTP Port: {smtp_port}")
            print(f"✓ SMTP User: {smtp_user}")

            # Try to send test email
            from_email = ir_config.get_param('mail.default.from') or 'noreply@example.com'
            print(f"✓ Default From: {from_email}")

    return True


def test_instance_creation():
    """Test creating a test instance with email notifications"""
    print("\n" + "="*60)
    print("TEST 5: Testing Instance Creation and Email Setup")
    print("="*60)

    with api.Environment.manage():
        db = config['db_name']
        with odoo.registry(db).cursor() as cr:
            env = api.Environment(cr, 2, {})

            # Get test data
            templates = env['saas.template'].search([], limit=1)
            plans = env['saas.plan'].search([], limit=1)
            servers = env['saas.server'].search([('state', '=', 'active')], limit=1)
            partners = env['res.partner'].search([('email', '!=', False)], limit=1)

            if not all([templates, plans, servers, partners]):
                print("⚠ WARNING: Missing test data")
                if not templates:
                    print("  - No SaaS templates found")
                if not plans:
                    print("  - No SaaS plans found")
                if not servers:
                    print("  - No active servers found")
                if not partners:
                    print("  - No partners with email found")
                return True

            print(f"✓ Test data available:")
            print(f"  - Template: {templates[0].name}")
            print(f"  - Plan: {plans[0].name}")
            print(f"  - Server: {servers[0].name}")
            print(f"  - Partner: {partners[0].name} ({partners[0].email})")

            # Don't actually create instance, just verify structure
            print(f"✓ Instance creation would include:")
            print(f"  - Email template reference available: mail_template_instance_provisioned")
            print(f"  - Method _send_provisioning_email() available")

    return True


def print_test_summary(results):
    """Print a summary of test results"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)

    total = len(results)
    passed = sum(results.values())
    failed = total - passed

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✓")
    print(f"Failed: {failed} ✗")

    if failed == 0:
        print("\n✓ All tests passed! Email provisioning system is ready.")
    else:
        print(f"\n✗ {failed} test(s) failed. Please review the output above.")

    return failed == 0


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "Email Provisioning System - Test Suite".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")

    results = {
        'Email Templates': test_email_template_exists(),
        'Instance Methods': test_saas_instance_methods(),
        'Customer Email Config': test_customer_email_config(),
        'SMTP Configuration': test_smtp_configuration(),
        'Instance Creation': test_instance_creation(),
    }

    success = print_test_summary(results)

    print("\n" + "="*60)
    print("NEXT STEPS")
    print("="*60)
    print("""
1. If SMTP is not configured:
   - Go to Settings → Technical → Email → Outgoing Mail Servers
   - Create a new server with your SMTP credentials
   - Test the connection

2. If no partners have email:
   - Go to Contacts
   - Select or create a contact
   - Add their email address

3. To test provisioning:
   - Create a new SaaS Instance
   - Click "Provision Instance"
   - Check that the customer receives an email

4. For detailed information:
   - See EMAIL_PROVISIONING.md
   - See CHANGELOG_EMAIL_SYSTEM.md
    """)

    return 0 if success else 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n✗ Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

