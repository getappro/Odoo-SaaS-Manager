# Testing Guide - SaaS Client Agent Module

This guide provides comprehensive testing procedures for the `saas_client_agent` module.

## 🧪 Automated Tests

### Running Unit Tests

```bash
# Run all tests for the module
odoo-bin -d test_database -i saas_client_agent --test-enable --stop-after-init

# Run specific test class
odoo-bin -d test_database --test-tags saas_client_agent.test_saas_client_config

# Run with coverage
odoo-bin -d test_database -i saas_client_agent --test-enable --stop-after-init \
  --coverage saas_client_agent --coverage-html coverage_report
```

### Test Coverage

The automated tests cover:

✅ **Configuration Management**
- Singleton configuration creation
- User count computation
- Usage percentage calculation
- User limit validation

✅ **User Limit Enforcement**
- User creation allowed under limit
- User creation blocked at limit
- Portal users not counted
- Enforcement can be disabled
- Error messages contain helpful info

## 🖥️ Manual Testing Procedures

### 1. Menu Visibility Tests

#### Test 1.1: Regular User Cannot See Technical Menus

**Prerequisites:**
- Create a test user with `base.group_user` only (not `base.group_system`)

**Steps:**
1. Login as regular user
2. Check the main menu

**Expected Result:**
- ❌ "SaaS Client" menu should NOT be visible
- ✅ Can access Settings menu

**Actual Result:** _[To be filled]_

---

#### Test 1.2: System Admin Can See Technical Menus

**Prerequisites:**
- Login as administrator (has `base.group_system`)

**Steps:**
1. Login as administrator
2. Check the main menu
3. Navigate to SaaS Client menu

**Expected Result:**
- ✅ "SaaS Client" menu is visible
- ✅ Can open Configuration submenu
- ✅ Can view/edit configuration records

**Actual Result:** _[To be filled]_

---

### 2. Settings Tab Tests

#### Test 2.1: Subscription Tab Visible to All Users

**Prerequisites:**
- Login as any user (regular or admin)

**Steps:**
1. Navigate to Settings
2. Look for "Subscription" tab/section

**Expected Result:**
- ✅ "Subscription" section is visible
- ✅ Shows current usage metrics
- ✅ Shows user limit
- ✅ Shows usage percentage
- ✅ Shows Instance ID

**Actual Result:** _[To be filled]_

---

#### Test 2.2: Usage Metrics Display Correctly

**Prerequisites:**
- Module installed and configured
- Know the current user count

**Steps:**
1. Navigate to Settings → Subscription
2. Check displayed metrics
3. Create a new user
4. Refresh Settings page
5. Check metrics again

**Expected Result:**
- ✅ Initial metrics match actual count
- ✅ Metrics update after new user creation
- ✅ Percentage is calculated correctly
- ✅ Alert styling changes based on percentage:
  - Green: < 80%
  - Yellow: 80-94%
  - Red: >= 95%

**Actual Result:** _[To be filled]_

---

#### Test 2.3: Upgrade Request Button

**Prerequisites:**
- Navigate to Settings → Subscription

**Steps:**
1. Click "Request Upgrade" button
2. Read the notification

**Expected Result:**
- ✅ Notification appears
- ✅ Shows contact information
- ✅ Shows Instance ID
- ✅ Message is clear and actionable

**Actual Result:** _[To be filled]_

---

### 3. User Limit Enforcement Tests

#### Test 3.1: User Creation Under Limit

**Prerequisites:**
- Configure limit higher than current users
- Enable limit enforcement

**Steps:**
1. Navigate to Settings → Users & Companies → Users
2. Create a new internal user
3. Save

**Expected Result:**
- ✅ User is created successfully
- ✅ No error or warning

**Actual Result:** _[To be filled]_

---

#### Test 3.2: User Creation At Limit

**Prerequisites:**
- Configure limit equal to current users
- Enable limit enforcement

**Steps:**
1. Navigate to Settings → Users & Companies → Users
2. Try to create a new internal user
3. Save

**Expected Result:**
- ❌ Error message appears
- ✅ Error says "User Limit Reached"
- ✅ Error mentions upgrade option
- ✅ Error includes Instance ID
- ✅ Error suggests contacting support
- ❌ User is NOT created

**Actual Result:** _[To be filled]_

---

#### Test 3.3: Portal User Creation (Should Always Work)

**Prerequisites:**
- Configure limit equal to current users
- Enable limit enforcement

**Steps:**
1. Navigate to Settings → Users & Companies → Users
2. Create a new portal user (share=True)
3. Save

