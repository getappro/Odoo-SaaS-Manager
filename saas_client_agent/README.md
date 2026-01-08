# SaaS Client Agent

Lightweight agent installed in SaaS client instances to receive and enforce commands from the master `saas_manager`.

## Features

### Phase 1: User Limit Enforcement
- ✅ Receive user limits from master via RPC
- ✅ Enforce user creation limits locally
- ✅ Report current user count back to master
- ✅ Store configuration locally (no constant master dependency)
- ✅ Periodic heartbeat sync with master

## Installation

### In Client Instance

1. Install the module:
```bash
# Option 1: Via UI
# Apps → Search "SaaS Client Agent" → Install

# Option 2: Via command line
odoo-bin -d your_database -i saas_client_agent
```

2. Configure the agent:
```python
# Access: Settings → SaaS Client → Configuration

# Or via Python:
config = env['saas.client.config'].get_config()
config.write({
    'master_url': 'http://master.example.com:8069',
    'master_database': 'master_db',
    'user_limit': 10,  # This will be synced from master
})

# Trigger initial sync
config.action_sync_with_master()
```

## Configuration

### System Parameters

Configure in `Settings → Technical → Parameters → System Parameters`:

- `saas_client.master_url`: URL of the master SaaS manager
- `saas_client.master_database`: Database name of the master

### Configuration Fields

| Field | Type | Description |
|-------|------|-------------|
| `instance_uuid` | Char | Unique identifier for this instance (auto-generated) |
| `master_url` | Char | Master server URL (e.g., http://master.example.com:8069) |
| `master_database` | Char | Master database name |
| `user_limit` | Integer | Maximum number of active users allowed |
| `current_users` | Integer | Number of currently active users (computed) |
| `users_percentage` | Float | Percentage of user limit used (computed) |
| `is_limit_enforced` | Boolean | Whether to block user creation when limit is reached |
| `last_sync_date` | Datetime | Last successful sync with master server |
| `sync_status` | Selection | Sync status (success/warning/error/never) |

## RPC API Reference

The client agent exposes the following JSON-RPC endpoints for the master server:

### 1. Set User Limit

**Endpoint:** `/saas/set_user_limit`

**Method:** POST (JSON-RPC)

**Parameters:**
- `instance_uuid` (string): Unique identifier of instance
- `user_limit` (integer): New user limit value

**Returns:**
```json
{
    "success": true,
    "user_limit": 10,
    "current_users": 5,
    "users_percentage": 50.0
}
```

**Example:**
```python
import requests

response = requests.post(
    "http://client.example.com:8069/saas/set_user_limit",
    json={
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "instance_uuid": "abc-123-def-456",
            "user_limit": 10
        },
        "id": 1
    }
)
```

### 2. Get Users Count

**Endpoint:** `/saas/get_users_count`

**Method:** POST (JSON-RPC)

**Parameters:**
- `instance_uuid` (string): Unique identifier of instance

**Returns:**
```json
{
    "success": true,
    "current_users": 5,
    "user_limit": 10,
    "users_percentage": 50.0,
    "is_limit_enforced": true
}
```

### 3. Get Status

**Endpoint:** `/saas/get_status`

**Method:** POST (JSON-RPC)

**Parameters:**
- `instance_uuid` (string): Unique identifier of instance

**Returns:**
```json
{
    "success": true,
    "instance_uuid": "abc-123-def-456",
    "current_users": 5,
    "user_limit": 10,
    "users_percentage": 50.0,
    "last_sync_date": "2024-01-15T10:30:00",
    "sync_status": "success",
    "is_limit_enforced": true
}
```

## User Limit Enforcement

### How It Works

1. When a new internal user is created, the system checks the current user count
2. If the count would exceed the limit, user creation is blocked with a clear error message
3. Portal users (share=True) are NOT counted toward the limit
4. OdooBot (user ID 1) is excluded from the count

### Error Messages

When limit is reached:
```
User limit reached (10/10). Please contact your administrator to upgrade your plan.
```

### Warnings

When approaching limit (≥80%):
```
Approaching user limit: 8/10 users (80.0%)
```

## Periodic Sync

The module includes a cron job that syncs with the master server every hour:

- **Cron Name:** SaaS Client: Sync with Master
- **Frequency:** Every 1 hour
- **Action:** `model.cron_sync_with_master()`

You can manually trigger a sync:
```python
config = env['saas.client.config'].get_config()
config.action_sync_with_master()
```

## Troubleshooting

### Sync Errors

**Problem:** "Master URL or database not configured"

**Solution:** Configure the master URL and database:
```python
config = env['saas.client.config'].get_config()
config.write({
    'master_url': 'http://master.example.com:8069',
    'master_database': 'master_db',
})
```

**Problem:** HTTP connection errors

**Solution:** 
- Verify master server is accessible from client instance
- Check firewall rules
- Verify master URL is correct
- Check network connectivity

### User Creation Blocked

**Problem:** Cannot create users even when below limit

**Solution:** 
1. Check if limit enforcement is enabled:
```python
config = env['saas.client.config'].get_config()
print(config.is_limit_enforced)  # Should be True
```

2. Check current user count:
```python
print(config.current_users, config.user_limit)
```

3. Temporarily disable enforcement (not recommended):
```python
config.is_limit_enforced = False
```

### Portal Users Counted

**Problem:** Portal users are being counted toward limit

**Solution:** This is a bug. Portal users (share=True) should NOT be counted. Check the code in `res_users.py`:
```python
active_users = self.env['res.users'].search_count([
    ('active', '=', True),
    ('share', '=', False),  # This excludes portal users
    ('id', '!=', 1),  # This excludes OdooBot
])
```

## Integration with saas_manager

The master `saas_manager` module can communicate with client instances using the RPC API.

See the `saas_manager` module documentation for details on:
- Sending user limits to instances
- Fetching current user counts
- Monitoring instance health

## Security

- The RPC endpoints use `auth='public'` to allow master-to-client communication
- Access rights are controlled via `saas.client.config` model permissions
- In production, consider implementing:
  - API key authentication
  - IP whitelist for master server
  - Rate limiting

## Future Enhancements

### Phase 2: Suspension
- Middleware to block all access when suspended
- Suspension status API
- Custom suspension page

### Phase 3: Storage Limits
- Monitor database size
- Block attachment uploads when limit reached

### Phase 4: Metrics & Monitoring
- Send CPU/RAM/disk metrics to master
- Heartbeat for instance health
- Performance tracking

## License

LGPL-3

## Author

Your Company - https://www.example.com
