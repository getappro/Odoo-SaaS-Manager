# SaaS Access Control - Usage Examples

## Quick Start

### 1. Suspend an Instance

```python
from datetime import datetime

# Create suspension record
suspension = env['saas.suspension'].create({
    'instance_id': env['saas.instance'].browse([instance_id])[0].id,
    'reason': 'payment',  # Options: expired, payment, abuse, request, maintenance, other
    'description': 'Customer payment failed on 2026-01-01',
    'notes': 'Customer contacted support, waiting for payment resolution',
})

# Instance state automatically changes to 'suspended'
# Users can no longer access instance (except admins)
# Suspension state synced to instance via RPC
```

### 2. Resume a Suspended Instance

```python
# Find and resume suspension
suspension = env['saas.suspension'].search([
    ('instance_id', '=', instance_id),
    ('state', '=', 'active'),
], limit=1)

if suspension:
    suspension.action_resume()
    # Instance is now accessible again
    # Users can log in
    # Suspension state synced to instance
```

### 3. Create Support Session with JWT Token

```python
from datetime import datetime, timedelta

# Create support session
session = env['support.session'].create({
    'instance_id': instance_id,
    'support_user_id': env.user.id,
    'reason': 'troubleshooting',
    'description': 'Customer reported invoice module not working',
    'allowed_actions': 'view',  # Options: view, edit, full
    'allowed_ip': '192.168.1.100',  # Optional: restrict to specific IP
    'expires_at': datetime.now() + timedelta(hours=4),  # Token valid for 4 hours
})

# Share this token with support staff
token = session.jwt_token
print(f"Support token: {token}")
print(f"Expires: {session.expires_at}")
```

### 4. Verify Token from Instance

Instance-side code to verify support token:

```python
import requests

# Get token from support staff
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Verify token with master
response = requests.post(
    'http://master.example.com/support/verify-token',
    json={'token': token},
    timeout=5
)

result = response.json()
if result.get('valid'):
    payload = result['payload']
    print(f"Valid token for support user: {payload['support_user']}")
    print(f"Reason: {payload['reason']}")
    print(f"Allowed actions: {payload['allowed_actions']}")
    
    # Grant access based on payload
    if payload['allowed_actions'] == 'view':
        # Read-only access
        pass
    elif payload['allowed_actions'] == 'edit':
        # Edit access
        pass
    elif payload['allowed_actions'] == 'full':
        # Full access
        pass
else:
    print(f"Invalid token: {result.get('error')}")
```

### 5. Revoke Support Token Immediately

```python
# Find active session
session = env['support.session'].search([
    ('id', '=', session_id),
    ('state', '=', 'active'),
], limit=1)

if session:
    session.action_revoke()
    # Token is now invalid
    # Any access attempts will be denied
```

### 6. Extend Support Session Duration

```python
# Find session
session = env['support.session'].browse([session_id])

# Extend by 4 more hours
session.action_extend(hours=4)
print(f"New expiration: {session.expires_at}")
```

### 7. View Access History

```python
# Get all access logs for an instance
logs = env['access.log'].get_instance_logs(instance_id, limit=100)

for log in logs:
    print(f"{log.timestamp} | {log.user_id.name} | {log.action} | {log.status}")

# Get failed access attempts
failed = env['access.log'].get_failed_access_logs(instance_id)
for log in failed:
    print(f"FAILED: {log.timestamp} - {log.error_message}")

# Get logs for specific support session
session_logs = env['access.log'].get_session_logs(session_id)
print(f"Session {session_id} has {len(session_logs)} access logs")
```

### 8. Monitor Suspensions

```python
# Get all active suspensions
suspensions = env['saas.suspension'].search([
    ('state', '=', 'active'),
])

print(f"Total suspended instances: {len(suspensions)}")

for suspension in suspensions:
    days_suspended = (datetime.now() - suspension.suspended_date).days
    print(f"  - {suspension.instance_id.name}: {suspension.reason} ({days_suspended} days)")

# Get expiring suspensions (created more than 7 days ago)
from datetime import timedelta
cutoff = datetime.now() - timedelta(days=7)
old_suspensions = env['saas.suspension'].search([
    ('state', '=', 'active'),
    ('suspended_date', '<', cutoff),
])
print(f"Long-term suspensions ({len(old_suspensions)}): Should review")
```

### 9. Audit Trail for Compliance

