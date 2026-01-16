# Installation Guide - SaaS Client Agent Module

Quick guide to install and configure the SaaS Client Agent module in Odoo 18.

## 📋 Prerequisites

- Odoo 18.0 installed and running
- Python 3.10 or higher
- PostgreSQL 12 or higher
- `requests` Python library
- System administrator access to Odoo

## 📦 Installation Steps

### Step 1: Copy Module to Addons

```bash
# Navigate to your Odoo addons directory
cd /path/to/odoo/addons/

# Copy the module
cp -r /path/to/saas_client_agent ./

# Verify the module is copied
ls -la saas_client_agent/
```

### Step 2: Set Correct Permissions

```bash
# Set ownership (replace 'odoo' with your Odoo user)
sudo chown -R odoo:odoo saas_client_agent/

# Set read permissions
sudo chmod -R 755 saas_client_agent/
```

### Step 3: Update Apps List

1. **Enable Developer Mode:**
   - Settings → Activate Developer Mode
   - Or append `?debug=1` to URL

2. **Update Apps List:**
   - Apps → Update Apps List
   - Click "Update" button
   - Wait for completion

### Step 4: Install Module

1. Navigate to **Apps**
2. Remove "Apps" filter
3. Search for "SaaS Client Agent"
4. Click **Install** button
5. Wait for installation to complete

## ⚙️ Initial Configuration

### Step 5: Configure Instance (System Admin Only)

1. Navigate to **SaaS Client** menu (only visible to system admins)
2. Click on **Configuration**
3. Configure the following:

   **Instance Information:**
   - Instance UUID is auto-generated ✅
   
   **Master Server Connection:**
   - Master Server URL: `https://your-master-server.com`
   - API Key: `your-api-key-here`
   
   **Subscription Limits:**
   - User Limit: `10` (adjust as needed)
   - Storage Limit (GB): `10.0` (adjust as needed)
   - ✅ Enforce Limits (checked)
   
   **Heartbeat Settings:**
   - Heartbeat Interval: `60` minutes (default)

4. Click **Save**

### Step 6: Test Manual Sync

1. In the configuration form, click **Sync with Master** button
2. Verify success notification appears
3. Check "Last Heartbeat" timestamp updates

## 🔐 User Setup

### For Regular Users (Optional)

Regular users automatically get access to:
- Settings → Subscription (view usage)
- Upgrade request button
- Usage warnings

No additional configuration needed!

### For System Administrators

System administrators automatically get:
- All regular user features
- SaaS Client menu access
- Configuration management
- Manual sync capability

## ✅ Verification

### Verify Installation

```bash
# Check module is installed
cd /path/to/odoo
./odoo-bin shell -d your_database

# In Python shell:
>>> env['ir.module.module'].search([('name', '=', 'saas_client_agent')]).state
'installed'

>>> env['saas.client.config'].search([]).ensure_one().instance_uuid
'your-instance-uuid-here'
```

### Verify Menus

**As System Admin:**
- ✅ Can see "SaaS Client" menu
- ✅ Can access Configuration

**As Regular User:**
- ❌ Cannot see "SaaS Client" menu
- ✅ Can see Settings → Subscription

### Verify User Limits

1. Navigate to Settings → Subscription
2. Check displayed usage matches actual user count
3. Try creating a user:
   - If under limit: ✅ Should succeed
   - If at limit: ❌ Should show helpful error

## 🔧 Configuration Options

### Adjusting User Limit

**Via UI (System Admin):**
1. SaaS Client → Configuration
2. Modify "User Limit" field
3. Save

**Via Code:**
```python
config = env['saas.client.config'].get_config()
config.write({'user_limit': 50})
```

### Disabling Enforcement (Emergency)

If you need to temporarily disable limit enforcement:

1. SaaS Client → Configuration
2. Uncheck "Enforce Limits"
3. Save

**Warning:** This allows unlimited user creation!

### Changing Heartbeat Interval

**Default:** 60 minutes

**To change:**
1. SaaS Client → Configuration
2. Modify "Heartbeat Interval (minutes)"
3. Save

**Recommended values:**
- Development: 5-15 minutes
- Production: 30-60 minutes

