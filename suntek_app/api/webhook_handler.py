import frappe
import requests
from frappe.utils import get_datetime_str


def get_ambassador_lead_details(doc_type, doc):
    lead_details = None

    if doc_type == "Lead":
        if doc.source == "Ambassador" and doc.custom_ambassador:
            lead_details = {
                "lead_id": doc.name,
                "ambassador_id": doc.custom_ambassador,
                "ambassador_mobile_number": doc.custom_ambassador_mobile_number or "",
                "mobile_no": doc.mobile_no or "",
                "first_name": doc.first_name or "",
                "last_name": doc.last_name or "",
                "email": doc.email_id or "",
                "lead_owner": doc.lead_owner or "",
                "enquiry_status": doc.custom_enquiry_status or "",
                "department": doc.custom_department or "",
            }

    elif doc_type == "Opportunity":
        if doc.custom_ambassador:
            lead_id = None
            if doc.opportunity_from == "Lead" and doc.party_name:
                lead_id = doc.party_name

            if lead_id:
                try:
                    lead = frappe.get_doc("Lead", lead_id)
                    lead_details = {
                        "lead_id": lead_id,
                        "ambassador_id": doc.custom_ambassador,
                        "ambassador_mobile_number": doc.custom_ambassador_mobile_number
                        or "",
                        "mobile_no": lead.mobile_no or "",
                        "first_name": lead.first_name or "",
                        "last_name": lead.last_name or "",
                        "email": lead.email_id or "",
                        "lead_owner": lead.lead_owner or "",
                        "enquiry_status": doc.custom_enquiry_status or "",
                        "department": doc.custom_department or "",
                        "opportunity_id": doc.name,
                    }
                except Exception:
                    pass

    elif doc_type == "Quotation":
        if doc.custom_ambassador:
            lead_id = None
            if doc.quotation_to == "Lead":
                lead_id = doc.party_name
            elif doc.opportunity:
                opportunity = frappe.get_doc("Opportunity", doc.opportunity)
                if opportunity.opportunity_from == "Lead":
                    lead_id = opportunity.party_name

            if lead_id:
                try:
                    lead = frappe.get_doc("Lead", lead_id)
                    lead_details = {
                        "lead_id": lead_id,
                        "ambassador_id": doc.custom_ambassador,
                        "ambassador_mobile_number": doc.custom_ambassador_mobile_number
                        or "",
                        "mobile_no": lead.mobile_no or "",
                        "first_name": lead.first_name or "",
                        "last_name": lead.last_name or "",
                        "email": lead.email_id or "",
                        "lead_owner": lead.lead_owner or "",
                        "enquiry_status": lead.custom_enquiry_status or "",
                        "department": lead.custom_department or "",
                        "opportunity_id": doc.opportunity or "",
                        "quotation_id": doc.name,
                    }
                except Exception:
                    pass

    elif doc_type == "Sales Order":
        try:
            opportunity_id = None
            quotation_id = None
            lead_id = None

            if hasattr(doc, "opportunity") and doc.opportunity:
                opportunity_id = doc.opportunity

                try:
                    opportunity = frappe.get_doc("Opportunity", opportunity_id)

                    if opportunity.custom_ambassador:
                        if (
                            opportunity.opportunity_from == "Lead"
                            and opportunity.party_name
                        ):
                            lead_id = opportunity.party_name
                            lead = frappe.get_doc("Lead", lead_id)

                            lead_details = {
                                "lead_id": lead_id,
                                "ambassador_id": opportunity.custom_ambassador,
                                "ambassador_mobile_number": opportunity.custom_ambassador_mobile_number
                                or "",
                                "mobile_no": lead.mobile_no or "",
                                "first_name": lead.first_name or "",
                                "last_name": lead.last_name or "",
                                "email": lead.email_id or "",
                                "lead_owner": lead.lead_owner or "",
                                "enquiry_status": lead.custom_enquiry_status or "",
                                "department": lead.custom_department or "",
                                "opportunity_id": opportunity_id,
                                "sales_order_id": doc.name,
                            }

                            quotation_list = frappe.get_all(
                                "Quotation",
                                filters={"opportunity": opportunity_id},
                                fields=["name"],
                            )

                            if quotation_list:
                                lead_details["quotation_id"] = quotation_list[0].name
                except Exception as e:
                    frappe.log_error(
                        f"Error getting opportunity details for sales order {doc.name}: {str(e)}",
                        "Ambassador Sales Order Webhook Error",
                    )

            if not lead_details and doc.custom_ambassador:
                quotation_field_options = [
                    "sales_order_from_quotation",
                    "quotation",
                    "prevdoc_docname",
                ]
                for field in quotation_field_options:
                    if hasattr(doc, field) and doc.get(field):
                        quotation_id = doc.get(field)
                        break

                if not quotation_id and hasattr(doc, "items") and doc.items:
                    for item in doc.items:
                        if item.get("prevdoc_docname"):
                            quotation_id = item.prevdoc_docname
                            break

                if quotation_id:
                    try:
                        quotation = frappe.get_doc("Quotation", quotation_id)

                        if quotation.opportunity:
                            opportunity_id = quotation.opportunity

                        if quotation.quotation_to == "Lead" and quotation.party_name:
                            lead_id = quotation.party_name
                        elif opportunity_id:
                            opportunity = frappe.get_doc("Opportunity", opportunity_id)
                            if (
                                opportunity.opportunity_from == "Lead"
                                and opportunity.party_name
                            ):
                                lead_id = opportunity.party_name

                        if lead_id:
                            lead = frappe.get_doc("Lead", lead_id)

                            lead_details = {
                                "lead_id": lead_id,
                                "ambassador_id": doc.custom_ambassador,
                                "ambassador_mobile_number": doc.custom_ambassador_mobile_number
                                or "",
                                "mobile_no": lead.mobile_no or "",
                                "first_name": lead.first_name or "",
                                "last_name": lead.last_name or "",
                                "email": lead.email_id or "",
                                "lead_owner": lead.lead_owner or "",
                                "enquiry_status": lead.custom_enquiry_status or "",
                                "department": lead.custom_department or "",
                                "opportunity_id": opportunity_id or "",
                                "quotation_id": quotation_id,
                                "sales_order_id": doc.name,
                            }
                    except Exception as e:
                        frappe.log_error(
                            f"Error getting quotation details for sales order {doc.name}: {str(e)}",
                            "Ambassador Sales Order Webhook Error",
                        )

            if not lead_details and doc.custom_ambassador:
                frappe.log_error(
                    f"Sales Order {doc.name} has ambassador {doc.custom_ambassador} but couldn't find associated lead",
                    "Ambassador Sales Order Debug",
                )

        except Exception as e:
            frappe.log_error(
                f"Error processing sales order {doc.name}: {str(e)}",
                "Ambassador Sales Order Webhook Error",
            )

    return lead_details


