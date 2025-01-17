import frappe
import requests
import json


def send_to_neodove(doc, method=None):
    """Send document data to Neodove campaign URL"""
    try:

        setting_value = frappe.db.get_single_value("Suntek Settings", "send_lead_enquiry_data_to_neodove_after_update")

        if not setting_value:
            return

        campaign_id = doc.get("custom_neodove_campaign_id")
        if not campaign_id:
            campaign_id = frappe.db.get_single_value("Suntek Settings", "default_campaign_enquiries")
            integration_url = frappe.db.get_single_value("Suntek Settings", "integration_url")
        else:
            integration_url = frappe.db.get_value("Neodove Campaign", {"campaign_id": campaign_id}, "integration_url")
        if not integration_url:
            return

        final_url = f"{integration_url}?update=true" if method == "on_update" else integration_url

        if doc.doctype == "Lead":
            payload = {
                "id": doc.name,
                "name": f"{(doc.first_name or '')} {(doc.last_name or '')}".strip(),
                "Enquiry Source": doc.source or "",
                "status": doc.status or "",
                "department": doc.custom_department or "",
                "enquiry status": doc.custom_enquiry_status or "",
                "customer category": doc.custom_customer_category or "",
                "mobile": doc.mobile_no or "",
                "phone": doc.phone or "",
                "Request Type": doc.request_type or "",
                "capacity": doc.custom_capacity or "",
                "UOM": doc.custom_uom or "",
            }
        else:
            payload = {
                "id": doc.name,
                "name": doc.party_name or "",
                "Enquiry Source": doc.source or "",
                "status": doc.status or "",
                "department": doc.custom_department or "",
                "enquiry status": doc.custom_enquiry_status or "",
                "customer category": doc.custom_customer_category or "",
                "mobile": doc.contact_mobile or "",
                "phone": doc.contact_phone or "",
                "Request Type": doc.request_type or "",
                "capacity": doc.custom_capacity or "",
                "UOM": doc.custom_uom or "",
            }

        headers = {"Content-Type": "application/json"}
        response = requests.post(final_url, data=json.dumps(payload), headers=headers, timeout=10)
        response.raise_for_status()

        frappe.logger().debug(f"Neodove Response for {doc.doctype} {doc.name}: {response.text}")

    except Exception as e:

        frappe.logger().error(f"Error sending to Neodove for {doc.doctype} {doc.name}: {str(e)}")
        frappe.log_error(
            title=f"Neodove Error - {doc.doctype}",
            message=f"Error sending {doc.doctype} {doc.name} to Neodove: {str(e)}\nPayload: {payload if 'payload' in locals() else 'Not created'}",
        )
