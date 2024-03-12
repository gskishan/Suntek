
import frappe
def validate(doc,method):
    leads = frappe.db.get_list('Lead',
    filters={
        'mobile_no': doc.mobile_no
    },
    fields=['name', 'mobile_no'],
    as_list=True
    )

    if leads:
        frappe.throw("Duplicate Mobile no {0}".format(doc.mobile_no))
