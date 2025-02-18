import frappe

from suntek_app.suntek.utils.api_handler import create_api_response, parse_request_data


@frappe.whitelist(allow_guest=True)
def create_ambassador():
    data = parse_request_data(frappe.request.data)

    ambassador = frappe.new_doc("Ambassador")

    ambassador.ambassador_name = data.get("name")
    ambassador.ambassador_mobile_number = data.get("mobile_no")
    ambassador.email_id = data.get("email_id")

    frappe.set_user("Administrator")
    ambassador.save()
    frappe.db.commit()
    return create_api_response(200, "success", "success", data)
