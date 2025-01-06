import re
from typing import Dict, List

import frappe


def change_power_plant_assigned_status(doc, method):
    doc.status = "Assigned" if check_customer_details(doc) else "Unassigned"


def check_customer_details(doc):
    return bool(doc.customer and doc.customer_mobile_no)


def customer_contains_mobile_number(doc):
    return bool(doc.customer_mobile_no)


def validate_mobile_number(number):
    # Ensure number is a string before matching
    number = str(number)
    pattern = r"^(\+91[-]?)?[6-9]\d{9}$"
    if re.match(pattern, number):
        return True
    else:
        return False


def check_customer_mobile_number(doc, method=None):
    if doc.customer:
        if not customer_contains_mobile_number(doc):
            frappe.throw(
                "Customer mobile number is mandatory. Please update the customer's mobile number or select a customer with a valid mobile number.",
            )
        else:
            if not validate_mobile_number(doc.customer_mobile_no):
                frappe.throw(
                    "Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.",
                )


@frappe.whitelist()
def create_power_plant(plant_id, plant_name=None, oem=None):
    if frappe.db.exists("Solar Power Plants", {"plant_id": plant_id}):
        frappe.throw(f"A Solar Power Plant with ID {plant_id} already exists.")

    plant = frappe.new_doc("Solar Power Plants")
    plant.plant_id = plant_id
    plant.plant_name = plant_name
    plant.oem = oem
    plant.insert()
    return plant


@frappe.whitelist()
def create_power_plants(plants: List[Dict]):
    """
    Create multiple power plants and track existing ones

    Args:
        plants: List of dictionaries containing plant details
        {
            "plants": [
                {"plant_id": "123", "plant_name": "Plant A", "oem": "Growatt"},
                {"plant_id": "456", "plant_name": "Plant B", "oem": "Solis"}
            ]
        }

    Returns:
        Dict containing created and existing plants
    """
    response = {"created": [], "existing": []}

    for plant_data in plants:
        plant_id = plant_data.get("plant_id")

        if not plant_id:
            continue

        if frappe.db.exists("Solar Power Plants", {"plant_id": plant_id}):
            # Get existing plant details
            existing_plant = frappe.get_doc("Solar Power Plants", {"plant_id": plant_id})
            response["existing"].append({"plant_id": plant_id, "plant_name": existing_plant.plant_name, "oem": existing_plant.oem})
        else:
            try:
                # Create new plant
                plant = frappe.new_doc("Solar Power Plants")
                plant.plant_id = plant_id
                plant.plant_name = plant_data.get("plant_name")
                plant.oem = plant_data.get("oem")
                plant.insert()

                response["created"].append({"plant_id": plant_id, "plant_name": plant.plant_name, "oem": plant.oem})
            except Exception as e:
                frappe.log_error(f"Error creating plant {plant_id}: {str(e)}")
                continue

    return response
