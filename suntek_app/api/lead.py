import frappe

from suntek_app.suntek.utils.api_handler import (
    create_api_response,
    parse_request_data,
    validate_auth_token,
)


@frappe.whitelist(allow_guest=True)
def create_lead_from_ambassador():
    if frappe.request.headers.get(
        "X-Django-Server-Authorization"
    ) and validate_auth_token(
        frappe.request.headers.get("X-Django-Server-Authorization")
    ):
        if not frappe.request.method == "POST":
            return create_api_response(405, "method not allowed", "Method Not Allowed")

        data = parse_request_data(frappe.request.data)

        return create_api_response(
            201, "created", "Lead created successfully", data=data
        )

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")
