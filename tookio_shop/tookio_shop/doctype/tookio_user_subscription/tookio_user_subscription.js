// Copyright (c) 2025, Tookio and contributors
// For license information, please see license.txt

frappe.ui.form.on("Tookio User Subscription", {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.dashboard.add_comment(__('Mobile Users: Click the three dots at the top right to manage your subscription. Desktop Users: Use the "Manage Subscription" button below for the best experience.'), true);
		}
		
		if (!frm.is_new()) {
			frm.add_custom_button(__('Manage Subscription'), function() {
				show_subscription_renewal_dialog(frm);
			}).addClass('btn-primary');
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
	
	if (frm.doc.current_subscription === values.subscription_plan) {
		frappe.msgprint({
			title: __('Same Plan Selected'),
			indicator: 'orange',
			message: __('You already have an active subscription to this plan. Please select a different plan to upgrade.')
		});
		return;
	}
	
	if (current_plan && selected_plan && selected_plan.price < current_plan.price) {
		frappe.msgprint({
			title: __('Downgrade Not Allowed'),
			indicator: 'red',
			message: __(`
				<div style="padding: 10px;">
					<p>You cannot downgrade from <strong>${current_plan.subscription_name}</strong> to <strong>${selected_plan.subscription_name}</strong>.</p>
					<hr>
					<p>Your current subscription will remain active until <strong>${frm.doc.subscription_end_date}</strong>.</p>
					<p>After it expires, you can subscribe to any plan you prefer.</p>
				</div>
			`)
		});
		return;
	}
	
	proceed_with_plan_change(frm, values, subscriptions, dialog, selected_plan);
}

function proceed_with_plan_change(frm, values, subscriptions, dialog, selected_plan) {
	frappe.call({
		method: 'tookio_shop.api.calculate_subscription_upgrade_cost',
		args: {
			user_subscription: frm.doc.name,
			new_subscription: values.subscription_plan
		},
		callback: function(r) {
			if (r.message) {
				let cost_info = r.message;
				
				frappe.confirm(
					`
					<div style="padding: 10px;">
						<h4>Subscription Upgrade Confirmation</h4>
						<p><strong>Current Plan:</strong> ${frm.doc.current_subscription}</p>
						<p><strong>New Plan:</strong> ${values.subscription_plan}</p>
						<hr>
						<p><strong>New Plan Price:</strong> ${selected_plan.currency} ${selected_plan.price.toLocaleString()}</p>
						${cost_info.credit_from_old_plan > 0 ? 
							`<p><strong>Credit from Current Plan:</strong> -${selected_plan.currency} ${cost_info.credit_from_old_plan.toLocaleString()} (${cost_info.days_remaining} days remaining)</p>` 
							: ''}
						<p style="font-size: 16px; margin-top: 10px;"><strong>Total Amount to Pay:</strong> ${selected_plan.currency} ${cost_info.amount_to_pay.toLocaleString()}</p>
						<hr>
						<p style="color: #d32f2f; font-weight: bold;">Your current subscription will be replaced with the new plan.</p>
						<p>Are you sure you want to proceed?</p>
					</div>
					`,
					function() {
						initiate_mpesa_payment(frm, values, cost_info, dialog);
					},
					function() {
						frappe.show_alert({
							message: __('Subscription upgrade cancelled'),
							indicator: 'blue'
						});
					}
				);
			}
		}
	});
}

function initiate_mpesa_payment(frm, values, cost_info, dialog) {
	dialog.hide();
	
	let loading_dialog = new frappe.ui.Dialog({
		title: __('Processing Payment'),
		fields: [{
			fieldname: 'loading_html',
			fieldtype: 'HTML',
			options: `
				<div style="text-align: center; padding: 30px;">
					<div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;">
						<span class="sr-only">Loading...</span>
					</div>
					<h4 style="margin-top: 20px;">Initiating M-Pesa Payment...</h4>
					<p>Please wait while we process your request.</p>
				</div>
			`
		}]
	});
	
	loading_dialog.show();
	loading_dialog.$wrapper.find('.modal-header .close').hide();
	
	frappe.call({
		method: 'tookio_shop.api.initiate_subscription_payment',
		args: {
			user_subscription: frm.doc.name,
			new_subscription: values.subscription_plan,
			phone_number: values.phone_number,
			amount: cost_info.amount_to_pay
		},
		callback: function(r) {
			if (r.message && r.message.success) {
				loading_dialog.fields_dict.loading_html.$wrapper.html(`
					<div style="text-align: center; padding: 30px;">
						<div class="spinner-border text-success" role="status" style="width: 3rem; height: 3rem;">
							<span class="sr-only">Loading...</span>
						</div>
						<h4 style="margin-top: 20px; color: green;">M-Pesa Prompt Sent!</h4>
						<p>Please check your phone and enter your M-Pesa PIN.</p>
						<p><strong>Amount:</strong> KES ${cost_info.amount_to_pay}</p>
						<p><strong>Phone:</strong> ${values.phone_number}</p>
						<hr>
						<p style="font-size: 12px; color: #666;">
							Waiting for payment confirmation...
						</p>
					</div>
				`);
				
				check_payment_status(r.message.transaction_id, frm, loading_dialog);
			} else {
				loading_dialog.hide();
				frappe.msgprint({
					title: __('Payment Failed'),
					indicator: 'red',
					message: r.message ? r.message.message : __('Failed to initiate payment. Please try again.')
				});
			}
		},
		error: function(r) {
			loading_dialog.hide();
			frappe.msgprint({
				title: __('Error'),
				indicator: 'red',
				message: __('An error occurred while initiating payment. Please try again.')
			});
		}
	});
}

function check_payment_status(transaction_id, frm, loading_dialog) {
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
						loading_dialog.fields_dict.loading_html.$wrapper.html(`
							<div style="text-align: center; padding: 30px;">
								<div style="font-size: 48px; color: green;">&#10004;</div>
								<h4 style="margin-top: 20px; color: green;">Payment Successful!</h4>
								<p>Your subscription has been updated.</p>
								<p style="font-size: 12px; color: #666;">Refreshing page...</p>
							</div>
						`);
						setTimeout(function() {
							loading_dialog.hide();
							frm.reload_doc();
						}, 2000);
					} else if (r.message.status === 'Failed') {
						clearInterval(check_interval);
						loading_dialog.hide();
						frappe.msgprint({
							title: __('Payment Failed'),
							indicator: 'red',
							message: __('Payment was not successful. Please try again.')
						});
					}
				}
			}
		});
	}, 5000);
	
	setTimeout(function() {
		clearInterval(check_interval);
		if (loading_dialog && loading_dialog.is_visible) {
			loading_dialog.hide();
			frappe.msgprint({
				title: __('Payment Timeout'),
				indicator: 'orange',
				message: __('Payment confirmation timed out. Please check M-Pesa Transaction list for status.')
			});
		}
	}, 120000);
}
