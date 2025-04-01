import frappe


def execute():
    if frappe.db.exists("DocType", "Ambassador"):
        doc = frappe.get_doc("DocType", "Ambassador")
        doc.module = "suntek"
        doc.save()
