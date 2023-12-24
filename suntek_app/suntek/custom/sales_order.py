import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_project


@frappe.whitelist()
def auto_project_creation_on_submit(doc,method):
    project_make = make_project(doc)
    project_make.save()
