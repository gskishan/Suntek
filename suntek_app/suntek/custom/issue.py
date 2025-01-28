import frappe
import requests

from suntek_app.suntek.custom.lead import parse_request_data
from suntek_app.suntek.utils.api_handler import create_api_response

CATEGORY_MAP = {
    "advisory": "Advisory",
    "suggestions": "Suggestions",
    "inverter_abnormal": "Inverter Abnormal",
    "storage_machine_failed": "Storage Machine Failed",
    "monitoring_system_problems": "Monitoring System Problem",
    "other_questions": "Other Questions",
}


@frappe.whitelist(allow_guest=True)
def create_issue_from_api():
    """Create an issue from API request with proper validation and error handling.

    Request Body:
    ```{
        "custom_phone_number": str,          # Required. Customer's phone number
        "subject": str,                      # Required. Issue subject/title
        "customer_name": str,                # Optional. Name for new customer if not found
        "custom_inverter_serial_no": str,    # Optional. Serial number of the inverter
        "custom_mode_of_complaint": str,     # Optional. Description of the issue
        "custom_source": str,                # Optional. Source of the issue (defaults to "Customer App")
        "custom_product_category": str,      # Optional. Category of the product issue
                                            # Valid categories: "advisory", "suggestions",
                                            # "inverter_abnormal", "storage_machine_failed",
                                            # "monitoring_system_problems", "other_questions"
        "custom_images": list[str]           # Optional. List of image URLs
    }```

    Returns:
        dict: Response containing status and issue details
        ```{
            "status": "success",
            "message": "Issue created successfully",
            "data": {
                "name": str,          # Issue ID
                "subject": str,       # Issue subject
                "customer": str,      # Customer ID
                "issue_status": str,  # Status of the issue
                "mobile_no": str      # Customer's phone number
            }
        }```

    Raises:
        401: Invalid or missing API token
        400: Validation error or missing required fields
        403: Permission error
        404: Resource not found
        500: Server error
    """
    try:

        auth_token = frappe.request.headers.get("X-Django-Server-Authorization")
        if not auth_token or auth_token.split(" ")[1] != frappe.get_doc("Suntek Settings").get_password("solar_ambassador_api_token"):
            return create_api_response(401, "error", "Invalid or missing API token")

        if frappe.request.method != "POST":
            return create_api_response(405, "error", "Method Not Allowed. Only POST requests are supported.")

        frappe.set_user('developer@suntek.co.in')
        issue_api_data = parse_request_data(frappe.request.data)

        issue = frappe.new_doc("Issue")

        mobile_no = issue_api_data.get("custom_phone_number")
        if not mobile_no:
            return create_api_response(400, "error", "Phone number is required")

        mobile_no = issue_api_data.get("custom_phone_number")
        if not mobile_no:
            return create_api_response(400, "error", "Phone number is required")

        customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, ["name", "customer_name"], as_dict=1)

        if customer:
            issue.customer = customer.name
            issue.custom_existing_customer = 1
        else:
            # Create new customer if not found
            customer_name = issue_api_data.get("customer_name", f"Customer {mobile_no}")  # Default name if not provided

            new_customer = frappe.new_doc("Customer")
            new_customer.customer_name = customer_name
            new_customer.mobile_no = mobile_no
            new_customer.customer_type = "Individual"
            new_customer.insert(ignore_permissions=True)

            issue.customer = new_customer.name
            issue.custom_existing_customer = 0

        issue.subject = issue_api_data.get("subject")
        issue.custom_inverter_serial_no = issue_api_data.get("custom_inverter_serial_no")
        issue.custom_source = issue_api_data.get("source", "Customer App")
        issue.custom_mode_of_complaint = issue_api_data.get(
            "custom_mode_of_complaint", ""
        )  # This field is not actually mode of complaint, it is the description in the document

        custom_product_category = issue_api_data.get("custom_product_category")
        for key, value in CATEGORY_MAP.items():
            if key in custom_product_category:
                issue.custom_product_category = value
                break

        for image_url in issue_api_data.get("custom_images", []):
            issue.append("custom_images", {"issue_image": image_url})

        issue.insert(ignore_permissions=True)
        frappe.db.commit()

        return create_api_response(
            201,
            "success",
            "Issue created successfully",
            {
                "name": issue.name,
                "subject": issue.subject,
                "customer": issue.customer,
                "issue_status": issue.status,
                "mobile_no": mobile_no,
            },
        )

    except frappe.ValidationError as e:
        frappe.log_error(message=str(e), title="Issue Creation Validation Error")
        return create_api_response(400, "error", str(e))

    except frappe.PermissionError as e:
        frappe.log_error(message=str(e), title="Issue Creation Permission Error")
        return create_api_response(403, "error", str(e))
    except frappe.DoesNotExistError as e:
        frappe.log_error(message=str(e), title="Issue Creation Not Found Error")
        return create_api_response(404, "error", str(e))
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
