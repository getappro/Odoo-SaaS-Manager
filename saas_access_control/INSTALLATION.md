# SaaS Access Control - Installation & Deployment Guide

## Installation Steps

### 1. Pre-requisites

```bash
# Install Python JWT library
pip install PyJWT>=2.0.0
```

### 2. Add Module to Odoo

The module is located at:
```
extra-addons/GetapPRO/saas_access_control/
```

### 3. Install via Odoo UI

1. Go to **Apps** menu
2. Remove the "Installed" filter
3. Search for "SaaS Access Control"
4. Click **Install**

Or via command line:
```bash
cd /opt/GetapERP/GetapERP-V18
./odoo-bin -u saas_access_control -d dev
```

### 4. Post-Installation Configuration

1. **Change JWT Secret Key** (CRITICAL FOR PRODUCTION)
   - Go to Settings > Configuration > SaaS Access Control
   - Update `saas_access_control.jwt_secret_key`
   - Use a strong, random value (min 32 characters)
   
   ```bash
   # Generate secure secret
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Assign Security Groups**
   - Go to Settings > Users > Select user
   - In "Other" tab, find "SaaS Access Control" section
   - Assign groups:
     - **SaaS Admin**: Full access to suspensions, sessions, logs
     - **SaaS Support**: Can create and manage support sessions

3. **Configure Log Retention** (Optional)
   - Go to Settings > Configuration > SaaS Access Control
   - Set `saas_access_control.log_retention_days`
   - Default: 90 days

### 5. Verify Installation

In Odoo terminal:
```python
# Check if models are loaded
models = env['ir.model'].search([('model', 'in', [
    'saas.suspension',
    'support.session', 
    'access.log'
])])
print(f"Installed: {len(models)} models")

# Check security groups
groups = env['res.groups'].search([('name', 'ilike', 'SaaS')])
print(f"Groups: {len(groups)}")
```

## Deployment Checklist

### Development Environment

- [ ] Module installed and tested
- [ ] JWT secret key is unique
- [ ] Test suspension workflow
- [ ] Test support session creation and token verification
- [ ] Verify access logs are created

### Staging Environment

- [ ] Change JWT secret key to production value
- [ ] Test with actual instances
- [ ] Verify middleware blocks suspended instances
- [ ] Test with multiple support users
- [ ] Verify email notifications (if configured)

### Production Environment

- [ ] **Backup database before deploying**
- [ ] Use strong JWT secret key (min 32 chars, random)
- [ ] Enable middleware in settings
- [ ] Configure log retention based on compliance needs
- [ ] Set up automated log cleanup (cron job)
- [ ] Create admin user for SaaS management
- [ ] Test end-to-end suspension and access workflows
- [ ] Document procedures for support team
- [ ] Set up monitoring for failed access attempts
- [ ] Configure backup strategy for audit logs

### Automated Log Cleanup (Optional)

Add a cron job to clean up old logs:

```python
# In a scheduled action (Settings > Automation > Scheduled Actions)

# Create new record:
name: Cleanup Old Access Logs
Model: access.log
Method: cleanup_old_logs
Interval Number: 1
Interval Type: Days
Execute Every: 90 days

# Or run manually via terminal:
env['access.log'].cleanup_old_logs(days=90)
```

## Security Hardening

### 1. JWT Secret Key Management

**Never** commit JWT secret key to version control.

```bash
# Generate from environment variable in production
export SAAS_JWT_SECRET=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# Or use a secrets management service:
# - HashiCorp Vault
# - AWS Secrets Manager
# - Azure Key Vault
```

### 2. IP Whitelisting

For sensitive instances, always use IP restrictions:

```python
session = env['support.session'].create({
    'instance_id': instance.id,
    'support_user_id': user.id,
    'reason': 'emergency',
    'allowed_ip': '203.0.113.42',  # Support office IP
    'allowed_actions': 'view',
})
```

### 3. Short Expiration for Sensitive Access

```python
# For emergency support access
session = env['support.session'].create({
    'instance_id': critical_instance.id,
    'support_user_id': user.id,
    'reason': 'emergency',
    'expires_at': fields.Datetime.now() + timedelta(hours=2),  # 2 hours only
})
```

### 4. Regular Audit Review

Schedule weekly reviews of:
- Failed access attempts
- Suspended instances
- Active support sessions
- Revoked tokens

```python
# Get failed access attempts this week
from datetime import timedelta
cutoff = datetime.now() - timedelta(days=7)

failed = env['access.log'].search([
    ('status', '!=', 'success'),
    ('timestamp', '>=', cutoff),
])
print(f"Failed access attempts: {len(failed)}")
```

## Troubleshooting

### Module Installation Issues

```bash
# Check for missing Python dependencies
python -c "import jwt"  # Should not raise ImportError

# Check module manifest
cd extra-addons/GetapPRO/saas_access_control
python -m py_compile __manifest__.py

# Check for Python syntax errors
python -m py_compile models/*.py controllers/*.py
```

### Instance Still Accessible After Suspension

**Symptom**: Instance is suspended but users can still access it

**Solutions**:
1. Check middleware is enabled: Settings > Configuration > `enable_middleware`
2. Check user is not in `group_saas_admin`
3. Verify suspension record has `state = 'active'`
4. Check browser cache and clear cookies
5. Review access logs for debugging

### JWT Token Verification Fails

**Symptom**: "Invalid token" error on support access

**Solutions**:
1. Verify both systems have same JWT secret key
2. Check token hasn't expired: `expires_at` timestamp
3. Check IP restriction if set: `allowed_ip`
4. Verify user has permission to use token
5. Check system clock is synchronized between servers

### Performance Issues

If access control checks are slow:

1. Add database index on frequently searched fields:
   ```sql
   CREATE INDEX idx_saas_suspension_instance ON saas_suspension(instance_id);
   CREATE INDEX idx_support_session_instance ON support_session(instance_id);
   CREATE INDEX idx_access_log_timestamp ON access_log(timestamp);
   ```

2. Archive old logs more frequently:
   ```python
   env['access.log'].cleanup_old_logs(days=30)  # Keep only 30 days
   ```

3. Monitor and optimize database queries:
   ```bash
   # Enable PostgreSQL query logging
   # In postgresql.conf:
   log_duration = on
   log_min_duration_statement = 1000  # Log queries > 1s
   ```

## Integration with Existing Systems

### LDAP/Active Directory

If using LDAP authentication:

```python
# Users synced via LDAP will automatically work
# Just ensure groups are mapped:
# res.groups.group_saas_admin -> AD Group: Odoo-SaaS-Admin
# res.groups.group_saas_support -> AD Group: Odoo-Support
```

### Email Notifications

If email is configured, support sessions can send notifications:

```python
# Email template will be created during installation
# Customize at: Settings > Email > Templates > "SaaS: Support Session Created"
```

### External Audit Systems

Access logs can be exported to external systems:

```python
# Example: Export to Splunk
import requests
import json

logs = env['access.log'].search([('timestamp', '>=', cutoff)])
for log in logs:
    event = {
        'timestamp': log.timestamp,
        'instance': log.instance_id.name,
        'user': log.user_id.login,
        'action': log.action,
        'ip': log.ip_address,
        'status': log.status,
    }
    requests.post('https://splunk.company.com/event', json=event)
```

## Support & Issues

For issues, check:

1. **Module logs**: Check Odoo logs for errors
2. **Database logs**: Check PostgreSQL logs for query errors
3. **Browser console**: Check for JavaScript errors
4. **Documentation**: Review README.md for usage examples

Email: support@example.com