```python
from datetime import datetime, timedelta

# Get all access for past month
cutoff = datetime.now() - timedelta(days=30)
logs = env['access.log'].search([
    ('timestamp', '>=', cutoff),
    ('instance_id', '=', instance_id),
])

# Generate report
by_user = {}
by_action = {}
by_status = {}

for log in logs:
    # By user
    user_key = log.user_id.login
    by_user[user_key] = by_user.get(user_key, 0) + 1
    
    # By action
    action_key = log.action
    by_action[action_key] = by_action.get(action_key, 0) + 1
    
    # By status
    status_key = log.status
    by_status[status_key] = by_status.get(status_key, 0) + 1

print("=== Access Report ===")
print("\nBy User:")
for user, count in sorted(by_user.items(), key=lambda x: x[1], reverse=True):
    print(f"  {user}: {count}")

print("\nBy Action:")
for action, count in sorted(by_action.items(), key=lambda x: x[1], reverse=True):
    print(f"  {action}: {count}")

print("\nBy Status:")
for status, count in sorted(by_status.items(), key=lambda x: x[1], reverse=True):
    print(f"  {status}: {count}")
```

### 10. Automated Suspension on Expiration

```python
from datetime import datetime, timedelta

# In a scheduled action or cron job:
# Check all active instances
instances = env['saas.instance'].search([
    ('state', '=', 'active'),
    ('expiration_date', '!=', False),
])

for instance in instances:
    if instance.expiration_date <= datetime.now():
        # Create suspension
        suspension = env['saas.suspension'].create({
            'instance_id': instance.id,
            'reason': 'expired',
            'description': f'Instance expired on {instance.expiration_date}',
        })
        print(f"Suspended: {instance.name}")
```

### 11. Send Notification on Suspension

```python
# Override to customize suspension notifications
suspension = env['saas.suspension'].create({...})

# Send notification to customer
mail_template = env.ref('saas_access_control.mail_template_suspension')
mail_template.send_mail(
    suspension.id,
    force_send=True,
    email_values={
        'email_to': suspension.instance_id.partner_id.email,
    }
)
```

### 12. Cleanup Old Logs

```python
# Remove logs older than 90 days
count = env['access.log'].cleanup_old_logs(days=90)
print(f"Deleted {count} old access logs")

# Can be scheduled as daily cron job:
# Settings > Automation > Scheduled Actions
# Add action to run cleanup_old_logs(days=90) daily
```

## Advanced Usage

### Custom Suspension Reasons

Extend the model to add custom reasons:

```python
class SaasSuspension(models.Model):
    _inherit = 'saas.suspension'
    
    reason = fields.Selection([
        # ... existing options ...
        ('custom_reason', 'Custom Reason'),
    ])
```

### Custom Access Control Rules

Extend middleware to add custom rules:

```python
class AccessMiddleware(http.Controller):
    _inherit = 'access_middleware.AccessMiddleware'
    
    def _should_block_access(self, instance):
        """Override to add custom blocking rules"""
        # Check parent class logic
        if super()._should_block_access(instance):
            return True
        
        # Add custom logic
        if instance.custom_field == 'some_value':
            return True
        
        return False
```

### Integration with Payment System

```python
# When payment fails
def payment_failure_handler(subscription):
    # Find instances for this subscription
    instances = env['saas.instance'].search([
        ('subscription_id', '=', subscription.id),
    ])
    
    for instance in instances:
        # Create suspension
        env['saas.suspension'].create({
            'instance_id': instance.id,
            'reason': 'payment',
            'description': f'Payment failed for {subscription.name}',
        })
        
        # Send notification
        instance.message_post(
            body=f"Instance suspended due to payment failure",
            message_type='notification',
        )
```

### Real-time Monitoring Dashboard

```python
# Create a custom view for monitoring
dashboard_data = {
    'total_instances': len(env['saas.instance'].search([])),
    'active_suspensions': len(env['saas.suspension'].search([('state', '=', 'active')])),
    'active_support_sessions': len(env['support.session'].search([('state', '=', 'active')])),
    'failed_access_today': len(env['access.log'].search([
        ('status', '!=', 'success'),
        ('timestamp', '>=', datetime.now().replace(hour=0, minute=0, second=0)),
    ])),
}

return dashboard_data
```

## Performance Tips

1. **Use context filtering**: Filter results before loading into memory
2. **Limit log queries**: Use `limit` parameter to avoid large result sets
3. **Index frequently searched fields**: Database indexes on instance_id, timestamp
4. **Archive old logs**: Regular cleanup keeps logs table performant
5. **Use readonly=True**: For audit logs, don't allow modifications

## Security Best Practices

1. **Always use HTTPS** for token transmission
2. **Never log passwords** in access logs
3. **Rotate JWT secret key** periodically
4. **Use IP restrictions** for sensitive instances
5. **Short expiration times** for emergency access
6. **Regular audit reviews** of access logs
7. **Immediately revoke** compromised tokens
8. **Enable two-factor authentication** for admin users

