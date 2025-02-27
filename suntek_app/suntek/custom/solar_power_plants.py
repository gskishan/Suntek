import time
from typing import Dict

import frappe
import requests

from suntek_app.suntek.custom.lead import parse_request_data
from suntek_app.suntek.utils.api_handler import create_api_response


def handle_solar_ambassador_webhook(doc, method=None):
    try:
        old_doc = doc.get_doc_before_save() if method == "on_update" else None

        webhook_data = {
            "plant_id": doc.plant_id,
            "plant_name": doc.plant_name,
        }

        current_customers = {}
        old_customers = {}
        customers_data = []

        if doc.customers:
            for customer in doc.customers:
                if customer.mobile_no:
                    customer_data = {
                        "customer": customer.suntek_customer,
                        "customer_email": customer.email if customer.email else None,
                        "customer_mobile": customer.mobile_no,
                    }
                    current_customers[customer.mobile_no] = customer_data
                    customers_data.append(customer_data)

        if old_doc and old_doc.customers:
            for customer in old_doc.customers:
                if customer.mobile_no:
                    old_customers[customer.mobile_no] = {
                        "customer": customer.suntek_customer,
                        "customer_email": customer.email if customer.email else None,
                        "customer_mobile": customer.mobile_no,
                    }

        added_mobiles = set(current_customers.keys()) - set(old_customers.keys())
        removed_mobiles = set(old_customers.keys()) - set(current_customers.keys())

        if added_mobiles:
            webhook_data.update(
                {
                    "action": "customer_assigned",
                    "customers": customers_data,
                    "added_customers": [
                        current_customers[mobile] for mobile in added_mobiles
                    ],
                }
            )
        elif removed_mobiles:
            webhook_data.update(
                {
                    "action": "customer_removed",
                    "customers": customers_data,
                    "removed_customers": [
                        old_customers[mobile] for mobile in removed_mobiles
                    ],
                }
            )
        else:
            return

        success = send_webhook(webhook_data)
        if not success:
            frappe.log_error(
                message=f"Failed to send webhook for plant {doc.plant_id}",
                title="Webhook Error",
            )

    except Exception as e:
        frappe.log_error(
            message=f"Error in webhook handler for plant {doc.plant_id}: {str(e)}",
            title="Webhook Handler Error",
        )


def send_webhook(data: Dict) -> bool:
    max_retries = 3
    retry_delay = 1

    for attempt in range(max_retries):
        if attempt > 0:
            time.sleep(retry_delay * attempt)

        try:
            settings = frappe.get_doc("Suntek Settings")
            django_api_url = (
                f"{settings.get('django_api_url')}/power-plant/webhook/assign-plants/"
            )
            api_token = settings.get_password("solar_ambassador_api_token")

            if not django_api_url or not api_token:
                frappe.log_error(
                    "Django webhook URL or API token not configured in Suntek Settings"
                )
                return False

            headers = {
                "X-Django-Server-Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                django_api_url, json=data, headers=headers, timeout=10
            )

            if response.status_code == 200:
                return True

            if attempt == max_retries - 1:
                frappe.log_error(
                    message=f"Django server webhook failed: Status {response.status_code} - {response.text}",
                    title="Webhook Error",
                )

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                frappe.log_error(
                    message=f"Network error sending webhook: {str(e)}",
                    title="Webhook Network Error",
                )
        except Exception as e:
            frappe.log_error(
                message=f"Unexpected error sending webhook: {str(e)}",
                title="Webhook Error",
            )
            return False

    return False


@frappe.whitelist(allow_guest=True)
def create_power_plant(plant_id, plant_name=None, oem=None):
    """Create power plant and send webhook to Django server"""
    if frappe.db.exists("Solar Power Plants", {"plant_id": plant_id}):
        frappe.throw(f"A Solar Power Plant with ID {plant_id} already exists.")

    try:
        frappe.set_user("developer@suntek.co.in")

        plant = frappe.new_doc("Solar Power Plants")
        plant.plant_id = plant_id
        plant.plant_name = plant_name
        plant.oem = oem
        plant.insert()

        return plant

    except Exception as e:
        frappe.log_error(
            message=f"Error creating plant {plant_id}: {str(e)}",
            title="Power Plant Creation Error",
        )
        frappe.throw(f"Error creating power plant: {str(e)}")


@frappe.whitelist(allow_guest=True)
def create_power_plant_from_api():
    """Create a new Solar Power Plant from API request

    Returns:
        Response: API response with appropriate status code and message
    """
    try:
        auth_token = frappe.request.headers.get("X-Django-Server-Authorization")
        if not auth_token:
            return create_api_response(401, "error", "Unauthorized")

        auth_token = auth_token.split("Bearer ")[1]

        settings = frappe.get_doc("Suntek Settings")
        api_token = settings.get_password("solar_ambassador_api_token")

        if auth_token != api_token:
            return create_api_response(401, "error", "Unauthorized")

        if frappe.request.method != "POST":
            return create_api_response(405, "error", "Method not allowed")

        data = parse_request_data(frappe.request.data)

        plant_id = data.get("plant_id")
        if not plant_id:
            return create_api_response(400, "error", "Plant ID is required")

        if frappe.db.exists("Solar Power Plants", {"plant_id": plant_id}):
            return create_api_response(
                409, "error", f"Plant with ID {plant_id} already exists"
            )

        frappe.set_user("developer@suntek.co.in")
        plant = frappe.get_doc(
            {
                "doctype": "Solar Power Plants",
                "plant_id": plant_id,
                "plant_name": data.get("plant_name"),
                "oem": data.get("oem"),
            }
        ).insert(ignore_permissions=True)

        frappe.db.commit()

        return create_api_response(
            201,
            "success",
            "Power plant created successfully",
            data={
                "plant_id": plant.plant_id,
                "plant_name": plant.plant_name,
                "oem": plant.oem,
            },
        )

    except frappe.PermissionError:
        return create_api_response(403, "error", "Permission denied")
    except frappe.ValidationError as e:
        return create_api_response(400, "error", str(e))
    except Exception as e:
        frappe.log_error(
            message=f"Error creating power plant: {str(e)}",
            title="Power Plant Creation Error",
        )
        return create_api_response(500, "error", "Internal server error")
