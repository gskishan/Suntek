import frappe
from frappe.utils.response import build_response


def create_api_response(status_code, status, message, data=None):
    """Helper function to create consistent API responses"""
    frappe.local.response.http_status_code = status_code
    response = {"status": status, "message": message}
    if data:
        response["data"] = data
    frappe.local.response.update(response)
    return build_response("json")
