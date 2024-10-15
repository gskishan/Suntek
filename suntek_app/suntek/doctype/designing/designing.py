# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document
from frappe.model.mapper import get_mapped_doc
from frappe.utils import flt
from collections import Counter


class Designing(Document):
	def validate(self):
		self.get_duplicate_item()
		self.update_designing_on_save()
		if self.is_new() and not self.custom_capacity and self.custom_project:
			pro=frappe.get_doc("Project",self.custom_project)
			self.custom_capacity=pro.custom_capacity

	def get_duplicate_item(self):
		item_codes = [item.item_code for item in self.bom]
		duplicates = [item_code for item_code, count in Counter(item_codes).items() if count > 1]
		if duplicates:
			frappe.throw("Duplicate Items found: {}".format(", ".join(duplicates)))
	
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

	@frappe.whitelist()	
	def get_opportunity_details(self):
		if self.is_new() and self.custom_project:
			project_doc=frappe.get_doc("Project",self.custom_project)
			so= project_doc.sales_order
			opportunity= frappe.db.get_value('Sales Order', so, 'custom_opportunity_name')
			op=frappe.get_doc("Opportunity", opportunity)
			self.opportunity_name=op.name
			self.customer_name=project_doc.customer
			self.customer_number=project_doc.custom_customer_mobile
			self.opportunity_owner=op.opportunity_owner
			self.sales_person=op.custom_sales_excecutive
			self.poc_name=project_doc.custom_poc_person_name
			self.poc_contact=project_doc.custom_poc_mobile_no
			self.custom_capacity=project_doc.custom_capacity
			if op.customer_address:
				formattedAddress=frappe.get_doc("Address", op.customer_address)
				self.site_location = (
				    (formattedAddress.name or "") + '\n' +
				    (formattedAddress.address_line1 or "") + '\n' +
				    (formattedAddress.address_line2 or "") + '\n' +
				    (formattedAddress.city or "") + '\n' +
				    (formattedAddress.state or "") + '\n' +
				    (formattedAddress.pincode or "") + '\n' +
				    (formattedAddress.country or "")
				)




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
def make_bom(source_name, target_doc=None):
	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		source_doc = frappe.get_doc(source)
	doclist = get_mapped_doc("Designing", source_name, {
		"Designing": {
			"doctype": "BOM",
			"field_map": {
				"custom_project": "project",
			}
		},
		"Designing Item":{
			"doctype": "BOM Item",
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
	def update_item(obj, target, source_parent):
		qty=(
			flt(obj.qty) - flt(obj.transferred)
			if flt(obj.qty) > flt(obj.transferred)
			else 0
			)
		target.qty = qty
		target.against_designing_item=obj.name
		target.against_designing=obj.parent
		target.conversion_factor=1
		company= frappe.db.get_value('Project', source_parent.custom_project, 'company')
		warehouse= frappe.db.get_value('Company', company, 'custom_default_warehouse')
		target.s_warehouse=warehouse

	def set_missing_values(source, target):
		doc = frappe.get_doc(target)
		source_doc = frappe.get_doc(source)
		doc.against_designing=source_doc.name
		target.set_transfer_qty()
		target.set_actual_qty()
		target.calculate_rate_and_amount(raise_error_if_no_rate=False)
		#target.stock_entry_type = "Material Transfer to Customer"
		target.customer=source_doc.customer_name
		company= frappe.db.get_value('Project', source.custom_project, 'company')
		warehouse= frappe.db.get_value('Company',company, 'custom_default_warehouse')
		target.from_warehouse=warehouse

		

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
			},
			"postprocess": update_item,
			"condition":lambda doc: (
					flt(doc.transferred, doc.precision("transferred"))
					< flt(doc.qty, doc.precision("qty"))
				)

		}
	}, target_doc, set_missing_values)
	return doclist
