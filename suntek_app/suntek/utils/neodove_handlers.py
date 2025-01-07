import frappe


def process_call_recordings(lead, recordings):
    """Process and add call recordings to lead with error handling"""
    try:
        if not _validate_recording_inputs(lead, recordings):
            return

        _ensure_lead_exists(lead)

        new_recordings = _filter_new_recordings(lead, recordings)
        _add_recordings_to_lead(lead, new_recordings)

        _save_lead_with_recordings(lead)

    except frappe.ValidationError as e:
        frappe.logger().error(
            f"Validation error processing recordings for lead {lead.name}: {str(e)}"
        )
        raise
    except Exception as e:
        frappe.logger().error(
            f"Error processing recordings for lead {lead.name}: {str(e)}\n"
            f"Traceback: {frappe.get_traceback()}"
        )
        raise frappe.ValidationError(f"Failed to process recordings: {str(e)}")


def _validate_recording_inputs(lead, recordings):
    """Validate input parameters"""
    if not recordings:
        frappe.logger().debug("No recordings to process")
        return False

    if not lead:
        frappe.logger().error("No lead provided")
        raise frappe.ValidationError("Lead is required")

    return True


def _ensure_lead_exists(lead):
    """Ensure lead exists in database"""
    if not lead.name:
        try:
            lead.save(ignore_permissions=True)
            frappe.db.commit()
        except Exception as e:
            frappe.logger().error(f"Failed to save lead: {str(e)}")
            raise frappe.ValidationError("Failed to save lead")


def _filter_new_recordings(lead, recordings):
    """Filter out existing recordings"""
    new_recordings = []
    existing_urls = set()

    if lead.get("custom_call_recordings"):
        existing_urls = {rec.recording_url for rec in lead.custom_call_recordings}

    for recording in recordings:
        if not recording.get("recording_url"):
            continue

        if recording["recording_url"] not in existing_urls:
            new_recordings.append(recording)

    return new_recordings


def _add_recordings_to_lead(lead, new_recordings):
    """Add new recordings to lead"""
    for recording in new_recordings:
        try:
            lead.append(
                "custom_call_recordings",
                {
                    "doctype": "Neodove Call Recordings",
                    "call_duration_in_sec": recording.get("call_duration_in_sec") or 0,
                    "recording_url": recording["recording_url"],
                    "enquiry": lead.name,
                    "parenttype": "Lead",
                    "parentfield": "custom_call_recordings",
                    "parent": lead.name,
                },
            )
        except Exception as e:
            frappe.logger().error(f"Failed to add recording: {str(e)}")
            raise frappe.ValidationError(f"Failed to add recording: {str(e)}")


def _save_lead_with_recordings(lead):
    """Save lead with new recordings"""
    try:
        lead.flags.ignore_validate_update_after_submit = True
        lead.save(ignore_permissions=True)
        frappe.db.commit()
    except Exception as e:
        frappe.logger().error(f"Failed to save lead with recordings: {str(e)}")
        raise frappe.ValidationError("Failed to save recordings")
