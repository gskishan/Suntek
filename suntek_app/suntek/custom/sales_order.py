import frappe
from erpnext.selling.doctype.sales_order.sales_order import make_project

def on_update(doc):
    if doc.docstatus == 1 and not doc.amended_from:
    # Create Project from Sales Order
        if not frappe.db.exists("Project", {"project_name": doc.name}):
            project_make = make_project(doc)
            project_make.custom_poc_person_name = doc.custom_person_name
            project_make.custom_poc_mobile_no = doc.custom_another_mobile_no
            project_make.save()

        create_subsidy_or_discom(project_make)
    elif doc.amended_from and doc.project:
        project = frappe.get_doc("Project", doc.project)
        project.db_set("sales_order", doc.name)

@frappe.whitelist()
def auto_project_creation_on_submit(doc, method):
    # Ensure the document is submitted before creating a project
    # if doc.docstatus == 1 and not doc.amended_from:
    #     # Create Project from Sales Order
    #     if not frappe.db.exists("Project", {"project_name": doc.name}):

    #         project_make = make_project(doc)
    #         project_make.custom_poc_person_name = doc.custom_person_name
    #         project_make.custom_poc_mobile_no = doc.custom_another_mobile_no
    #         project_make.save()
        
    #     # Create subsidy or discom records if applicable
    #     create_subsidy_or_discom(project_make)
    # elif doc.amended_from and doc.project:
    #     # Update existing project if present
    #     project = frappe.get_doc("Project", doc.project)
    #     project.db_set("sales_order", doc.name)
    
    # Update opportunity linked with the Sales Order
    update_opportunity(doc)

def create_subsidy_or_discom(project):
    """Creates Discom and Subsidy records based on the project's custom type of case."""
    if project.custom_type_of_case == "Subsidy":
        # Create Discom record
        discom = frappe.new_doc('Discom')
        discom.project_name = project.name
        discom.sales_order = project.sales_order
        discom.customer_name = project.customer
        discom.save()
        
        # Create Subsidy record
        subsidy = frappe.new_doc('Subsidy')
        subsidy.project_name = project.name
        subsidy.sales_order = project.sales_order
        subsidy.customer_name = project.customer
        subsidy.save()

    elif project.custom_type_of_case == "Non Subsidy":
        # Create only Discom record
        discom = frappe.new_doc('Discom')
        discom.project_name = project.name
        discom.sales_order = project.sales_order
        discom.customer_name = project.customer
        discom.save()

def update_opportunity(doc):
    """Update the opportunity amount if Sales Order is linked with a quotation item and opportunity."""
    first_item = doc.items[0] if doc.items else None
    if first_item and first_item.quotation_item:
        quotation_item = frappe.get_doc("Quotation Item", first_item.quotation_item)
        
        # Check if the quotation item is linked to an opportunity
        if quotation_item.prevdoc_docname and quotation_item.prevdoc_doctype == "Opportunity":
            opportunity = frappe.get_doc(quotation_item.prevdoc_doctype, quotation_item.prevdoc_docname)
            opportunity.db_set("opportunity_amount", doc.rounded_total, update_modified=False)



