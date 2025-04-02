import re

import frappe
from frappe.model.document import Document


class SolarPowerPlants(Document):
    def before_save(self):
        self.check_customer_mobile_number()
        self.change_power_plant_assigned_status()

    def change_power_plant_assigned_status(self):
        self.status = "Assigned" if self.check_customer_details() else "Unassigned"

    def check_customer_details(self):
        return bool(self.customers and len(self.customers) > 0)

    def validate_mobile_number(self, number):
        MOBILE_NUMBER_PATTERN = re.compile(r"^(\+91[-]?)?[6-9]\d{9}$")
        return bool(MOBILE_NUMBER_PATTERN.match(str(number)))

    def check_customer_mobile_number(self):
        if self.customers:
            for customer in self.customers:
                if not customer.mobile_no:
                    frappe.throw("Customer mobile number is mandatory for all customers in the table.")
                if not self.validate_mobile_number(customer.mobile_no):
                    frappe.throw(
                        f"Invalid mobile number '{customer.mobile_no}' for customer "
                        f"{customer.suntek_customer}! Please enter a 10-digit number "
                        "starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-."
                    )
