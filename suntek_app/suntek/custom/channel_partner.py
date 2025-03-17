import random

import frappe


from suntek_app.suntek.utils.api_handler import create_api_response


@frappe.whitelist(allow_guest=True)
def create_channel_partner():
    try:
        channel_partner = frappe.new_doc("Channel Partner")

        # Generate random names
        first_names = [
            "John",
            "Michael",
            "David",
            "Robert",
            "James",
            "Sarah",
            "Mary",
            "Patricia",
            "Jennifer",
            "Linda",
        ]
        last_names = [
            "Smith",
            "Johnson",
            "Williams",
            "Jones",
            "Brown",
            "Davis",
            "Miller",
            "Wilson",
            "Moore",
            "Taylor",
        ]

        channel_partner.first_name = random.choice(first_names)
        channel_partner.last_name = random.choice(last_names)
        channel_partner.salutation = random.choice(["Mr", "Mrs", "Ms", "Dr"])
        channel_partner.channel_partner_code = f"CP-{generate_random_number()}"
        channel_partner.mobile_number = generate_mobile_number()
        channel_partner.suntek_mobile_number = generate_mobile_number()
        channel_partner.suntek_email = generate_random_email(is_suntek_email=True)
        channel_partner.email = generate_random_email(is_suntek_email=False)
        channel_partner.status = "Active"
        channel_partner.contact_person = (
            f"{random.choice(first_names)} {random.choice(last_names)}"
        )

        # Set specific district as requested
        channel_partner.district = "RAN-TS-00001"

        # Get a random firm from Channel Partner Firm doctype
        firms = frappe.get_all("Channel Partner Firm", fields=["name"])
        if firms:
            channel_partner.channel_partner_firm = random.choice(firms).name
        else:
            frappe.throw("No Channel Partner Firms found in the system")

        channel_partner.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()

        return create_api_response(
            200,
            "success",
            "Channel Partner Created Successfully",
            channel_partner.as_dict(),
        )
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Channel Partner Creation Failed")
        return create_api_response(
            500, "error", "Channel Partner Creation Failed", str(e)
        )


def generate_random_number():
    return random.randint(1000, 9999)


def generate_mobile_number():
    return f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"


def generate_random_email(is_suntek_email=False):
    random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
    domain = (
        "suntek.com"
        if is_suntek_email
        else random.choice(["gmail.com", "yahoo.com", "outlook.com"])
    )
    return f"{random_string}@{domain}"
