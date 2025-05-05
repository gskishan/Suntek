import frappe

from suntek_app.suntek.utils.share import share_document


def execute():
    print("PATCH: Sharing Leads to Lead Owners")

    integrated_leads = frappe.get_all(
        "Lead",
        filters={"source": ["in", ["Ambassador", "Just Dial"]]},
        fields=["name", "first_name", "mobile_no", "source"],
    )

    leads_shared = 0
    unshaed_leads = 0
    leads_shared_after_patch = 0
    leads_unshared_after_patch = 0

    for lead in integrated_leads:
        lead_doc = frappe.get_doc("Lead", lead.name)
        existing_docshare = frappe.db.exists(
            "DocShare",
            {
                "share_doctype": "Lead",
                "share_name": lead_doc.name,
                "user": lead_doc.lead_owner,
            },
        )

        if existing_docshare:
            leads_shared += 1

        if not existing_docshare:
            unshaed_leads += 1

            shared_doc = share_document(
                doctype="Lead",
                doc_name=lead.name,
                user_email=lead.lead_owner,
                read=1,
                write=1,
                share=1,
                notify=0,
            )

            if shared_doc:
                leads_shared_after_patch += 1
                print(f"Shared {lead_doc.name} with {lead_doc.lead_owner}.")
            else:
                leads_unshared_after_patch += 1
                print(f"Lead {lead_doc.name} not shared.")

        else:
            print(f"Lead {lead_doc.name} was already shared")

    print(f"Leads shared before patch: {leads_shared}")
    print(f"Leads unshared before patch: {unshaed_leads}")
    print(f"Leads shared after patch: {leads_shared_after_patch}")
    print(f"Leads unshared after patch: {leads_unshared_after_patch}")
