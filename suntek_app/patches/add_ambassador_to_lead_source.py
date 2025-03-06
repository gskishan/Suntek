import frappe


def execute():
    lead_source = frappe.new_doc("Lead Source")

    lead_source.name = "Ambassador"
    lead_source.source_name = "Ambassador"

    lead_source.save()
    frappe.db.commit()

    print("Created Lead Source: Ambassador")
