import frappe
from frappe.model.mapper import get_mapped_doc
def on_submit(doc,method):
	for d in doc.items:
		if d.against_designing_item and d.against_designing:
			desgn=frappe.get_doc("Designing Item",d.against_designing_item)
			desgn.db_set("transferred",desgn.transferred+d.qty)


def on_cancel(doc,method):
	for d in doc.items:
		if d.against_designing_item and d.against_designing:
			desgn=frappe.get_doc("Designing Item",d.against_designing_item)
			desgn.db_set("transferred",desgn.transferred-d.qty)
