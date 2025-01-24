import frappe
import requests
from suntek_app.suntek.custom.lead import parse_request_data


@frappe.whitelist(allow_guest=True)
def create_issue_from_api():
    try:
        frappe.set_user("Administrator")

        issue_api_data = parse_request_data(frappe.request.data)

        issue = frappe.new_doc("Issue")

        issue.subject = issue_api_data.get("subject")
        issue.custom_product_category = issue_api_data.get("custom_product_category")
        issue.custom_inverter_serial_no = issue_api_data.get("custom_inverter_serial_no")
        issue.customer = issue_api_data.get("customer")
        issue.custom_source = issue_api_data.get("source", "Customer App")

        images = issue_api_data.get("custom_images", [])

        if images:
            for image_url in images:
                issue.append("custom_images", {"issue_image": image_url})

        issue.insert(ignore_permissions=True)
        frappe.db.commit()

        result = {
            "status": "success",
            "message": "Issue created successfully",
            "data": {"name": issue.name, "subject": issue.subject},
        }

    except Exception as e:
        result = {"status": "error", "message": str(e), "data": issue_api_data}
        frappe.db.rollback()

    finally:
        frappe.set_user("Guest")
        return result


def send_issue_update_to_ambassador_api(doc, method):

    webhook_data = {
        "name": doc.name,
        "raised_by": doc.raised_by,
        "subject": doc.subject,
        "customer": doc.customer,
        "issue_status": doc.status,
        "contact_person": doc.custom_contact_person_name,
        "contact_person_phone": doc.custom_contact_person_mobile,
        "closed_opening_date": doc.custom_closedpending_date,
    }

    settings = frappe.get_doc("Suntek Settings")
    django_api_url = f"{settings.get("django_api_url")}webhook/issue-updated"
    api_token = settings.get_password("solar_ambassador_api_token")

    if not django_api_url or not api_token:
        frappe.log_error("Django webhook URL or API token not configured in Suntek Settings")
        return False

    headers = {"X-Django-Server-Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

    response = requests.post(django_api_url, json=webhook_data, headers=headers, timeout=10)

    if response.status_code != 200:
        frappe.log_error(f"Failed to send webhook for issue {doc.name}: {response.text}", title="Webhook Error")
        return False

    return True


"""
if dispose_remarks := neodove_data.get("dispose_remarks", "").strip():
    opp.append(
        "custom_neodove_dispose_remarks",
        {
            "remarks": dispose_remarks,
            "updated_on": frappe.utils.now_datetime(),
        },
    )
"""
