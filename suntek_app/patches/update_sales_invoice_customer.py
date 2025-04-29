import frappe


def execute():
    try:
        invoices = frappe.get_list("Sales Invoice", filters={"name": ["in", ["SES/0071/25-26", "SES/0069/25-26"]]})
        customer = frappe.get_doc("Customer", "Suntek Energy Systems Private limited - 4")
        billing_address = frappe.get_doc("Address", "MP Billing-Billing")
        contact_person = frappe.get_doc("Contact", "Suntek Energy Systems Private limited-5")

        for invoice in invoices:
            invoice_doc = frappe.get_doc("Sales Invoice", invoice.name)
            invoice_doc.db_set("customer", customer.name)
            invoice_doc.db_set("customer_address", billing_address.name)
            invoice_doc.db_set("address_display", create_address_string(billing_address))
            invoice_doc.db_set("contact_person", contact_person.name)
            invoice_doc.db_set("contact_mobile", contact_person.mobile_no)
            invoice_doc.db_set("shipping_address_name", billing_address.name)
            invoice_doc.db_set("shipping_address", create_address_string(billing_address))
            invoice_doc.db_set("contact_display", contact_person.name)

        frappe.db.commit()

    except Exception as e:
        frappe.log_error(f"Error updating sales invoice customer: {e}")
        frappe.db.rollback()
        print(f"Error updating sales invoice customer: {e}")


def create_address_string(address_doc):
    address_string = ""

    if address_doc.address_line1:
        address_string += f"{address_doc.address_line1}\n"
    if address_doc.address_line2:
        address_string += f"{address_doc.address_line2}\n"
    if address_doc.city:
        address_string += f"{address_doc.city}\n"
    if address_doc.state:
        address_string += f"{address_doc.state}\n"
    if address_doc.pincode:
        address_string += f"{address_doc.pincode}\n"
    if address_doc.country:
        address_string += f"{address_doc.country}\n\n"
    if address_doc.email_id:
        address_string += f"{address_doc.email_id}\n"
    if address_doc.gstin:
        address_string += f"{address_doc.gstin}\n"

    return address_string