**Expected Result:**
- ✅ Portal user is created successfully
- ✅ No error (portal users don't count toward limit)

**Actual Result:** _[To be filled]_

---

#### Test 3.4: User Creation With Enforcement Disabled

**Prerequisites:**
- Configure limit equal to current users
- DISABLE limit enforcement

**Steps:**
1. Navigate to SaaS Client → Configuration
2. Uncheck "Enforce Limits"
3. Save
4. Try to create a new internal user

**Expected Result:**
- ✅ User is created successfully
- ✅ No error (enforcement disabled)

**Actual Result:** _[To be filled]_

---

### 4. Warning Banner Tests

#### Test 4.1: Warning Banner at 80% Usage

**Prerequisites:**
- Configure limit so current usage is >= 80%

**Steps:**
1. Login to Odoo
2. Check for warning banner at top of screen
3. Navigate to different pages

**Expected Result:**
- ✅ Yellow warning banner appears
- ✅ Shows current usage
- ✅ Shows "Upgrade your plan" link
- ✅ Shows progress bar
- ✅ Banner persists across pages

**Actual Result:** _[To be filled]_

---

#### Test 4.2: Critical Warning Banner at 95% Usage

**Prerequisites:**
- Configure limit so current usage is >= 95%

**Steps:**
1. Login to Odoo
2. Check warning banner

**Expected Result:**
- ✅ Red warning banner appears
- ✅ More urgent styling than 80% warning
- ✅ All other elements same as 80% test

**Actual Result:** _[To be filled]_

---

#### Test 4.3: No Banner Under 80% Usage

**Prerequisites:**
- Configure limit so current usage is < 80%

**Steps:**
1. Login to Odoo
2. Check for warning banner

**Expected Result:**
- ❌ No warning banner displayed

**Actual Result:** _[To be filled]_

---

### 5. Configuration Tests (System Admin Only)

#### Test 5.1: View Configuration

**Prerequisites:**
- Login as system administrator

**Steps:**
1. Navigate to SaaS Client → Configuration
2. Open configuration record

**Expected Result:**
- ✅ Form view displays
- ✅ Shows Instance UUID
- ✅ Shows connection settings
- ✅ Shows limits
- ✅ Shows current usage
- ✅ Shows last heartbeat time

**Actual Result:** _[To be filled]_

---

#### Test 5.2: Manual Sync

**Prerequisites:**
- Configure master server URL and API key
- Open configuration record

**Steps:**
1. Click "Sync with Master" button
2. Check notification

**Expected Result:**
- ✅ Success notification appears
- ✅ Last heartbeat timestamp updates

**Actual Result:** _[To be filled]_

---

#### Test 5.3: Modify User Limit

**Prerequisites:**
- Open configuration record

**Steps:**
1. Change user limit value
2. Save
3. Navigate to Settings → Subscription
4. Check displayed limit

**Expected Result:**
- ✅ Limit is updated
- ✅ New limit displays in Settings
- ✅ Percentage recalculates

**Actual Result:** _[To be filled]_

---

### 6. Dashboard Widget Tests

#### Test 6.1: Dashboard Data API

**Prerequisites:**
- Module installed

**Steps:**
1. Open browser console
2. Execute RPC call:
```javascript
odoo.rpc('/web/dataset/call_kw/res.users/get_saas_usage_info', {
    model: 'res.users',
    method: 'get_saas_usage_info',
    args: [],
    kwargs: {}
}).then(console.log);
```

**Expected Result:**
- ✅ Returns JSON object with:
  - current_users
  - user_limit
  - users_percentage
  - warning_level
  - show_warning
  - can_create_users
  - users_remaining

**Actual Result:** _[To be filled]_

---

## 🐛 Known Issues & Workarounds

### Issue 1: Warning Banner Not Showing

**Symptom:** Warning banner doesn't appear even at 80%+ usage

**Possible Causes:**
- JavaScript not loaded
- Component not registered

**Workaround:**
1. Clear browser cache
2. Restart Odoo server
3. Check browser console for errors

---

### Issue 2: Settings Tab Not Visible

**Symptom:** Subscription tab missing in Settings

**Possible Causes:**
- View inheritance not loaded
- Module not fully installed

**Workaround:**
1. Upgrade module
2. Clear cache
3. Verify view is in database

---

## 📊 Test Results Template

Use this template to document test results:

```
## Test Session: [Date]

**Tester:** [Name]
**Odoo Version:** 18.0
**Module Version:** 1.0.0
**Environment:** [Development/Staging/Production]

### Summary
- Tests Run: XX
- Tests Passed: XX
- Tests Failed: XX
- Tests Skipped: XX

### Detailed Results

#### Menu Visibility
- Test 1.1: ✅ PASS
- Test 1.2: ✅ PASS

#### Settings Tab
- Test 2.1: ✅ PASS
- Test 2.2: ⚠️ FAIL - [Details]
- Test 2.3: ✅ PASS

[Continue for all tests...]

### Issues Found
1. [Issue description]
   - Severity: High/Medium/Low
   - Steps to reproduce
   - Expected vs Actual behavior

### Notes
[Any additional observations]
```

---

## 🚀 Performance Testing

### Load Test: Multiple User Creation

**Objective:** Test performance when creating many users near limit

**Steps:**
1. Set user limit to current + 100
2. Create 95 users programmatically
3. Measure response times
4. Check for performance degradation

**Expected:**
- ✅ No significant slowdown
- ✅ Warnings appear appropriately
- ✅ All validations work correctly

---

## 🔒 Security Testing

### Test: Non-Admin Access Control

**Objective:** Ensure security groups work correctly

**Steps:**
1. Create user without base.group_system
2. Try to access configuration directly via URL:
   - `/web#model=saas.client.config`
3. Try to execute actions via RPC

**Expected:**
- ❌ Access denied
- ❌ Cannot view/edit configuration
- ✅ Can still view Settings → Subscription

---

## ✅ Test Completion Checklist

Before marking testing as complete, verify:

- [ ] All automated tests pass
- [ ] All manual tests executed and documented
- [ ] Security tests pass
- [ ] Performance is acceptable
- [ ] Documentation matches implementation
- [ ] No critical bugs remain
- [ ] Screenshots captured for UI features
- [ ] Test results documented

---

**Last Updated:** [Date]
**Version:** 1.0.0
