import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_project


@frappe.whitelist()
def validate(self,method):
	for d in self.items:
		d.bom_no=None


@frappe.whitelist()
def auto_project_creation_on_submit(doc,method):
	if not doc.amended_from:
		
		project_make = make_project(doc)
		project_make.custom_poc_person_name=doc.custom_person_name
		project_make.custom_poc_mobile_no=doc.custom_another_mobile_no
		project_make.save()
		create_subsidy(project_make)
	else:
		if doc.project:
			poj=frappe.get_doc("Project",doc.project)
			poj.db_set("sales_order",doc.name)
	update_opportunity(doc)
