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


def create_address(title: str, doctype: str, docname: str):
    address = frappe.get_doc(
        {
            "doctype": "Address",
            "is_primary_address": 1,
            "is_shipping_address": 1,
            "address_title": title,
            "address_line1": "Test Address Line 1",
            "address_line2": "Test Address Line 2",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "pincode": "500001",
            "phone": "9876543210",
            "email_id": "test@example.com",
            "links": [{"link_doctype": doctype, "link_name": docname}],
        }
    )
    address.insert()
    return address


def create_contact(
    first_name: str, last_name: str, email: str, mobile_number: str, doctype: str = None, docname: str = None
):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email,
            "mobile_no": mobile_number,
        }
    )

    if doctype and docname:
        contact.append("links", {"link_doctype": doctype, "link_name": docname})

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


def create_channel_partner_firm(firm_name: str, status: str = "Pending Approval"):
    firm = frappe.get_doc(
        {
            "doctype": "Channel Partner Firm",
            "firm_name": firm_name,
            "status": "Pending Approval",
        }
    )
    firm.insert()

    address = create_address(firm_name, "Channel Partner Firm", firm.name)
    contact = create_contact(firm_name, "", "firm@example.com", "9876543210", "Channel Partner Firm", firm.name)
    customer = create_customer(firm_name)

    firm.address = address.name
    firm.contact_person = contact.name
    firm.customer = customer.name
    firm.save()

    if status != "Pending Approval":
        firm.status = status
        firm.save()

    return firm


def create_channel_partner_firm_with_attachments(firm_name: str, status: str = "Pending Approval"):
    firm = create_channel_partner_firm(firm_name, status="Pending Approval")

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


def create_channel_partner_firm_with_sales_partner(firm_name: str, commission_rate: float, territory: str):
    firm = create_channel_partner_firm_with_attachments(firm_name)
    sales_partner = create_sales_partner(firm_name, commission_rate, territory)

    firm.linked_sales_partner = sales_partner.name
    firm.save()

    return firm


def create_valid_channel_partner_firm():
    firm = create_channel_partner_firm_with_attachments("_Test Firm 001", status="Active")
    return firm


def create_channel_partner(channel_partner_name: str, status="Pending Approval", fill_mandatory: bool = False):
    firm = create_valid_channel_partner_firm()
    contact = create_contact(channel_partner_name, "", "test@example.com", "9876543210")

    address = create_address(channel_partner_name, "Contact", contact.name)

    if fill_mandatory:
        channel_partner = frappe.get_doc(
            {
                "doctype": "Channel Partner",
                "channel_partner_name": channel_partner_name,
                "status": status,
                "channel_partner_firm": firm.name,
                "first_name": channel_partner_name,
                "email": "test@example.com",
                "suntek_email": "suntek.test@example.com",
                "mobile_number": "9876543210",
                "contact": contact.name,
                "channel_partner_address": address.name,
                "district": "Hyderabad",
                "pan_number": "ABCDE1234F",
                "id_proof": "https://example.com/id_proof.pdf",
                "pan_card": "https://example.com/pan_card.pdf",
                "photograph": "https://example.com/photo.jpg",
                "electricity_bill": "https://example.com/electricity_bill.pdf",
            }
        )
        channel_partner.insert()
        return channel_partner

    else:
        channel_partner = frappe.get_doc(
            {
                "doctype": "Channel Partner",
                "channel_partner_name": channel_partner_name,
                "status": status,
            }
        )
        channel_partner.insert()
        return channel_partner
