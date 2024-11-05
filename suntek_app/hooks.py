from . import __version__ as app_version

app_name = "suntek_app"
app_title = "suntek"
app_publisher = "kishan"
app_description = "custom_app"
app_email = "gskishan"
app_license = "123"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/suntek_app/css/suntek_app.css"
# app_include_js = "/assets/suntek_app/js/suntek_app.js"

# include js, css files in header of web template
# web_include_css = "/assets/suntek_app/css/suntek_app.css"
# web_include_js = "/assets/suntek_app/js/suntek_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "suntek_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {
    "Lead" : "public/js/lead.js",
    "Opportunity" : "public/js/opportunity.js",
    "Quotation" : "public/js/quotation.js",
    "Product Bundle" : "public/js/product_bundle.js",
    "Project" : "public/js/project.js",
    "Sales Order": "public/js/sales_order.js",
    "Customer": "public/js/customer.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Material Request": "public/js/material_request.js",
    "Stock Entry": "public/js/stock_entry.js",
  "BOM": "public/js/bom.js",
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
#	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
#	"methods": "suntek_app.utils.jinja_methods",
#	"filters": "suntek_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "suntek_app.install.before_install"
# after_install = "suntek_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "suntek_app.uninstall.before_uninstall"
# after_uninstall = "suntek_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "suntek_app.utils.before_app_install"
# after_app_install = "suntek_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "suntek_app.utils.before_app_uninstall"
# after_app_uninstall = "suntek_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "suntek_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes
override_doctype_dashboards = {
	"Opportunity": "suntek_app.suntek.custom_dashboard.dashboard.update_opportunity_dashboard",
    "Lead": "suntek_app.suntek.custom_dashboard.dashboard.update_enquiry_dashboard",
}



override_doctype_class = {
	"Contact": "suntek_app.suntek.custom.contact.CustomContact",
	"Quotation": "suntek_app.custom_script.quotation.CustomQuotation",
	"Salary Slip": "suntek_app.custom_script.salary_slip.CustomSalarySlip",
}

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Lead": {
        "validate": ["suntek_app.suntek.custom.lead.change_enquiry_status",
                    "suntek_app.suntek.custom.lead.set_enquiry_name"]

    },
    "Opportunity": {
        "validate": ["suntek_app.suntek.custom.opportunity.change_opportunity_status",
                    "suntek_app.suntek.custom.opportunity.set_opportunity_name"],
	    "on_update":  "suntek_app.custom_script.opportunity.on_update"
	    
    },
    "Sales Order": {
        "on_submit":"suntek_app.suntek.custom.sales_order.auto_project_creation_on_submit",
	# "validate":"suntek_app.suntek.custom.sales_order.validate"
    },
   "Project": {
        "on_update":"suntek_app.suntek.custom.project.on_update",
	"validate":"suntek_app.suntek.custom.project.validate"
    },
    "Price List": {
	        "validate" : "suntek_app.custom_script.price_list.validate"
    },
	"Item Price": {
	        "validate" : "suntek_app.custom_script.item_price.validate"
    },
    "Quotation": {
		"validate":  "suntek_app.custom_script.quotation.validate",
	},
	"Employee": {
		"on_update":  "suntek_app.custom_script.employee.on_update",
	},
	"Stock Entry": {
        "on_submit":"suntek_app.suntek.custom.stock_entry.on_submit",
	"on_cancel":"suntek_app.suntek.custom.stock_entry.on_cancel"
    },

}   

# doc_events = {
#	"*": {
#		"on_update": "method",
#		"on_cancel": "method",
#		"on_trash": "method"
#	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#	"all": [
#		"suntek_app.tasks.all"
#	],
#	"daily": [
#		"suntek_app.tasks.daily"
#	],
#	"hourly": [
#		"suntek_app.tasks.hourly"
#	],
#	"weekly": [
#		"suntek_app.tasks.weekly"
#	],
#	"monthly": [
#		"suntek_app.tasks.monthly"
#	],
# }

# Testing
# -------

# before_tests = "suntek_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
#	"frappe.desk.doctype.event.event.get_events": "suntek_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
#	"Task": "suntek_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["suntek_app.utils.before_request"]
# after_request = ["suntek_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["suntek_app.utils.before_job"]
# after_job = ["suntek_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
#	{
#		"doctype": "{doctype_1}",
#		"filter_by": "{filter_by}",
#		"redact_fields": ["{field_1}", "{field_2}"],
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_2}",
#		"filter_by": "{filter_by}",
#		"partial": 1,
#	},
#	{
#		"doctype": "{doctype_3}",
#		"strict": False,
#	},
#	{
#		"doctype": "{doctype_4}"
#	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
#	"suntek_app.auth.validate"
# ]


fixtures = [
    "Custom Field"
]
