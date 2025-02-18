import re

import frappe
from frappe import _
from frappe.model.document import Document


class Ambassador(Document):
    def before_insert(self):
        self.validate_email()

    def validate_email(self):
        if not re.match(
            "[A-Za-z0-9\._%+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}",
            self.email_id,
        ):
            frappe.throw(_("Invalid Email Format"))
