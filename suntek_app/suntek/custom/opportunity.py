import frappe

def change_opportunity_status(doc,method):
    pass
    

def set_opportunity_name(doc,method):

    if doc.name:
        doc.custom_opportunity_name = doc.name
