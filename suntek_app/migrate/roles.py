import frappe


def create_sales_order_report_user():
    try:
        so_report_user = frappe.db.exists("Role", "Sales Order Report User")
        so_report_user_perms = frappe.db.exists(
            "Custom DocPerm", {"role": "Sales Order Report User"}
        )
        if so_report_user_perms:
            frappe.db.delete("Custom DocPerm", {"role": "Sales Order Report User"})
            print("Deleted Permissions for Sales Order Report User")

        if so_report_user:
            frappe.db.delete("Role", "Sales Order Report User")
            print("Deleted Role Sales Order Report User")

        if not so_report_user:
            role = frappe.new_doc("Role")
            role.role_name = "Sales Order Report User"
            role.desk_access = 1
            role.save(ignore_permissions=True)

        if not so_report_user_perms:
            perms = frappe.new_doc("Custom DocPerm")
            perms.role = "Sales Order Report User"
            perms.parent = "Sales Order"
            perms.permlevel = 0

            perms.report = 1
            perms.read = 0
            perms.write = 0
            perms.export = 1
            perms.email = 1

            perms.save(ignore_permissions=True)

        frappe.db.commit()
    except Exception as e:
        frappe.log_error(
            "Permission Creation Error",
            f"{str(e)} Error during creating Sales Order Report User role and permissions",
            reference_doctype="Role",
        )
