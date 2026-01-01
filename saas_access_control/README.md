# SaaS Access Control Module

## Overview

The SaaS Access Control module provides comprehensive management of instance suspension and secure remote support access for SaaS environments.

## Features

### 1. Instance Suspension
- **Automatic Suspension**: Suspend instances due to:
  - Subscription expiration
  - Failed payments
  - Terms of Service violations
  - Maintenance
  - User requests

- **Access Blocking**: Non-admin users cannot access suspended instances
- **Bypass for Admins**: SaaS admins can always access instances
- **Sync to Instance**: Suspension state synchronized to remote instances via RPC
- **Resume Tracking**: Track who resumed and when

### 2. Support Access Portal
- **JWT Tokens**: Generate time-limited JWT tokens for support staff
- **Token Expiration**: Default 24-hour expiration, extendable
- **IP Restrictions**: Optionally restrict tokens to specific IP addresses
- **Action Control**: Three levels of access:
  - View Only: Read-only access
  - Edit: Can modify data
  - Full: Unrestricted access
- **Token Revocation**: Immediately revoke compromised tokens

### 3. Audit & Compliance
- **Access Logs**: Log all access attempts with:
  - User identification
  - Timestamp
  - IP address
  - Action type
  - Status (success/failed/denied)
  - Error details
- **Session Tracking**: Track support session usage
- **Log Retention**: Automatic cleanup of old logs (configurable)

## Models

### saas.suspension
Manages instance suspension lifecycle.

**Key Fields:**
- `instance_id`: The suspended instance
- `reason`: Reason for suspension (expired, payment, abuse, etc.)
- `description`: Detailed description
- `suspended_date`: When suspension started
- `resumed_date`: When suspension was lifted
- `state`: Active or Resolved
- `created_by_id`: Admin who created suspension
- `resumed_by_id`: Admin who resumed instance

**Key Methods:**
- `action_resume()`: Resume a suspended instance
- `_sync_suspension_state_to_instance()`: Sync state to remote instance

### support.session
Manages temporary support access sessions.

**Key Fields:**
- `instance_id`: Instance being supported
- `support_user_id`: Support staff member
- `reason`: Why support is needed (troubleshooting, maintenance, etc.)
- `jwt_token`: Generated JWT token (read-only for admins)
- `expires_at`: Token expiration time
- `allowed_actions`: Level of access (view, edit, full)
- `allowed_ip`: Optional IP restriction
- `access_count`: Number of times token was used
- `state`: Active, Expired, or Revoked

**Key Methods:**
- `create()`: Create session and generate JWT token
- `verify_token()`: Verify JWT token validity
- `action_revoke()`: Immediately revoke token
- `action_extend()`: Extend token expiration
- `log_access()`: Log token usage

### access.log
Audit trail for all access events.

**Key Fields:**
- `instance_id`: Affected instance
- `session_id`: Related support session (if applicable)
- `user_id`: User performing action
- `action`: Type of action (access, login, create, write, delete, etc.)
- `timestamp`: When action occurred
- `ip_address`: IP address of requester
- `status`: Success, failed, or denied
- `error_message`: Any error details

**Key Methods:**
- `get_instance_logs()`: Get logs for specific instance
- `get_user_logs()`: Get logs for specific user
- `get_session_logs()`: Get logs for specific support session
- `get_failed_access_logs()`: Get failed access attempts
- `cleanup_old_logs()`: Remove logs older than N days

## Controllers

### AccessMiddleware
Intercepts requests and checks suspension status.

**Routes:**
- `POST /web`: Checks if instance is suspended
- `POST /jsonrpc`: Checks suspension for JSON-RPC calls

**Behavior:**
- Allows access if instance is not suspended
- Allows admins to always access
- Returns 403 with suspension details for regular users

### SupportPortal
Provides secure support access APIs.

