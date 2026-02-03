# Quick Setup Guide - Subscription Renewal with M-Pesa

## Step 1: Configure M-Pesa Settings

1. Navigate to **Tookio Mpesa Settings** in ERPNext
2. Fill in the following:
   - **Title:** Default Tookio Mpesa Settings
   - **Consumer Key:** Your Daraja API consumer key
   - **Consumer Secret:** Your Daraja API consumer secret
   - **Environment:** Sandbox (for testing) or Production
   - **Is Active:** ✓ Check this
   - **Till Number:** Your M-Pesa till number
   - **Business Shortcode:** Your business shortcode (e.g., 174379 for sandbox)
   - **Passkey:** Your STK push passkey

3. Click **Save**

## Step 2: Create Subscription Plans

1. Navigate to **Tookio Subscription** list
2. Create the following plans:

### Free Plan
```
Subscription Name: Free Plan
Price: 0
Currency: KES
Shop Limit: 1
Products Limit: 50
Sales Invoice Limit: 200
Enabled: ✓
```

### Starter Plan
```
Subscription Name: Starter
Price: 500
Currency: KES
Shop Limit: 3
Products Limit: 200
Sales Invoice Limit: 1000
Enabled: ✓
```

### Premium Plan
```
Subscription Name: Premium
Price: 1500
Currency: KES
Shop Limit: 10
Products Limit: 1000
Sales Invoice Limit: 5000
Enabled: ✓
```

## Step 3: Create/Update User Subscription

1. Navigate to **Tookio User Subscription** list
2. Open a user's subscription (or create new)
3. Set initial subscription:
   - **User:** Select user
   - **Current Subscription:** Starter
   - **Subscription Start Date:** Today
   - **Subscription End Date:** Today + 30 days
   - **Status:** Active
4. Save

## Step 4: Test Subscription Renewal

1. Open the user's Tookio User Subscription
2. Click **Actions → Renew Subscription**
3. In the dialog:
   - View current subscription details
   - Select **Premium** from dropdown
   - See plan details appear
   - Enter M-Pesa phone number (format: 0712345678)
4. Click **Proceed to Payment**
5. Review upgrade confirmation showing:
   - Current plan: Starter
   - New plan: Premium
   - Credit from old plan (prorated)
   - Total amount to pay
6. Click **Yes, Proceed**
7. Check your phone for STK push
8. Enter M-Pesa PIN
9. Wait for confirmation
10. Subscription will auto-update on successful payment

## Step 5: Verify M-Pesa Integration

### Test STK Push
```python
# In ERPNext console
import frappe
from tookio_mpesa.utils import test_till_payment

# Test with your phone number
result = test_till_payment("0712345678", 1)
print(result)
```

### Check Transaction Status
1. Navigate to **Mpesa Transaction** list
2. Find your test transaction
3. Verify:
   - Status: Success/Pending/Failed
   - Account Reference: Shows TUSUB-XXXXXXX|Premium
   - Mpesa Receipt Number: Set on success

## Step 6: Verify Subscription Update

1. Refresh the Tookio User Subscription
2. Verify:
   - **Current Subscription:** Premium
   - **Status:** Active
   - **Limits updated:** Shop: 10, Products: 1000
   - **Subscription History:** Shows old Starter plan with status "Replaced"

## Troubleshooting

### STK Push Not Received
- Check Tookio Mpesa Settings are active
- Verify phone number format
- Check consumer key/secret are correct
- For sandbox: use test phone 254712345678

### Payment Successful But Subscription Not Updated
- Check **Error Log** for errors
- Verify webhook is accessible
- Check Mpesa Transaction `account_reference` field
- Manually trigger: 
  ```python
  from tookio_shop.api import process_subscription_upgrade
  process_subscription_upgrade('TUSUB-0000001', 'Premium', 'MPESA-XXX')
  ```

### Prorated Credit Not Calculating
- Ensure subscription_end_date is set on current plan
- Verify current subscription has a price
- Check days_remaining is positive

## Production Checklist

Before going live:

- [ ] Update M-Pesa settings to Production environment
- [ ] Set production consumer key/secret
- [ ] Set production business shortcode
- [ ] Set production passkey
- [ ] Verify callback URL is HTTPS
- [ ] Test with real M-Pesa account
- [ ] Set up SSL certificate
- [ ] Configure proper email settings for notifications
- [ ] Test all subscription plans
- [ ] Document your Till number and shortcode settings

## Important Notes

1. **Sandbox Testing:** Safaricom sandbox may not send actual STK push. Use test credentials provided by Safaricom.

2. **Callback URL:** Must be HTTPS in production. For local testing, use ngrok or similar tunneling service.

3. **Phone Format:** Accepts both 0712345678 and 254712345678 formats.

4. **Subscription Duration:** Currently set to 1 month. Modify in `process_subscription_upgrade()` if needed.

5. **Email Notifications:** Ensure SMTP is configured in ERPNext for upgrade confirmation emails.

## Testing Commands

```bash
# Bench console
bench --site your-site console

# Then in Python:
import frappe

# Test M-Pesa credentials
from tookio_mpesa.utils import test_mpesa_credentials
result = test_mpesa_credentials()
print(result)

# Check available subscriptions
from tookio_shop.api import get_available_subscriptions
plans = get_available_subscriptions()
print(plans)

# Calculate upgrade cost
from tookio_shop.api import calculate_subscription_upgrade_cost
cost = calculate_subscription_upgrade_cost('TUSUB-0000001', 'Premium')
print(cost)
```

## Need Help?

Check the detailed documentation in `SUBSCRIPTION_RENEWAL_IMPLEMENTATION.md`
