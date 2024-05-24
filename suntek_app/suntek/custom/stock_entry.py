import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def get_address_display(party):
    if party:
        from erpnext.accounts.party import get_party_details
        address_display = get_party_details(party)

        return address_display

def on_submit(doc,method):
	if doc.stock_entry_type=='Material Transfer to Customer':
		for d in doc.items:
			if d.against_designing_item and d.against_designing:
				if frappe.db.exists("Designing Item", d.against_designing_item):
					desgn=frappe.get_doc("Designing Item",d.against_designing_item)
					desgn.db_set("transferred",desgn.transferred+d.qty)


def on_cancel(doc,method):
	if doc.stock_entry_type=='Material Transfer to Customer':
		for d in doc.items:
			if d.against_designing_item and d.against_designing:
				if frappe.db.exists("Designing Item", d.against_designing_item):
					desgn=frappe.get_doc("Designing Item",d.against_designing_item)
					desgn.db_set("transferred",desgn.transferred-d.qty)
