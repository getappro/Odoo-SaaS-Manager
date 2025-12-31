# 🚀 SaaS Manager - Quick Start Guide

## 5-Minute Setup (No Phase 2 implementation)

This guide helps you install and explore the SaaS Manager module structure.

### Prerequisites
- Odoo 18 installed and running
- PostgreSQL database
- Access to Odoo configuration file

### Step 1: Copy Module (30 seconds)

```bash
# Copy the saas_manager folder to your Odoo addons directory
cp -r saas_manager /path/to/odoo/addons/

# Or create a symlink
ln -s /path/to/saas_manager /path/to/odoo/addons/
```

### Step 2: Configure Odoo (1 minute)

Edit your `odoo.conf`:

```ini
[options]
# ESSENTIAL: Enable subdomain-based database routing
dbfilter = ^%h$

# Recommended settings
workers = 4
db_maxconn = 64
proxy_mode = True
```

**Important:** The `dbfilter = ^%h$` setting is critical for multi-DB routing!

### Step 3: Restart Odoo (30 seconds)

```bash
# If using systemd
sudo systemctl restart odoo

# Or if running manually
sudo service odoo restart
```

### Step 4: Install Module (2 minutes)

1. Open Odoo in your browser
2. Go to **Apps** menu
3. Click **Update Apps List**
4. Search for "SaaS Manager"
5. Click **Install**

### Step 5: Configure Base Domain (30 seconds)

After installation:

1. Go to **Settings → Technical → Parameters → System Parameters**
2. Find `saas.base_domain`
3. Change value from `example.com` to your actual domain
4. Save

### Step 6: Explore the Module (2 minutes)

Access the **SaaS Manager** main menu to explore:

#### Templates
- **Menu:** SaaS Manager → Configuration → Templates
- **What to see:** 4 pre-configured templates (Blank, Restaurant, E-commerce, Services)
- **Try:** Click on a template, view its description
- **Note:** "Create Template DB" button shows TODO Phase 2 message

#### Plans
- **Menu:** SaaS Manager → Configuration → Plans
- **What to see:** 3 subscription plans with pricing
- **Try:** Switch between List, Kanban views
- **Note:** Observe user limits, storage limits, prices

#### Instances
- **Menu:** SaaS Manager → Operations → Instances
- **What to create:** A test instance
  - Name: "Demo Instance"
  - Customer: Choose any partner
  - Subdomain: "demo-client"
  - Template: "Restaurant Template"
  - Plan: "Professional"
- **Note:** "Provision Instance" button shows TODO Phase 2 message

#### Subscriptions
- **Menu:** SaaS Manager → Operations → Subscriptions
- **What to see:** Subscription management interface
- **Try:** Create a subscription for your test instance

## What Works Now (Without Phase 2)

✅ **Fully Functional:**
- Module installation
- All menu items
- All views (form, list, kanban)
- Data creation (templates, plans, instances, subscriptions)
- Security groups (User, Manager, Administrator)
- State workflows on instances
- Search and filters
- Data validation

⏳ **Shows TODO Message (Phase 2 Required):**
- Template database creation
- Instance provisioning
- Database cloning
- Subdomain configuration
- User/storage metrics
- Actual instance access

## Explore the Code

### Key Files to Review

```bash
# Core business logic
saas_manager/models/saas_instance.py    # Provisioning orchestration
saas_manager/models/saas_template.py    # Template management
saas_manager/models/saas_plan.py        # Subscription plans

# Views (Odoo 18 compliant)
saas_manager/views/saas_instance_views.xml
saas_manager/views/saas_template_views.xml

# Security
saas_manager/security/saas_security.xml
saas_manager/security/ir.model.access.csv

# Data
saas_manager/data/saas_template_data.xml
saas_manager/data/saas_plan_data.xml
```

### Look for TODO Comments

All Phase 2 implementation points are marked with `TODO Phase 2`:

```bash
# Find all TODO items
grep -r "TODO Phase 2" saas_manager/models/
```

## Test the Module

### Create Test Data

1. **Create a customer:**
   - Contacts → Create
   - Name: "Test Company"
   - Save

2. **Create an instance:**
   - SaaS Manager → Operations → Instances → Create
   - Name: "Test Instance"
   - Customer: "Test Company"
   - Subdomain: "testcompany"
   - Template: "Restaurant Template"
   - Plan: "Professional"
   - Save

3. **Observe the computed fields:**
   - Domain: `testcompany.example.com` (auto-computed)
   - State: `draft` (initial state)

4. **Try state transitions:**
   - Click "Provision Instance" (shows TODO message)
   - Manually change state to "Active"
   - Try "Suspend" button
   - Try "Reactivate" button

### Verify Security

1. **Create test users:**
   - User with "SaaS Manager / User" group (read-only)
   - User with "SaaS Manager / Manager" group (CRUD)
   - User with "SaaS Manager / Administrator" group (full access)

2. **Test permissions:**
   - User can only read instances
   - Manager can create/edit instances but not templates
   - Admin can access everything

## Next Steps: Phase 2 Implementation

To make the module fully functional, implement these TODO functions:

### 1. Database Operations (`psycopg2`)
```python
# saas_manager/models/saas_instance.py
def _clone_template_database(self):
    # Implement PostgreSQL template cloning
    # CREATE DATABASE client1 WITH TEMPLATE template_restaurant
```

### 2. Instance Customization (`odoorpc`)
```python
def _neutralize_database(self):
    # Reset passwords, anonymize demo data
    
def _customize_instance(self):
    # Apply customer branding
    
def _create_client_admin(self):
    # Create admin user with credentials
```

### 3. Infrastructure
```python
def _configure_subdomain(self):
    # Configure DNS and reverse proxy
    # Cloudflare API, Nginx config, etc.
```

### 4. Monitoring
```python
def _compute_current_users(self):
    # Query instance database for user count
    
def _compute_storage_used(self):
    # Calculate PostgreSQL database size
```

## Troubleshooting

### Module Not Appearing in Apps
```bash
# Check module is in addons path
ls /path/to/odoo/addons/saas_manager

# Check Odoo log for errors
tail -f /var/log/odoo/odoo-server.log

# Update apps list
# Apps → Update Apps List
```

### Installation Fails
```bash
# Check Python syntax
python3 -m py_compile saas_manager/models/*.py

# Check XML syntax
python3 check_module.py

# Review Odoo logs for specific error
```

### Views Not Loading
```bash
# Check XML is valid
python3 << 'EOF'
import xml.etree.ElementTree as ET
ET.parse('saas_manager/views/saas_instance_views.xml')
print("✓ XML is valid")
EOF
```

## Documentation

- **README.md** - Complete feature documentation
- **CONFIGURATION.md** - Production setup guide
- **IMPLEMENTATION_SUMMARY.md** - Technical overview
- **This file** - Quick start for testing

## Support

For implementation help:
1. Check inline code comments (detailed TODOs)
2. Review IMPLEMENTATION_SUMMARY.md
3. See example implementations in code comments
4. Consult CONFIGURATION.md for infrastructure setup

## Success Checklist

After following this guide, you should have:

- [x] Module installed successfully
- [x] All menus accessible
- [x] Templates visible (4 items)
- [x] Plans visible (3 items)
- [x] Test instance created
- [x] Views working (list, form, kanban)
- [x] Security groups configured
- [x] Understanding of TODO Phase 2 items

**Congratulations! You've successfully set up the SaaS Manager module structure.**

Next: Implement Phase 2 functions to enable actual provisioning! 🚀
