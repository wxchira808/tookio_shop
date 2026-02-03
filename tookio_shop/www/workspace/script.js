// TOOKIO Workspace Navigation Handler
window.handleNavigation = function(action) {
    console.log('Button clicked:', action);

    // Check if frappe is available
    if (typeof frappe === 'undefined') {
        console.error('Frappe is not available');
        return;
    }

    console.log('Frappe available, navigating...');

    try {
        // Frappe navigation methods for different actions
        switch(action) {
            // Shop Management
            case 'add-shop':
                frappe.new_doc('Shop');
                break;
            case 'view-shops':
                frappe.set_route('List', 'Shop');
                break;
            case 'view-dashboard':
                frappe.set_route('dashboard-view','Tookio Shop Dashboard');
                break;

            // Products/Items
            case 'add-product':
                frappe.new_doc('Product');
                break;
            case 'view-products':
                frappe.set_route('List', 'Product');
                break;

            // Stock Management
            case 'manage-stock':
                frappe.new_doc('Product Stock');
                break;
            case 'stock-transactions':
                frappe.set_route('List', 'Product Stock');
                break;
            case 'stock-report':
                frappe.set_route('query-report', 'Shop Stock Balance');
                break;

            // Sales
            case 'make-sale':
                frappe.new_doc('Sale Invoice');
                break;
            case 'view-invoices':
                frappe.set_route('List', 'Sale Invoice');
                break;
            case 'sales-report':
                frappe.set_route('query-report', 'Time Period Sales');
                break;
            case 'profit-analysis':
                frappe.set_route('query-report', 'Item Profit Analysis');
                break;

            // Purchases
            case 'add-purchase':
                frappe.new_doc('Tookio Purchase');
                break;
            case 'view-purchases':
                frappe.set_route('List', 'Tookio Purchase');
                break;

            // Subscriptions
            case 'subscriptions':
                window.location.href = '/subscriptions';
                break;

            default:
                console.log('Unknown action:', action);
                frappe.msgprint('Navigation for "' + action + '" not configured yet.');
        }
    } catch (error) {
        console.error('Navigation error:', error);
        frappe.msgprint('Navigation failed: ' + error.message);
    }
};

// Function to load user's full name
function loadUserGreeting() {
    try {
        if (typeof frappe !== 'undefined' && frappe.user && frappe.user.full_name) {
            const fullName = frappe.user.full_name();
            const greetingElement = document.getElementById('userGreeting');
            if (greetingElement && fullName) {
                greetingElement.textContent = `Hi ${fullName}! 👋`;
            }
        }
    } catch (error) {
        console.log('Could not load user name:', error);
        // Fallback to generic greeting
    }
}

// Initialize workspace
document.addEventListener('DOMContentLoaded', function() {
    console.log('TOOKIO workspace loaded successfully!');

    // Load user greeting
    loadUserGreeting();

    // Add subtle hover effects
    var cards = document.querySelectorAll('.card');
    cards.forEach(function(card) {
        // Touch device support
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
        });

        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
});

console.log('TOOKIO workspace script loaded!');