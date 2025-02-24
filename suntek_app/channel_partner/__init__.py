import frappe
from frappe.permissions import add_permission


def setup_channel_partner():
    if not frappe.db.exists("Role", "Channel Partner"):
        role = frappe.new_doc("Role")
        role.role_name = "Channel Partner"
        role.desk_access = 1
        role.save(ignore_permissions=True)
        print("Created Channel Partner role")

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
        "Warehouse": {"permissions": ["read", "write"]},
        "Warehouse Type": {"permissions": ["read"]},
        "Sales Order Item": {"permissions": ["read", "write", "create", "delete"]},
        "Item": {"permissions": ["read", "write"]},
        "Subcontracting Order Item": {"permissions": ["read", "write", "create"]},
        "Purchase Order Item": {"permissions": ["read", "write", "create"]},
        "Purchase Invoice Item": {"permissions": ["read", "write", "create"]},
        "Sales Invoice Item": {"permissions": ["read", "write", "create"]},
        "Purchase Receipt Item": {"permissions": ["read", "write", "create"]},
        "BOM Item": {"permissions": ["read", "write", "create"]},
        "BOM": {"permissions", ["read", "write", "create"]},
        "Subcontracting Order": {"permissions": ["read", "write", "create"]},
        "Subcontracting BOM": {"permissions": ["read", "write", "create"]},
        "Subcontracting BOM Item": {"permissions": ["read", "write", "create"]},
    }

    role = "Channel Partner"

    for doctype, config in doctype_permissions.items():
        try:
            existing_perms = frappe.get_all(
                "Custom DocPerm",
                filters={"parent": doctype, "role": role},
                fields=["permlevel", "read", "write", "create", "delete", "if_owner"],
            )

            for ptype in config["permissions"]:
                perm_exists = False
                for perm in existing_perms:
                    if perm.get(ptype):
                        perm_exists = True
                        break

                if not perm_exists:
                    add_permission(doctype, role, permlevel=0, ptype=ptype)
                    print(f"{doctype}: Added {ptype} permission for role {role}")

                    if ptype in config.get("if_owner", []):
                        permission = frappe.get_doc(
                            {
                                "doctype": "Custom DocPerm",
                                "parent": doctype,
                                "role": role,
                                "permlevel": 0,
                                ptype: 1,
                                "if_owner": 1,
                            }
                        )
                        permission.save(ignore_permissions=True)
                        print(f"Added 'Only if Creator' for {ptype} on {doctype}")

            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Error setting up permissions for {doctype}: {str(e)}")


def setup_channel_partner_parent_warehouse_type():
    if not frappe.db.exists("Warehouse Type", "Channel Partner"):
        warehouse_type = frappe.new_doc("Warehouse Type")
        warehouse_type.name = "Channel Partner"
        warehouse_type.save()
        frappe.db.commit()
        print("Created Channel Partner warehouse type")


def setup_channel_partner_parent_warehouse():
    warehouse_name = "Channel Partner Parent - SESP"
    if not frappe.db.exists(
        "Warehouse",
        {
            "name": warehouse_name,
            "is_group": 1,
        },
    ):
        wh = frappe.new_doc("Warehouse")
        wh.warehouse_name = "Channel Partner Parent"
        wh.company = "Suntek Energy Systems Pvt. Ltd."
        wh.is_group = 1
        wh.warehouse_type = "Channel Partner"
        wh.save(ignore_permissions=True)
        frappe.db.commit()
        print(f"Created Channel Partner Parent Warehouse: {wh.name}")
