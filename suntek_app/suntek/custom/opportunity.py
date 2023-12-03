import frappe

def change_opportunity_status(doc,method):
    
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status

def set_opportunity_name(doc,method):

    if doc.name:
        doc.custom_opportunity_name = doc.name