def get_mobile_app_status(doc_type, status):
    """
    Map document status to mobile app status
    Returns one of: Open, In Progress, Confirmed, Cancelled
    """

    if doc_type == "Lead":
        status_mapping = {
            "Open": "Open",
            "Replied": "In Progress",
            "Opportunity": "In Progress",
            "Quotation": "In Progress",
            "Lost Quotation": "Cancelled",
            "Interested": "In Progress",
            "Converted": "Confirmed",
            "Do Not Contact": "Cancelled",
        }
    elif doc_type == "Quotation":
        status_mapping = {
            "Draft": "In Progress",
            "Open": "In Progress",
            "Replied": "In Progress",
            "Partially Ordered": "In Progress",
            "Ordered": "Confirmed",
            "Lost": "Cancelled",
            "Cancelled": "Cancelled",
            "Expired": "Cancelled",
        }
    elif doc_type == "Sales Order":
        status_mapping = {
            "Draft": "In Progress",
            "On Hold": "In Progress",
            "To Deliver and Bill": "Confirmed",
            "To Bill": "Confirmed",
            "To Deliver": "Confirmed",
            "Completed": "Confirmed",
            "Cancelled": "Cancelled",
            "Closed": "Cancelled",
        }
    else:
        status_mapping = {
            "Open": "Open",
            "Closed": "Cancelled",
            "Customer Confirmed": "Confirmed",
            "In Progress": "In Progress",
            "New": "Open",
            "Payment pending": "In Progress",
            "PO send": "Confirmed",
            "Waiting on client approval": "In Progress",
            "Rejected by client": "Cancelled",
            "Rejected by Suntek": "Cancelled",
            "Quotation": "In Progress",
            "Converted": "Confirmed",
            "Lost": "Cancelled",
            "Replied": "In Progress",
        }

    if doc_type == "Lead":
        return status_mapping.get(status, "Open")
    elif doc_type in ["Quotation", "Opportunity"]:
        return status_mapping.get(status, "In Progress")
    elif doc_type == "Sales Order":
        return status_mapping.get(status, "Confirmed")
    else:
        return status_mapping.get(status, "Open")


