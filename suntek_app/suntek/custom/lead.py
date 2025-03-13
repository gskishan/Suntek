import hmac

import frappe
from frappe.model.mapper import get_mapped_doc

from suntek_app.suntek.utils.api_handler import create_api_response, parse_request_data
from suntek_app.suntek.utils.lead_utils import _set_missing_values, get_next_telecaller
from suntek_app.suntek.utils.neodove_utils.neodove_handler import (
    handle_lead_update,
    handle_opportunity_update,
)
from suntek_app.suntek.utils.share import share_document
from suntek_app.suntek.utils.validation_utils import (
    duplicate_check,
    validate_mobile_number,
)


def set_state(doc, method):
    doc.state = doc.custom_suntek_state or ""


def save_name_changes_to_contact(doc, method=None):
    contact = frappe.db.get_value(
        "Contact", {"mobile_no": doc.mobile_no}, ["name"], as_dict=1
    )
    if not contact:
        return

    contact_doc = frappe.get_doc("Contact", contact.name)

    salutations = {s.name for s in frappe.db.get_list("Salutation")}
    name_parts = doc.lead_name.split()
    if name_parts and name_parts[0] in salutations:
        name_parts.pop(0)

    if not name_parts:
        first_name = middle_name = last_name = ""
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1] if len(name_parts) > 1 else ""
        middle_name = " ".join(name_parts[1:-1]) if len(name_parts) > 2 else ""

    contact_doc.first_name = first_name
    contact_doc.last_name = last_name
    contact_doc.middle_name = middle_name

    contact_doc.save()
    frappe.db.commit()


def share_lead_after_insert_with_enquiry_owner(doc, method=None):
    """Share the document with the lead owner with read, write and share permissions"""
    if doc.is_new():
        return

    share_document(
        doctype="Lead",
        doc_name=doc.name,
        user_email=doc.lead_owner,
        read=1,
        write=1,
        share=1,
        notify=1,
    )


def validate_enquiry_mobile_no(doc, method=None):
    """Validate enquiry's mobile number before save, should be 10 digits, should not contain spaces, should start 6, 7, 8, 9"""
    try:
        mobile_no = doc.mobile_no.replace(" ", "")

        try:
            int(mobile_no)
        except ValueError:
            frappe.throw("Mobile number should contain only digits")

        if len(mobile_no) != 10:
            frappe.throw("Mobile number should be exactly 10 digits")

        if mobile_no[0] not in "6789":
            frappe.throw("Mobile number should start with 6, 7, 8 or 9")

        doc.mobile_no = mobile_no

    except Exception as e:
        frappe.log_error(
            "Validation Error",
            f"Error validating enquiry mobile number: {str(e)}",
            "Lead",
        )
        frappe.throw(f"Invalid mobile number: {str(e)}")


def set_lead_owner(doc, method):
    """Set lead_owner to current user if not set"""
    if not doc.lead_owner and doc.is_new():
        doc.lead_owner = frappe.session.user
        doc.custom_enquiry_owner_name = frappe.get_value(
            "User", frappe.session.user, "full_name"
        )


def change_enquiry_status(doc, method):
    try:
        validate_mobile_number(doc.mobile_no)
        duplicate_check(doc)

        if doc.lead_owner:
            return

        enable_round_robin = frappe.db.get_single_value(
            "Suntek Settings", "enable_round_robin_assignment_to_enquiries"
        )
        if not enable_round_robin:
            return

        is_import = (
            frappe.flags.in_import if hasattr(frappe.flags, "in_import") else False
        )
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
                    "custom_is_channel_partnered": "custom_is_channel_partnered",
                    "custom_channel_partner": "custom_channel_partner",
                    "custom_channel_partner_name": "custom_channel_partner_name",
                    "custom_suntek_state": "custom_suntek_state",
                    "custom_suntek_city": "custom_suntek_city",
                    "custom_suntek_district": "custom_suntek_district",
                },
            }
        },
        target_doc,
        set_missing_values,
    )

    return target_doc


@frappe.whitelist(allow_guest=True)
def create_lead_from_neodove_dispose():
    """Handle incoming Neodove webhook requests to create/update leads or opportunities"""
    try:
        is_enabled = frappe.get_doc("Suntek Settings").get_value(
            "enable_neodove_integration"
        )

        if not is_enabled:
            return create_api_response(400, "error", "Neodove integration is disabled")

        api_key = frappe.request.headers.get("X-Neodove-API-Key")
        if not api_key:
            return create_api_response(401, "error", "API key missing")

        if not _validate_api_key(api_key):
            return create_api_response(401, "error", "Invalid API key")

        neodove_data = parse_request_data(frappe.request.data)
        campaign_id = neodove_data.get("campaign_id")

        if not campaign_id:
            return create_api_response(400, "error", "Campaign ID is required")

        campaign = _get_campaign_info(campaign_id)
        if not campaign:
            return create_api_response(
                404, "error", f"Campaign not found: {campaign_id}"
            )

        mobile = neodove_data.get("mobile")
        agent_email = neodove_data.get("agent_email")
        lead_stage = neodove_data.get("lead_stage_name")

        frappe.set_user(agent_email)

        result = (
            handle_opportunity_update(neodove_data, mobile, agent_email, lead_stage)
            if campaign.pipeline_name
            and campaign.pipeline_name.lower() == "opportunities"
            else handle_lead_update(
                neodove_data, mobile, agent_email, lead_stage, "", "", ""
            )
        )

        return create_api_response(200, "success", result["message"], result)

    except Exception as e:
        frappe.log_error(
            message=f"Neodove webhook error: {str(e)}\n{frappe.get_traceback()}",
            title="Neodove Webhook Error",
        )
        return create_api_response(500, "error", str(e))


def _validate_api_key(api_key: str) -> bool:
    """Validate API key with optimized caching"""
    CACHE_KEY = "neodove_webhook_secret"
    CACHE_TTL = 3600

    try:
        stored_key = frappe.cache().get_value(CACHE_KEY)

        if stored_key and hmac.compare_digest(api_key, stored_key):
            return True

        current_key = frappe.get_doc("Suntek Settings").get_password(
            "neodove_webhook_secret"
        )

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
