import frappe


def execute():
    try:
        channel_partner_exists = frappe.db.exists("Customer Group", "Channel Partner")

        if not channel_partner_exists:
            customer_group = frappe.new_doc("Customer Group")
            customer_group.customer_group_name = "Channel Partner"
            customer_group.parent_customer_group = "All Customer Groups"

            customer_group.save()
            frappe.db.commit()
            print("Channel Partner customer group created successfully")
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(
            f"Failed to create Channel Partner customer group: {str(e)}",
            "Customer Group Creation Error",
        )