## 🐛 Troubleshooting

### Module Not Appearing in Apps List

**Problem:** Can't find module in Apps list

**Solutions:**
1. Update Apps List (Apps → Update Apps List)
2. Clear browser cache
3. Verify module is in correct addons path:
   ```bash
   odoo-bin -c /etc/odoo/odoo.conf --addons-path
   ```
4. Check Odoo logs for errors:
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

### Installation Fails

**Problem:** Installation fails with errors

**Solutions:**
1. Check dependencies are installed:
   ```bash
   pip3 install requests
   ```

2. Verify file permissions:
   ```bash
   ls -la /path/to/odoo/addons/saas_client_agent/
   ```

3. Check Odoo logs for specific error:
   ```bash
   grep -i "saas_client_agent" /var/log/odoo/odoo-server.log
   ```

4. Try manual installation:
   ```bash
   odoo-bin -d your_database -i saas_client_agent --stop-after-init
   ```

### Settings Tab Not Visible

**Problem:** Subscription tab missing in Settings

**Solutions:**
1. Clear browser cache (Ctrl+F5)
2. Upgrade module:
   - Apps → Search "SaaS Client Agent"
   - Click "Upgrade"
3. Verify view inheritance:
   ```python
   env['ir.ui.view'].search([('name', '=', 'res.config.settings.form.inherit.saas')])
   ```

### Menus Visible to Wrong Users

**Problem:** Regular users see SaaS Client menu (or vice versa)

**Solutions:**
1. Verify user groups:
   - Settings → Users & Companies → Users
   - Check user has correct groups
2. Clear cache and re-login
3. Verify menu security:
   ```python
   menu = env['ir.ui.menu'].search([('name', '=', 'SaaS Client')])
   menu.groups_id  # Should be base.group_system
   ```

### User Limit Not Working

**Problem:** Can create users beyond limit

**Solutions:**
1. Check enforcement is enabled:
   - SaaS Client → Configuration
   - "Enforce Limits" should be checked
2. Verify model override:
   ```python
   env['res.users']._name  # Should have our override
   ```
3. Check logs for errors during user creation

### Heartbeat Not Syncing

**Problem:** Last heartbeat never updates

**Solutions:**
1. Configure master server URL and API key
2. Check scheduled action is active:
   - Settings → Technical → Automation → Scheduled Actions
   - Search for heartbeat cron
   - Verify "Active" is checked
3. Manually trigger:
   ```python
   env['saas.heartbeat'].send_heartbeat()
   ```
4. Check logs:
   ```bash
   grep -i "heartbeat" /var/log/odoo/odoo-server.log
   ```

## 📊 Post-Installation Checks

Run these checks after installation:

```bash
# 1. Module installed
odoo-bin shell -d your_database -c "print(env['ir.module.module'].search([('name', '=', 'saas_client_agent')]).state)"

# 2. Configuration exists
odoo-bin shell -d your_database -c "print(env['saas.client.config'].search_count([]))"

# 3. Views loaded
odoo-bin shell -d your_database -c "print(env['ir.ui.view'].search_count([('name', 'like', 'saas')]))"

# 4. Access rights configured
odoo-bin shell -d your_database -c "print(env['ir.model.access'].search([('model_id.model', '=', 'saas.client.config')]))"
```

All commands should return valid data (not 0 or empty).

## 🚀 Next Steps

After successful installation:

1. **Configure limits** based on your subscription plan
2. **Test user creation** to verify enforcement works
3. **Set up master server connection** for sync
4. **Review documentation:**
   - [README.md](README.md) - Feature overview
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures
5. **Train users** on using Settings → Subscription

## 📞 Support

If you encounter issues not covered here:

1. Check module logs:
   ```bash
   grep -i "saas_client_agent\|saas.client" /var/log/odoo/odoo-server.log
   ```

2. Review documentation:
   - README.md
   - TESTING_GUIDE.md

3. Contact support:
   - Email: support@yourcompany.com
   - Include: Instance ID, error logs, Odoo version

---

**Last Updated:** January 2026
**Module Version:** 1.0.0
**Odoo Version:** 18.0
