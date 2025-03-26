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
    try:
        if frappe.request.headers.get("X-Django-Server-Authorization") and validate_auth_token(
            frappe.request.headers.get("X-Django-Server-Authorization")
        ):
            if not frappe.request.method == "POST":
                frappe.log_error(
                    f"Method not allowed: {frappe.request.method}",
                    "Lead API: Invalid Method",
                )
                return create_api_response(405, "method not allowed", "Method Not Allowed")

            frappe.set_user("developer@suntek.co.in")

            try:
                data = parse_request_data(frappe.request.data)
            except Exception as e:
                frappe.log_error(
                    f"Error parsing request data: {str(e)}\nRequest data: {frappe.request.data}",
                    "Lead API: Data Parse Error",
                )
                return create_api_response(400, "bad request", "Invalid request data format")

            first_name = data.get("first_name")
            mobile_no = data.get("mobile_number")

            ambassador_mobile_no = data.get("ambassador_mobile_no")
            ambassador_name = data.get("ambassador_name")

            ambassador_data = data.get("ambassador_data", {})

            if not first_name or not mobile_no or not ambassador_mobile_no:
                frappe.log_error(
                    f"Missing required fields: first_name={bool(first_name)}, mobile_no={bool(mobile_no)}, ambassador_mobile_no={bool(ambassador_mobile_no)}",
                    "Lead API: Missing Required Fields",
                )
                return create_api_response(
                    400,
                    "bad request",
                    "Missing Name or Mobile Number or Ambassador Mobile Number",
                )

            if not validate_mobile_number(mobile_no):
                frappe.log_error(
                    f"Invalid mobile number: {mobile_no}",
                    "Lead API: Invalid Mobile Number",
                )
                return create_api_response(400, "bad_request", "Invalid Mobile Number")

            existing_lead = frappe.db.get_value("Lead", {"mobile_no": mobile_no}, ["name"], as_dict=1)
            if existing_lead:
                frappe.log_error(
                    f"Duplicate lead with mobile number: {mobile_no}, Lead ID: {existing_lead.get('name')}",
                    "Lead API: Duplicate Lead",
                )
                return create_api_response(
                    409,
                    "duplicate",
                    f"Lead with mobile number {mobile_no} already exists",
                    data={"existing_lead_id": existing_lead},
                )

            last_name = data.get("last_name")
            email_id = data.get("email")

            try:
                ambassador_result = get_or_create_ambassador(ambassador_mobile_no, ambassador_name, ambassador_data)
                ambassador_id = ambassador_result["name"]
                ambassador_created = ambassador_result["created"]
            except Exception as e:
                frappe.log_error(
                    f"Ambassador creation error: {str(e)}\nData: {ambassador_mobile_no}, {ambassador_name}, {ambassador_data}",
                    "Lead API: Ambassador Creation Failure",
                )
                return create_api_response(400, "bad request", str(e))

            try:
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

                return create_api_response(201, "created", "Lead created successfully", data=response_data)
            except Exception as e:
                frappe.log_error(
                    f"Lead creation error: {str(e)}\nLead data: {first_name}, {last_name}, {mobile_no}, {email_id}, {ambassador_id}",
                    "Lead API: Lead Creation Failure",
                )
                return create_api_response(500, "server_error", f"Error creating lead: {str(e)}")

        frappe.log_error(
            f"Authentication failure: {frappe.request.headers.get('X-Django-Server-Authorization')}",
            "Lead API: Authentication Failure",
        )
        return create_api_response(401, "unauthorized", "Missing or Invalid auth")
    except Exception as e:
        frappe.log_error(
            f"Unhandled exception in create_lead_from_ambassador: {str(e)}",
            "Lead API: Unhandled Exception",
        )
        return create_api_response(500, "server_error", "Internal server error")


def get_or_create_ambassador(mobile_number, ambassador_name=None, data=None):
    try:
        if not mobile_number:
            error_msg = "Mobile number is required to get or create an ambassador"
            frappe.log_error(error_msg, "Ambassador Creation: Missing Mobile Number")
            frappe.throw(error_msg)

        ambassador = frappe.db.get_value(
            "Ambassador",
            {"ambassador_mobile_number": mobile_number},
            ["name"],
            as_dict=1,
        )

        was_created = False

        if not ambassador:
            if not ambassador_name:
                error_msg = "Ambassador name is required to create a new ambassador"
                frappe.log_error(
                    f"Missing ambassador name for mobile: {mobile_number}",
                    "Ambassador Creation: Missing Name",
                )
                frappe.throw(error_msg)

            try:
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
            except Exception as e:
                frappe.log_error(
                    f"Ambassador creation error: {str(e)}\nData: {ambassador_data}",
                    "Ambassador Creation: Database Error",
                )
                raise

        return {"name": ambassador["name"], "created": was_created}
    except Exception as e:
        frappe.log_error(
            f"Unhandled exception in get_or_create_ambassador: {str(e)}\nMobile: {mobile_number}, Name: {ambassador_name}",
            "Ambassador Creation: Unhandled Exception",
        )
        raise
