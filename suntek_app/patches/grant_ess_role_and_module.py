import frappe


def execute():
    module_name = "Employee Self Service"
    role_name = "Employee Self Service"

    log_message = f"Starting to add '{module_name}' module and '{role_name}' role to eligible users"
    print(log_message)
    frappe.log_error(log_message, "Employee Self Service Access Update")

    if not frappe.db.exists("Role", role_name):
        error_message = f"Role '{role_name}' does not exist in the system. Patch cannot continue."
        print(error_message)
        frappe.log_error(error_message, "Employee Self Service Access Update Error")
        return {"status": "error", "message": error_message}

    module_updated_count = 0
    role_updated_count = 0
    skipped_count = 0

    users = frappe.get_all(
        "User", filters={"enabled": 1, "user_type": "System User"}, fields=["name", "email", "full_name"]
    )

    for user in users:
        try:
            is_employee = frappe.db.exists("Employee", {"user_id": user.name, "status": "Active"})

            if not is_employee:
                skipped_count += 1
                continue

            user_doc = frappe.get_doc("User", user.name)
            changes_made = False

            blocked_modules = frappe.get_all(
                "Block Module", filters={"parent": user.name, "module": module_name}, fields=["name"]
            )

            if blocked_modules:
                for blocked in blocked_modules:
                    frappe.db.delete("Block Module", blocked.name)
                changes_made = True
                module_updated_count += 1
                print(f"Unblocked '{module_name}' module for user: {user.name}")

            has_role = False
            for role in user_doc.roles:
                if role.role == role_name:
                    has_role = True
                    break

            if not has_role:
                user_doc.append("roles", {"role": role_name})
                user_doc.save()
                changes_made = True
                role_updated_count += 1
                print(f"Added '{role_name}' role to user: {user.name}")

            if changes_made:
                frappe.db.commit()

        except Exception as e:
            frappe.db.rollback()
            error_message = f"Failed to update access for user {user.name}: {str(e)}"
            print(error_message)
            frappe.log_error(error_message, "Employee Self Service Access Update Error")

    completion_message = f"""
    Employee Self Service Access Update Complete:
    - Total users processed: {len(users)}
    - Skipped (not employees): {skipped_count}
    - Module unblocked for: {module_updated_count} users
    - Role added to: {role_updated_count} users
    """

    print(completion_message)
    frappe.log_error(completion_message, "Employee Self Service Access Update Complete")

    return {
        "total_users": len(users),
        "skipped_users": skipped_count,
        "module_updates": module_updated_count,
        "role_updates": role_updated_count,
    }
