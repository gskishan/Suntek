import frappe
import json

from suntek_app.suntek.utils.api_handler import create_api_response


def parse_request_data(data):
    """Parse request data from bytes to JSON if needed"""
    if isinstance(data, bytes):
        return json.loads(data.decode("utf-8"))
    return data


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
        frappe.log_error(
            "District creation failed", "Failed to create districts", "District"
        )
        return create_api_response(500, "error", "Internal server error", str(e))
