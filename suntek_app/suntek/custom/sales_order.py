import frappe


@frappe.whitelist()
def auto_project_creation_on_submit(doc, method):
    if doc.docstatus == 1 and not doc.amended_from:
        project_make = None
        if not frappe.db.exists("Project", {"project_name": doc.name}):
            project_make = make_project(doc)
            project_make.custom_poc_person_name = doc.custom_person_name
            project_make.custom_poc_mobile_no = doc.custom_another_mobile_no
            project_make.save()

            if doc.custom_type_of_case == "Subsidy":
                create_subsidy(project_make)
                create_discom(project_make)
            elif doc.custom_type_of_case == "Non Subsidy":
                create_discom(project_make)

    elif doc.amended_from and doc.project:
        project = frappe.get_doc("Project", doc.project)
        project.db_set("sales_order", doc.name)

    update_opportunity(doc)


@frappe.whitelist()
def delete_linked_documents_on_cancel(doc, method):
    """Delete linked documents when a sales order is cancelled."""
    if doc.docstatus == 2:
        projects = frappe.get_all("Project", filters={"sales_order": doc.name}, fields=["name"])

        for project in projects:
            subsidies = frappe.get_all("Subsidy", filters={"project_name": project.name}, fields=["name"])
            for subsidy in subsidies:
                frappe.delete_doc("Subsidy", subsidy.name, force=1)

            discoms = frappe.get_all("Discom", filters={"project_name": project.name}, fields=["name"])
            for discom in discoms:
                frappe.delete_doc("Discom", discom.name, force=1)

            frappe.delete_doc("Project", project.name, force=1)


def create_discom(project):
    """Creates Discom record based on the project's custom type of case."""

    discom = frappe.new_doc("Discom")
    discom.project_name = project.name
    discom.sales_order = project.sales_order
    discom.customer_name = project.customer
    discom.save()


def create_subsidy(project):
    """Creates Subsidy record based on the project's custom type of case."""

    subsidy = frappe.new_doc("Subsidy")
    subsidy.project_name = project.name
    subsidy.sales_order = project.sales_order
    subsidy.customer_name = project.customer
    subsidy.save()


def update_opportunity(doc):
    """Update the opportunity amount if Sales Order is linked with a quotation item and opportunity."""
    first_item = doc.items[0] if doc.items else None
    if first_item and first_item.quotation_item:
        quotation_item = frappe.get_doc("Quotation Item", first_item.quotation_item)

        if quotation_item.prevdoc_docname and quotation_item.prevdoc_doctype == "Opportunity":
            opportunity = frappe.get_doc(quotation_item.prevdoc_doctype, quotation_item.prevdoc_docname)
            opportunity.db_set("opportunity_amount", doc.rounded_total, update_modified=False)


@frappe.whitelist()
def make_project(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def postprocess(source, doc):
        doc.project_type = "External"
        doc.project_name = source_name.name
        doc.sales_order = source_name.name
        doc.custom_capacity = source_name.custom_capacity

        doc.custom_type_of_case = source_name.custom_type_of_case

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Project",
                "validation": {"docstatus": ["in", [0, 1]]},
                "field_map": {
                    "name": "sales_order",
                    "base_grand_total": "estimated_costing",
                    "net_total": "total_sales_amount",
                },
            },
        },
        target_doc,
        postprocess,
    )

    return doc


def get_location_data(doc, method):
    pass


def fetch_attachments_from_opportunity(doc, method):
    if doc.custom_opportunity_name != "":
        print("doc.custom_opportunity_name: ", doc.custom_opportunity_name)
        opportunity = frappe.get_doc("Opportunity", {"name": doc.custom_opportunity_name})
        print(opportunity)
        opportunity_attachments = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Opportunity",
                "attached_to_name": opportunity.name,
            },
            fields=["file_name", "file_url"],
        )

        if opportunity_attachments:
            for attachment in opportunity_attachments:
                has_attachment = frappe.db.get_value(
                    "File",
                    {
                        "file_url": attachment.file_url,
                        "attached_to_doctype": "Sales Order",
                        "attached_to_name": doc.name,
                    },
                )

                if not has_attachment:
                    opportunity_attachment = frappe.get_doc(
                        {
                            "doctype": "File",
                            "file_name": attachment.file_name,
                            "file_url": attachment.file_url,
                            "attached_to_doctype": "Sales Order",
                            "attached_to_name": doc.name,
                        }
                    )

                    opportunity_attachment.insert()
                    opportunity_attachment.reload()
                    print("opportunity_attachment: ", opportunity_attachment)


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    from erpnext.selling.doctype.sales_order.sales_order import (
        make_sales_invoice as _make_sales_invoice,
    )

    si = _make_sales_invoice(source_name, target_doc)

    return si
