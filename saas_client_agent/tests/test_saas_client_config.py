# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSaaSClientConfig(TransactionCase):
    """Test SaaS Client Configuration"""

    def setUp(self):
        super(TestSaaSClientConfig, self).setUp()
        self.SaaSConfig = self.env['saas.client.config']
        
    def test_01_get_or_create_config(self):
        """Test get_config creates singleton configuration"""
        # Clear any existing config
        self.SaaSConfig.search([]).unlink()
        
        # Get config (should create new one)
        config = self.SaaSConfig.get_config()
        
        self.assertTrue(config, "Configuration should be created")
        self.assertEqual(config.user_limit, 10, "Default user limit should be 10")
        self.assertTrue(config.is_limit_enforced, "Limit enforcement should be enabled by default")
        
    def test_02_current_users_computation(self):
        """Test current users computation"""
        config = self.SaaSConfig.get_config()
        
        # Get current user count
        initial_count = config.current_users
        
        # Create a new internal user
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testuser@example.com',
            'share': False,  # Internal user
        })
        
        # Recompute and check
        config._compute_current_usage()
        self.assertEqual(
            config.current_users,
            initial_count + 1,
            "Current users should increase by 1"
        )
        
        # Clean up
        user.unlink()
        
    def test_03_usage_percentage_computation(self):
        """Test usage percentage computation"""
        config = self.SaaSConfig.get_config()
        config.write({'user_limit': 10})
        
        # Force a specific user count for testing
        config._compute_current_usage()
        current = config.current_users
        
        expected_percentage = (current / 10) * 100
        config._compute_percentages()
        
        self.assertEqual(
            config.users_percentage,
            expected_percentage,
            "Usage percentage should be calculated correctly"
        )
        
    def test_04_check_user_limit_allowed(self):
        """Test user limit check when under limit"""
        config = self.SaaSConfig.get_config()
        config.write({'user_limit': 999})  # High limit
        
        allowed, message = config.check_user_limit()
        
        self.assertTrue(allowed, "Should allow user creation when under limit")
        
    def test_05_check_user_limit_reached(self):
        """Test user limit check when at limit"""
        config = self.SaaSConfig.get_config()
        
        # Set limit equal to current users
        config._compute_current_usage()
        config.write({'user_limit': config.current_users})
        
        allowed, message = config.check_user_limit()
        
        self.assertFalse(allowed, "Should not allow user creation when at limit")
        self.assertIn("limit reached", message.lower(), "Message should mention limit reached")
        
    def test_06_limit_enforcement_disabled(self):
        """Test that limits can be disabled"""
        config = self.SaaSConfig.get_config()
        config.write({
            'is_limit_enforced': False,
            'user_limit': 0,  # Set to 0 to ensure enforcement is truly disabled
        })
        
        allowed, message = config.check_user_limit()
        
        self.assertTrue(allowed, "Should allow user creation when enforcement is disabled")
        
    def test_07_sync_action(self):
        """Test manual sync action"""
        config = self.SaaSConfig.get_config()
        config.write({
            'master_url': 'https://master.example.com',
            'master_api_key': 'test-key',
        })
        
        result = config.action_sync_with_master()
        
        self.assertEqual(
            result.get('type'),
            'ir.actions.client',
            "Sync action should return client action"
        )
