import frappe
from frappe.model.mapper import get_mapped_doc

from suntek_app.suntek.utils.lead_utils import (
    _set_missing_values,
    get_or_create_lead,
    process_other_properties,
    update_lead_basic_info,
)
from suntek_app.suntek.utils.share import share_document


def get_department_from_campaign(campaign_name):
    """Map campaign names to departments"""
    department_mapping = {
        "Domestic Sales": "Domestic (Residential) Sales Team - SESP",
        "Channel Partner": "Channel Partner - SESP",
        "Commercial Sales": "Commercial & Industrial (C&I) - SESP",
    }
    return department_mapping.get(campaign_name)


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


def handle_opportunity_update(neodove_data, mobile_no, lead_owner, lead_stage):
    try:
        existing_opp = frappe.get_list(
            "Opportunity",
            filters={"contact_mobile": mobile_no},
            fields=["name"],
            limit=1,
        )

        if existing_opp:
            opp = frappe.get_doc("Opportunity", existing_opp[0].name)
        else:
            existing_enquiry = frappe.get_list(
                "Lead", filters={"mobile_no": mobile_no}, fields=["name"], limit=1
            )

            if not existing_enquiry:
                return {
                    "success": False,
                    "message": f"No existing enquiry found with mobile number: {mobile_no}",
                }

            opp = custom_make_opportunity(existing_enquiry[0].name)
            if not opp:
                return {
                    "success": False,
                    "message": "Failed to create opportunity from enquiry",
                }

        opp.opportunity_owner = neodove_data.get("agent_email")
        owner_name = frappe.db.get_value(
            "User", neodove_data.get("agent_email"), "full_name"
        )
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
                existing_urls = {
                    rec.recording_url for rec in opp.custom_call_recordings
                }

            now = frappe.utils.now_datetime()
            for recording in call_recordings:
                recording_url = recording.get("recording_url")
                if recording_url and recording_url not in existing_urls:
                    opp.append(
                        "custom_call_recordings",
                        {
                            "call_duration_in_sec": recording.get(
                                "call_duration_in_sec", 0
                            ),
                            "recording_url": recording_url,
                            "recording_time": now,
                        },
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
            neodove_data.get("other_properties", [{}])[0].get("contact_list_name")
            if neodove_data.get("other_properties")
            else ""
        )
        opp.custom_neodove_campaign_name = neodove_data.get("campaign_name")
        opp.custom_neodove_campaign_id = neodove_campaign_id
        opp.custom_neodove_campaign_url = campaign_url

        opp.flags.ignore_validate_update_after_submit = True
        opp.save(ignore_permissions=True)

        existing_enquiry = frappe.get_list(
            "Lead", filters={"mobile_no": mobile_no}, fields=["name"], limit=1
        )
        if existing_enquiry and lead_owner:
            share_document(
                doctype="Lead",
                doc_name=existing_enquiry[0].name,
                user_email=lead_owner,
                read=1,
                write=1,
                share=1,
                notify=1,
            )

        frappe.db.commit()

        return {
            "success": True,
            "message": "Opportunity updated successfully",
            "opportunity_name": opp.name,
        }

    except Exception as e:
        frappe.log_error(
            title="Opportunity Update Error",
            message=f"Error updating opportunity for mobile {mobile_no}: {str(e)}\n{frappe.get_traceback()}",
        )
        return {"success": False, "message": f"Error updating opportunity: {str(e)}"}


def handle_lead_update(
    neodove_data,
    mobile_no,
    lead_owner,
    lead_stage,
    DEFAULT_DEPARTMENT,
    DEFAULT_SALUTATION,
    DEFAULT_SOURCE,
):
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
                    {
                        "call_duration_in_sec": recording.get(
                            "call_duration_in_sec", 0
                        ),
                        "recording_url": recording_url,
                        "recording_time": now,
                    },
                )

    if lead.name and lead_owner:
        share_document(
            doctype="Lead",
            doc_name=lead.name,
            user_email=lead_owner,
            read=1,
            write=1,
            share=1,
            notify=1,
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
        "message": "Lead created successfully"
        if is_new
        else "Lead updated successfully",
        "lead_name": lead.name,
        "url": lead.custom_neodove_campaign_url,
    }
