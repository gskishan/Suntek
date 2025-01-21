# suntek/suntek/doctype/suntek_settings/suntek_settings.py

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
        # Generate secret key and random data server side
        secret_key = secrets.token_hex(32)
        random_data = json.dumps({"timestamp": secrets.token_hex(8)}).encode()

        # Generate HMAC token
        token = hmac.new(secret_key.encode(), random_data, hashlib.sha256).hexdigest()

        # Save secret key to settings
        settings = frappe.get_doc("Suntek Settings")
        settings.neodove_webhook_secret = secret_key
        settings.save()

        return token

    except Exception as e:
        frappe.log_error(message=f"Error generating webhook token: {str(e)}", title="Webhook Token Generation Error")
        frappe.throw("Error generating webhook token")
