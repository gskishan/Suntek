import frappe
from frappe.model.document import Document
import hmac
import hashlib
import secrets
import json


class SuntekSettings(Document):
    pass


@frappe.whitelist()
def generate_webhook_secret():
    """Generate a new HMAC token with server-side secret and data"""
    if not frappe.has_permission("Suntek Settings", "write"):
        frappe.throw("Not permitted to generate webhook secret")

    try:

        secret_key = secrets.token_hex(32)
        random_data = json.dumps({"timestamp": secrets.token_hex(8)}).encode()

        token = hmac.new(secret_key.encode(), random_data, hashlib.sha256).hexdigest()

        settings = frappe.get_doc("Suntek Settings")
        settings.neodove_webhook_secret = secret_key
        settings.save()

        return token

    except Exception as e:
        frappe.log_error(message=f"Error generating webhook token: {str(e)}", title="Webhook Token Generation Error")
        frappe.throw("Error generating webhook token")


@frappe.whitelist()
def generate_solar_ambassador_api_token():
    if not frappe.has_permission("Suntek Settings", "write"):
        frappe.throw("Not permitted to generate API token")

    try:
        secret_key = secrets.token_hex(32)
        random_data = json.dumps({"timestamp": secrets.token_hex(8)}).encode()

        token = hmac.new(secret_key.encode(), random_data, hashlib.sha256).hexdigest()

        settings = frappe.get_doc("Suntek Settings")
        settings.solar_ambassador_api_token = secret_key
        settings.save()

        return token

    except Exception as e:
        frappe.log_error(message=f"Error generating API token: {str(e)}")
        frappe.throw("Error generating API token")


@frappe.whitelist(allow_guest=True)
def test_django_api_auth():
    """Verify incoming Django request using stored secret key"""
    try:
        # Get the authorization header
        auth_token = frappe.request.headers.get('X-Django-Server-Authorization')
        if not auth_token or not auth_token.startswith('Bearer '):
            return {'status': 'error', 'message': 'Missing or invalid authorization header'}

        incoming_token = auth_token.split(' ')[1]

        # Get the stored secret key from Suntek Settings
        settings = frappe.get_doc('Suntek Settings')
        stored_token = settings.get_password("solar_ambassador_api_token")

        print(incoming_token, "\n", stored_token)

        if not stored_token:
            return {'status': 'error', 'message': 'API token not configured in Suntek Settings'}

        # Direct token comparison
        if incoming_token != stored_token:
            return {'status': 'error', 'message': 'Invalid authentication token'}

        return {'status': 'success', 'message': 'Authentication successful'}

    except Exception as e:
        frappe.log_error(title="Authentication Error", message=str(e))
        return {'status': 'error', 'message': f'Authentication failed: {str(e)}'}
