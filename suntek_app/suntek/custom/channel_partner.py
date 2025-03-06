import random
import frappe
from suntek_app.suntek.utils.api_handler import create_api_response


def get_districts():
    districts = frappe.cache().get_value("all_districts")
    if not districts:
        districts = [d.name for d in frappe.get_all("District", fields=["name"])]
        frappe.cache().set_value("all_districts", districts, expires_in_sec=3600)
    return districts


@frappe.whitelist(allow_guest=True)
def create_channel_partner():
    try:
        channel_partner = frappe.new_doc("Channel Partner")

        channel_partner.first_name = f"first name {generate_random_number()}"
        channel_partner.last_name = f"last name {generate_random_number()}"
        channel_partner.salutation = "Mr"
        channel_partner.channel_partner_code = f"{generate_random_number()}"
        channel_partner.mobile_number = generate_mobile_number()
        channel_partner.suntek_mobile_number = generate_mobile_number()
        channel_partner.suntek_email = generate_random_email(is_suntek_email=True)
        channel_partner.email = generate_random_email(is_suntek_email=False)
        channel_partner.status = "Active"
        channel_partner.contact_person = (
            f"Test Contact Person {generate_random_number()}"
        )

        districts = get_districts()
        if districts:
            channel_partner.district = random.choice(districts)
        else:
            frappe.throw("No districts found in the system")

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
    return random.randint(1, 1000)


def generate_mobile_number():
    return f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"


def generate_random_email(is_suntek_email=False):
    return (
        f"test{generate_random_number()}@test.com"
        if not is_suntek_email
        else f"test{generate_random_number()}@suntek.com"
    )