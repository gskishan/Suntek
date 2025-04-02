import json

import frappe
from frappe.utils.response import build_response


def parse_request_data(data):
    """Parse request data from bytes to JSON if needed"""
    if isinstance(data, bytes):
        return json.loads(data.decode("utf-8"))
    return data


def create_api_response(status_code, status, message, data=None):
    """Helper function to create consistent API responses"""
    frappe.local.response.http_status_code = status_code
    response = {"status": status, "message": message}
    if data:
        response["data"] = data
    frappe.local.response.update(response)
    return build_response("json")


def validate_auth_token(auth_token: str) -> bool:
    if not auth_token:
        return False
    try:
        token = auth_token.split(" ")[1]
        return token == frappe.get_doc("Suntek Settings").get_password("solar_ambassador_api_token")
    except (IndexError, AttributeError):
        return False
