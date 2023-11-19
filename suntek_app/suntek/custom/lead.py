import frappe

def change_enquiry_status(doc,method):
    
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status
