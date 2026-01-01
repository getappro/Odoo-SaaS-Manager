# SaaS Access Control - Deployment Notes

**Date**: January 1, 2026  
**Version**: 18.0.1.0.0  
**Status**: Ready for Testing

## Module Structure

```
saas_access_control/
├── __init__.py                          # Package initialization
├── __manifest__.py                      # Module metadata
├── README.md                            # User documentation
├── INSTALLATION.md                      # Installation guide
├── USAGE_EXAMPLES.md                    # Usage examples
├── DEPLOYMENT_NOTES.md                  # This file
│
├── models/
│   ├── __init__.py
│   ├── saas_suspension.py               # Instance suspension management
│   ├── support_session.py               # Support access sessions & JWT
│   ├── access_logs.py                   # Audit logging
│   └── saas_instance_access.py          # Instance extension
│
├── controllers/
│   ├── __init__.py
│   ├── access_middleware.py             # Request interception & blocking
│   └── support_portal.py                # Support access API
│
├── security/
│   ├── access_control_security.xml      # Security rules
│   └── ir.model.access.csv              # Model access control
│
├── views/
│   ├── saas_suspension_views.xml        # All view definitions
│   ├── support_session_views.xml        # Placeholder
│   ├── access_logs_views.xml            # Placeholder
│   └── saas_instance_extended.xml       # Instance form extension
│
├── data/
│   └── ir_config_parameter.xml          # Default configuration
│
└── tests/
    ├── __init__.py
    └── test_saas_access_control.py      # Unit tests
```

## Key Features Implemented

### 1. Instance Suspension
- [x] Create suspension records with reason and description
- [x] Automatic state synchronization to suspended/resumed
- [x] RPC sync to remote instances
- [x] Admin bypass for access
- [x] User-friendly suspension page (HTML response)
- [x] Resume tracking (who and when)

### 2. Support Access Portal
- [x] JWT token generation with configurable expiration
- [x] Token verification endpoint for instances
- [x] Support session creation with reasons
- [x] Three levels of access control (view/edit/full)
- [x] Optional IP restriction per token
- [x] Token revocation capability
- [x] Session extension
- [x] Access counting

### 3. Audit & Logging
- [x] Comprehensive access log model
- [x] Log creation on all access types
- [x] Failed access tracking
- [x] IP address logging
- [x] Automatic log cleanup by age
- [x] Query helpers for compliance reporting

### 4. Security & Access Control
- [x] Two security groups (admin/support)
- [x] Row-level access rules
- [x] Model-level permissions
- [x] Middleware for HTTP request interception
- [x] Middleware for JSON-RPC interception

## Dependencies

### Python Packages
- `PyJWT>=2.0.0` - For JWT token generation and verification

### Odoo Modules
- `base` - Core Odoo functionality
- `web` - Web interface
- `mail` - Email support
- `saas_manager` - Main SaaS module

## Testing Checklist

### Unit Tests
- [ ] Run test suite: `./odoo-bin -u saas_access_control -d dev --test-enable`
- [ ] All tests pass
- [ ] No SQL errors
- [ ] No Python errors

### Functional Tests
- [ ] Create suspension, verify instance is inaccessible
- [ ] Create support session, get JWT token
- [ ] Verify JWT token in another instance
- [ ] Revoke token, verify access denied
- [ ] Resume suspension, verify instance is accessible
- [ ] Check access logs are created for all actions
- [ ] View suspension and access log reports

### Security Tests
- [ ] Non-admin user cannot access suspended instance
- [ ] Admin user can always access
- [ ] Invalid JWT token is rejected
- [ ] Expired JWT token is rejected
- [ ] IP restricted token is enforced
- [ ] Failed access is logged with error details
- [ ] Logs cannot be modified (readonly)

### Performance Tests
- [ ] Suspension check doesn't timeout
- [ ] JWT verification is fast (<100ms)
- [ ] Access log queries return in <1s
- [ ] Cleanup of old logs completes quickly

## Known Limitations

1. **Instance-side component not included**
   - This module handles master-side suspension and access control
   - Instance-side middleware must be implemented separately
   - Instance calls `/support/verify-token` endpoint for JWT validation

2. **Email templates not created**
   - Suspension notification emails must be configured manually
   - Create mail templates in Settings > Email > Templates

3. **No built-in 2FA**
   - JWT tokens are the only authentication factor
   - Implement 2FA separately if needed

