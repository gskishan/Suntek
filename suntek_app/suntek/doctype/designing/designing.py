# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class Designing(Document):
	def onload(self):
		if self.docstatus == 1:
			self.update_designing_status()

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
		
		self.designing_status = "Completed"


	def update_opportunity_status_section(self):
		if not self.opportunity_name:
			return

		opportunity_doc = frappe.get_doc("Opportunity",self.opportunity_name)

		opportunity_doc.custom_designing_number = self.name
		opportunity_doc.custom_bom = self.bom
		opportunity_doc.custom_designing_status = self.designing_status
		opportunity_doc.save()
