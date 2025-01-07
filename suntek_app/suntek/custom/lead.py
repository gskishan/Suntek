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
    # return {"success": False, "message": "Not implemented yet"}

    default_department = "All Departments"
    default_salutation = "Mx"

    try:
        neodove_data = frappe.request.data

        if isinstance(neodove_data, bytes):
            neodove_data = json.loads(neodove_data.decode("utf-8"))

        custom_executive_name = None
        call_recordings = []

        mobile_no = neodove_data.get("mobile")
        lead_owner = neodove_data.get("agent_email")
        customer_detail_form_response = neodove_data.get("customer_detail_form_response")
        custom_neodove_lead_stage = neodove_data.get("lead_stage_name")

        first_name, middle_name, last_name = extract_first_and_last_name(neodove_data.get("name"))
        custom_executive_name = get_executive_name(customer_detail_form_response)
        contact_list_name = get_contact_list_name(neodove_data)

        # Check if lead exists with this mobile number
        existing_lead = frappe.get_list("Lead", filters={"mobile_no": mobile_no}, fields=["name"], limit=1)

        if existing_lead:
            # Update existing lead
            lead = frappe.get_doc("Lead", existing_lead[0].name)
        else:
            # Create new lead
            lead = frappe.new_doc("Lead")
            lead.mobile_no = mobile_no

        # Update common fields
        lead.first_name = first_name
        lead.middle_name = middle_name
        lead.last_name = last_name
        lead.lead_owner = lead_owner
        lead.custom_contact_list_name = contact_list_name
        lead.custom_neodove_lead_stage = custom_neodove_lead_stage

        # if neodove_data.get("call_recordings"):
        #     call_recordings = neodove_data.get("call_recordings")

        #     for recording in call_recordings:
        #         lead.append(
        #             "custom_call_recordings",
        #             {
        #                 "call_duration_in_sec": recording.get("call_duration_in_sec"),
        #                 "recording_url": recording.get("recording_url"),
        #                 "enquiry": lead.name,
        #             },
        #         )

        if neodove_data.get("call_recordings"):
            call_recordings = neodove_data.get("call_recordings")

            for recording in call_recordings:
                if not recording.get("call_duration_in_sec") or not recording.get("recording_url"):
                    continue

                existing_recording = False

                if recording.get("recording_url"):
                    existing_recording = frappe.get_list(
                        "Neodove Call Recordings",
                        filters={"recording_url": recording.get("recording_url")},
                        fields=["name"],
                        limit=1,
                    )

                if existing_recording:
                    continue

                lead.append(
                    "custom_call_recordings",
                    {
                        "call_duration_in_sec": recording.get("call_duration_in_sec"),
                        "recording_url": recording.get("recording_url"),
                        "enquiry": lead.name,
                    },
                )

        if custom_executive_name is None:
            custom_executive_name = ""
        lead.custom_executive_name = custom_executive_name

        if not existing_lead:
            lead.custom_department = default_department
            lead.salutation = default_salutation

        # Process other properties
        if neodove_data.get("other_properties"):
            properties = neodove_data["other_properties"][0].get("properties", [])
            for prop in properties:
                name = prop.get("name", "").lower()
                value = prop.get("value")

                if name == "enquiry owner name":
                    lead.custom_enquiry_owner_name = value
                elif name == "enquiry date":
                    formatted_date = convert_date_format(value)
                    if formatted_date:
                        lead.custom_enquiry_date = formatted_date
                elif name == "location":
                    lead.custom_location = value
                elif name == "uom":
                    lead.custom_uom = value
                elif name == "customer category":
                    lead.custom_customer_category = value
                elif name == "source":
                    lead.source = value
                elif name == "capacity":
                    lead.custom_capacity = value

        # Handle dispose remarks
        dispose_remarks = neodove_data.get("dispose_remarks")
        if dispose_remarks and dispose_remarks.strip():
            # Create a new row in custom_neodove_remarks table
            lead.append(
                "custom_neodove_remarks",
                {
                    "remarks": dispose_remarks,
                    "date": frappe.utils.nowdate(),
                    "time": frappe.utils.nowtime(),
                    "updated_on": frappe.utils.now_datetime(),
                    "agent": neodove_data.get("agent_name"),
                },
            )

        # Validate mobile number
        if not validate_mobile_number(mobile_no):
            frappe.throw(
                "Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.",
            )

        if existing_lead:
            lead.save(ignore_permissions=True)
            message = "Lead updated successfully"
        else:
            lead.insert(ignore_permissions=True)
            message = "Lead created successfully"

        frappe.db.commit()

        return {
            "success": True,
            "message": message,
            "lead_name": lead.name,
            "custom_executive_name": custom_executive_name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Neodove Lead Creation/Update Error")
        return {
            "success": False,
            "message": str(e),
        }
