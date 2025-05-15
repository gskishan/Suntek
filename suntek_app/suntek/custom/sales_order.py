import frappe


def create_project_discom_subsidy_before_submit(doc, method):
    if frappe.db.exists("Project", {"project_name": doc.name}):
        _delete_documents_linked_to_sales_order(doc)

    new_project = make_project(doc)
    new_project.custom_poc_person_name = doc.custom_person_name
    new_project.custom_poc_mobile_no = doc.custom_another_mobile_no

    if doc.custom_project_template:
        new_project.project_template = doc.custom_project_template

    new_project.save()

    if doc.custom_type_of_case == "Subsidy":
        create_subsidy(new_project)
        create_discom(new_project)
    elif doc.custom_type_of_case == "Discom":
        create_discom(new_project)

    doc.project = new_project.name

    frappe.db.set_value("Sales Order", doc.name, "project", new_project.name, update_modified=False)

    update_opportunity(doc)


@frappe.whitelist()
def auto_project_creation_on_submit(doc, method):  # Deprecated
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
        _delete_documents_linked_to_sales_order(doc)


def _delete_documents_linked_to_sales_order(doc):
    projects = frappe.get_all("Project", filters={"sales_order": doc.name}, fields=["name"])

    for project in projects:
        subsidies = frappe.get_all("Subsidy", filters={"project_name": project.name}, fields=["name"])
        discoms = frappe.get_all("Discom", filters={"project_name": project.name}, fields=["name"])

        for subsidy in subsidies:
            frappe.delete_doc("Subsidy", subsidy.name, force=1)
        for discom in discoms:
            frappe.delete_doc("Discom", discom.name, force=1)
        doc.db_set("project", None)


def create_discom(project):
    """Creates Discom record based on the project's custom type of case."""

    discom = frappe.new_doc("Discom")
    discom.project_name = project.name
    discom.sales_order = project.sales_order
    discom.customer_name = project.customer
    discom.state = project.custom_state if project.custom_state else None
    discom.branch = project.custom_branch if project.custom_branch else None
    discom.save()


def create_subsidy(project):
    """Creates Subsidy record based on the project's custom type of case."""

    subsidy = frappe.new_doc("Subsidy")
    subsidy.project_name = project.name
    subsidy.sales_order = project.sales_order
    subsidy.customer_name = project.customer
    subsidy.state = project.custom_state if project.custom_state else None
    subsidy.branch = project.custom_branch if project.custom_branch else None
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
        ignore_permissions=True,
    )

    return doc


def get_location_data(doc, method):
    pass


def fetch_attachments_from_opportunity(doc, method):
    if doc.custom_opportunity_name != "":
        opportunity = frappe.get_doc("Opportunity", {"name": doc.custom_opportunity_name})

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


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    from erpnext.selling.doctype.sales_order.sales_order import (
        make_sales_invoice as _make_sales_invoice,
    )

    si = _make_sales_invoice(source_name, target_doc)

    return si


def share_sales_order_with_sales_person(doc, method):
    """Share the sales order to the sales person after it is created."""

    if doc.sales_person:
        sales_person = frappe.get_doc("Sales Person", {"sales_person_name": doc.sales_person})

        if sales_person:
            sales_person_employee = frappe.get_doc("Employee", {"name": sales_person.employee})

            if sales_person_employee:
                if not frappe.db.exists(
                    "DocShare",
                    {
                        "share_doctype": doc.doctype,
                        "share_name": doc.name,
                        "user": sales_person_employee.user_id,
                    },
                ):
                    shared_doc = frappe.new_doc("DocShare")
                    shared_doc.share_doctype = doc.doctype
                    shared_doc.share_name = doc.name
                    shared_doc.user = sales_person_employee.get("user_id")
                    shared_doc.read = 1
                    shared_doc.write = 1
                    shared_doc.share = 1
                    shared_doc.notify_by_email = 1

                    shared_doc.insert()


def set_project_template(doc, method):
    if doc.docstatus == 0:
        type_of_case = doc.custom_type_of_case
        department = doc.custom_department
        order_type = doc.order_type

        if order_type == "Sales":
            if department == "Domestic (Residential) Sales Team - SESP":
                doc.custom_project_template = "Boilerplate Project Template"
