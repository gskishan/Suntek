import frappe

def change_enquiry_status(doc,method):
    
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status
    duplicate_check(doc)

def set_enquiry_name(doc,method):

    if doc.name:
        doc.custom_enquiry_name = doc.name
        
def duplicate_check(doc):
    leads = frappe.db.get_list('Lead',
    filters={
        'mobile_no': doc.mobile_no
    },
    fields=['name', 'mobile_no'],
    as_list=True
    )

    if leads:
        frappe.throw("Duplicate Mobile no {0}".format(doc.mobile_no))
