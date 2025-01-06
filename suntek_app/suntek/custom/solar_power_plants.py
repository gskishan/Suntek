import re

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
