import frappe


def fetch_attachments_from_opportunity(doc, method):
    if doc.custom_opportunity_name != "":
        print("doc.custom_opportunity_name: ", doc.custom_opportunity_name)
        opportunity = frappe.get_doc(
            "Opportunity", {"name": doc.custom_opportunity_name}
        )
        print(opportunity)
        opportunity_attachments = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Opportunity",
                "attached_to_name": opportunity.name,
            },
            fields=["file_name", "file_url"],
        )

        if opportunity_attachments:
            for attachment in opportunity_attachments:
                has_attachment = frappe.db.get_value(
                    "File",
                    {
                        "file_url": attachment.file_url,
                        "attached_to_doctype": "Quotation",
                        "attached_to_name": doc.name,
                    },
                )

                if not has_attachment:
                    opportunity_attachment = frappe.get_doc(
                        {
                            "doctype": "File",
                            "file_name": attachment.file_name,
                            "file_url": attachment.file_url,
                            "attached_to_doctype": "Quotation",
                            "attached_to_name": doc.name,
                        }
                    )

                    opportunity_attachment.insert()
                    opportunity_attachment.reload()
                    print("opportunity_attachment: ", opportunity_attachment)
