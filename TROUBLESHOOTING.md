# 🔧 SaaS Manager Troubleshooting Guide

## 🎯 Overview

This guide covers common issues with the SaaS Manager module, particularly focusing on RPC-based template creation.

---

## ✅ NEW: RPC-Based Template Creation (No More Subprocess Issues!)

**Good News:** The module now uses Odoo's JSON-RPC API instead of subprocess calls. This eliminates most environment and dependency issues.

**If you're experiencing the old "ModuleNotFoundError: No module named 'reportlab'" error, upgrade to the RPC-based implementation.**

---

## 🔥 Common RPC Issues

### Issue 1: "Failed to connect to Odoo RPC endpoint"

**Symptom:**
```
UserError: Failed to connect to Odoo RPC endpoint.

URL: http://localhost:8069

Error: HTTPConnectionPool(host='localhost', port=8069): Max retries exceeded
```

**Causes:**
1. Odoo is not running
2. Wrong `web.base.url` configured
3. Firewall blocking connection
4. Network issues

**Solutions:**

**1. Verify Odoo is Running:**
```bash
sudo systemctl status odoo
# or
ps aux | grep odoo-bin
```

**2. Check web.base.url Parameter:**
```bash
cd /path/to/odoo
./odoo-bin shell -d your_database

>>> env['ir.config_parameter'].get_param('web.base.url')
'http://localhost:8069'  # Should return this or your actual URL
```

**3. Test RPC Endpoint:**
```bash
curl -I http://localhost:8069/jsonrpc
# Should return: HTTP/1.1 200 OK
```

**4. Check Firewall:**
```bash
sudo ufw status
# Ensure port 8069 is allowed
```

---

### Issue 2: "RPC Error while creating database"

**Symptom:**
```
UserError: RPC Error while creating database.

Error: FATAL: password authentication failed for user "odoo"
# or
Error: database "template_restaurant" already exists
```

**Causes:**
1. Incorrect master password (`admin_passwd`)
2. Database already exists
3. PostgreSQL permission issues

**Solutions:**

**1. Verify Master Password:**
```bash
grep admin_passwd /etc/odoo/odoo.conf
# Should show: admin_passwd = your_password
```

**2. Check if Database Exists:**
```bash
sudo -u postgres psql -c "\l" | grep template_
# Lists all template databases
```

**3. Drop Existing Database (if needed):**
```bash
sudo -u postgres psql
DROP DATABASE template_restaurant;
\q
```

**4. Verify PostgreSQL Permissions:**
```bash
sudo -u postgres psql
\du odoo
# Should show: CREATEDB permission
```

---

### Issue 3: "Authentication failed via RPC"

**Symptom:**
```
UserError: Authentication failed via RPC.

Error: Login failed
```

**Causes:**
1. Wrong admin credentials (default: admin/admin)
2. Admin user doesn't exist in new database
3. Database not initialized properly

**Solutions:**

**1. Try Default Credentials:**
```bash
# For newly created databases, default is:
# Login: admin
# Password: admin

# Test login via web:
http://localhost:8069/web?db=template_restaurant
```

**2. Reset Admin Password:**
```bash
cd /path/to/odoo
./odoo-bin shell -d template_restaurant

>>> admin_user = env['res.users'].search([('login', '=', 'admin')], limit=1)
>>> admin_user.password = 'admin'
>>> env.cr.commit()
```

**3. Check User Exists:**
```bash
sudo -u postgres psql template_restaurant
SELECT login, active FROM res_users WHERE login = 'admin';
```

---

### Issue 4: "Module not found" during Installation

**Symptom:**
```
WARNING: Module mail not found
WARNING: Module portal not found
```

**Causes:**
1. Modules not in addons path
2. Apps list not updated
3. Typo in module name

**Solutions:**

**1. Update Apps List:**
```bash
cd /path/to/odoo
./odoo-bin shell -d template_restaurant

>>> env['ir.module.module'].update_list()
>>> env.cr.commit()
```

**2. Verify Module Exists:**
```bash
find /path/to/odoo/addons -name "__manifest__.py" -path "*/mail/*"
```

