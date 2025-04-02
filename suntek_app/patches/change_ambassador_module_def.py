import frappe


def execute():
    if frappe.db.exists("DocType", "Ambassador"):
        doc = frappe.get_doc("DocType", "Ambassador")

        if doc.module != "suntek":
            doc.module = "suntek"
            doc.save()
