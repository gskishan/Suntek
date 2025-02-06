import frappe
from frappe.share import add as add_share


def share_document(doctype, doc_name, user_email):
    """Share document with agent if not already shared"""
    try:
        existing_share = frappe.get_all(
            "DocShare",
            filters={
                "share_doctype": doctype,
                "share_name": doc_name,
                "user": user_email,
            },
            limit=1,
        )

        if existing_share:
            return True

        add_share(
            doctype=doctype,
            name=doc_name,
            user=user_email,
            read=1,
            write=1,
            submit=0,
            share=1,
            everyone=0,
            notify=1,
        )

        frappe.db.commit()
        return True
    except Exception as e:
        frappe.log_error(
            f"Error sharing {doctype} {doc_name} with {user_email}: {str(e)}",
            f"{doctype} Sharing Error",
        )
        return False
