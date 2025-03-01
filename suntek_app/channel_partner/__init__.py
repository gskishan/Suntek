import frappe
from frappe.permissions import add_permission


def setup_channel_partner():
    role_exists = frappe.db.exists("Role", "Channel Partner")

    if not role_exists:
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
        "Sales Order": {
            "permissions": ["read", "write", "create", "delete"],
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
        "BOM": {"permissions": ["read", "write", "create"]},
        "Subcontracting Order": {"permissions": ["read", "write", "create"]},
        "Subcontracting BOM": {"permissions": ["read", "write", "create"]},
        "Subcontracting BOM Item": {"permissions": ["read", "write", "create"]},
    }

    role = "Channel Partner"

    for doctype in doctype_permissions.keys():
        frappe.db.delete("Custom DocPerm", {"parent": doctype, "role": role})

    for doctype, config in doctype_permissions.items():
        try:
            permission = frappe.new_doc("Custom DocPerm")
            permission.parent = doctype
            permission.role = role
            permission.permlevel = 0

            permission.read = 0
            permission.write = 0
            permission.create = 0
            permission.delete = 0
            permission.export = 1

            for ptype in config["permissions"]:
                setattr(permission, ptype, 1)

            if "if_owner" in config:
                permission.if_owner = 1

            permission.save(ignore_permissions=True)
            frappe.db.commit()

        except Exception as e:
            frappe.log_error(f"Error managing permission for {doctype}: {str(e)}")
            print(f"Error managing permission for {doctype}: {str(e)}")


def setup_channel_partner_parent_warehouse_type():
    if not frappe.db.exists("Warehouse Type", "Channel Partner"):
        warehouse_type = frappe.new_doc("Warehouse Type")
        warehouse_type.name = "Channel Partner"
        warehouse_type.save()
        frappe.db.commit()


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
