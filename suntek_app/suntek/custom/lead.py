import frappe

def change_enquiry_status(doc,method):
    
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status

def set_enquiry_name(doc,method):

    if doc.name:
        doc.custom_enquiry_name = doc.name
