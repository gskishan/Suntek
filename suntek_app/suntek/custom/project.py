

import frappe
from frappe import _

@frappe.whitelist()
def on_update(doc,method):
	if doc.custom_type_of_case == "Subsidy":
		if not doc.custom_discom_id:
			
			discomDoc = frappe.new_doc('Discom');
			discomDoc.project_name = doc.name
			discomDoc.sales_order = doc.sales_order
			discomDoc.customer_name =doc.customer
			discomDoc.save()


            
                      
		if not doc.custom_subsidy_id:
			subsidyDoc = frappe.new_doc('Subsidy')
			subsidyDoc.project_name = doc.name
			subsidyDoc.sales_order = doc.sales_order
			subsidyDoc.customer_name = doc.customer
			subsidyDoc.save()
                       
	elif doc.custom_type_of_case == "Non Subsidy":
		if not doc.custom_discom_id:

			discomDoc = frappe.new_doc('Discom')
			discomDoc.project_name = doc.name
			discomDoc.sales_order = doc.sales_order
			discomDoc.customer_name =doc.customer
			discomDoc.save()
            
        
    
            
