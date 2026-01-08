# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

"""
Tests for SaaS Client Agent
"""

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestSaasClientConfig(TransactionCase):
    """Test cases for saas.client.config model"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a test config
        self.config = self.env['saas.client.config'].create({
            'master_url': 'http://localhost:8069',
            'master_database': 'master_db',
            'user_limit': 5,
            'is_limit_enforced': True,
        })

    def test_config_creation(self):
        """Test config creation with auto-generated UUID"""
        self.assertIsNotNone(self.config)
        self.assertIsNotNone(self.config.instance_uuid)
        self.assertEqual(self.config.user_limit, 5)
        self.assertTrue(self.config.is_limit_enforced)

    def test_get_config_singleton(self):
        """Test get_config returns singleton"""
        config1 = self.env['saas.client.config'].get_config()
        config2 = self.env['saas.client.config'].get_config()
        self.assertEqual(config1.id, config2.id)

    def test_current_users_computation(self):
        """Test current users count computation"""
        # Count existing internal users
        initial_count = self.env['res.users'].search_count([
            ('active', '=', True),
            ('share', '=', False),
            ('id', '!=', 1),  # Exclude OdooBot
        ])
        
        self.assertEqual(self.config.current_users, initial_count)

    def test_users_percentage_computation(self):
        """Test usage percentage computation"""
        # Set known values
        self.config.user_limit = 10
        
        # Percentage should be calculated
        if self.config.current_users > 0:
            expected_percentage = (self.config.current_users / 10) * 100
            self.assertEqual(self.config.users_percentage, expected_percentage)

    def test_check_user_limit_allowed(self):
        """Test check_user_limit when below limit"""
        self.config.user_limit = 100  # Set high limit
        allowed, message = self.config.check_user_limit()
        self.assertTrue(allowed)
        self.assertEqual(message, "")

    def test_check_user_limit_exceeded(self):
        """Test check_user_limit when limit exceeded"""
        self.config.user_limit = 1  # Set low limit
        allowed, message = self.config.check_user_limit()
        self.assertFalse(allowed)
        self.assertIn("User limit reached", message)

    def test_check_user_limit_not_enforced(self):
        """Test check_user_limit when enforcement disabled"""
        self.config.is_limit_enforced = False
        self.config.user_limit = 1
        allowed, message = self.config.check_user_limit()
        self.assertTrue(allowed)


class TestResUsersLimit(TransactionCase):
    """Test cases for user limit enforcement in res.users"""

    def setUp(self):
        """Set up test data"""
        super().setUp()

        # Create a test config with enforcement enabled
        self.config = self.env['saas.client.config'].sudo().get_config()
        self.config.write({
            'user_limit': 100,  # Set high limit to allow test user creation
            'is_limit_enforced': True,
        })

    def test_user_creation_below_limit(self):
        """Test user creation succeeds when below limit"""
        # Set high limit
        self.config.user_limit = 100
        
        # Create a user should succeed
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test_user_limit_1',
            'email': 'test1@example.com',
        })
        
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')

    def test_user_creation_at_limit(self):
        """Test user creation fails when at limit"""
        # Set limit to current count
        current_count = self.env['res.users'].search_count([
            ('active', '=', True),
            ('share', '=', False),
            ('id', '!=', 1),
        ])
        self.config.user_limit = current_count
        
        # Try to create a user - should fail
        with self.assertRaises(ValidationError) as cm:
            self.env['res.users'].create({
                'name': 'Test User Over Limit',
                'login': 'test_user_over_limit',
                'email': 'over@example.com',
            })
        
        self.assertIn("User limit reached", str(cm.exception))

    def test_portal_user_not_counted(self):
        """Test that portal users don't count toward limit"""
        # Set limit to current count
        current_count = self.env['res.users'].search_count([
            ('active', '=', True),
            ('share', '=', False),
            ('id', '!=', 1),
        ])
        self.config.user_limit = current_count
        
        # Create a portal user should succeed
        portal_user = self.env['res.users'].create({
            'name': 'Portal User',
            'login': 'portal_user_test',
            'email': 'portal@example.com',
            'share': True,  # Portal user
        })
        
        self.assertIsNotNone(portal_user)
        self.assertTrue(portal_user.share)

    def test_enforcement_disabled(self):
        """Test user creation when enforcement is disabled"""
        self.config.is_limit_enforced = False
        self.config.user_limit = 1  # Set low limit
        
        # Create user should succeed even with low limit
        user = self.env['res.users'].create({
            'name': 'Test User No Enforcement',
            'login': 'test_user_no_enforce',
            'email': 'noenforce@example.com',
        })
        
        self.assertIsNotNone(user)
