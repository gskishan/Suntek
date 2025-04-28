# Copyright (c) 2025, kishan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ItemPriceMatrix(Document):
    def validate(self):
        # Skip checkbox validation for new documents
        if not self.is_new():
            self.validate_checkboxes()

    @frappe.whitelist()
    def validate_checkboxes(self):
        # Don't validate for new documents
        if getattr(self, "is_new", lambda: False)():
            return

        if self.selling == 0 and self.buying == 0:
            frappe.throw("You must select at least one of the Selling or Buying checkboxes.")
        if self.selling == 1 and self.buying == 1:
            frappe.throw("You cannot select both Selling and Buying checkboxes at the same time.")

    @frappe.whitelist()
    def fetch_item_price_from_price_list(self):
        if not self.item:
            frappe.throw("Please select an Item first.")

        if self.is_new():
            # Set default selling for new documents if nothing is selected
            if not self.selling and not self.buying:
                self.selling = 1

        item_price = self._fetch_price_list_rate(self.item, self.buying, self.selling)
        self.item_price = item_price
        self.save()
        return item_price

    def _fetch_price_list_rate(self, item_code, buying=0, selling=0):
        if buying == 1:
            return frappe.get_doc("Item Price", {"item_code": item_code, "buying": 1}).price_list_rate
        elif selling == 1:
            return frappe.get_doc("Item Price", {"item_code": item_code, "selling": 1}).price_list_rate
        else:
            frappe.throw("Please select either Buying or Selling checkbox to fetch the price list rate.")
