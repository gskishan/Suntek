import hmac
import json

import frappe
import werkzeug.wrappers
from frappe.model.mapper import get_mapped_doc

from suntek_app.suntek.utils.lead_utils import (
    get_next_telecaller,
    get_or_create_lead,
    process_other_properties,
    update_lead_basic_info,
)
from suntek_app.suntek.utils.validation_utils import (
    duplicate_check,
    validate_mobile_number,
)


def before_import(doc, method=None):
    """Thie function executes when doing a data import, it removes the lead_owner which by default gets set to the person doing data import."""

    duplicate_check(doc)

    if doc.lead_owner == frappe.session.user:
        doc.lead_owner = None
        doc.custom_enquiry_owner_name = None


def set_lead_owner(doc, method):
    """Set lead_owner to current user if not set"""
    if not doc.lead_owner and doc.is_new():
        doc.lead_owner = frappe.session.user
        doc.custom_enquiry_owner_name = frappe.get_value("User", frappe.session.user, "full_name")


def change_enquiry_status(doc, method):
    try:
        validate_mobile_number(doc.mobile_no)
        duplicate_check(doc)

        if doc.lead_owner:
            return

        enable_round_robin = frappe.db.get_single_value("Suntek Settings", "enable_round_robin_assignment_to_enquiries")
        if not enable_round_robin:
            return

        is_import = frappe.flags.in_import if hasattr(frappe.flags, "in_import") else False
        is_digital_marketing = doc.source == "Digital Marketing"

        if is_import or is_digital_marketing:
            next_telecaller = get_next_telecaller()
            if next_telecaller:
                doc.lead_owner = next_telecaller
                user = frappe.get_doc("User", next_telecaller)
                doc.custom_enquiry_owner_name = user.full_name

    except frappe.ValidationError:
        raise
    except Exception as e:
        frappe.log_error(f"Error in change_enquiry_status: {str(e)}", "Lead Assignment")
        frappe.throw(str(e))


def set_enquiry_name(doc, method):
    """Set custom_enquiry_name to name if not set"""
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


@frappe.whitelist(allow_guest=True)
def create_lead_from_neodove_dispose():
    """Handle incoming Neodove webhook requests to create/update leads or opportunities"""
    try:

        is_enabled = frappe.get_doc('Suntek Settings').get_value('enable_neodove_integration')

        if not is_enabled:
            frappe.throw("Neodove integration is disabled")

        frappe.set_user("Administrator")

        api_key = frappe.request.headers.get('X-Neodove-API-Key')
        if not api_key:
            return _error_response('API key missing', 401)

        if not _validate_api_key(api_key):
            return _error_response('Invalid API key', 401)

        neodove_data = parse_request_data(frappe.request.data)
        campaign_id = neodove_data.get("campaign_id")

        if not campaign_id:
            return _error_response('Campaign ID is required')

        campaign = _get_campaign_info(campaign_id)
        if not campaign:
            return _error_response(f"Campaign not found: {campaign_id}")

        mobile = neodove_data.get("mobile")
        agent_email = neodove_data.get("agent_email")
        lead_stage = neodove_data.get("lead_stage_name")

        result = (
            handle_opportunity_update(neodove_data, mobile, agent_email, lead_stage)
            if campaign.pipeline_name and campaign.pipeline_name.lower() == "opportunities"
            else handle_lead_update(neodove_data, mobile, agent_email, lead_stage, "", "", "")
        )

        return result

    except Exception as e:
        frappe.log_error(message=f"Neodove webhook error: {str(e)}\n{frappe.get_traceback()}", title="Neodove Webhook Error")
        return _error_response(str(e))
    finally:
        frappe.set_user("Guest")


def _validate_api_key(api_key: str) -> bool:
    """Validate API key with optimized caching"""
    CACHE_KEY = "neodove_webhook_secret"
    CACHE_TTL = 3600

    try:

        stored_key = frappe.cache().get_value(CACHE_KEY)

        if stored_key and hmac.compare_digest(api_key, stored_key):
            return True

        current_key = frappe.get_doc('Suntek Settings').get_password("neodove_webhook_secret")

        if current_key and current_key != stored_key:
            frappe.cache().set_value(CACHE_KEY, current_key, expires_in_sec=CACHE_TTL)

        return hmac.compare_digest(api_key, current_key) if current_key else False

    except Exception as e:
        frappe.log_error(f"API key validation error: {str(e)}", "Neodove Webhook")
        return False


