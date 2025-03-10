import re

import frappe
from frappe import _
from frappe.model.document import Document


class Ambassador(Document):
    def before_insert(self):
        self.validate_email()
        self.validate_mobile_number()
        self.validate_ifsc_code()

    def validate(self):
        self.validate_email()
        self.validate_mobile_number()
        self.validate_ifsc_code()

    def validate_email(self):
        if self.email_id and not re.match(
            r"[A-Za-z0-9\._%+\-]+@[A-Za-z0-9\.\-]+\.[A-Za-z]{2,}",
            self.email_id,
        ):
            frappe.throw(_("Invalid Email Format"))

    def validate_mobile_number(self):
        if not self.ambassador_mobile_number:
            frappe.throw(_("Mobile Number is mandatory"))

        if not re.match(r"^[0-9]{10}$", self.ambassador_mobile_number):
            frappe.throw(_("Mobile Number must be 10 digits"))

    def validate_ifsc_code(self):
        if self.ifsc_code and not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", self.ifsc_code):
            frappe.throw(_("Invalid IFSC Code Format. It should be like ABCD0123456"))
