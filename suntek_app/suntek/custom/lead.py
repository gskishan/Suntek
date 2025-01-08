import json

import frappe
import werkzeug.wrappers
from frappe.model.mapper import get_mapped_doc

from suntek_app.suntek.custom.solar_power_plants import validate_mobile_number
from suntek_app.suntek.utils.lead_utils import add_dispose_remarks, get_or_create_lead, process_other_properties, update_lead_basic_info


def change_enquiry_status(doc, method):
    duplicate_check(doc)
    if not validate_mobile_number(doc.mobile_no):
        frappe.throw(
            "Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.",
        )


def set_enquiry_name(doc, method):
    if doc.name:
        doc.custom_enquiry_name = doc.name


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


@frappe.whitelist()
def create_lead_from_neodove_dispose():
    try:
        # Constants
        DEFAULT_DEPARTMENT = "All Departments"
        DEFAULT_SALUTATION = ""
        DEFAULT_SOURCE = "Neodove"

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

        # Get or create lead
        lead = get_or_create_lead(mobile_no)
        is_new = not bool(lead.get("name"))

        # Prepare all updates before saving
        if is_new:
            lead.custom_department = DEFAULT_DEPARTMENT
            lead.salutation = DEFAULT_SALUTATION
            lead.source = DEFAULT_SOURCE

        # Update basic info
        update_lead_basic_info(lead, neodove_data, lead_owner, lead_stage)

        # Process recordings before saving
        if neodove_data.get("call_recordings"):
            _prepare_recordings(lead, neodove_data["call_recordings"])

        # Process other properties
        if neodove_data.get("other_properties"):
            process_other_properties(lead, neodove_data["other_properties"])

        # Add dispose remarks
        if dispose_remarks := neodove_data.get("dispose_remarks", "").strip():
            add_dispose_remarks(lead, dispose_remarks, neodove_data.get("agent_name"))

        # Save everything in one go
        lead.flags.ignore_validate_update_after_submit = True
        lead.save(ignore_permissions=True)
        frappe.db.commit()

        return {
            "success": True,
            "message": ("Lead created successfully" if is_new else "Lead updated successfully"),
            "lead_name": lead.name,
            "custom_executive_name": lead.custom_executive_name,
        }

    except Exception as e:
        frappe.log_error(frappe.get_traceback(), "Neodove Lead Creation/Update Error")
        return {"success": False, "message": str(e)}


def _prepare_recordings(lead, recordings):
    """Prepare recordings to be added to lead without saving"""
    if not recordings:
        return

    existing_urls = set()
    if lead.get("custom_call_recordings"):
        existing_urls = {rec.recording_url for rec in lead.custom_call_recordings}

    for recording in recordings:
        if not recording.get("recording_url") or recording["recording_url"] in existing_urls:
            continue

        lead.append(
            "custom_call_recordings",
            {
                "doctype": "Neodove Call Recordings",
                "call_duration_in_sec": recording.get("call_duration_in_sec") or 0,
                "recording_url": recording["recording_url"],
                "enquiry": lead.name if lead.name else None,
                "parenttype": "Lead",
                "parentfield": "custom_call_recordings",
                "parent": lead.name if lead.name else None,
            },
        )


@frappe.whitelist(allow_guest=True)
def create_lead_from_facebook():
    print("#########")
    print(parse_request_data(frappe.request.data))
    print("#########")

    local_verify_token = frappe.get_doc("Suntek Settings").facebook_verify_token

    if frappe.request.args.get("hub.verify_token") == local_verify_token:
        challenge = frappe.request.args.get("hub.challenge")
        response = werkzeug.wrappers.Response()
        response.mimetype = "text/plain"
        response.response = challenge
        return response


def parse_request_data(data):
    """Parse request data from bytes to JSON if needed"""
    if isinstance(data, bytes):
        return json.loads(data.decode("utf-8"))
    return data
