from typing import Dict, List
import frappe
from suntek_app.suntek.utils.validation_utils import convert_date_format, extract_first_and_last_name, format_date


# def get_next_telecaller():
#     try:
#         # First check if round robin is enabled in Suntek Settings
#         enable_round_robin = frappe.db.get_single_value("Suntek Settings", "enable_round_robin_assignment_to_enquiries")

#         if not enable_round_robin:
#             frappe.log_error("Round robin assignment is disabled", "Telecaller Assignment")
#             return None

#         # Get next active telecaller based on last assigned time
#         telecallers = frappe.db.sql(
#             """
#             SELECT
#                 email,
#                 last_assigned
#             FROM
#                 `tabTelecaller Queue`
#             WHERE
#                 is_active = 1
#             ORDER BY
#                 COALESCE(last_assigned, '1900-01-01')
#             LIMIT 1
#             """,
#             as_dict=1,
#         )

#         if not telecallers:
#             frappe.log_error("No active telecallers found", "Telecaller Assignment")
#             return None

#         next_telecaller = telecallers[0]

#         # Update last assigned time
#         frappe.db.set_value("Telecaller Queue", {"email": next_telecaller.email}, "last_assigned", frappe.utils.now_datetime())
#         frappe.db.commit()

#         return next_telecaller.email

#     except Exception as e:
#         frappe.log_error(f"Error in telecaller assignment: {str(e)}", "Telecaller Assignment")
#         return None


def get_next_telecaller():
    try:
        # Get next active telecaller based on last assigned time
        telecallers = frappe.db.sql(
            """
            SELECT
                email,
                last_assigned
            FROM
                `tabTelecaller Queue`
            WHERE
                is_active = 1
            ORDER BY
                COALESCE(last_assigned, '1900-01-01')
            LIMIT 1
            """,
            as_dict=1,
        )

        if not telecallers:
            frappe.log_error("No active telecallers found", "Telecaller Assignment")
            return None

        next_telecaller = telecallers[0]

        # Update last assigned time
        frappe.db.set_value("Telecaller Queue", {"email": next_telecaller.email}, "last_assigned", frappe.utils.now_datetime())
        frappe.db.commit()

        return next_telecaller.email

    except Exception as e:
        frappe.log_error(f"Error in telecaller assignment: {str(e)}", "Telecaller Assignment")
        return None


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
    city = get_lead_location(neodove_data)

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
            "city": city,
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

            if prop.get("name") == "Enquiry Date":
                # value = format_date(value)
                value = convert_date_format(value)

            if value:
                lead.set(field_name, value)


def get_contact_list_name(data):
    if data.get("other_properties") and len(data["other_properties"]) > 0:
        return data["other_properties"][-1].get("contact_list_name")
    return ""


def get_executive_name(customer_detail_form_response):
    for response in customer_detail_form_response:
        if response["question_text"] == "EXECUTIVE NAME":
            return response["answer"]
    return ""


def get_lead_location(data: dict) -> str:
    """
    Get lead location from properties and return it as city
    Args:
        data (dict): Input data containing properties
    Returns:
        str: City value or empty string if not found
    """
    # Early return if data is empty or None
    if not data:
        return ""

    city = ""

    # Check custom contact properties first
    if custom_props := data.get("custom_contact_properties", []):
        if properties := custom_props[0].get("properties", []):
            for prop in properties:
                if prop.get("custom_column_name") == "Location":
                    city = prop.get("custom_column_value", "")
                    break

    # Check other properties if location not found
    if not city and (other_props := data.get("other_properties", [])):
        if properties := other_props[0].get("properties", []):
            for prop in properties:
                if prop.get("name") == "Location":
                    city = prop.get("value", "")
                    break

    return city
