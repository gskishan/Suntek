import frappe
from erpnext.selling.doctype.quotation.quotation import Quotation
from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

class CustomQuotation(Quotation):
    def validate(self):
        # Calling the base Quotation's validate method
        super(CustomQuotation, self).validate()

        # Custom validations and assignments
        self.set_status()
        self.validate_uom_is_integer("stock_uom", "stock_qty")
        self.validate_uom_is_integer("uom", "qty")
        self.validate_valid_till()

        # Only call validate_shopping_cart_items() if defined in Quotation
        if hasattr(self, 'validate_shopping_cart_items'):
            self.validate_shopping_cart_items()

        # Setting custom customer name if the quotation is to a customer or lead
        self.set_custom_customer_name()

        # Setting `with_items` if there are items in the quotation
        if self.items:
            self.with_items = 1

        # Generating a packing list based on items
        make_packing_list(self)

    def set_custom_customer_name(self):
        # Custom method to set customer name based on quotation_to
        if self.party_name:
            if self.quotation_to == "Customer":
                self.customer_name = frappe.db.get_value("Customer", self.party_name, "customer_name")
            elif self.quotation_to == "Lead":
                lead_name, company_name = frappe.db.get_value("Lead", self.party_name, ["lead_name", "company_name"])
                self.customer_name = company_name or lead_name

@frappe.whitelist()
def get_grandtotal(quotation=None):
    # Fetch and return grand total for a specified quotation
    if quotation:
        qt = frappe.get_doc("Quotation", quotation)
        return qt.grand_total
    return None
