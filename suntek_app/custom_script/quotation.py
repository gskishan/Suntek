import frappe
from erpnext.selling.doctype.quotation.quotation import Quotation
from erpnext.selling.doctype.quotation.quotation import *
class CustomQuotation (Quotation):
	def validate(self):
		super(Quotation, self).validate()
		self.set_status()
		self.validate_uom_is_integer("stock_uom", "stock_qty")
		self.validate_uom_is_integer("uom", "qty")
		self.validate_valid_till()
		self.set_custom_customer_name()
		if self.items:
			self.with_items = 1

		from erpnext.stock.doctype.packed_item.packed_item import make_packing_list

		make_packing_list(self)
        
	def set_custom_customer_name(self):
		if self.party_name and self.quotation_to == "Customer":
			self.customer_name = frappe.db.get_value("Customer", self.party_name, "customer_name")
		elif self.party_name and self.quotation_to == "Lead":
			lead_name, company_name = frappe.db.get_value(
				"Lead", self.party_name, ["lead_name", "company_name"]
			)
			pass


    


@frappe.whitelist()
def validate(self,method):
    pass
    #for d in self.items:
        #d.custom_total_gst_rate=d.igst_rate+d.cgst_rate+d.sgst_rate
        #d.custom_total_gst_amount=d.igst_amount+d.cgst_amount+d.sgst_amount


@frappe.whitelist()
def get_grandtotal(quotation=None):
    if quotation:
        qt=frappe.get_doc("Quotation",quotation)
        gt_grand=qt.grand_total
        return gt_grand
