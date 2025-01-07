import json
import re

import frappe
from frappe.model.mapper import get_mapped_doc


def change_enquiry_status(doc, method):
    duplicate_check(doc)
    if not validate_mobile_number(doc.mobile_no):
        frappe.throw(
            "Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.",
        )


def set_enquiry_name(doc, method):
    if doc.name:
        doc.custom_enquiry_name = doc.name


def validate_mobile_number(number):
    # Ensure number is a string before matching
    number = str(number)
    pattern = r"^(\+91[-]?)?[6-9]\d{9}$"
    if re.match(pattern, number):
        return True
    else:
        return False


@frappe.whitelist()
def custom_make_opportunity(source_name, target_doc=None):
    def set_missing_values(source, target):
        _set_missing_values(source, target)
        target.custom_enquiry_status = "Open"
        target.custom_company_name = source.company_name

    target_doc = get_mapped_doc(
        "Lead",
        source_name,
        {
            "Lead": {
                "doctype": "Opportunity",
                "field_map": {
                    "campaign_name": "campaign",
                    "doctype": "opportunity_from",
                    "name": "party_name",
                    "lead_name": "contact_display",
                    "company_name": "customer_name",
                    "email_id": "contact_email",
                    "mobile_no": "contact_mobile",
                    "lead_owner": "opportunity_owner",
                    "custom_enquiry_owner_name": "custom_opportunity_owner_name",
                    "notes": "notes",
                },
            }
        },
        target_doc,
        set_missing_values,
    )

    return target_doc


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


def duplicate_check(doc):
    mobile_no = str(doc.mobile_no)  # Ensure mobile_no is a string
    sql = """select * from `tabLead` where mobile_no="{0}" and name!="{1}" """.format(mobile_no, doc.name)
    data = frappe.db.sql(sql, as_dict=True)
    if data:
        frappe.errprint(data)
        frappe.throw(
            "Duplicate mobile no {} already linked to <b>{}</b> ".format(mobile_no, data[0].custom_enquiry_owner_name),
        )


def extract_first_and_last_name(name: str):
    if not name:
        return "", "", ""

    name_parts = [part for part in name.strip().split() if part]

    if len(name_parts) == 1:
        return name_parts[0], "", ""
    elif len(name_parts) == 2:
        return name_parts[0], "", name_parts[1]
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_name = " ".join(name_parts[1:-1])
        return first_name, middle_name, last_name


def convert_date_format(date_str):
    """Convert date from dd-mm-yyyy to yyyy-mm-dd"""
    if not date_str:
        return None
    try:
        day, month, year = date_str.split("-")
        return f"{year}-{month}-{day}"
    except Exception:
        return None


def get_executive_name(customer_detail_form_response):
    for response in customer_detail_form_response:
        if response["question_text"] == "EXECUTIVE NAME":
            return response["answer"]
    return ""


def get_contact_list_name(data):
    if data.get("other_properties") and len(data["other_properties"]) > 0:
        return data["other_properties"][0].get("contact_list_name")
    return ""


@frappe.whitelist()
def create_lead_from_neodove_dispose():
    try:
        # Constants
        DEFAULT_DEPARTMENT = "All Departments"
        DEFAULT_SALUTATION = "Mx"

        # Parse request data
        neodove_data = parse_request_data(frappe.request.data)

        # Extract essential data
        mobile_no = neodove_data.get("mobile")
        lead_owner = neodove_data.get("agent_email")
        lead_stage = neodove_data.get("lead_stage_name")

        # Validate mobile number first
        if not validate_mobile_number(mobile_no):
            return {
                "success": False,
                "message": "Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.",
            }

        lead = get_or_create_lead(mobile_no)

        update_lead_basic_info(lead, neodove_data, lead_owner, lead_stage)

        if neodove_data.get("call_recordings"):
            process_call_recordings(lead, neodove_data["call_recordings"])
        if neodove_data.get("other_properties"):
            process_other_properties(lead, neodove_data["other_properties"])
        if dispose_remarks := neodove_data.get("dispose_remarks", "").strip():
            add_dispose_remarks(lead, dispose_remarks, neodove_data.get("agent_name"))
        if not lead.get("name"):
            lead.custom_department = DEFAULT_DEPARTMENT
            lead.salutation = DEFAULT_SALUTATION

        is_new = not bool(lead.get("name"))
        lead.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": "Lead created successfully" if is_new else "Lead updated successfully",
            "lead_name": lead.name,
            "custom_executive_name": lead.custom_executive_name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Neodove Lead Creation/Update Error")
        return {"success": False, "message": str(e)}


def parse_request_data(data):
    """Parse request data from bytes to JSON if needed"""
    if isinstance(data, bytes):
        return json.loads(data.decode("utf-8"))
    return data


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
        }
    )


def process_call_recordings(lead, recordings):
    """Process and add call recordings"""
    for recording in recordings:
        if not (recording.get("call_duration_in_sec") and recording.get("recording_url")):
            continue

        if not frappe.get_list("Neodove Call Recordings", filters={"recording_url": recording["recording_url"]}, limit=1):
            lead.append(
                "custom_call_recordings",
                {
                    "call_duration_in_sec": recording["call_duration_in_sec"],
                    "recording_url": recording["recording_url"],
                },
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
