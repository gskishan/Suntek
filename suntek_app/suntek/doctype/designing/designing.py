# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class Designing(Document):
	def validate(self):
		self.update_designing_on_save()
	
	def after_insert(self):
		self.update_designing_on_save()
		self.update_opportunity_status_section()

	def on_submit(self):
		self.update_designing_status()
		self.update_opportunity_status_section()
		

	def update_designing_on_save(self):
		
		self.designing_status = "Open"
			
	def update_designing_status(self):
		
		self.db_set("designing_status","Completed")


	@frappe.whitelist()
	def update_old_status(self):
		sql="""select name from `tabDesigning` where docstatus=1 """
		for d in  frappe.db.sql(sql,as_dict=True):
			doc_d=frappe.get_doc("Designing",d.name)
			doc_d.db_set("designing_status","Completed")


	def update_opportunity_status_section(self):
		if not self.opportunity_name:
			return

		opportunity_doc = frappe.get_doc("Opportunity",self.opportunity_name)

		opportunity_doc.custom_designing_number = self.name
		opportunity_doc.custom_designing_status = self.designing_status
		opportunity_doc.save()


@frappe.whitelist()
def get_items(source_name, target_doc=None):
	def set_missing_values(source, target):
		preperation_order_note = frappe.get_doc(target)
	doclist = get_mapped_doc("Designing", source_name, {
		"Designing": {
			"doctype": "Delivery Note",
			"field_map": {
				"customer": "customer",
				"sub_customer": "sub_customer",
				"required_date": "required_date",
                "requested_date": "requested_date",
				"warehouse": "warehouse",
                "address_html": "customer_primary_address",
                "address_and_contact_details": "address_and_contact_details"
			}
		},
		"Item Grid":{
			"doctype": "Preparation Item Grid",
			"field_map": {
				"item_code": "item_code",
                "item_name": "item_name",
				"item_description": "item_description",
				"required_date": "required_date",
				"qty_required": "qty_required",
                "uom": "uom"
			}
		}
	}, target_doc, set_missing_values)
	return doclist
