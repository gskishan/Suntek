import re

import frappe
from frappe.model.document import Document


class SolarPanelPricingRule(Document):
    def validate(self):
        self.validate_height()
        self.validate_capacity()

        if self.is_new():
            if not self.price_list:
                self.price_list = self.get_price_list()

    def validate_height(self):
        if not self.min_height:
            frappe.throw("Minimum Height is required")
        if not self.max_height:
            frappe.throw("Maximum Height is required")
        if self.min_height == 0.00:
            frappe.throw("Minimum Height cannot be zero")
        if self.max_height == 0.00:
            frappe.throw("Maximum Height cannot be zero")
        if self.min_height > self.max_height:
            frappe.throw("Minumum height cannot be greater than maximum height")
        if self.min_height == self.max_height:
            frappe.throw("Minimum and maximum height cannot be the same")

    def validate_capacity(self):
        if not self.min_capacity:
            frappe.throw("Minimum capacity is required")
        if not self.max_capacity:
            frappe.throw("Maximum capacity is required")
        if self.min_capacity == 0:
            frappe.throw("Minimum capacity cannot be zero")
        if self.max_capacity == 0:
            frappe.throw("Maximum capacity cannot be zero")
        if self.min_capacity > self.max_capacity:
            frappe.throw("Minumum capacity cannot be greater than maximum capacity")
        if self.min_capacity == self.max_capacity:
            frappe.throw("Minimum and maximum capacity cannot be the same")

    @frappe.whitelist()
    def get_price_list(self):
        return frappe.get_doc("Price List", {"selling": 1}).price_list_name

    @frappe.whitelist()
    def fetch_item_price_from_price_list(self):
        if not self.item:
            return

        item_price = self._fetch_price_list_rate(self.item)

        if self.is_new():
            self.base_price = item_price
            return item_price
        else:
            self.item_base_price = item_price
            self.save()
            return item_price

    def _fetch_price_list_rate(self, item):
        try:
            price_doc = frappe.get_doc("Item Price", {"item_code": item, "selling": 1})
            return price_doc.price_list_rate if price_doc else 0
        except Exception as e:
            frappe.log_error(f"Error fetching price list rate: {str(e)}")
            return 0


@frappe.whitelist()
def get_price_from_solar_panel_pricing_rule(item_code, capacity, height):
    try:
        if not item_code or not capacity or not height:
            return None

        height_value = extract_height(height)

        if not height_value:
            return None

        price_rules = frappe.get_list(
            "Solar Panel Pricing Rule",
            filters={
                "item": item_code,
                "min_capacity": ["<=", float(capacity)],
                "max_capacity": [">=", float(capacity)],
                "min_height": ["<=", float(height_value)],
                "max_height": [">=", float(height_value)],
                "disabled": 0,
            },
            fields=["name"],
        )

        if not price_rules or len(price_rules) == 0:
            return None

        price_rule = frappe.get_doc("Solar Panel Pricing Rule", price_rules[0].name)
        return price_rule.final_price
    except Exception as e:
        frappe.log_error(f"Error fetching price from solar panel config: {str(e)}")
        return None


def extract_height(height_str):
    match = re.match(r"([0-9]*\.?[0-9]+)", height_str)

    if match:
        return float(match.group(1))
