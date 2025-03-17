import frappe


def execute():
    """
    Create the 'Refer & Earn' module if it doesn't exist,
    then change the Ambassador doctype's module to 'Refer & Earn'
    """
    # Create "Refer & Earn" module if it doesn't exist
    if not frappe.db.exists("Module Def", "Refer & Earn"):
        module = frappe.new_doc("Module Def")
        module.module_name = "Refer & Earn"
        module.app_name = "suntek_app"
        module.custom = False
        module.save()
        frappe.db.commit()
        print("Created 'Refer & Earn' module")
    else:
        print("'Refer & Earn' module already exists")

    # Change Ambassador doctype's module
    if frappe.db.exists("DocType", "Ambassador"):
        ambassador = frappe.get_doc("DocType", "Ambassador")
        old_module = ambassador.module

        # Skip if already in the correct module
        if old_module == "Refer & Earn":
            print("Ambassador doctype is already in 'Refer & Earn' module")
            return

        print(f"Changing Ambassador module from '{old_module}' to 'Refer & Earn'")

        # Update the module
        ambassador.module = "Refer & Earn"
        ambassador.save()
        frappe.db.commit()

        # Clear cache to apply changes immediately
        frappe.clear_cache(doctype="Ambassador")

        print("Ambassador doctype module updated successfully")
        print(
            "Note: You may need to manually move the JSON and Python files to the new module directory"
        )
    else:
        print("Warning: DocType 'Ambassador' does not exist")
