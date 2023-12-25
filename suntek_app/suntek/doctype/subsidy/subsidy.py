# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Subsidy(Document):
	def after_insert(self):
		self.update_project_on_save()

	def after_save(self):
		self.update_project_on_save()

	def on_submit(self):
		self.update_project_on_submit()

	def update_project_on_save(self):
		# Check if the Discom document is linked to a Project
		if self.project_name:
			project = frappe.get_doc("Project", self.project_name)
			project.custom_subsidy_id = self.name
			project.custom_subsidy_status = "Draft"
			project.save()

	def update_project_on_submit(self):
		# Similar to update_project_on_save, check if the Discom document is linked to a Project
		if self.project_name:
			project = frappe.get_doc("Project", self.project_name)
			project.custom_subsidy_id = self.name
			project.custom_subsidy_status = "Submitted"
			project.save()