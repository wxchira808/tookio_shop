"""
Scheduled task to handle subscription expiry
Runs daily to auto-downgrade expired subscriptions to Free Plan
"""

import frappe
from frappe.utils import today


@frappe.whitelist()
def check_and_process_expired_subscriptions():
    """Daily task to check for expired subscriptions and auto-downgrade them"""
    try:
        current_date = today()
        
        # Find all Active subscriptions that have expired
        expired_subs = frappe.get_all(
            "Tookio User Subscription",
            filters={
                "status": "Active",
                "subscription_end_date": ["<", current_date],
                "current_subscription": ["!=", "Free Plan"]
            },
            fields=["name", "user", "current_subscription", "subscription_end_date"]
        )
        
        if expired_subs:
            frappe.logger().info(f"⏰ Found {len(expired_subs)} expired subscriptions to process")
            
            for sub_data in expired_subs:
                try:
                    doc = frappe.get_doc("Tookio User Subscription", sub_data["name"])
                    
                    # Auto-downgrade to free plan
                    frappe.logger().info(f"🔄 Auto-downgrading {doc.user} subscription ({doc.current_subscription}) - EXPIRED")
                    
                    doc.status = "Expired"
                    doc.current_subscription = "Free Plan"
                    doc.subscription_start_date = current_date
                    doc.subscription_end_date = None  # Free plan never expires
                    doc.shop_limit = 1
                    doc.products_limit = 50
                    doc.sales_invoice_limit = 200
                    
                    # Add to history
                    doc.append("subscription_history", {
                        "tookio_subscription": "Free Plan",
                        "subscription_start_date": current_date,
                        "subscription_end_date": None,
                        "status": "Expired"
                    })
                    
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    
                    frappe.logger().info(f"✅ Successfully downgraded {doc.user} to Free Plan")
                    
                except Exception as e:
                    frappe.logger().error(f"❌ Failed to process expired subscription {sub_data['name']}: {str(e)}")
            
            frappe.logger().info(f"🎉 Processed {len(expired_subs)} expired subscriptions")
        else:
            frappe.logger().info("✨ No expired subscriptions to process")
        
        return {
            "success": True,
            "processed_count": len(expired_subs),
            "message": f"Processed {len(expired_subs)} expired subscriptions"
        }
    
    except Exception as e:
        frappe.logger().error(f"❌ Error in check_and_process_expired_subscriptions: {str(e)}")
        return {
            "success": False,
            "message": f"Error: {str(e)}"
        }


def schedule_expired_subscription_check():
    """
    Register this in hooks.py:
    
    scheduler_events = {
        "daily": [
            "tookio_shop.subscription_expiry_task.check_and_process_expired_subscriptions"
        ]
    }
    """
    pass
