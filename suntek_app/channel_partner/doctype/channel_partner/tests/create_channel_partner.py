import frappe

from suntek_app.channel_partner.doctype.channel_partner_firm.tests.create_firm import (
    create_firm_with_attachments,
)


def create_valid_channel_partner_firm():
    firm = create_firm_with_attachments("_Test Firm 001", status="Active")
    return firm


def create_contact(first_name: str, last_name: str, email: str, mobile_number: str):
    contact = frappe.get_doc(
        {
            "doctype": "Contact",
            "first_name": first_name,
            "last_name": last_name,
            "email_id": email,
            "mobile_no": mobile_number,
        }
    )

    contact.insert()
    return contact


def create_channel_partner(channel_partner_name: str, status="Pending Approval", fill_mandatory: bool = False):
    firm = create_valid_channel_partner_firm()
    contact = create_contact(channel_partner_name, "", "test@example.com", "9876543210")

    address = frappe.get_doc(
        {
            "doctype": "Address",
            "address_title": channel_partner_name,
            "address_type": "Billing",
            "address_line1": "Test Address Line 1",
            "city": "Hyderabad",
            "state": "Telangana",
            "country": "India",
            "pincode": "500001",
            "phone": "9876543210",
            "email_id": "test@example.com",
            "contact": contact.name,
        }
    )
    address.insert()

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
