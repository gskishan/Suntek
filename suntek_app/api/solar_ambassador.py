import frappe

from suntek.utils.api_handler import create_api_response


@frappe.whitelist(allow_guest=True)
def create_ambassador():
    return create_api_response(
        200,
        "success",
        "success",
    )
