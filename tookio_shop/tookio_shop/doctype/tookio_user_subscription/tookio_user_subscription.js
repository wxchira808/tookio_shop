// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tookio User Subscription", {
	refresh(frm) {
		// Add mobile/desktop notice at the top
		if (!frm.is_new()) {
			frm.dashboard.add_comment(`
				<div style="padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107; margin-bottom: 10px;">
					<strong>📱 Mobile Users:</strong> Click the <strong>three dots (⋮)</strong> at the top right to manage your subscription.
					<br><strong>💻 Desktop Users:</strong> Use the "Manage Subscription" button below for the best experience.
				</div>
			`, true);
		}
		
		// Replace "Actions" dropdown with direct "Manage Subscription" button
		if (!frm.is_new()) {
			frm.add_custom_button(__('Manage Subscription'), function() {
				show_subscription_renewal_dialog(frm);
			}).addClass('btn-primary');  // Black button style
		}
	},
});

function show_subscription_renewal_dialog(frm) {
	// First, get available subscription plans
	frappe.call({
		method: 'tookio_shop.api.get_available_subscriptions',
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				let subscriptions = r.message;
				
				// Create dialog
				let d = new frappe.ui.Dialog({
					title: __('Renew/Upgrade Subscription'),
					fields: [
						{
							label: __('Current Subscription'),
							fieldname: 'current_subscription_info',
							fieldtype: 'HTML',
							options: get_current_subscription_html(frm)
						},
						{
							fieldname: 'subscription_break',
							fieldtype: 'Section Break',
							label: __('Select New Subscription Plan')
						},
						{
							label: __('Subscription Plan'),
							fieldname: 'subscription_plan',
							fieldtype: 'Select',
							options: subscriptions.map(s => s.name).join('\n'),
							reqd: 1,
							onchange: function() {
								let selected = this.get_value();
								let plan = subscriptions.find(s => s.name === selected);
								if (plan) {
									d.fields_dict.plan_details.html(get_plan_details_html(plan));
								}
							}
						},
						{
							fieldname: 'plan_details',
							fieldtype: 'HTML',
							options: ''
						},
						{
							fieldname: 'phone_break',
							fieldtype: 'Section Break',
							label: __('Payment Details')
						},
						{
							label: __('M-Pesa Phone Number'),
							fieldname: 'phone_number',
							fieldtype: 'Data',
							reqd: 1,
							description: __('Format: 0712345678 or 254712345678')
						}
					],
					primary_action_label: __('Proceed to Payment'),
					primary_action: function(values) {
						process_subscription_renewal(frm, values, subscriptions, d);
					}
				});
				
				d.show();
			} else {
				frappe.msgprint(__('No subscription plans available'));
			}
		}
	});
}

function get_current_subscription_html(frm) {
	let html = `
		<div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px; margin-bottom: 10px;">
			<h4 style="margin-top: 0;">Current Subscription Details</h4>
			<table class="table table-borderless" style="margin: 0;">
				<tr>
					<td><strong>Plan:</strong></td>
					<td>${frm.doc.current_subscription || 'None'}</td>
				</tr>
				<tr>
					<td><strong>Status:</strong></td>
					<td><span class="indicator ${frm.doc.status === 'Active' ? 'green' : 'red'}">${frm.doc.status}</span></td>
				</tr>
				<tr>
					<td><strong>Start Date:</strong></td>
					<td>${frm.doc.subscription_start_date || 'N/A'}</td>
				</tr>
				<tr>
					<td><strong>End Date:</strong></td>
					<td>${frm.doc.subscription_end_date || 'No expiry'}</td>
				</tr>
			</table>
		</div>
	`;
	return html;
}

function get_plan_details_html(plan) {
	let html = `
		<div style="padding: 10px; background-color: #e8f5e9; border-radius: 5px; margin-top: 10px;">
			<h5 style="margin-top: 0; color: #2e7d32;">${plan.subscription_name}</h5>
			<p style="margin: 5px 0;"><strong>Price:</strong> ${plan.currency} ${plan.price.toLocaleString()}</p>
			<p style="margin: 5px 0;"><strong>Shop Limit:</strong> ${plan.shop_limit}</p>
			<p style="margin: 5px 0;"><strong>Products Limit:</strong> ${plan.products_limit}</p>
			<p style="margin: 5px 0;"><strong>Sales Invoice Limit:</strong> ${plan.sales_invoice_limit || 'Unlimited'}</p>
			${plan.description ? `<p style="margin: 5px 0; font-style: italic;">${plan.description}</p>` : ''}
		</div>
	`;
	return html;
}

