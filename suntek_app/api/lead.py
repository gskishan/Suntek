import frappe

from suntek_app.suntek.utils.api_handler import (
    create_api_response,
    parse_request_data,
    validate_auth_token,
)
from suntek_app.suntek.utils.lead_utils import get_next_telecaller
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

        frappe.set_user("developer@suntek.co.in")

        data = parse_request_data(frappe.request.data)

        first_name = data.get("first_name")
        mobile_no = data.get("mobile_number")

        ambassador_mobile_no = data.get("ambassador_mobile_no")
        ambassador_name = data.get("ambassador_name")

        ambassador_data = data.get("ambassador_data", {})

        if not first_name or not mobile_no or not ambassador_mobile_no:
            return create_api_response(
                400,
                "bad request",
                "Missing Name or Mobile Number or Ambassador Mobile Number",
            )

        if not validate_mobile_number(mobile_no):
            return create_api_response(400, "bad_request", "Invalid Mobile Number")

        existing_lead = frappe.db.get_value(
            "Lead", {"mobile_no": mobile_no}, ["name"], as_dict=1
        )
        if existing_lead:
            return create_api_response(
                409,
                "duplicate",
                f"Lead with mobile number {mobile_no} already exists",
                data={"existing_lead_id": existing_lead},
            )

        last_name = data.get("last_name")
        email_id = data.get("email")

        try:
            ambassador_result = get_or_create_ambassador(
                ambassador_mobile_no, ambassador_name, ambassador_data
            )
            ambassador_id = ambassador_result["name"]
            ambassador_created = ambassador_result["created"]
        except Exception as e:
            return create_api_response(400, "bad request", str(e))

        lead = frappe.new_doc("Lead")
        lead_owner = get_next_telecaller()

        lead.update(
            {
                "first_name": first_name,
                "last_name": last_name,
                "mobile_no": mobile_no,
                "email_id": email_id,
                "source": "Ambassador",
                "lead_owner": lead_owner,
                "custom_ambassador": ambassador_id,
            }
        )

        lead.save()
        frappe.db.commit()

        response_data = dict(data)
        response_data["lead_id"] = lead.name
        response_data["ambassador_id"] = ambassador_id
        response_data["ambassador_created"] = ambassador_created

        return create_api_response(
            201, "created", "Lead created successfully", data=response_data
        )

    return create_api_response(401, "unauthorized", "Missing or Invalid auth")


def get_or_create_ambassador(mobile_number, ambassador_name=None, data=None):
    if not mobile_number:
        frappe.throw("Mobile number is required to get or create an ambassador")

    ambassador = frappe.db.get_value(
        "Ambassador", {"ambassador_mobile_number": mobile_number}, ["name"], as_dict=1
    )

    was_created = False

    if not ambassador:
        if not ambassador_name:
            frappe.throw("Ambassador name is required to create a new ambassador")

        new_ambassador = frappe.new_doc("Ambassador")
        ambassador_data = {
            "ambassador_name": ambassador_name,
            "ambassador_mobile_number": mobile_number,
            "status": "Active",
            "type_of_account": "Redeem",
        }

        if data and isinstance(data, dict):
            ambassador_data.update(data)

        new_ambassador.update(ambassador_data)

        new_ambassador.save()
        frappe.db.commit()

        ambassador = {"name": new_ambassador.name}
        was_created = True

    return {"name": ambassador["name"], "created": was_created}
