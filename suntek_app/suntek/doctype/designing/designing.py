# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc

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
		doc = frappe.get_doc(target)
		source_doc = frappe.get_doc(source)
		doc.against_designing=source_doc.name
	doclist = get_mapped_doc("Designing", source_name, {
		"Designing": {
			"doctype": "Delivery Note",
			"field_map": {
				"customer_name": "customer",
				"custom_project": "project",
			}
		},
		"Designing Item":{
			"doctype": "Delivery Note Item",
			"field_map": {
				"item_code": "item_code",
                "item_name": "item_name",
				"item_description": "item_description",
				"qty": "qty",
				"rate": "rate",
                "uom": "uom"
			}
		}
	}, target_doc, set_missing_values)
	return doclist

@frappe.whitelist()
def make_material_request(source_name, target_doc=None):
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		source_doc = frappe.get_doc(source)
		doc.against_designing=source_doc.name
	doclist = get_mapped_doc("Designing", source_name, {
		"Designing": {
			"doctype": "Material Request",
			"field_map": {
				"customer_name": "customer",
				"custom_project": "project",
			}
		},
		"Designing Item":{
			"doctype": "Material Request Item",
			"field_map": {
				"item_code": "item_code",
                "item_name": "item_name",
				"item_description": "item_description",
				"qty": "qty",
				"rate": "rate",
                "uom": "uom"
			}
		}
	}, target_doc, set_missing_values)
	return doclist

@frappe.whitelist()
def make_stock_entry(source_name, target_doc=None):
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		source_doc = frappe.get_doc(source)
		doc.against_designing=source_doc.name
	doclist = get_mapped_doc("Designing", source_name, {
		"Designing": {
			"doctype": "Stock Entry",
			"field_map": {
				"customer_name": "customer",
				"custom_project": "project",
			}
		},
		"Designing Item":{
			"doctype": "Stock Entry Detail",
			"field_map": {
				"item_code": "item_code",
                "item_name": "item_name",
				"item_description": "item_description",
				"qty": "qty",
				"rate": "rate",
                "uom": "uom"
			}
		}
	}, target_doc, set_missing_values)
	return doclist
