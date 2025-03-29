import random

import frappe

from suntek_app.suntek.utils.api_handler import create_api_response, parse_request_data


@frappe.whitelist()
def is_user_linked_to_channel_partner():
    user = frappe.session.user

    if user == "Administrator":
        return False

    return frappe.db.exists("Channel Partner", {"linked_user": user})


@frappe.whitelist(allow_guest=True)
def create_states():
    try:
        states_data = parse_request_data(frappe.request.data)
        frappe.set_user("Administrator")
        for state in states_data:
            new_state = frappe.new_doc("State")

            new_state.state = state.get("state")
            new_state.state_code = state.get("state_code")
            new_state.country = state.get("Country")
            new_state.insert()
            new_state.save()
        created_states = frappe.get_list("State")
        frappe.db.commit()
        return create_api_response(
            200,
            "success",
            "states data received",
            created_states,
        )
    except Exception as e:
        frappe.log_error("State Creation Failed", "Failed to create state", "State")
        return create_api_response(
            500,
            "error",
            "Internal server error",
            str(e),
        )


@frappe.whitelist(allow_guest=True)
def create_cities():
    try:
        cities_data = parse_request_data(frappe.request.data)
        frappe.set_user("Administrator")

        for city in cities_data:
            new_city = frappe.new_doc("City")

            new_city.city = city.get("city")
            new_city.state = city.get("state")
            new_city.country = city.get("country")
            new_city.insert()
            new_city.save()
        frappe.db.commit()

        created_cities = frappe.db.get_list("City")

        return create_api_response(201, "success", "cities_created", created_cities)
    except Exception as e:
        frappe.log_error("City creation failed", "Failed to create cities", "City")
        return create_api_response(500, "error", "Internal server error", str(e))


@frappe.whitelist(allow_guest=True)
def create_districts():
    try:
        districts_data = parse_request_data(frappe.request.data)
        frappe.set_user("Administrator")

        for district in districts_data:
            new_district = frappe.new_doc("District")

            new_district.district = district.get("district")
            new_district.city = district.get("city")
            new_district.insert()
            new_district.save()

        frappe.db.commit()

        created_districts = frappe.db.get_list("District")

        return create_api_response(
            201,
            "success",
            "districts_created",
            created_districts,
        )
    except Exception as e:
        frappe.log_error("District creation failed", "Failed to create districts", "District")
        return create_api_response(500, "error", "Internal server error", str(e))


@frappe.whitelist(allow_guest=True)
def create_channel_partner():
    try:
        frappe.set_user("Administrator")
        channel_partner = frappe.new_doc("Channel Partner")

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

        districts = frappe.get_list("District", fields=["name"])
        district = random.choice(districts)

        channel_partner.first_name = random.choice(first_names)
        channel_partner.last_name = random.choice(last_names)
        channel_partner.salutation = random.choice(["Mr", "Mrs", "Ms", "Dr"])
        channel_partner.mobile_number = generate_mobile_number()
        channel_partner.suntek_mobile_number = generate_mobile_number()
        channel_partner.suntek_email = generate_random_email(is_suntek_email=True)
        channel_partner.email = generate_random_email(is_suntek_email=False)
        channel_partner.status = "Active"
        channel_partner.default_buying_list = "Standard Buying"
        channel_partner.default_selling_list = "Standard Selling"
        channel_partner.contact_person = f"{random.choice(first_names)} {random.choice(last_names)}"

        # channel_partner.district = "RAN-TS-00001"
        channel_partner.district = district.name

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
        return create_api_response(500, "error", "Channel Partner Creation Failed", str(e))


def generate_random_number():
    return random.randint(1000, 9999)


def generate_mobile_number():
    return f"{random.randint(6, 9)}{random.randint(100000000, 999999999)}"


def generate_random_email(is_suntek_email=False):
    random_string = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=8))
    domain = "suntek.com" if is_suntek_email else random.choice(["gmail.com", "yahoo.com", "outlook.com"])
    return f"{random_string}@{domain}"
