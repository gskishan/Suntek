import frappe
import requests
import json


def send_to_neodove(doc, method=None):
    """Send document data to Neodove campaign URL"""
    try:

        campaign_id = doc.get("custom_neodove_campaign_id")
        if not campaign_id:
            return

        integration_url = frappe.db.get_value("Neodove Campaign", {"campaign_id": campaign_id}, "integration_url")

        if not integration_url:
            return

        update_url = f"{integration_url}?update=true"

        if doc.doctype == "Lead":
            payload = {
                "id": doc.name,
                "name": f"{doc.first_name or ''} {doc.last_name or ''}".strip(),
                "source": doc.source or "",
                "status": doc.status or "",
                "department": doc.custom_department or "",
                "enquiry_status": doc.custom_enquiry_status or "",
                "customer_category": doc.custom_customer_category or "",
                "mobile_no": doc.mobile_no or "",
                "phone": doc.phone or "",
                "request_type": doc.request_type or "",
                "capacity": doc.custom_capacity or "",
                "uom": doc.custom_uom or "",
            }
        else:
            payload = {
                "id": doc.name,
                "name": doc.party_name or "",
                "source": doc.source or "",
                "status": doc.status or "",
                "department": doc.custom_department or "",
                "enquiry_status": doc.custom_enquiry_status or "",
                "customer_category": doc.custom_customer_category or "",
                "mobile_no": doc.contact_mobile or "",
                "phone": doc.contact_phone or "",
                "request_type": doc.request_type or "",
                "capacity": doc.custom_capacity or "",
                "uom": doc.custom_uom or "",
            }

        headers = {"Content-Type": "application/json"}
        response = requests.post(update_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()

        frappe.logger().debug(f"Neodove Update Response for {doc.doctype} {doc.name}: {response.text}")

    except Exception as e:
        frappe.logger().error(f"Error updating Neodove for {doc.doctype} {doc.name}: {str(e)}")
        frappe.log_error(
            title=f"Neodove Update Error - {doc.doctype}",
            message=f"Error updating {doc.doctype} {doc.name} in Neodove: {str(e)}\nPayload: {payload if 'payload' in locals() else 'Not created'}",
        )
