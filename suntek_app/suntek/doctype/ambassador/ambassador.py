import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import validate_email_address


class Ambassador(Document):
    def autoname(self):
        self.name = make_autoname("SES-AMBS-.#####")

    def validate(self):
        self.validate_email()
        self.validate_mobile_number()
        self.validate_ifsc_code()
        self.validate_aadhar_number()
        self.validate_pan_number()
        self.validate_bank_account_number()

    def validate_aadhar_number(self):
        if self.aadhar_number and not re.match(r"^\d{12}$", self.aadhar_number):
            frappe.throw(_("Aadhar Number must be 12 digits"))

    def validate_pan_number(self):
        if self.pan_number and not re.match(
            r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", self.pan_number
        ):
            frappe.throw(_("Invalid PAN Number Format"))

    def validate_email(self):
        if self.email_id:
            try:
                validate_email_address(self.email_id)
            except Exception:
                frappe.throw(_("Invalid Email Address"))

    def validate_mobile_number(self):
        if not self.ambassador_mobile_number:
            frappe.throw(_("Mobile Number is mandatory"))

        if not re.match(r"^[0-9]{10}$", self.ambassador_mobile_number):
            frappe.throw(_("Mobile Number must be 10 digits"))

    def validate_ifsc_code(self):
        if self.ifsc_code and not re.match(r"^[A-Z]{4}[0-9]{7}$", self.ifsc_code):
            frappe.throw(_("Invalid IFSC Code Format. It should be like ABCD0123456"))

    def validate_bank_account_number(self):
        if self.bank_account_number:
            # Remove any spaces or special characters
            clean_account_number = re.sub(r"[^0-9]", "", self.bank_account_number)

            # Check if it contains only digits
            if not clean_account_number.isdigit():
                frappe.throw(_("Bank Account Number should contain only digits"))

            # Check length (typically between 9 and 18 digits)
            if len(clean_account_number) < 9 or len(clean_account_number) > 18:
                frappe.throw(_("Bank Account Number should be between 9 and 18 digits"))
