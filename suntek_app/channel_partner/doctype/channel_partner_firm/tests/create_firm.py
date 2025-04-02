import frappe


def create_customer(firm_name: str):
    customer = frappe.get_doc(
        {
            "doctype": "Customer",
            "customer_name": firm_name,
            "customer_type": "Company",
            "customer_group": "All Customer Groups",
            "territory": "All Territories",
            "customer_primary_contact": "Test Contact",
            "customer_primary_contact_email": "test@example.com",
        }
    )
    customer.insert()
    return customer


def create_address(firm_name: str, firm):
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "is_primary_address": 1,
            "is_shipping_address": 1,
            "address_title": firm_name,
            "address_line1": "Test Address Line 1",
            "address_line2": "Test Address Line 2",
            "city": "Hyderabad",
            "state": "Telangana",
            "postal_code": "500001",
            "country": "India",
            "links": [{"link_doctype": "Channel Partner Firm", "link_name": firm.name}],
        }
    )
    address.insert()
    return address


def create_contact(firm_name: str, firm):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": firm_name,
            "links": [{"link_doctype": "Channel Partner Firm", "link_name": firm.name}],
        }
    )
    contact.insert()
    return contact


def create_sales_partner(firm_name: str, commission_rate: float, territory: str):
    sales_partner = frappe.get_doc(
        {
            "doctype": "Sales Partner",
            "partner_name": firm_name,
            "commission_rate": commission_rate,
            "territory": territory,
        }
    )
    sales_partner.insert()
    return sales_partner


def create_firm(firm_name: str, status: str = "Pending Approval"):
    firm = frappe.get_doc(
        {
            "doctype": "Channel Partner Firm",
            "firm_name": firm_name,
            "status": "Pending Approval",
        }
    )
    firm.insert()

    address = create_address(firm_name, firm)
    contact = create_contact(firm_name, firm)
    customer = create_customer(firm_name)

    firm.address = address.name
    firm.contact_person = contact.name
    firm.customer = customer.name
    firm.save()

    if status != "Pending Approval":
        firm.status = status
        firm.save()

    return firm


def create_firm_with_attachments(firm_name: str, status: str = "Pending Approval"):
    firm = create_firm(firm_name, status="Pending Approval")

    firm.business_registration = "https://example.com/business_registration.pdf"
    firm.agreement = "https://example.com/agreement.pdf"
    firm.noc_for_stock = "https://example.com/noc_for_stock.pdf"
    firm.address_proof = "https://example.com/address_proof.pdf"
    firm.commission_rate = 10.0

    firm.save()

    if status != "Pending Approval":
        firm.status = status
        firm.save()

    return firm


def create_firm_with_sales_partner(firm_name: str, commission_rate: float, territory: str):
    firm = create_firm_with_attachments(firm_name)
    sales_partner = create_sales_partner(firm_name, commission_rate, territory)

    firm.linked_sales_partner = sales_partner.name
    firm.save()

    return firm
