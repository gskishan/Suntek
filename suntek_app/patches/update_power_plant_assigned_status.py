def execute():
    import frappe

    power_plants = frappe.db.sql(
        """
        SELECT DISTINCT parent
        FROM `tabSolar Power Plant Customer`
        WHERE parenttype = 'Solar Power Plants'
    """,
        as_dict=1,
    )
    for plant in power_plants:
        doc = frappe.get_doc("Solar Power Plants", plant.parent)
        if doc.status == "Unassigned":
            doc.status = "Assigned"
            doc.save()

    frappe.db.commit()

    print(f"Updated {len(power_plants)} from Unassigned to Assigned")
