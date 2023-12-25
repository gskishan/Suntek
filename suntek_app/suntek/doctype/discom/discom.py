# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class Discom(Document):
	def after_insert(self):
		self.update_project_on_save()

	def after_save(self):
		self.update_project_on_save()

	def on_submit(self):
		self.update_project_on_submit()

	def update_project_on_save(self):
		if self.project_name:
			project = frappe.get_doc("Project", self.project_name)
			project.custom_discom_id = self.name
			project.custom_discom_status = "Draft"
			project.save()

	def update_project_on_submit(self):

		if self.project_name:
			project = frappe.get_doc("Project", self.project_name)
			project.custom_discom_id = self.name
			project.custom_discom_status = "Submitted"
			project.save()