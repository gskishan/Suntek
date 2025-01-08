from typing import Dict, List

import frappe

from suntek_app.suntek.utils.validation_utils import (
    convert_date_format, extract_first_and_last_name)


def get_or_create_lead(mobile_no):
    """Get existing lead or create new one"""
    existing_lead = frappe.get_list("Lead", filters={"mobile_no": mobile_no}, fields=["name"], limit=1)
    if existing_lead:
        return frappe.get_doc("Lead", existing_lead[0].name)
    return frappe.new_doc("Lead")


def update_lead_basic_info(lead, neodove_data, lead_owner, lead_stage):
    """Update basic lead information"""
    first_name, middle_name, last_name = extract_first_and_last_name(neodove_data.get("name"))
    contact_list_name = get_contact_list_name(neodove_data)
    executive_name = get_executive_name(neodove_data.get("customer_detail_form_response", []))
    custom_capacity = ""
    custom_uom = ""
    form_response: List[Dict] = neodove_data.get("customer_detail_form_response")
    neodove_campaign = neodove_data.get("campaign_name")

    for item in form_response:
        if item["question_text"] == "Capacity":
            custom_capacity = item["answer"]
        if item["question_text"] == "UOM":
            custom_uom = item["answer"]

    lead.update(
        {
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "lead_owner": lead_owner,
            "custom_contact_list_name": contact_list_name,
            "custom_neodove_lead_stage": lead_stage,
            "custom_executive_name": executive_name or "",
            "mobile_no": neodove_data.get("mobile"),
            "custom_capacity": custom_capacity,
            "custom_uom": custom_uom,
            "custom_neodove_campaign_name": neodove_campaign,
        }
    )


def add_dispose_remarks(lead, remarks, agent_name):
    """Add dispose remarks to lead"""
    lead.append(
        "custom_neodove_remarks",
        {
            "remarks": remarks,
            "date": frappe.utils.nowdate(),
            "time": frappe.utils.nowtime(),
            "updated_on": frappe.utils.now_datetime(),
            "agent": agent_name,
        },
    )


def process_other_properties(lead, other_properties):
    """Process and update other properties from Neodove data"""
    if not other_properties or not isinstance(other_properties, list):
        return

    first_property = other_properties[0]
    if not first_property or not isinstance(first_property, dict):
        return

    properties = first_property.get("properties", [])
    if not properties:
        return

    # Map property names to lead fields
    property_mapping = {
        "ID": "custom_neodove_id",
        "Enquiry Owner Name": "custom_enquiry_owner_name",
        "Enquiry Date": "custom_enquiry_date",
        "Source": "source",
        "Location": "custom_location",
        "UOM": "custom_uom",
        "Capacity": "custom_capacity",
    }

    for prop in properties:
        field_name = property_mapping.get(prop.get("name"))
        if field_name:
            value = prop.get("value")

            # Special handling for Enquiry Date
            if prop.get("name") == "Enquiry Date":
                value = convert_date_format(value)

            # Update the lead field if we have a value
            if value:
                lead.set(field_name, value)


# Add this function to lead_utils.py
def get_contact_list_name(data):
    if data.get("other_properties") and len(data["other_properties"]) > 0:
        return data["other_properties"][-1].get("contact_list_name")
    return ""


def get_executive_name(customer_detail_form_response):
    for response in customer_detail_form_response:
        if response["question_text"] == "EXECUTIVE NAME":
            return response["answer"]
    return ""