**Routes:**
- `GET /support/portal`: Support portal landing page
- `POST /support/verify-token`: Verify JWT token (called by instances)
- `POST /support/request-access`: Request support access
- `GET /support/access-list`: Get user's support sessions
- `POST /support/revoke-session/<id>`: Revoke a session
- `GET /support/access-logs/<instance_id>`: Get access logs

## Security Groups

- **group_saas_admin**: Full access to all features
- **group_saas_support**: Can create and manage support sessions

## Configuration

### Settings (ir.config_parameter)
- `saas_access_control.jwt_secret_key`: Secret key for JWT signing (CHANGE IN PRODUCTION!)
- `saas_access_control.session_duration_hours`: Default support session duration (default: 24)
- `saas_access_control.log_retention_days`: How long to keep logs (default: 90)
- `saas_access_control.enable_middleware`: Enable access middleware (default: True)

## Usage Examples

### Suspending an Instance
```python
from datetime import datetime

suspension = env['saas.suspension'].create({
    'instance_id': instance.id,
    'reason': 'payment',
    'description': 'Payment failed on 2026-01-01',
})
```

### Creating Support Session
```python
session = env['support.session'].create({
    'instance_id': instance.id,
    'support_user_id': user.id,
    'reason': 'troubleshooting',
    'description': 'Customer reported login issues',
    'allowed_actions': 'view',
    'allowed_ip': '192.168.1.100',
})
# session.jwt_token contains the token to share
```

### Verifying Token (from instance)
```python
import requests

response = requests.post(
    'http://master.example.com/support/verify-token',
    json={'token': jwt_token}
)
# Returns {
#     'valid': True/False,
#     'payload': {...} or 'error': 'message'
# }
```

### Getting Access Logs
```python
logs = env['access.log'].get_instance_logs(instance.id, limit=100)
for log in logs:
    print(f"{log.timestamp} - {log.user_id.name} - {log.action} - {log.status}")
```

## Integration with saas_manager

The module extends saas_manager with:

1. **Instance Suspension** on saas.instance:
   - When instance reaches expiration, admin can create suspension
   - Suspension blocks regular user access
   - Admin can resume at any time

2. **Support Access** from master:
   - Master admin creates support session
   - JWT token shared with support staff
   - Support staff accesses instance with token
   - All access logged for compliance

3. **RPC Synchronization**:
   - Suspension state synced to instance via RPC
   - Instance-side middleware can also block access
   - Dual-layer protection

## Installation

1. Install module in Odoo
2. Change JWT secret key in settings (Settings > Configuration)
3. Configure log retention if needed
4. Assign groups to users:
   - Assign `saas_access_control.group_saas_admin` to administrators
   - Assign `saas_access_control.group_saas_support` to support staff

## Best Practices

### Security
1. **Change JWT Secret**: Update `saas_access_control.jwt_secret_key` in production
2. **IP Restrictions**: Use IP restrictions for critical instances
3. **Short Expiration**: Use shorter expiration for sensitive access (e.g., 4 hours)
4. **Monitor Logs**: Regularly review access logs for suspicious activity
5. **Token Rotation**: Don't reuse tokens across sessions

### Operations
1. **Document Suspensions**: Always add detailed description when suspending
2. **Audit Trail**: Keep logs for minimum 90 days
3. **Session Review**: Review support sessions periodically
4. **Revoke Promptly**: Revoke support tokens immediately when not needed

## Troubleshooting

### Instance still accessible after suspension
- Check if user is in `group_saas_admin`
- Verify suspension record has `state = 'active'`
- Check middleware is enabled in settings

### Token verification fails
- Verify JWT secret key matches on both servers
- Check token hasn't expired
- Verify IP if restriction is set

### Access logs not appearing
- Check `saas_access_control.enable_middleware` is True
- Verify access log creation isn't failing (check logs)
- Check log retention period hasn't removed them

## Future Enhancements

- Rate limiting on failed access attempts
- Two-factor authentication for support access
- Biometric/hardware key support
- Advanced audit reporting
- Integration with external identity providers
- Scheduled suspension/resume

## Support

For issues or questions, contact support@example.com

