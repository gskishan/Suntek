import frappe
from frappe.share import add as add_share


def share_document(
    doctype,
    doc_name,
    user_email,
    read: int = 0,
    write: int = 0,
    submit: int = 0,
    share: int = 0,
    everyone: int = 0,
    notify: int = 0,
):
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
            read=read or 0,
            write=write or 0,
            submit=submit or 0,
            share=share or 0,
            everyone=everyone or 0,
            notify=notify or 0,
        )

        return True
    except Exception as e:
        frappe.log_error(
            f"Error sharing {doctype} {doc_name} with {user_email}: {str(e)}",
            f"{doctype} Sharing Error",
        )
        return False
