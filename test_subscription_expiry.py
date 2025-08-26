#!/usr/bin/env python3
"""
Test script to verify subscription expiry logic
Run this with: bench --site your-site execute tookio_shop.test_subscription_expiry.test_expiry_logic
"""

import frappe
from tookio_shop.utils import check_and_handle_expired_subscriptions, get_user_subscription_status

def test_expiry_logic():
    """Test the subscription expiry handling"""
    try:
        print("Testing subscription expiry logic...")
        
        # Run the expiry check
        check_and_handle_expired_subscriptions()
        print("✅ Expiry check completed successfully")
        
        # Test getting user subscription status
        test_user = "Administrator"
        status = get_user_subscription_status(test_user)
        print(f"✅ User subscription status for {test_user}: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Error in test: {str(e)}")
        frappe.log_error(f"Test error: {str(e)}", "Subscription Test Error")
        return False

if __name__ == "__main__":
    test_expiry_logic()
