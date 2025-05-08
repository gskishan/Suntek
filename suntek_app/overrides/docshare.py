import frappe


def share_opportunity_with_designer(doc, method):
    """
    Checks if a doc is a Sales order.
    If it is a sales order, then it shares the opportunity to the users with whom the Sales Order is shared.
    """

    if doc.share_doctype == "Sales Order":
        sales_order = frappe.get_doc("Sales Order", {"name": doc.share_name})
        opportunity = sales_order.custom_opportunity_name
        if opportunity:
            opportunity_doc = frappe.get_doc("Opportunity", opportunity)

            if not frappe.db.exists(
                "DocShare",
                {
                    "share_doctype": "Opportunity",
                    "share_name": opportunity_doc.name,
                    "user": doc.user,
                },
            ):
                opportunity_docshare = frappe.new_doc("DocShare")

                opportunity_docshare.share_doctype = "Opportunity"
                opportunity_docshare.share_name = opportunity_doc.name
                opportunity_docshare.user = doc.user
                opportunity_docshare.read = doc.read
                opportunity_docshare.write = doc.write
                opportunity_docshare.share = doc.share
                opportunity_docshare.submit = 0
                opportunity_docshare.notify_by_email = 1

                opportunity_docshare.insert()
