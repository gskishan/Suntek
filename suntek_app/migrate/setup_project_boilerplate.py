import frappe


def create_project_type():
    if not frappe.db.exists("Project Type", {"project_type": "Boilerplate Project Type"}):
        try:
            project_type = frappe.new_doc("Project Type")
            project_type.project_type = "Boilerplate Project Type"
            project_type.insert()
            print(f"Created Project Type: {project_type.name}")
            return project_type.name
        except Exception as e:
            frappe.log_error(
                title="Error setting up Project boilerplate",
                message=str(e),
                reference_doctype="Project Type",
            )
    else:
        return frappe.db.get_value("Project Type", {"project_type": "Boilerplate Project Type"}, "name")


def create_task_type():
    task_types = []

    for i in range(1, 4):
        type_name = f"Boilerplate Task Type {i}"
        if not frappe.db.exists("Task Type", {"name": type_name}):
            try:
                task_type = frappe.new_doc("Task Type")
                task_type.name = type_name
                task_type.weight = i * 10
                task_type.insert()
                print(f"Created Task Type: {task_type.name}")
                task_types.append(task_type.name)
            except Exception as e:
                frappe.log_error(
                    title=f"Error setting up Task Type {i}",
                    message=str(e),
                    reference_doctype="Task Type",
                )
        else:
            task_types.append(type_name)

    return task_types


def create_tasks():
    task_types = create_task_type()
    tasks = []

    for i in range(1, 4):
        task_subject = f"Boilerplate Task {i}"
        task_exists = frappe.db.exists("Task", {"subject": task_subject})

        if not task_exists:
            try:
                task = frappe.new_doc("Task")
                task.subject = task_subject
                task.is_template = 1
                task.status = "Template"
                task.duration = i * 3
                task.expected_time = i * 3 * 8
                task.type = task_types[i - 1]
                task.insert()
                print(f"Created Task: {task.name}")
                tasks.append(task.name)
            except Exception as e:
                frappe.log_error(
                    title=f"Error setting up Task {i}",
                    message=str(e),
                    reference_doctype="Task",
                )
        else:
            tasks.append(frappe.db.get_value("Task", {"subject": task_subject}, "name"))

    return tasks


def add_dependent_tasks():
    tasks = []

    for i in range(1, 4):
        task_subject = f"Boilerplate Task {i}"
        task_id = frappe.db.get_value("Task", {"subject": task_subject}, "name")
        if task_id:
            tasks.append(task_id)

    if len(tasks) >= 3:
        try:
            task3 = frappe.get_doc("Task", tasks[2])

            existing_deps = [d.task for d in task3.depends_on]

            if tasks[0] not in existing_deps:
                task3.append("depends_on", {"task": tasks[0]})

            if tasks[1] not in existing_deps:
                task3.append("depends_on", {"task": tasks[1]})

            task3.save()
            print(f"Added dependencies to task: {task3.name}")

        except Exception as e:
            frappe.log_error(
                title="Error setting up task dependencies",
                message=str(e),
                reference_doctype="Task",
            )


def create_project_template():
    project_type = create_project_type()
    template_name = "Boilerplate Project Template"

    tasks = []
    for i in range(1, 4):
        task_subject = f"Boilerplate Task {i}"
        task_id = frappe.db.get_value("Task", {"subject": task_subject}, "name")
        if task_id:
            task_doc = frappe.get_doc("Task", task_id)
            tasks.append(
                {
                    "task": task_id,
                    "subject": task_doc.subject,
                }
            )

    if not frappe.db.exists("Project Template", template_name):
        try:
            template = frappe.new_doc("Project Template")
            template.name = template_name
            template.project_type = project_type

            for task_data in tasks:
                template.append("tasks", task_data)

            template.insert()
            print(f"Created Project Template: {template.name}")
            return template.name
        except Exception as e:
            frappe.log_error(
                title="Error setting up Project Template",
                message=str(e),
                reference_doctype="Project Template",
            )
            print(f"Error creating Project Template: {str(e)}")
    else:
        return template_name


def setup_boilerplate():
    """Main function to set up the entire project boilerplate"""
    create_project_type()
    create_task_type()
    tasks = create_tasks()
    add_dependent_tasks()
    create_project_template()

    print("Project boilerplate setup complete!")
