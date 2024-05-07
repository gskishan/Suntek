import frappe
from frappe import _
from frappe.utils import get_link_to_form


@frappe.whitelist()
def validate(doc, method):
    leads = frappe.db.get_list(
        'Lead',
        filters={
            'mobile_no': doc.mobile_no,
            'name': ('!=', doc.name)  
        },
        fields=['name', 'mobile_no']
    )
    
    if leads:
        lead = leads[0]
        frappe.throw(_("Duplicate Mobile no {0} {1}").format(
            doc.mobile_no,
            get_link_to_form("Lead", lead['name'])
        ))
