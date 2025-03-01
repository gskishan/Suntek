import frappe


def set_channel_partner_data_in_bom(doc, method):
    if doc.project:
        project = frappe.get_doc("Project", doc.project)

        doc.custom_channel_partner = (
            project.custom_channel_partner if project.custom_channel_partner else None
        )
