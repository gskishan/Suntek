import frappe
from frappe.permissions import add_permission


def setup_channel_partner():
    if not frappe.db.exists("Role", "Channel Partner"):
        role = frappe.new_doc("Role")
        role.role_name = "Channel Partner"
        role.desk_access = 1
        role.save(ignore_permissions=True)

    doctype_permissions = {
        "Channel Partner": ["read", "write", "create", "delete"],
        "Customer": ["read", "write", "create"],
        "Lead": ["read", "write", "create"],
        "Opportunity": ["read", "write", "create"],
    }

    role = "Channel Partner"

    for doctype, permissions in doctype_permissions.items():
        try:
            for ptype in permissions:
                add_permission(doctype, role, permlevel=0, ptype=ptype)

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Error setting up permissions for {doctype}: {str(e)}")


def before_migrate():
    setup_channel_partner()
