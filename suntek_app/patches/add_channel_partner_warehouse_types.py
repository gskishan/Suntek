import frappe


def execute():
    try:
        for warehouse_type in ["Sales", "Subsidy"]:
            if not frappe.db.exists("Warehouse Type", warehouse_type):
                doc = frappe.new_doc("Warehouse Type")
                doc.name = warehouse_type
                doc.insert(ignore_permissions=True)

                frappe.db.commit()
                print(f"Created Warehouse Type: {warehouse_type}")
            else:
                print(f"Warehouse Type {warehouse_type} already exists")
    except Exception as e:
        frappe.log_error("Patch Error", f"Error creating warehouse types: {str(e)}")
        raise e