def _get_campaign_info(campaign_id: str) -> dict:
    """Get campaign info with caching"""
    CACHE_KEY = f"neodove_campaign_{campaign_id}"
    CACHE_TTL = 300

    campaign = frappe.cache().get_value(CACHE_KEY)
    if not campaign:
        campaign = frappe.db.get_value(
            "Neodove Campaign",
            filters={"campaign_id": campaign_id},
            fieldname=["name", "pipeline_name", "campaign_name"],
            as_dict=1,
        )
        if campaign:
            frappe.cache().set_value(CACHE_KEY, campaign, expires_in_sec=CACHE_TTL)

    return campaign


def _error_response(message: str, status_code: int = 400) -> dict:
    """Standardized error response"""
    return {"success": False, "message": message, "status_code": status_code}


@frappe.whitelist(allow_guest=True)
def create_lead_from_facebook():

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


@frappe.whitelist()
def bulk_assign_unassigned_leads():
    """
    Bulk assign unassigned leads using round robin assignment
    Returns dict with success status and message
    """
    try:

        unassigned_leads = frappe.get_all("Lead", filters={"lead_owner": ["in", ["", None]], "status": ["!=", "Converted"]}, fields=["name"])

        if not unassigned_leads:
            frappe.msgprint("No unassigned leads found")
            return

        telecallers = frappe.db.sql(
            """
            SELECT email FROM `tabTelecaller Queue`
            WHERE is_active = 1
            ORDER BY COALESCE(last_assigned, '1900-01-01')
            """,
            as_dict=1,
        )

        if not telecallers:
            frappe.msgprint("No active telecallers available for assignment")
            return

        assigned_count = 0
        failed_count = 0
        telecaller_index = 0
        total_telecallers = len(telecallers)

        for lead in unassigned_leads:
            try:
                current_telecaller = telecallers[telecaller_index]["email"]
                user = frappe.get_doc("User", current_telecaller)

                frappe.db.set_value(
                    "Lead", lead.name, {"lead_owner": current_telecaller, "custom_enquiry_owner_name": user.full_name}, update_modified=True
                )

                frappe.db.set_value("Telecaller Queue", {"email": current_telecaller}, "last_assigned", frappe.utils.now_datetime())

                assigned_count += 1

                telecaller_index = (telecaller_index + 1) % total_telecallers

            except Exception as e:
                failed_count += 1
                frappe.log_error(message=f"Failed to assign lead {lead.name}: {str(e)}", title="Lead Assignment Error")
                continue

        frappe.db.commit()

        if assigned_count > 0:
            frappe.msgprint(f"Successfully assigned {assigned_count} leads")
        if failed_count > 0:
            frappe.msgprint(f"Failed to assign {failed_count} leads. Check error log for details.", indicator="yellow")

    except Exception as e:
        frappe.log_error(message=f"Error in bulk lead assignment: {str(e)}", title="Bulk Lead Assignment Error")
        frappe.msgprint("Error in bulk assignment. Check error log for details", indicator="red")


def get_department_from_campaign(campaign_name):
    """Map campaign names to departments"""
    department_mapping = {
        "Domestic Sales": "Domestic (Residential) Sales Team - SESP",
        "Channel Partner": "Channel Partner - SESP",
        "Commercial Sales": "Commercial & Industrial (C&I) - SESP",
    }
    return department_mapping.get(campaign_name)


