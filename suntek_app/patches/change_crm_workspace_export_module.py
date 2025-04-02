import frappe


def execute():
    workspace = frappe.get_doc("Workspace", "CRM")

    if workspace:
        if workspace.module != "CRM":
            workspace.module = "CRM"
            workspace.save(ignore_permissions=True)
            frappe.db.commit()
            print("Successfully changed export module of CRM workspace from 'suntek' to 'CRM'")
    else:
        print("CRM workspace not found")