**3. Check Addons Path:**
```bash
grep addons_path /etc/odoo/odoo.conf
# Should include path to Odoo standard addons
```

---

### Issue 5: "Timeout during module installation"

**Symptom:**
```
ReadTimeout: HTTPSConnectionPool: Read timed out
```

**Causes:**
1. Module installation takes longer than timeout (600s)
2. Server under heavy load
3. Network issues

**Solutions:**

**1. Install Fewer Modules:**
```python
# Instead of installing all at once:
modules_to_install = ['base', 'web']  # Start with basics
template._install_modules_via_rpc(base_url, db_name, modules_to_install)

# Then install others:
modules_to_install = ['mail', 'portal']
template._install_modules_via_rpc(base_url, db_name, modules_to_install)
```

**2. Check Odoo Logs:**
```bash
tail -f /var/log/odoo/odoo-server.log
# Look for module installation progress
```

**3. Increase System Resources:**
- Add more RAM
- Use faster disk (SSD)
- Reduce other server load

---

## 🔧 Configuration Issues

### Issue 6: Missing `web.base.url` Parameter

**Symptom:**
Template creation starts but uses wrong URL or fails silently.

**Solution:**
```bash
cd /path/to/odoo
./odoo-bin shell -d your_main_db

>>> env['ir.config_parameter'].sudo().set_param('web.base.url', 'http://localhost:8069')
>>> env.cr.commit()
```

---

### Issue 7: Missing or Weak `admin_passwd`

**Symptom:**
RPC calls fail with "Access Denied" or authentication errors.

**Solution:**
```bash
# Edit odoo.conf
sudo nano /etc/odoo/odoo.conf

# Add or update:
admin_passwd = your_strong_password_here

# Restart Odoo
sudo systemctl restart odoo
```

**Generate Strong Password:**
```bash
openssl rand -base64 32
```

---

## 📚 Legacy Issues (Pre-RPC Implementation)

### ❌ DEPRECATED: "ModuleNotFoundError: No module named 'reportlab'"

**This issue no longer exists with RPC implementation.**

If you're still experiencing this, you're using an old version. Upgrade to the RPC-based implementation.

<details>
<summary>Click to see legacy solution (not recommended)</summary>
```

The subprocess-based approach had issues with:
- Python environment isolation
- Module dependencies (reportlab, etc.)
- Path dependencies
- Complex error handling

**Solution:** Use the RPC-based implementation (current version).

</details>

---

## 🧪 Testing & Verification

### Test RPC Configuration

**1. Test RPC Endpoint:**
```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "db",
      "method": "list",
      "args": []
    },
    "id": 1
  }'
```

**Expected Output:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": ["database1", "database2", ...]
}
```

**2. Test Authentication:**
```bash
curl -X POST http://localhost:8069/jsonrpc \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
      "service": "common",
      "method": "version",
      "args": []
    },
    "id": 1
  }'
```

**Expected Output:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "server_version": "18.0",
    ...
  }
}
```

---

## 📖 Additional Resources

- **RPC_API_GUIDE.md** - Complete RPC API reference and troubleshooting
- **CONFIGURATION.md** - RPC configuration guide
- **QUICKSTART.md** - Quick start with RPC template creation
- [Odoo External API Documentation](https://www.odoo.com/documentation/18.0/developer/reference/external_api.html)

---

## 🆘 Getting Help

If issues persist:

1. **Check Odoo logs:**
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

2. **Check PostgreSQL logs:**
   ```bash
   tail -f /var/log/postgresql/postgresql-*.log
   ```

3. **Enable debug mode:**
   ```bash
   # Add to odoo.conf
   log_level = debug
   
   # Restart Odoo
   sudo systemctl restart odoo
   ```

4. **Review detailed RPC troubleshooting:** See `saas_manager/RPC_API_GUIDE.md`

5. **Contact support** with:
   - Error message
   - Odoo logs
   - Configuration details (odoo.conf)
   - System parameters
   - Steps to reproduce

---

**Last Updated:** December 2024  
**Odoo Version:** 18.0  
**Module:** saas_manager  
**RPC Implementation:** Phase 1.5 ✅
