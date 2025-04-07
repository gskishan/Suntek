from typing import Any

import frappe

from suntek_app.suntek.utils.api_handler import create_api_response, parse_request_data
from suntek_app.suntek.utils.lead_utils import get_next_telecaller


@frappe.whitelist(allow_guest=True)
def get_lead_from_just_dial():
    try:
        token = frappe.request.headers.get("X-Just-Dial-Auth-Token")

        if not _validate_token(token):
            return create_api_response(401, "unauthorized", "Unauthorized")

        frappe.set_user("developer@suntek.co.in")
        data = parse_request_data(frappe.request.data)
        mobile = data.get("mobile")

        if mobile and frappe.db.exists("Lead", {"mobile_no": mobile}):
            return create_api_response(409, "conflict", "Lead already exists")

        lead = _create_lead(data)
        lead.insert()

        return create_api_response(201, "success", "Lead created successfully", data)
    except Exception as e:
        frappe.log_error(
            title="Just Dial Lead Creation Error",
            message=str(e),
            reference_doctype="Lead",
        )

        return create_api_response(
            500,
            "internal_server_error",
            "Internal Server Error",
            {"error": str(e)},
        )


def _validate_token(token: str | None) -> bool:
    if not token:
        return False

    try:
        stored_token = frappe.get_doc("Suntek Settings").get_password("just_dial_auth_token")
        return token == stored_token
    except Exception:
        return False


def _create_lead(data: dict[str, Any]) -> Any:
    lead = frappe.new_doc("Lead")

    lead.first_name, lead.last_name = _split_name(data.get("name", ""))
    lead.mobile_no = data.get("mobile")
    lead.phone = data.get("phone")
    lead.email_id = data.get("email")
    lead.source = "Just Dial"
    lead.status = "Open"
    lead.owner = get_next_telecaller()

    pincode = data.get("pincode")
    if pincode:
        lead.pincode = pincode
        if frappe.db.exists("District PIN Code", {"pin_code": pincode}):
            lead.custom_suntek_pin_code = pincode

    city_name = data.get("city")
    if city_name:
        try:
            city = frappe.get_doc("City", city_name)
            lead.custom_suntek_city = city.name
            lead.custom_suntek_state = city.state
        except Exception:
            pass

    prefix = data.get("prefix", "")
    if prefix:
        salutation = prefix.replace(".", "")
        if frappe.db.exists("Salutation", salutation):
            lead.salutation = salutation

    return lead


def _split_name(name: str) -> tuple[str, str]:
    if not name:
        return "", ""

    name_parts = name.split(" ", 1)
    return name_parts[0], name_parts[1] if len(name_parts) > 1 else ""
