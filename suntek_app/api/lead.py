import frappe

from suntek_app.suntek.utils.api_handler import (
    create_api_response,
    parse_request_data,
    validate_auth_token,
)
from suntek_app.suntek.utils.validation_utils import validate_mobile_number


@frappe.whitelist(allow_guest=True)
def create_lead_from_ambassador():
    if frappe.request.headers.get(
        "X-Django-Server-Authorization"
    ) and validate_auth_token(
        frappe.request.headers.get("X-Django-Server-Authorization")
    ):
        if not frappe.request.method == "POST":
            return create_api_response(405, "method not allowed", "Method Not Allowed")

        frappe.set_user("Administrator")

        data = parse_request_data(frappe.request.data)

        first_name = data.get("first_name")
        mobile_no = data.get("mobile_number")

        if not first_name or not mobile_no:
            return create_api_response(
                400, "bad request", "Missing Name or Mobile Number"
            )

        if not validate_mobile_number(mobile_no):
            return create_api_response(400, "bad_request", "Invalid Mobile Number")

        last_name = data.get("last_name")
        email_id = data.get("email")

        lead = frappe.new_doc("Lead")

        # lead_owner = get_next_telecaller()

        lead.update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "mobile_no": mobile_no,
                "email_id": email_id,
                "source": "Ambassador",
                # "lead_owner": lead_owner,
            }
        )

        lead.save()
        frappe.db.commit()

        return create_api_response(
            201, "created", "Lead created successfully", data=data
        )

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")