4. **Synchronous RPC calls**
   - Suspension state synced via RPC to instances
   - If instance is unreachable, sync fails (but continues)
   - Async sync via message queue recommended for production

## Migration Path

If migrating from previous access control system:

```python
# Map old suspension records to new format
old_suspensions = env['old.suspension'].search([])
for old in old_suspensions:
    env['saas.suspension'].create({
        'instance_id': old.instance_id.id,
        'reason': old.type or 'other',
        'description': old.notes,
        'suspended_date': old.created_date,
        'state': 'active' if old.is_active else 'resolved',
    })
```

## Production Deployment Steps

1. **Backup Database**
   ```bash
   pg_dump -U odoo dev > /backups/dev-$(date +%Y%m%d).sql
   ```

2. **Install Module**
   ```bash
   cd /opt/GetapERP/GetapERP-V18
   ./odoo-bin -u saas_access_control -d dev --no-http
   ```

3. **Change Configuration** (CRITICAL)
   - Update JWT secret key
   - Configure email settings
   - Set log retention period

4. **Assign Security Groups**
   - Add users to appropriate groups
   - Test with test user

5. **Enable Middleware** (if not already)
   - Settings > Configuration > Enable Middleware

6. **Test End-to-End**
   - Create test suspension
   - Verify instance is blocked
   - Resume and verify access restored
   - Test support session workflow

7. **Monitor**
   - Watch logs for errors
   - Monitor access log growth
   - Review failed access attempts

8. **Document**
   - Update runbooks
   - Train support team
   - Create escalation procedures

## Rollback Plan

If issues occur:

1. **Stop Odoo**
   ```bash
   sudo systemctl stop odoo
   ```

2. **Restore Database**
   ```bash
   psql -U odoo < /backups/dev-20260101.sql
   ```

3. **Uninstall Module**
   ```bash
   cd /opt/GetapERP/GetapERP-V18
   ./odoo-bin -d dev --stop-after-init
   # Manually remove saas_access_control from installed modules
   ```

4. **Restart Odoo**
   ```bash
   sudo systemctl start odoo
   ```

## Monitoring & Maintenance

### Daily Tasks
- [ ] Monitor failed access attempts
- [ ] Check for errors in logs
- [ ] Verify suspensions are working

### Weekly Tasks
- [ ] Review access logs for compliance
- [ ] Check active support sessions
- [ ] Audit user group assignments

### Monthly Tasks
- [ ] Cleanup old logs
- [ ] Review suspension history
- [ ] Audit JWT token usage
- [ ] Review security group membership

### Quarterly Tasks
- [ ] Rotate JWT secret key
- [ ] Review and update access policies
- [ ] Assess need for additional features

## Support Contacts

- **Technical Issues**: dev-team@company.com
- **Security Issues**: security@company.com
- **Access Control Audit**: compliance@company.com

## Version History

### v18.0.1.0.0 (2026-01-01)
- Initial release
- Suspension management
- Support access portal
- Audit logging
- Middleware integration
- JWT token support

### Planned for v18.0.2.0.0
- Email notification templates
- Advanced reporting views
- Scheduled suspension/resume
- Rate limiting on failed access
- Two-factor authentication

## Appendix: Configuration Reference

### JWT Secret Key
```xml
<record id="saas_access_control_jwt_secret" model="ir.config_parameter">
    <field name="key">saas_access_control.jwt_secret_key</field>
    <field name="value">your-secret-key-here</field>
</record>
```

### Support Session Duration
```xml
<record id="saas_access_control_session_duration" model="ir.config_parameter">
    <field name="key">saas_access_control.session_duration_hours</field>
    <field name="value">24</field>  <!-- Default: 24 hours -->
</record>
```

### Log Retention
```xml
<record id="saas_access_control_log_retention" model="ir.config_parameter">
    <field name="key">saas_access_control.log_retention_days</field>
    <field name="value">90</field>  <!-- Keep 90 days of logs -->
</record>
```

### Enable Middleware
```xml
<record id="saas_access_control_enable_middleware" model="ir.config_parameter">
    <field name="key">saas_access_control.enable_middleware</field>
    <field name="value">True</field>
</record>
```

## Quick Links

- README.md - User documentation
- INSTALLATION.md - Installation & deployment guide
- USAGE_EXAMPLES.md - Code examples and best practices
- models/*.py - Model definitions
- controllers/*.py - API endpoints

