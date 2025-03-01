app_name = "suntek_app"
app_title = "suntek"
app_publisher = "kishan"
app_description = "custom_app"
app_email = "gskishan"
app_license = "123"

page_js = {"lead_funnel": "public/js/lead_funnel.js"}


doctype_js = {
    "Lead": "public/js/lead.js",
    "Opportunity": "public/js/opportunity.js",
    "Quotation": "public/js/quotation.js",
    "Product Bundle": "public/js/product_bundle.js",
    "Project": "public/js/project.js",
    "Sales Order": "public/js/sales_order.js",
    "Customer": "public/js/customer.js",
    "Delivery Note": "public/js/delivery_note.js",
    "Material Request": "public/js/material_request.js",
    "Stock Entry": "public/js/stock_entry.js",
    "BOM": "public/js/bom.js",
    "Channel Partner": "public/js/channel_partner_dashboard.js",
}

before_install = "suntek_app.install.before_install"

before_migrate = "suntek_app.migrate.before_migrate"
after_migrate = "suntek_app.migrate.after_migrate"

# override_whitelisted_methods = {
#     "erpnext.selling.doctype.sales_order.sales_order.make_sales_invoice": "suntek_app.overrides.sales_order.make_sales_invoice"
# }

override_doctype_dashboards = {
    "Opportunity": "suntek_app.suntek.custom_dashboard.dashboard.update_opportunity_dashboard",
    "Lead": "suntek_app.suntek.custom_dashboard.dashboard.update_enquiry_dashboard",
}


override_doctype_class = {
    "Contact": "suntek_app.suntek.custom.contact.CustomContact",
    "Quotation": "suntek_app.custom_script.quotation.CustomQuotation",
    "Salary Slip": "suntek_app.custom_script.salary_slip.CustomSalarySlip",
}
doc_events = {
    "Address": {
        "before_save": ["suntek_app.custom_script.address.add_enquiry_to_links"]
    },
    "Delivery Note": {
        "before_save": [
            "suntek_app.custom_script.delivery_note.set_channel_partner_data"
        ]
    },
    "Installation Note": {
        "before_save": [
            "suntek_app.custom_script.installation_note.set_channel_partner_data"
        ]
    },
    "BOM": {
        "before_save": [
            "suntek_app.custom_script.bom.set_channel_partner_data",
        ]
    },
    "Lead": {
        "validate": [
            "suntek_app.suntek.custom.lead.change_enquiry_status",
            "suntek_app.suntek.custom.lead.set_enquiry_name",
        ],
        "before_save": [
            "suntek_app.suntek.custom.lead.validate_enquiry_mobile_no",
            "suntek_app.suntek.custom.lead.change_enquiry_status",
            "suntek_app.suntek.custom.lead.set_lead_owner",
            "suntek_app.suntek.custom.lead.share_lead_after_insert_with_enquiry_owner",
            "suntek_app.suntek.custom.lead.set_state",
        ],
        "on_update": [
            "suntek_app.suntek.utils.neodove_utils.neodove_integration.send_to_neodove",
            "suntek_app.suntek.page.lead_funnel.lead_funnel.clear_cache",
            "suntek_app.suntek.custom.lead.save_name_changes_to_contact",
        ],
        "after_insert": [
            "suntek_app.suntek.utils.neodove_utils.neodove_integration.send_to_neodove",
            "suntek_app.suntek.page.lead_funnel.lead_funnel.clear_cache",
        ],
    },
    "Opportunity": {
        "validate": [
            "suntek_app.suntek.custom.opportunity.change_opportunity_status",
            "suntek_app.suntek.custom.opportunity.set_opportunity_name",
        ],
        "before_save": [
            "suntek_app.suntek.custom.opportunity.set_location_data",
        ],
        "on_update": [
            "suntek_app.suntek.utils.neodove_utils.neodove_integration.send_to_neodove",
        ],
        "after_insert": [
            "suntek_app.suntek.utils.neodove_utils.neodove_integration.send_to_neodove",
        ],
    },
    "Sales Order": {
        "on_submit": "suntek_app.suntek.custom.sales_order.auto_project_creation_on_submit",
    },
    "Project": {
        "validate": "suntek_app.suntek.custom.project.validate",
        # "before_save": ["suntek_app.suntek.custom.project.get_channel_partner_data"],
    },
    "Price List": {"validate": "suntek_app.custom_script.price_list.validate"},
    "Item Price": {"validate": "suntek_app.custom_script.item_price.validate"},
    "Quotation": {
        "validate": "suntek_app.custom_script.quotation.validate",
    },
    "Employee": {
        "on_update": "suntek_app.custom_script.employee.on_update",
    },
    "Stock Entry": {
        "on_submit": "suntek_app.suntek.custom.stock_entry.on_submit",
        "on_cancel": "suntek_app.suntek.custom.stock_entry.on_cancel",
    },
    "Solar Power Plants": {
        "on_update": [
            "suntek_app.suntek.custom.solar_power_plants.handle_solar_ambassador_webhook",
        ],
    },
    "Issue": {
        "on_update": [
            "suntek_app.suntek.custom.issue.send_issue_update_to_ambassador_api",
        ]
    },
}

fixtures = [{"doctype": "Warehouse Type", "filters": {"name": "Channel Partner"}}]


# fixtures = [
#     {"doctype": "Custom Field"},
#     {"doctype": "Property Setter"},
#     {"doctype": "Client Script"},
#     {"doctype": "Server Script"},
#     {"doctype": "Print Format"},
#     {"doctype": "Report", "filters": {"is_standard": "No"}},
#     {"doctype": "Web Form"},
#     {"doctype": "Workflow", "filters": {"is_active": 1}},
#     {"doctype": "Workflow State"},
#     {"doctype": "Workflow Action Master"},
#     {"doctype": "Notification"},
#     {"doctype": "Webhook"},
#     {"doctype": "HD Ticket Type"},
#     {"doctype": "Lead Source", "filters": {"source_name": "Channel Partner"}},
# ]
