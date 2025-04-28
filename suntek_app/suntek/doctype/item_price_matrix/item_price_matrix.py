import frappe
from frappe.model.document import Document

from suntek_app.utils.strings import extract_numeric_and_unit


class ItemPriceMatrix(Document):
    def validate(self):
        if not self.is_new():
            self.validate_checkboxes()

    @frappe.whitelist()
    def validate_checkboxes(self):
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
            if not self.selling and not self.buying:
                self.selling = 1

        item_price = self._fetch_price_list_rate(self.item, self.buying, self.selling)

        if self.is_new():
            self.item_base_price = item_price
            return item_price
        else:
            self.item_base_price = item_price
            self.save()
            return item_price

    def _fetch_price_list_rate(self, item_code, buying=0, selling=0):
        try:
            if selling == 1:
                price_doc = frappe.get_doc("Item Price", {"item_code": item_code, "selling": 1})
                return price_doc.price_list_rate if price_doc else 0
            elif buying == 1:
                price_doc = frappe.get_doc("Item Price", {"item_code": item_code, "buying": 1})
                return price_doc.price_list_rate if price_doc else 0
            else:
                frappe.throw("Please select either Buying or Selling checkbox to fetch the price list rate.")
        except Exception as e:
            frappe.log_error(f"Error fetching price list rate: {str(e)}")
            return 0


@frappe.whitelist()
def set_price_from_matrix(item_code, uom_1, uom_2):
    try:
        qty_1, uom_1_unit = extract_numeric_and_unit(uom_1)
        qty_2, uom_2_unit = extract_numeric_and_unit(uom_2)

        if uom_1_unit:
            uom_1_unit = uom_1_unit.lower()
        if uom_2_unit:
            uom_2_unit = uom_2_unit.lower()

        if not all([qty_1, uom_1_unit, qty_2, uom_2_unit]):
            return None

        matrices = frappe.db.sql(
            """
            SELECT
                name,
                min_uom_1,
                max_uom_1,
                min_uom_2,
                max_uom_2,
                final_item_price,
                uom_category_1,
                uom_category_2
            FROM `tabItem Price Matrix`
            WHERE
                item = %s
                AND status = 'Enabled'
        """,
            (item_code),
            as_dict=1,
        )

        for matrix in matrices:
            matrix_uom_1 = (matrix.uom_category_1 or "").lower()
            matrix_uom_2 = (matrix.uom_category_2 or "").lower()

            if matrix_uom_1 != uom_1_unit or matrix_uom_2 != uom_2_unit:
                continue

            min_1 = float(matrix.min_uom_1 or 0)
            max_1 = float(matrix.max_uom_1 or 999999)
            min_2 = float(matrix.min_uom_2 or 0)
            max_2 = float(matrix.max_2 or 999999)

            if min_1 <= qty_1 <= max_1 and min_2 <= qty_2 <= max_2:
                price = matrix.final_item_price

                return float(price)

        return None

    except Exception as e:
        frappe.log_error(f"Error in set_price_from_matrix: {str(e)}")
        return None
