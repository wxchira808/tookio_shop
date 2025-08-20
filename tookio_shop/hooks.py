app_name = "tookio_shop"
app_title = "Tookio Shop"
app_publisher = "Tookio"
app_description = "A simple system for whatsapp and instagram based online sellers to be able to track their sales, create sales invoices and also track stock for their items."
app_email = "bwkinyua01@gmail.com"
app_license = "mit"



# This tells Frappe to load our custom JS file on all website pages, including login
# web_include_js = "/assets/tookio_shop/js/signup.js"

# This tells Frappe to use our custom signup form template
# signup_form_template = "tookio_shop/templates/pages/signup.html"

# This tells Frappe to use our Python function instead of the default one
# override_whitelisted_methods = {
# 	"frappe.core.doctype.user.user.sign_up": "tookio_shop.overrides.user.sign_up"
# }

doc_events = {
      "User": {
        "after_insert": "tookio_shop.utils.setup_new_user"
    },
    "Product": {
        "before_insert": "tookio_shop.utils.check_item_limit"
    },
    "Shop": {
        "before_insert": "tookio_shop.utils.check_shop_limit"
    },
    "Sale Invoice": {
        "validate": "tookio_shop.utils.prevent_negative_stock"
    },
    # Removed Product Stock after_insert hook to fix AttributeError
}

fixtures = [
    {
        "dt": "Custom DocPerm"
    },
     {
        "dt": "Workspace",
        "filters": [
            ["name", "in", [
                "Tookio"

           ]]
        ]
    }
]

# Override login page
# Note: Frappe serves pages placed in templates/pages/<name>.html automatically at /<name>.
# The custom route rule previously pointed to a non-page path and caused 404s. We now provide
# templates/pages/login.html so /login will be served without a custom rule.
# website_route_rules = [
#    {"from_route": "/login", "to_route": "tookio_shop/templates/login"}
# ]

# Add custom JS
# signup JS removed; no app-level web_include_js so default Frappe pages remain unchanged


default_module_profile = "Default Restricted Profile"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "tookio_shop",
# 		"logo": "/assets/tookio_shop/logo.png",
# 		"title": "Tookio Shop",
# 		"route": "/tookio_shop",
# 		"has_permission": "tookio_shop.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/tookio_shop/css/tookio_shop.css"
# app_include_js = "/assets/tookio_shop/js/tookio_shop.js"

# include js, css files in header of web template
# web_include_css = "/assets/tookio_shop/css/tookio_shop.css"
# web_include_js = "/assets/tookio_shop/js/tookio_shop.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "tookio_shop/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "tookio_shop/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "tookio_shop.utils.jinja_methods",
# 	"filters": "tookio_shop.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "tookio_shop.install.before_install"
# after_install = "tookio_shop.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "tookio_shop.uninstall.before_uninstall"
# after_uninstall = "tookio_shop.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "tookio_shop.utils.before_app_install"
# after_app_install = "tookio_shop.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "tookio_shop.utils.before_app_uninstall"
# after_app_uninstall = "tookio_shop.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "tookio_shop.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"tookio_shop.tasks.all"
# 	],
# 	"daily": [
# 		"tookio_shop.tasks.daily"
# 	],
# 	"hourly": [
# 		"tookio_shop.tasks.hourly"
# 	],
# 	"weekly": [
# 		"tookio_shop.tasks.weekly"
# 	],
# 	"monthly": [
# 		"tookio_shop.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "tookio_shop.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "tookio_shop.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "tookio_shop.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["tookio_shop.utils.before_request"]
# after_request = ["tookio_shop.utils.after_request"]

# Job Events
# ----------
# before_job = ["tookio_shop.utils.before_job"]
# after_job = ["tookio_shop.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"tookio_shop.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

