def change_power_plant_assigned_status(doc, method):
    if check_customer_details(doc, method):
        doc.status = "Assigned"
    else:
        doc.status = "Unassigned"


def check_customer_details(doc):
    if doc.customer and doc.customer_mobile_no:
        return True
    return False
