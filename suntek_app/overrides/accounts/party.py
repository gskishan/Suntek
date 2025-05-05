import frappe
from erpnext.accounts.party import _get_party_details


@frappe.whitelist()
def get_party_details(
    party=None,
    account=None,
    party_type="Customer",
    company=None,
    posting_date=None,
    bill_date=None,
    price_list=None,
    currency=None,
    doctype=None,
    ignore_permissions=False,
    fetch_payment_terms_template=True,
    party_address=None,
    company_address=None,
    shipping_address=None,
    dispatch_address=None,
    pos_profile=None,
):
    if not party:
        return frappe._dict()
    if not frappe.db.exists(party_type, party):
        frappe.throw(frappe._("{0}: {1} does not exist").format(party_type, party))

    result = _get_party_details(
        party,
        account,
        party_type,
        company,
        posting_date,
        bill_date,
        price_list,
        currency,
        doctype,
        ignore_permissions,
        fetch_payment_terms_template,
        party_address,
        company_address,
        shipping_address,
        dispatch_address,
        pos_profile,
    )

    if party_type == "Customer":
        result["territory"] = ""
    return result