def send_ambassador_status_update(doc, method=None):
    try:
        doc_type = doc.doctype

        if (
            doc_type == "Sales Order"
            and hasattr(doc, "custom_ambassador")
            and doc.custom_ambassador
        ):
            frappe.log_error(
                f"Processing Sales Order {doc.name} with ambassador {doc.custom_ambassador}",
                "Ambassador Sales Order Processing",
            )

        lead_details = get_ambassador_lead_details(doc_type, doc)

        if not lead_details:
            if (
                doc_type == "Sales Order"
                and hasattr(doc, "custom_ambassador")
                and doc.custom_ambassador
            ):
                debug_info = {
                    "name": doc.name,
                    "ambassador": doc.custom_ambassador,
                    "customer": getattr(doc, "customer", ""),
                    "opportunity": getattr(doc, "opportunity", ""),
                    "has_items": hasattr(doc, "items") and bool(doc.items),
                    "creation_date": str(doc.creation),
                }
                frappe.log_error(
                    f"Sales Order details: {debug_info}",
                    "Ambassador Sales Order Debug - No Lead Found",
                )
            return

        settings = frappe.get_doc("Suntek Settings")

        if (
            not settings.django_api_url
            or settings.solar_ambassador_integration_status == "Disabled"
        ):
            return

        api_url = f"{settings.django_api_url}/api/leads/status_update/"
        api_token = f"Bearer {frappe.get_doc('Suntek Settings').get_password('solar_ambassador_api_token')}"

        if doc_type == "Lead":
            status = doc.status
            crm_status = doc.status
        elif doc_type == "Opportunity":
            status = doc.custom_enquiry_status or doc.status
            crm_status = f"Opportunity: {status}"
        elif doc_type == "Quotation":
            status = doc.status
            crm_status = f"Quotation: {status}"
        elif doc_type == "Sales Order":
            status = doc.status
            crm_status = f"Sales Order: {status}"
        else:
            return

        mobile_app_status = get_mobile_app_status(doc_type, status)

        capacity = None
        sales_order_value = None

        if doc_type == "Sales Order":
            capacity = doc.custom_capacity if hasattr(doc, "custom_capacity") else None
            sales_order_value = doc.grand_total if hasattr(doc, "grand_total") else None

        elif hasattr(doc, "custom_capacity"):
            capacity = doc.custom_capacity

        if lead_details.get("sales_order_id") and not sales_order_value:
            try:
                so_doc = frappe.get_doc("Sales Order", lead_details["sales_order_id"])
                sales_order_value = (
                    so_doc.grand_total if hasattr(so_doc, "grand_total") else None
                )
                if not capacity and hasattr(so_doc, "custom_capacity"):
                    capacity = so_doc.custom_capacity
            except Exception:
                pass

        payload = {
            "lead_id": lead_details.get("lead_id"),
            "ambassador_id": lead_details.get("ambassador_id"),
            "status": mobile_app_status,
            "crm_status": crm_status,
            "enquiry_status": lead_details.get("enquiry_status", ""),
            "department": lead_details.get("department", ""),
            "updated_at": get_datetime_str(doc.modified),
            "lead_owner": lead_details.get("lead_owner", ""),
            "mobile_no": lead_details.get("mobile_no", ""),
            "first_name": lead_details.get("first_name", ""),
            "last_name": lead_details.get("last_name", ""),
            "email": lead_details.get("email", ""),
        }

        if capacity is not None:
            payload["capacity"] = capacity

        if sales_order_value is not None:
            payload["sales_order_value"] = sales_order_value

        if lead_details.get("opportunity_id"):
            payload["opportunity_id"] = lead_details["opportunity_id"]
        if lead_details.get("quotation_id"):
            payload["quotation_id"] = lead_details["quotation_id"]
        if lead_details.get("sales_order_id"):
            payload["sales_order_id"] = lead_details["sales_order_id"]

        headers = {"X-Django-Server-Authorization": api_token}
        response = requests.post(api_url, json=payload, headers=headers)

        if response.status_code not in [200, 201]:
            frappe.log_error(
                f"Failed to send Ambassador status update: {response.text}",
                f"Ambassador {doc_type} Webhook Error",
            )
        else:
            if doc_type == "Sales Order":
                frappe.log_error(
                    f"Successfully sent update for Sales Order {doc.name} with status {mobile_app_status}",
                    "Ambassador Sales Order Success",
                )

    except Exception as e:
        frappe.log_error(
            f"Error sending Ambassador status update: {str(e)}",
            f"Ambassador {doc.doctype} Webhook Error",
        )
