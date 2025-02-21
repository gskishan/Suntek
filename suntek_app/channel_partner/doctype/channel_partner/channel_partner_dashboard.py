import frappe


@frappe.whitelist()
def get_dashboard_data(channel_partner):
    data = {
        "open_sales_orders": 0,
        "total_sales_orders": 0,
        "open_opportunities": 0,
        "total_opportunities": 0,
        "open_leads": 0,
        "total_leads": 0,
        "recent_orders": [],
    }

    data["open_sales_orders"] = frappe.db.count(
        "Sales Order",
        {
            "custom_channel_partner": channel_partner,
            "docstatus": 1,
            "status": ["not in", ["Completed", "Closed"]],
        },
    )
    data["total_sales_orders"] = frappe.db.count(
        "Sales Order", {"custom_channel_partner": channel_partner, "docstatus": 1}
    )

    data["open_opportunities"] = frappe.db.count(
        "Opportunity",
        {
            "custom_channel_partner": channel_partner,
            "status": [
                "not in",
                ["Closed", "Quotation", "Customer Confirmed", "Converted"],
            ],
        },
    )
    data["total_opportunities"] = frappe.db.count(
        "Opportunity", {"custom_channel_partner": channel_partner}
    )

    data["open_leads"] = frappe.db.count(
        "Lead",
        {
            "custom_channel_partner": channel_partner,
            "status": ["not in", ["Converted", "Do Not Contact", "Quotation"]],
        },
    )
    data["total_leads"] = frappe.db.count(
        "Lead", {"custom_channel_partner": channel_partner}
    )

    data["recent_orders"] = frappe.get_all(
        "Sales Order",
        filters={"custom_channel_partner": channel_partner, "docstatus": 1},
        fields=["name", "transaction_date", "grand_total", "status"],
        order_by="transaction_date desc",
        limit=5,
    )

    return data
