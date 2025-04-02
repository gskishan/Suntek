import json

import frappe
import requests
from bs4 import BeautifulSoup

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


def validate_auth_token(auth_token: str) -> bool:
    if not auth_token:
        return False
    try:
        token = auth_token.split(" ")[1]
        return token == frappe.get_doc("Suntek Settings").get_password("solar_ambassador_api_token")
    except (IndexError, AttributeError):
        return False


def create_or_get_customer(mobile_no, customer_name=None):
    customer = frappe.db.get_value("Customer", {"mobile_no": mobile_no}, ["name", "customer_name"], as_dict=1)

    if customer:
        return customer_name, True

    new_customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": customer_name or f"Customer {mobile_no}",
            "mobile_no": mobile_no,
            "customer_type": "Individual",
        }
    ).insert(ignore_permissions=True)

    return new_customer.name, False


def get_product_category(category_key):
    return CATEGORY_MAP.get(category_key, "Other Questions")


@frappe.whitelist(allow_guest=True)
def create_issue_from_api():
    """Create an issue from API request with proper validation and error handling.

    Request Headers:
    ```
    {
        "X-Django-Server-Authorization": "Bearer <API_TOKEN>"
        "Content-Type": "application/json"
    }
    ```

    Request Body:
    ```py
    {
        "custom_phone_number": str,
        "subject": str,
        "customer_name": str,
        "custom_inverter_serial_no": str,
        "custom_mode_of_complaint": str,
        "custom_source": str,
        "custom_product_category": str,



        "custom_images": list[str]
    }
    ```

    Returns:
        dict: Response containing status and issue details
        ```py
        {
            "status": "success",
            "message": "Issue created successfully",
            "data": {
                "name": str,
                "subject": str,
                "customer": str,
                "issue_status": str,
                "mobile_no": str
            }
        }
        ```

    Raises:
        401: Invalid or missing API token
        400: Validation error or missing required fields
        403: Permission error
        404: Resource not found
        500: Server error
    """
    try:
        auth_token = frappe.request.headers.get("X-Django-Server-Authorization")
        if not validate_auth_token(auth_token):
            return create_api_response(401, "error", "Invalid or missing API token")

        if frappe.request.method != "POST":
            return create_api_response(405, "error", "Method Not Allowed. Only POST requests are supported.")

        frappe.set_user("developer@suntek.co.in")
        issue_api_data = parse_request_data(frappe.request.data)

        mobile_no = issue_api_data.get("custom_phone_number")
        if not mobile_no:
            return create_api_response(400, "error", "Phone number is required")

        customer_name, is_existing = create_or_get_customer(mobile_no, issue_api_data.get("customer_name"))

        issue = frappe.get_doc(
            {
                "doctype": "Issue",
                "customer": customer_name,
                "custom_existing_customer": 1 if is_existing else 0,
                "subject": issue_api_data.get("subject"),
                "custom_inverter_serial_no": issue_api_data.get("custom_inverter_serial_no"),
                "custom_source": issue_api_data.get("source", "Customer App"),
                "custom_mode_of_complaint": issue_api_data.get("custom_mode_of_complaint", ""),
                "custom_product_category": get_product_category(issue_api_data.get("custom_product_category")),
                "custom_images": [{"issue_image": url} for url in issue_api_data.get("custom_images", [])],
            }
        ).insert(ignore_permissions=True)

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

    except (
        frappe.ValidationError,
        frappe.PermissionError,
        frappe.DoesNotExistError,
    ) as e:
        error_type = e.__class__.__name__.replace("Error", "")
        frappe.log_error(message=str(e), title=f"Issue Creation {error_type} Error")
        status_code = {"Validation": 400, "Permission": 403, "DoesNotExist": 404}[error_type]
        return create_api_response(status_code, "error", str(e))
    except Exception as e:
        frappe.log_error(message=str(e), title="Issue Creation Error")
        return create_api_response(500, "error", str(e))


def send_issue_update_to_ambassador_api(doc, method):
    if doc.custom_source == "Customer App":
        try:
            settings = frappe.get_doc("Suntek Settings")
            django_api_url = settings.get("django_api_url")
            api_token = settings.get_password("solar_ambassador_api_token")

            if not (django_api_url and api_token):
                frappe.log_error("Django webhook URL or API token not configured in Suntek Settings")
                return False

            comments_data = get_comments(doc) or []
            resolution_details = get_clean_html_content(doc.resolution_details)

            webhook_data = {
                "name": doc.name,
                "raised_by": doc.raised_by,
                "subject": doc.subject,
                "customer": doc.customer,
                "issue_status": doc.status,
                "contact_person": doc.custom_contact_person_name,
                "contact_person_phone": doc.custom_contact_person_mobile,
                "closed_opening_date": doc.custom_closedpending_date,
                "resolution_details": resolution_details,
                "comments": comments_data,
            }

            print(json.dumps(webhook_data, indent=4))  # TODO: Remove later

            response = requests.put(
                f"{django_api_url}/support/webhook/issue-updated",
                json=webhook_data,
                headers={
                    "X-Django-Server-Authorization": f"Bearer {api_token}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code != 200:
                frappe.log_error(f"Failed to send webhook for issue {doc.name}: {response.text}")
                return False

            return True
        except Exception as e:
            frappe.log_error(f"Error in send_issue_update_to_ambassador_api: {str(e)}")
            print(f"Error: {str(e)}")
            return False


def get_comments(doc, method=None):
    try:
        comments = frappe.get_all(
            "Comment",
            filters={"reference_doctype": "Issue", "reference_name": doc.name},
            fields=["name", "content", "creation", "owner"],
            order_by="creation desc",
        )

        if comments:
            comments_data = []
            for comment in comments:
                text = get_clean_html_content(comment.content)

                comments_data.append(
                    {
                        "comment_id": comment.name,
                        "content": text,
                        "owner": comment.owner,
                        "creation": comment.creation.strftime("%Y-%m-%d %H:%M:%S"),
                    }
                )

            return comments_data

    except Exception as e:
        print(str(e))


def get_clean_html_content(html_content):
    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.find("div", class_="ql-editor").get_text(strip=True)
    return text
