import frappe


def create_task_types():
    task_types = ["Design", "Manufacture", "Dispatch", "Installation", "Liason", "Project Review"]
    for i in range(0, len(task_types)):
        if not frappe.db.exists("Task Type", task_types[i]):
            task = frappe.new_doc("Task Type")
            task.name = task_types[i]
            task.description = f"{task_types[i]} related tasks"
            task.insert()
    frappe.db.commit()


def create_project_types():
    project_types = [
        "Domestic Subsidy and Discom",
        "Domestic Discom Only",
        "Domestic No Subsidy No Discom",
    ]

    for i in range(0, len(project_types)):
        if not frappe.db.exists("Project Type", {"project_type": project_types[i]}):
            project_type = frappe.get_doc(
                frappe._dict(
                    {
                        "doctype": "Project Type",
                        "project_type": project_types[i],
                        "description": f"Project for {project_types[i]}",
                    }
                )
            )

            project_type.insert()
    frappe.db.commit()


def create_tasks():
    tasks_map = {
        "Design": "Design",
        "Manufacture": "Manufacture",
        "Dispatch": "Dispatch",
        "Installation": "Installation",
        "Feasibility Study": "",
        "WCR": "",
        "Project Review": "Project Review",
    }

    for task_name, task_type in tasks_map.items():
        if not frappe.db.exists("Task", {"subject": task_name, "status": "Template", "is_template": 1}):
            task = frappe.new_doc("Task")
            task.update({"subject": task_name, "status": "Template", "is_template": 1})

            if task_type:
                task.update({"task_type": task_type})

            task.insert()

    frappe.db.commit()


def create_task_dependencies():
    """
    Create dependencies only for specific tasks based on conditions.
    """

    dependency_mapping = {
        "Manufacture": ["Design"],
        "Dispatch": ["Manufacture"],
        "Installation": ["Dispatch"],
    }

    for dependent_task_name, depends_on_tasks in dependency_mapping.items():
        dependent_task = frappe.get_list(
            "Task", filters={"subject": dependent_task_name, "status": "Template", "is_template": 1}, fields=["name"]
        )

        if not dependent_task:
            print(f"Task '{dependent_task_name}' not found, skipping dependency setup")
            continue

        dependent_task_doc = frappe.get_doc("Task", dependent_task[0].name)

        existing_deps = (
            [d.task for d in dependent_task_doc.depends_on] if hasattr(dependent_task_doc, "depends_on") else []
        )

        for dependency_name in depends_on_tasks:
            dependency = frappe.get_list(
                "Task", filters={"subject": dependency_name, "status": "Template", "is_template": 1}, fields=["name"]
            )

            if not dependency:
                print(f"Dependency task '{dependency_name}' not found, skipping")
                continue

            dependency_task_name = dependency[0].name

            if dependency_task_name not in existing_deps:
                dependent_task_doc.append("depends_on", {"task": dependency_task_name})
                print(f"Added dependency: {dependent_task_name} -> {dependency_name}")

        dependent_task_doc.save()

    frappe.db.commit()
    print("Task dependencies created successfully for specific tasks")


def setup_suntek_project_automation():
    """Main function to set up the entire suntek project automation"""
    create_task_types()
    create_project_types()
    create_tasks()
    create_task_dependencies()

    print("Suntek project automation setup complete!")
