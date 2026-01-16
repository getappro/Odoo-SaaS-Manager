# -*- coding: utf-8 -*-
from odoo.tests import TransactionCase, tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestUserLimitEnforcement(TransactionCase):
    """Test user limit enforcement"""

    def setUp(self):
        super(TestUserLimitEnforcement, self).setUp()
        self.SaaSConfig = self.env['saas.client.config']
        self.Users = self.env['res.users']
        
        # Setup test configuration
        self.config = self.SaaSConfig.get_config()
        
    def test_01_user_creation_allowed_under_limit(self):
        """Test user creation is allowed when under limit"""
        # Set high limit
        self.config.write({'user_limit': 999, 'is_limit_enforced': True})
        
        # Should not raise exception
        user = self.Users.create({
            'name': 'Test User Under Limit',
            'login': 'testunderlimit@example.com',
            'share': False,
        })
        
        self.assertTrue(user, "User should be created successfully")
        user.unlink()
        
    def test_02_user_creation_blocked_at_limit(self):
        """Test user creation is blocked when at limit"""
        # Set limit to current users
        self.config._compute_current_usage()
        self.config.write({
            'user_limit': self.config.current_users,
            'is_limit_enforced': True,
        })
        
        # Should raise ValidationError
        with self.assertRaises(
            ValidationError,
            msg="Should raise ValidationError when at user limit"
        ):
            self.Users.create({
                'name': 'Test User Over Limit',
                'login': 'testoverlimit@example.com',
                'share': False,
            })
            
    def test_03_portal_user_not_counted(self):
        """Test that portal users (share=True) don't count toward limit"""
        # Set limit to current users
        self.config._compute_current_usage()
        initial_count = self.config.current_users
        self.config.write({
            'user_limit': initial_count,
            'is_limit_enforced': True,
        })
        
        # Should not raise exception for portal user
        portal_user = self.Users.create({
            'name': 'Portal User',
            'login': 'portaluser@example.com',
            'share': True,  # Portal user
        })
        
        self.assertTrue(portal_user, "Portal user should be created successfully")
        
        # Verify count hasn't changed
        self.config._compute_current_usage()
        self.assertEqual(
            self.config.current_users,
            initial_count,
            "Portal users should not be counted"
        )
        
        portal_user.unlink()
        
    def test_04_limit_enforcement_can_be_disabled(self):
        """Test that limit enforcement can be disabled"""
        # Set limit to current users but disable enforcement
        self.config._compute_current_usage()
        self.config.write({
            'user_limit': self.config.current_users,
            'is_limit_enforced': False,
        })
        
        # Should not raise exception even though at limit
        user = self.Users.create({
            'name': 'Test User No Enforcement',
            'login': 'testnoenforce@example.com',
            'share': False,
        })
        
        self.assertTrue(user, "User should be created when enforcement is disabled")
        user.unlink()
        
    def test_05_error_message_contains_helpful_info(self):
        """Test that error message contains helpful information"""
        # Set limit to current users
        self.config._compute_current_usage()
        self.config.write({
            'user_limit': self.config.current_users,
            'is_limit_enforced': True,
        })
        
        # Try to create user and catch exception
        try:
            self.Users.create({
                'name': 'Test User',
                'login': 'testuser@example.com',
                'share': False,
            })
            self.fail("Should have raised ValidationError")
        except ValidationError as e:
            error_msg = str(e)
            
            # Check that error message contains helpful information
            self.assertIn('User Limit Reached', error_msg, "Should mention limit reached")
            self.assertIn('Upgrade', error_msg, "Should mention upgrade option")
            self.assertIn('Instance ID', error_msg, "Should include Instance ID")
            self.assertIn(self.config.instance_uuid, error_msg, "Should include actual UUID")
