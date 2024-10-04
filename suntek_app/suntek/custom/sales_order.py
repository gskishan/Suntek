import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_project


@frappe.whitelist()
def validate(self,method):
	for d in self.items:
		d.bom_no=None


@frappe.whitelist()
def auto_project_creation_on_submit(doc,method):
	if not doc.amended_from:
		if not doc.project:
			project_make = make_project(doc)
			project_make.custom_poc_person_name=doc.custom_person_name
			project_make.custom_poc_mobile_no=doc.custom_another_mobile_no
			project_make.save()
		create_subsidy(project_make)
	else:
		if doc.project:
			poj=frappe.get_doc("Project",doc.project)
			poj.db_set("sales_order",doc.name)
	update_opportunity(doc)

def create_subsidy(project_make):
	doc=project_make
	if doc.custom_type_of_case == "Subsidy":
				discomDoc = frappe.new_doc('Discom')
				discomDoc.project_name = doc.name
				discomDoc.sales_order = doc.sales_order
				discomDoc.customer_name =doc.customer
				discomDoc.save()


            
                      
				subsidyDoc = frappe.new_doc('Subsidy')
				subsidyDoc.project_name = doc.name
				subsidyDoc.sales_order = doc.sales_order
				subsidyDoc.customer_name = doc.customer
				subsidyDoc.save()
                       
	elif doc.custom_type_of_case == "Non Subsidy":
				discomDoc = frappe.new_doc('Discom')
				discomDoc.project_name = doc.name
				discomDoc.sales_order = doc.sales_order
				discomDoc.customer_name =doc.customer
				discomDoc.save()
            
        
    
            


def update_opportunity(doc):
    if doc.items[0].quotation_item:
        qi=frappe.get_doc("Quotation Item",doc.items[0].quotation_item)
        if qi.prevdoc_docname and qi.prevdoc_doctype=="Opportunity":
            op=frappe.get_doc(qi.prevdoc_doctype, qi.prevdoc_docname)
            op.db_set("opportunity_amount",doc.rounded_total, update_modified=False)
            
            
