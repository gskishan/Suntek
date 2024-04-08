import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_project


@frappe.whitelist()
def auto_project_creation_on_submit(doc,method):
    project_make = make_project(doc)
    project.custom_poc_person_name=doc.custom_poc_person_name
    project_make.custom_poc_mobile_no=doc.custom_poc_mobile_no
    project_make.save()
    update_opportunity(doc)

def update_opportunity(doc):
    if doc.items[0].quotation_item:
        qi=frappe.get_doc("Quotation Item",doc.items[0].quotation_item)
        if qi.prevdoc_docname and qi.prevdoc_doctype=="Opportunity":
            op=frappe.get_doc(qi.prevdoc_doctype, qi.prevdoc_docname)
            op.db_set("opportunity_amount",doc.rounded_total)
            
            
