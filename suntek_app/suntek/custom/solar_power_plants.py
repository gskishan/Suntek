def change_power_plant_assigned_status(doc, method):
    doc.status = "Assigned" if check_customer_details(doc) else "Unassigned"


def check_customer_details(doc):
    return bool(doc.customer and doc.customer_mobile_no)
