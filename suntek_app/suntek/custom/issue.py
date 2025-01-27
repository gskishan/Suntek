import frappe
import requests
from suntek_app.suntek.custom.lead import parse_request_data


from suntek_app.suntek.utils.api_handler import create_api_response


CATEGORY_MAP = {
    "advisory": "Advisory",
    "suggestions": "Suggestions",
    "inverter_abnormal": "Inverter Abnormal",
    "storage_machine_failed": "Storage Machine Failed",
    "monitoring_system_problems": "Monitoring System Problems",
    "other_questions": "Other Questions",
}


@frappe.whitelist(allow_guest=True)
def create_issue_from_api():
    try:

        auth_token = frappe.request.headers.get("X-Django-Server-Authorization")
        if auth_token:
            auth_token = auth_token.split(" ")[1]
        local_token = frappe.get_doc("Suntek Settings").get_password("solar_ambassador_api_token")

        if not auth_token or auth_token != local_token:
            return create_api_response(401, "error", "Invalid or missing API token")

        if frappe.request.method != "POST":
            return create_api_response(405, "error", "Method Not Allowed. Only POST requests are supported.")

        frappe.set_user('developer@suntek.co.in')

        issue_api_data = parse_request_data(frappe.request.data)

        issue = frappe.new_doc("Issue")

        mobile_no = issue_api_data.get("custom_phone_number")

        issue.subject = issue_api_data.get("subject")
        issue.custom_inverter_serial_no = issue_api_data.get("custom_inverter_serial_no")
        issue.custom_source = issue_api_data.get("source", "Customer App")
        issue.custom_mode_of_complaint = issue_api_data.get("custom_mode_of_complaint", "")

        customer = frappe.get_doc("Customer", {"mobile_no": mobile_no})

        if not customer:
            return create_api_response(404, "error", "Customer not found")

        issue.customer = customer.name

        custom_product_category = issue_api_data.get("custom_product_category")
        for key, value in CATEGORY_MAP.items():
            if key in custom_product_category:
                issue.custom_product_category = value
                break

        images = issue_api_data.get("custom_images", [])

        if images:
            for image_url in images:
                issue.append("custom_images", {"issue_image": image_url})

        issue.insert(ignore_permissions=True)
        frappe.db.commit()

        response = create_api_response(
            201,
            "success",
            "Issue created successfully",
            {
                "name": issue.name,
                "subject": issue.subject,
                "customer": issue.customer,
                "issue_status": issue.status,
            },
        )

        return response

    except Exception as e:
        frappe.log_error(message=str(e), title="Issue Creation Error")
        return create_api_response(500, "error", str(e))


def send_issue_update_to_ambassador_api(doc, method):
    try:
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
        django_api_url = f"{settings.get('django_api_url')}/support/webhook/issue-updated"
        api_token = settings.get_password("solar_ambassador_api_token")

        if not django_api_url or not api_token:
            frappe.log_error("Django webhook URL or API token not configured in Suntek Settings")
            return False

        headers = {
            "X-Django-Server-Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
        }

        response = requests.put(django_api_url, json=webhook_data, headers=headers)

        if response.status_code != 200:
            frappe.log_error(
                f"Failed to send webhook for issue {doc.name}: {response.text}",
            )
            return False

        return True
    except Exception as e:
        frappe.log_error(f"Error in send_issue_update_to_ambassador_api: {str(e)}")
        return False
