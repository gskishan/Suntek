import frappe

from suntek_app.suntek.utils.validation_utils import convert_date_format, convert_timestamp_to_date, extract_first_and_last_name


def _set_missing_values(source, target):
    address = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Address",
        },
        ["parent"],
        limit=1,
    )

    contact = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Contact",
        },
        ["parent"],
        limit=1,
    )

    if address:
        target.customer_address = address[0].parent

    if contact:
        target.contact_person = contact[0].parent


def get_next_telecaller():
    """Get next telecaller for lead assignment"""
    try:
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

        frappe.db.set_value(
            "Telecaller Queue",
            {"email": next_telecaller.email},
            "last_assigned",
            frappe.utils.now_datetime(),
        )
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
    """Updates basic lead information"""
    first_name, middle_name, last_name = extract_first_and_last_name(neodove_data.get("name"))
    contact_list_name = get_contact_list_name(neodove_data)
    city = get_lead_location(neodove_data)

    form_response = neodove_data.get("customer_detail_form_response")
    followup_date = neodove_data.get("follow_up_date")
    neodove_campaign = neodove_data.get("campaign_name")
    neodove_campaign_id = neodove_data.get("campaign_id")

    custom_capacity = ""
    custom_uom = ""
    formatted_date = ""

    if followup_date:
        formatted_date = convert_timestamp_to_date(str(followup_date))

    for item in form_response:
        if item["question_text"] == "Capacity":
            custom_capacity = item["answer"]
        if item["question_text"] == "UOM":
            custom_uom = item["answer"]

    pipeline_id = lead.get("custom_pipeline_id_enquiries")
    campaign_url = ""

    if pipeline_id and neodove_campaign_id:
        campaign_url = f"https://connect.neodove.com/campaign/{pipeline_id}/{neodove_campaign_id}"

    update_dict = {
        "first_name": first_name,
        "middle_name": middle_name,
        "last_name": last_name,
        "custom_contact_list_name": contact_list_name,
        "custom_neodove_lead_stage": lead_stage,
        "mobile_no": neodove_data.get("mobile"),
        "custom_capacity": custom_capacity,
        "custom_uom": custom_uom,
        "custom_neodove_campaign_name": neodove_campaign,
        "city": city,
        "custom_neodove_campaign_id": neodove_campaign_id,
        "custom_neodove_campaign_url": campaign_url,
        "custom_followup_date": formatted_date,
    }

    agent_email = neodove_data.get("agent_email")
    current_lead_owner = lead.get("lead_owner")

    if not current_lead_owner or (agent_email and current_lead_owner != agent_email):
        update_dict["lead_owner"] = lead_owner

    update_dict["lead_owner"] = lead_owner

    lead.update(update_dict)


def add_dispose_remarks(lead, remarks, agent_name, call_recordings=None):
    """Add dispose remarks and call recordings to lead"""
    if remarks:
        lead.append(
            "custom_neodove_remarks",
            {
                "remarks": remarks,
                "updated_on": frappe.utils.now_datetime(),
            },
        )

    if call_recordings:
        existing_urls = set()
        if lead.get("custom_call_recordings"):
            existing_urls = {rec.recording_url for rec in lead.custom_call_recordings}
        for recording in call_recordings:
            recording_url = recording.get("recording_url")
            if recording_url and recording_url not in existing_urls:
                lead.append(
                    "custom_call_recordings", {"call_duration_in_sec": recording.get("call_duration_in_sec", 0), "recording_url": recording_url}
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

                value = convert_date_format(value)

            if value:
                lead.set(field_name, value)


def get_contact_list_name(data):
    """Get contact list name from Neodove data"""
    if data.get("other_properties") and len(data["other_properties"]) > 0:
        return data["other_properties"][-1].get("contact_list_name")
    return ""


def get_lead_location(data: dict) -> str:
    """
    Get lead location from properties and return it as city
    Args:
        data (dict): Input data containing properties
    Returns:
        str: City value or empty string if not found
    """

    if not data:
        return ""

    city = ""

    if custom_props := data.get("custom_contact_properties", []):
        if properties := custom_props[0].get("properties", []):
            for prop in properties:
                if prop.get("custom_column_name") == "Location":
                    city = prop.get("custom_column_value", "")
                    break

    if not city and (other_props := data.get("other_properties", [])):
        if properties := other_props[0].get("properties", []):
            for prop in properties:
                if prop.get("name") == "Location":
                    city = prop.get("value", "")
                    break

    return city
