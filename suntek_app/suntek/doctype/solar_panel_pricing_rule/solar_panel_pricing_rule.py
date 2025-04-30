import frappe
from frappe.model.document import Document


class SolarPanelPricingRule(Document):
    def validate(self):
        if self.is_new():
            if not self.price_list:
                self.price_list = self.get_price_list()

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
def get_price_from_solar_panel_pricing_rule(item_code, kwp, height):
    try:
        if not item_code or not kwp or not height:
            return None

        price_rules = frappe.get_list(
            "Solar Panel Pricing Rule",
            filters={
                "item": item_code,
                "min_kwp": ["<=", float(kwp)],
                "max_kwp": [">=", float(kwp)],
                "height": height,
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