function process_subscription_renewal(frm, values, subscriptions, dialog) {
	let selected_plan = subscriptions.find(s => s.name === values.subscription_plan);
	let current_plan = subscriptions.find(s => s.name === frm.doc.current_subscription);
	
	// Check if user is trying to select the same plan
	if (frm.doc.current_subscription === values.subscription_plan) {
		frappe.msgprint({
			title: __('Same Plan Selected'),
			indicator: 'orange',
			message: __('You already have an active subscription to this plan. Please select a different plan to upgrade or downgrade.')
		});
		return;
	}
	
	// Check if downgrading - show message about letting it expire instead
	if (current_plan && selected_plan && selected_plan.price < current_plan.price) {
		frappe.confirm(
			`
			<div style="padding: 10px;">
				<h4 style="color: #f39c12;">⚠️ Downgrading Subscription</h4>
				<p>You're trying to downgrade from <strong>${current_plan.subscription_name}</strong> (${current_plan.currency} ${current_plan.price}) to <strong>${selected_plan.subscription_name}</strong> (${selected_plan.currency} ${selected_plan.price}).</p>
				<hr>
				<p style="background-color: #fff3cd; padding: 10px; border-radius: 5px;">
					<strong>💡 Recommendation:</strong> Instead of downgrading now, you can simply let your current subscription expire on <strong>${frm.doc.subscription_end_date}</strong>, then subscribe to the lower plan. This way you keep all the benefits of your current plan until it expires naturally.
				</p>
				<p>Do you still want to downgrade now and lose your current plan benefits?</p>
			</div>
			`,
			function() {
				// User still wants to downgrade, proceed with calculation
				proceed_with_plan_change(frm, values, subscriptions, dialog, selected_plan);
			},
			function() {
				frappe.show_alert({
					message: __('Good choice! Your current plan will remain active until expiry.'),
					indicator: 'blue'
				});
			}
		);
		return;
	}
	
	// For upgrades, proceed directly
	proceed_with_plan_change(frm, values, subscriptions, dialog, selected_plan);
}

function proceed_with_plan_change(frm, values, subscriptions, dialog, selected_plan) {
	// Calculate upgrade pricing
	frappe.call({
		method: 'tookio_shop.api.calculate_subscription_upgrade_cost',
		args: {
			user_subscription: frm.doc.name,
			new_subscription: values.subscription_plan
		},
		callback: function(r) {
			if (r.message) {
				let cost_info = r.message;
				
				// Show confirmation dialog with upgrade details
				frappe.confirm(
					`
					<div style="padding: 10px;">
						<h4>Subscription ${cost_info.is_upgrade ? 'Upgrade' : 'Change'} Confirmation</h4>
						<p><strong>Current Plan:</strong> ${frm.doc.current_subscription}</p>
						<p><strong>New Plan:</strong> ${values.subscription_plan}</p>
						<hr>
						<p><strong>New Plan Price:</strong> ${selected_plan.currency} ${selected_plan.price.toLocaleString()}</p>
						${cost_info.credit_from_old_plan > 0 ? 
							`<p><strong>Credit from Current Plan:</strong> -${selected_plan.currency} ${cost_info.credit_from_old_plan.toLocaleString()} (${cost_info.days_remaining} days remaining)</p>` 
							: ''}
						<p style="font-size: 16px; margin-top: 10px;"><strong>Total Amount to Pay:</strong> ${selected_plan.currency} ${cost_info.amount_to_pay.toLocaleString()}</p>
						<hr>
						<p style="color: #d32f2f; font-weight: bold;">⚠️ Your current subscription will be replaced with the new plan.</p>
						<p>Are you sure you want to proceed?</p>
					</div>
					`,
					function() {
						// User confirmed, initiate payment
						initiate_mpesa_payment(frm, values, cost_info, dialog);
					},
					function() {
						// User cancelled
						frappe.show_alert({
							message: __('Subscription change cancelled'),
							indicator: 'blue'
						});
					}
				);
			}
		}
	});
}

function initiate_mpesa_payment(frm, values, cost_info, dialog) {
	frappe.show_alert({
		message: __('Initiating M-Pesa payment...'),
		indicator: 'blue'
	});
	
	frappe.call({
		method: 'tookio_shop.api.initiate_subscription_payment',
		args: {
			user_subscription: frm.doc.name,
			new_subscription: values.subscription_plan,
			phone_number: values.phone_number,
			amount: cost_info.amount_to_pay
		},
		callback: function(r) {
			dialog.hide();
			
			if (r.message && r.message.success) {
				// Show success message with STK push prompt
				frappe.msgprint({
					title: __('Payment Initiated'),
					indicator: 'green',
					message: __(`
						<div style="padding: 10px;">
							<h4>✓ M-Pesa STK Push Sent!</h4>
							<p>Please check your phone and enter your M-Pesa PIN to complete the payment.</p>
							<p><strong>Amount:</strong> KES ${cost_info.amount_to_pay}</p>
							<p><strong>Phone:</strong> ${values.phone_number}</p>
							<hr>
							<p style="font-size: 12px; color: #666;">
								Your subscription will be automatically updated once payment is confirmed.
								You can check the payment status in M-Pesa Transaction list.
							</p>
						</div>
					`)
				});
				
				// Optionally, set up polling to check payment status
				check_payment_status(r.message.transaction_id, frm);
			} else {
				frappe.msgprint({
					title: __('Payment Failed'),
					indicator: 'red',
					message: r.message ? r.message.message : __('Failed to initiate payment. Please try again.')
				});
			}
		},
		error: function(r) {
			dialog.hide();
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('An error occurred while initiating payment. Please try again.')
			});
		}
	});
}

function check_payment_status(transaction_id, frm) {
	let check_interval = setInterval(function() {
		frappe.call({
			method: 'tookio_shop.api.check_subscription_payment_status',
			args: {
				transaction_id: transaction_id
			},
			callback: function(r) {
				if (r.message) {
					if (r.message.status === 'Success') {
						clearInterval(check_interval);
						frappe.show_alert({
							message: __('Payment successful! Subscription updated.'),
							indicator: 'green'
						}, 10);
						frm.reload_doc();
					} else if (r.message.status === 'Failed') {
						clearInterval(check_interval);
						frappe.show_alert({
							message: __('Payment failed. Please try again.'),
							indicator: 'red'
						}, 10);
					}
				}
			}
		});
	}, 5000); // Check every 5 seconds
	
	// Stop checking after 2 minutes
	setTimeout(function() {
		clearInterval(check_interval);
	}, 120000);
}
