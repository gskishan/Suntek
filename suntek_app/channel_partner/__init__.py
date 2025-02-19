import frappe
from frappe.permissions import add_permission


def setup_channel_partner():
    if not frappe.db.exists("Role", "Channel Partner"):
        role = frappe.new_doc("Role")
        role.role_name = "Channel Partner"
        role.desk_access = 1
        role.save(ignore_permissions=True)

    doctype_permissions = {
        "Channel Partner": {
            "permissions": ["read", "write", "create", "delete"],
        },
        "Customer": {
            "permissions": ["read", "write", "create"],
        },
        "Lead": {
            "permissions": ["read", "write", "create"],
        },
        "Opportunity": {
            "permissions": ["read", "write", "create"],
        },
        "Discom": {
            "permissions": ["read", "write", "create"],
            "if_owner": ["write"],
        },
    }

    role = "Channel Partner"

    for doctype, config in doctype_permissions.items():
        try:
            for ptype in config["permissions"]:
                add_permission(doctype, role, permlevel=0, ptype=ptype)
                print(f"{doctype}: Permission {ptype} set for role {role}")

                if ptype in config.get("if_owner", []):
                    permission = frappe.get_doc(
                        {
                            "doctype": "Custom DocPerm",
                            "parent": doctype,
                            "role": role,
                            "permlevel": 0,
                            ptype: 1,
                        }
                    )

                    if permission:
                        permission.if_owner = 1
                        permission.save(ignore_permissions=True)
                        print(
                            f"'Only if Creator' enabled for {ptype} permission on {doctype} for role {role}"
                        )

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Error setting up permissions for {doctype}: {str(e)}")