def handle_opportunity_update(neodove_data, mobile_no, lead_owner, lead_stage):
    try:
        existing_opp = frappe.get_list("Opportunity", filters={"contact_mobile": mobile_no}, fields=["name"], limit=1)

        if existing_opp:
            opp = frappe.get_doc("Opportunity", existing_opp[0].name)
        else:
            existing_enquiry = frappe.get_list("Lead", filters={"mobile_no": mobile_no}, fields=["name"], limit=1)

            if not existing_enquiry:
                return {"success": False, "message": f"No existing enquiry found with mobile number: {mobile_no}"}

            opp = custom_make_opportunity(existing_enquiry[0].name)
            if not opp:
                return {"success": False, "message": "Failed to create opportunity from enquiry"}

        opp.opportunity_owner = neodove_data.get("agent_email")
        owner_name = frappe.db.get_value("User", neodove_data.get("agent_email"), "full_name")
        if owner_name:
            opp.custom_opportunity_owner_name = owner_name

        department = get_department_from_campaign(neodove_data.get("campaign_name"))
        if department:
            opp.custom_department = department
            opp.flags.ignore_mandatory = False
        else:
            opp.flags.ignore_mandatory = True

        if dispose_remarks := neodove_data.get("dispose_remarks", "").strip():
            opp.append(
                "custom_neodove_dispose_remarks",
                {
                    "remarks": dispose_remarks,
                    "updated_on": frappe.utils.now_datetime(),
                },
            )

        if call_recordings := neodove_data.get("call_recordings"):

            existing_urls = set()
            if opp.get("custom_call_recordings"):
                existing_urls = {rec.recording_url for rec in opp.custom_call_recordings}

            now = frappe.utils.now_datetime()
            for recording in call_recordings:
                recording_url = recording.get("recording_url")
                if recording_url and recording_url not in existing_urls:
                    opp.append(
                        "custom_call_recordings",
                        {"call_duration_in_sec": recording.get("call_duration_in_sec", 0), "recording_url": recording_url, "recording_time": now},
                    )

        if opp.get("custom_call_recordings"):
            for rec in opp.custom_call_recordings:
                if not rec.recording_time:
                    rec.recording_time = frappe.utils.now_datetime()

        neodove_campaign_id = neodove_data.get("campaign_id")
        pipeline_id = opp.get("custom_pipeline_id_opportunities")

        campaign_url = ""
        if pipeline_id and neodove_campaign_id:
            campaign_url = f"https://connect.neodove.com/campaign/{pipeline_id}/{neodove_campaign_id}"

        opp.custom_neodove_lead_stage = lead_stage
        opp.custom_contact_list_name = (
            neodove_data.get("other_properties", [{}])[0].get("contact_list_name") if neodove_data.get("other_properties") else ""
        )
        opp.custom_neodove_campaign_name = neodove_data.get("campaign_name")
        opp.custom_neodove_campaign_id = neodove_campaign_id
        opp.custom_neodove_campaign_url = campaign_url

        opp.flags.ignore_validate_update_after_submit = True
        opp.save(ignore_permissions=True)
        frappe.db.commit()

        return {"success": True, "message": "Opportunity updated successfully", "opportunity_name": opp.name}

    except Exception as e:
        frappe.log_error(
            title="Opportunity Update Error", message=f"Error updating opportunity for mobile {mobile_no}: {str(e)}\n{frappe.get_traceback()}"
        )
        return {"success": False, "message": f"Error updating opportunity: {str(e)}"}


def handle_lead_update(neodove_data, mobile_no, lead_owner, lead_stage, DEFAULT_DEPARTMENT, DEFAULT_SALUTATION, DEFAULT_SOURCE):
    """Handle updates for Lead doctype"""
    lead = get_or_create_lead(mobile_no)
    is_new = not bool(lead.get("name"))

    if is_new:
        if not lead.get("custom_department"):
            lead.custom_department = "Tele Sales - SESP"
        lead.salutation = DEFAULT_SALUTATION
        lead.source = DEFAULT_SOURCE

    update_lead_basic_info(lead, neodove_data, lead_owner, lead_stage)

    if dispose_remarks := neodove_data.get("dispose_remarks", "").strip():
        lead.append(
            "custom_neodove_remarks",
            {
                "remarks": dispose_remarks,
                "updated_on": frappe.utils.now_datetime(),
            },
        )

    if call_recordings := neodove_data.get("call_recordings"):

        existing_urls = set()
        if lead.get("custom_call_recordings"):
            existing_urls = {rec.recording_url for rec in lead.custom_call_recordings}

        now = frappe.utils.now_datetime()
        for recording in call_recordings:
            recording_url = recording.get("recording_url")
            if recording_url and recording_url not in existing_urls:
                lead.append(
                    "custom_call_recordings",
                    {"call_duration_in_sec": recording.get("call_duration_in_sec", 0), "recording_url": recording_url, "recording_time": now},
                )

    if neodove_data.get("other_properties"):
        process_other_properties(lead, neodove_data["other_properties"])

    if lead.get("custom_call_recordings"):
        for rec in lead.custom_call_recordings:
            if not rec.recording_time:
                rec.recording_time = frappe.utils.now_datetime()

    lead.flags.ignore_validate_update_after_submit = True
    lead.save(ignore_permissions=True)

    frappe.db.commit()

    return {
        "success": True,
        "message": "Lead created successfully" if is_new else "Lead updated successfully",
        "lead_name": lead.name,
        "url": lead.custom_neodove_campaign_url,
    }
