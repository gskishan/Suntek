app_name = "suntek_app"
app_title = "suntek"
app_publisher = "kishan"
app_description = "custom_app"
app_email = "gskishan"
app_license = "123"

page_js = {"lead_funnel": "public/js/lead_funnel.js"}


doctype_js = {
    "Item": "public/js/item.js",
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

override_whitelisted_methods = {
    # "erpnext.stock.get_item_details.apply_price_list": "suntek_app.overrides.get_item_details.apply_price_list"
    "erpnext.stock.get_item_details.apply_price_list": "suntek_app.overrides.get_item_details.apply_price_list_for_solar_panel",
}


override_doctype_dashboards = {
    "Opportunity": "suntek_app.suntek.custom_dashboard.dashboard.update_opportunity_dashboard",
    "Lead": "suntek_app.suntek.custom_dashboard.dashboard.update_enquiry_dashboard",
}


override_doctype_class = {
    "Contact": "suntek_app.suntek.custom.contact.CustomContact",
    "Quotation": "suntek_app.custom_script.quotation.CustomQuotation",
    "Salary Slip": "suntek_app.custom_script.salary_slip.CustomSalarySlip",
}

permission_query_conditions = {
    "Lead": "suntek_app.permissions.lead.get_permission_query_conditions",
    "Opportunity": "suntek_app.permissions.opportunity.get_permission_query_conditions",
    "Quotation": "suntek_app.permissions.quotation.get_permission_query_conditions",
    "Sales Order": "suntek_app.permissions.sales_order.get_permission_query_conditions",
}

has_permission = {
    "Lead": "suntek_app.permissions.lead.has_permission",
    "Opportunity": "suntek_app.permissions.opportunity.has_permission",
    "Quotation": "suntek_app.permissions.quotation.has_permission",
    "Sales Order": "suntek_app.permissions.sales_order.has_permission",
}

doc_events = {
    "Address": {"before_save": ["suntek_app.custom_script.address.add_enquiry_to_links"]},
    "Delivery Note": {
        "before_save": [
            "suntek_app.custom_script.delivery_note.set_channel_partner_data",
        ]
    },
    "Installation Note": {"before_save": ["suntek_app.custom_script.installation_note.set_channel_partner_data"]},
    "BOM": {
        "before_save": [
            "suntek_app.custom_script.bom.set_channel_partner_data",
        ]
    },
    "Item": {"before_save": ["suntek_app.overrides.item.set_item_code_from_item_id"]},
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
            "suntek_app.api.webhook_handler.send_ambassador_status_update",
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
            "suntek_app.api.webhook_handler.send_ambassador_status_update",
        ],
        "after_insert": [
            "suntek_app.suntek.utils.neodove_utils.neodove_integration.send_to_neodove",
        ],
    },
    "Sales Order": {
        "on_submit": "suntek_app.suntek.custom.sales_order.auto_project_creation_on_submit",
        "on_update": [
            "suntek_app.api.webhook_handler.send_ambassador_status_update",
            "suntek_app.event_handlers.sales_order_event_handler.update_cppo_from_sales_order",
        ],
        "after_save": [
            "suntek_app.event_handlers.sales_order_event_handler.update_cppo_from_sales_order",
        ],
    },
    "Project": {
        "validate": "suntek_app.suntek.custom.project.validate",
        "before_save": ["suntek_app.suntek.custom.project.get_channel_partner_data"],
    },
    "Price List": {"validate": "suntek_app.custom_script.price_list.validate"},
    "Item Price": {"validate": "suntek_app.custom_script.item_price.validate"},
    "Quotation": {
        "validate": "suntek_app.custom_script.quotation.validate",
        "on_update": [
            "suntek_app.api.webhook_handler.send_ambassador_status_update",
        ],
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


fixtures = [
    {"doctype": "Warehouse Type", "filters": {"name": "Channel Partner"}},
    {
        "doctype": "Role",
        "filters": [
            [
                "name",
                "in",
                [
                    "Channel Partner",
                    "Channel Partner Manager",
                    "Sales Order Report User",
                    "Solar Power Plant Manager",
                ],
            ]
        ],
    },
    {
        "doctype": "Custom DocPerm",
        "filters": [
            [
                "role",
                "in",
                [
                    "Channel Partner",
                    "Channel Partner Manager",
                    "Sales Order Report User",
                    "Solar Power Plant Manager",
                ],
            ]
        ],
    },
    {
        "doctype": "Property Setter",
        "filters": [["name", "in", ["Sales Order-order_type-options"]]],
    },
    {
        "doctype": "Module Profile",
        "filters": [
            ["name", "=", "Channel Partner"],
        ],
    },
    {"doctype": "Stock Entry Type", "filters": [["name", "=", "Material Transfer to Channel Partner"]]},
]

website_route_rules = [
    {"from_route": "/dashboard/<path:app_path>", "to_route": "dashboard"},
]
