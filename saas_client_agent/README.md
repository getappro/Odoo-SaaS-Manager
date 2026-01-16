# SaaS Client Agent

**Client-side module for SaaS instance management in Odoo 18**

## 🎯 Overview

This module is installed on client SaaS instances to:
- Track usage metrics (users, storage)
- Enforce subscription limits
- Communicate with master server
- Provide professional dashboard and settings interface

## 🎨 User Experience

This module uses a **hybrid approach** for optimal user experience:

### For Regular Users
- ✅ Clean, professional interface (no technical menus)
- ✅ Usage information in Settings → Subscription
- ✅ Clear warning banners when approaching limits
- ✅ Helpful error messages with actionable steps
- ✅ Easy upgrade request process

### For System Administrators
- ✅ Full technical configuration access
- ✅ Manual sync with master server
- ✅ Advanced troubleshooting tools
- ✅ Direct RPC configuration

### What Users See
- **Dashboard Widget**: Usage overview (when > 80%)
- **Settings Tab**: Subscription plan and usage details
- **Error Messages**: Professional, helpful guidance
- **Upgrade Button**: Clear path to upgrade

### What's Hidden
- Technical sync configuration
- RPC endpoints and debugging
- Master server connection details
- Low-level instance management

## ✨ Features

### 1. User Limit Enforcement
- Automatic validation when creating new users
- Professional error messages with actionable steps
- Warning notifications at 90% capacity
- Configurable enforcement (can be disabled)

### 2. Settings Integration
- Dedicated "Subscription" tab in Settings
- Real-time usage metrics display
- Progress bars with color coding (green/yellow/red)
- One-click upgrade request button
- Instance ID for support contact

### 3. Usage Monitoring
- Real-time active user count
- Storage usage tracking (planned)
- Usage percentage calculations
- Visual progress indicators

### 4. Master Server Sync
- Periodic heartbeat to master server
- Manual sync capability for admins
- Automatic usage reporting
- Configuration management

### 5. Professional UX
- Hidden technical menus from regular users
- Clear upgrade paths
- Helpful error messages
- Transparent usage information

## 📦 Installation

```bash
# 1. Copy module to Odoo addons directory
cp -r saas_client_agent /path/to/odoo/addons/

# 2. Restart Odoo
sudo systemctl restart odoo

# 3. Update Apps List (activate developer mode)
# Settings → Apps → Update Apps List

# 4. Install module
# Search for "SaaS Client Agent" and click Install
```

## ⚙️ Configuration

### Initial Setup (System Administrators Only)

1. Navigate to **SaaS Client** menu (visible only to system admins)
2. Open the configuration record
3. Configure:
   - **Master Server URL**: URL of your SaaS master server
   - **API Key**: Authentication key for master server
   - **User Limit**: Maximum number of active users
   - **Storage Limit**: Maximum storage in GB
   - **Heartbeat Interval**: Sync frequency in minutes

### For Regular Users

1. Navigate to **Settings → Subscription**
2. View your current usage and plan information
3. Click **Request Upgrade** to upgrade your plan

## 🎯 Usage

### For Users
- View subscription info: **Settings → Subscription**
- Request upgrade: **Settings → Subscription → Request Upgrade**
- See usage warnings when approaching limits
- Get helpful error messages if limit reached

### For System Administrators
- Configure instance: **SaaS Client → Configuration**
- Manual sync: Click **Sync with Master** button
- Monitor usage: View metrics in configuration form
- Adjust limits: Modify user_limit and storage_limit_gb

## 🔧 Technical Details

### Models

#### saas.client.config
Main configuration model storing:
- Instance UUID (unique identifier)
- Master server connection details
- Subscription limits (users, storage)
- Current usage metrics (computed)
- Heartbeat configuration

#### saas.heartbeat
Transient model for periodic sync with master server

#### res.users (inherited)
Extended to:
- Check user limits on creation
- Show helpful error messages
- Provide usage data for dashboard widget

#### res.config.settings (inherited)
Extended to add Subscription tab with:
- Usage metrics display
- Upgrade request action
- Instance information

### Views

#### saas_client_config_views.xml
- Configuration form and list views
- Menu structure (restricted to base.group_system)

#### res_config_settings_views.xml
- Subscription tab in Settings
- Usage progress bars
- Upgrade request button

### Frontend Assets

#### usage_banner.js
OWL component for displaying usage warnings at >= 80% capacity

#### usage_banner.xml
Template for the usage banner widget

## 🔐 Security

### Access Control
- **System Administrators** (base.group_system):
  - Full access to configuration
  - Can see SaaS Client menu
  - Can modify all settings

- **Regular Users** (base.group_user):
  - Can view usage info (read-only)
  - Can access Settings → Subscription tab
  - Can request upgrades
  - Cannot see technical menus

### Menu Visibility
All SaaS Client menus are restricted to `base.group_system` group only.

## 📊 Usage Tracking

### User Counting
- Counts only internal users (share=False)
- Includes only active users
- Real-time calculation

### Storage Tracking
- Placeholder for future implementation
- Database size calculation planned

## 🚀 Upgrade Workflow

1. User sees warning at 80% capacity (banner + notification)
2. User reaches 90% capacity (critical warning)
3. User reaches 100% capacity (cannot create users)
4. User clicks **Request Upgrade** in Settings → Subscription
5. Notification shows Instance ID and contact information
6. Administrator processes upgrade request
7. Master server updates limits
8. Client syncs new limits on next heartbeat

## 🛠️ Development

### Adding Custom Limits
To add new limit types (e.g., modules, projects):

1. Add fields to `saas.client.config`:
   ```python
   module_limit = fields.Integer(string='Module Limit', default=50)
   current_modules = fields.Integer(compute='_compute_current_usage')
   ```

2. Update `_compute_current_usage` method

3. Add to Settings view in `res_config_settings_views.xml`

### Customizing Messages
Edit error messages in `res_users.py`:
- Change support email
- Modify upgrade instructions
- Customize warning thresholds

## 📈 Monitoring

### Heartbeat Logs
Monitor heartbeat activity in Odoo logs:
```bash
tail -f /var/log/odoo/odoo-server.log | grep "Heartbeat"
```

### Usage Alerts
Warning logs are created when:
- Usage >= 90% (warning level)
- User creation is blocked

## 🐛 Troubleshooting

### Users See Technical Menus
**Problem**: Regular users can see "SaaS Client" menu

**Solution**: Ensure menus have `groups="base.group_system"` attribute

### Subscription Tab Not Visible
**Problem**: Settings → Subscription tab is missing

**Solution**: 
1. Check module is installed
2. Verify view inheritance is correct
3. Clear browser cache and refresh

### User Limit Not Enforced
**Problem**: Can create users beyond limit

**Solution**:
1. Check `is_limit_enforced` is True in configuration
2. Verify `res.users` inheritance is loaded
3. Check logs for errors

### Heartbeat Not Working
**Problem**: Last heartbeat is never updated

**Solution**:
1. Configure master server URL and API key
2. Check scheduled action is active
3. Verify network connectivity to master server

## 🔄 Updates & Migration

### Upgrading from Previous Version
1. Update module code
2. Upgrade module in Odoo (Apps → SaaS Client Agent → Upgrade)
3. Verify configuration is preserved

## 📄 License

LGPL-3 (same as Odoo)

## 🤝 Contributing

This module is part of the Odoo SaaS Manager project. Contributions are welcome:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For questions or issues:
- Review this documentation
- Check inline code comments
- Contact: support@yourcompany.com

---

**Built with ❤️ for professional SaaS management**
