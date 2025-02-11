import frappe
from frappe.utils import today


@frappe.whitelist()
def validate(doc, method):
    if not doc.is_new():
        custom_copy_from_template(doc)


def custom_copy_from_template(self):
    """
    Copy tasks from template
    """
    if self.custom_project_template and not frappe.db.get_all(
        "Task",
        dict(project=self.name),
        limit=1,
    ):
        if not self.expected_start_date:
            self.expected_start_date = today()

        template = frappe.get_doc("Project Template", self.custom_project_template)

        if not self.project_type:
            self.project_type = template.project_type

        project_tasks = []
        tmp_task_details = []
        for task in template.tasks:
            template_task_details = frappe.get_doc("Task", task.task)
            tmp_task_details.append(template_task_details)
            task = self.create_task_from_template(template_task_details)
            project_tasks.append(task)

        self.dependency_mapping(tmp_task_details, project_tasks)


@frappe.whitelist()
def on_update(doc, method):
    pass
    # existing_project = frappe.db.get_value('Project', {'sales_order': doc.name}, ['name'])
    # if existing_project:
    # 	frappe.errprint(f"Project {existing_project} already exists for this Sales Order. Linking existing project.")
    # 	doc.project = existing_project
    # else:
    # 	frappe.errprint(f"No existing project for Sales Order {doc.name}. Creating new project.")
    # if doc.custom_type_of_case == "Subsidy":
    # 	if not doc.custom_discom_id:
    # 		if not frappe.db.get_value('Discom', {'project_name': doc.name}, ['sales_order', 'name'])

    # 			discomDoc = frappe.new_doc('Discom');
    # 			discomDoc.project_name = doc.name
    # 			discomDoc.sales_order = doc.sales_order
    # 			discomDoc.customer_name =doc.customer
    # 			discomDoc.save()

    # 	if not doc.custom_subsidy_id:
    # 		if not frappe.db.get_value('Subsidy', {'project_name': doc.name}, ['sales_order', 'name'])
    # 			frappe.errprint([doc.is_new(),doc.docstatus])
    # 			subsidyDoc = frappe.new_doc('Subsidy')
    # 			subsidyDoc.project_name = doc.name
    # 			subsidyDoc.sales_order = doc.sales_order
    # 			subsidyDoc.customer_name = doc.customer
    # 			subsidyDoc.save()

    # elif doc.custom_type_of_case == "Non Subsidy":
    # 	if not doc.custom_discom_id:
    # 		if not frappe.db.get_value('Discom', {'project_name': doc.name}, ['sales_order', 'name'])
    # 			discomDoc = frappe.new_doc('Discom')
    # 			discomDoc.project_name = doc.name
    # 			discomDoc.sales_order = doc.sales_order
    # 			discomDoc.customer_name =doc.customer
    # 			discomDoc.save()


def fetch_attachments_from_sales_order(doc, method):
    if doc.sales_order != "":
        print("doc.sales_order: ", doc.sales_order)
        sales_order = frappe.get_doc("Sales Order", {"name": doc.sales_order})
        print(sales_order)
        sales_order_attachments = frappe.get_all(
            "File",
            filters={
                "attached_to_doctype": "Sales Order",
                "attached_to_name": sales_order.name,
            },
            fields=["file_name", "file_url"],
        )

        print("sales_order_attachments: ", sales_order_attachments)

        if sales_order_attachments:
            for attachment in sales_order_attachments:
                has_attachment = frappe.db.get_value(
                    "File",
                    {
                        "file_url": attachment.file_url,
                        "attached_to_doctype": "Project",
                        "attached_to_name": doc.name,
                    },
                )

                if not has_attachment:
                    sales_order_attachment = frappe.get_doc(
                        {
                            "doctype": "File",
                            "file_name": attachment.file_name,
                            "file_url": attachment.file_url,
                            "attached_to_doctype": "Project",
                            "attached_to_name": doc.name,
                        }
                    )

                    sales_order_attachment.insert()
                    sales_order_attachment.reload()
                    print("sales_order_attachment: ", sales_order_attachment)
