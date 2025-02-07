import frappe
from frappe.model.document import Document
from suntek_app.suntek.utils.validation_utils import validate_mobile_number


class ChannelPartner(Document):
    def validate(self):
        self.validate_mobile_numbers()
        self.make_channel_partner_name()

    def make_channel_partner_name(self):
        self.channel_partner_name = f"{self.first_name}{' ' + self.last_name if self.last_name else ''}"

    def validate_mobile_numbers(self):
        if self.mobile_number and not validate_mobile_number(self.mobile_number):
            print(self.mobile_number)
            frappe.throw("Invalid mobile number. Mobile number should be 10 digits and start with 6-9")

        if self.suntek_mobile_number and not validate_mobile_number(self.suntek_mobile_number):
            frappe.throw("Invalid Suntek mobile number. Mobile number should be 10 digits and start with 6-9")

    @frappe.whitelist()
    def create_user(self):
        try:
            user = frappe.new_doc("User")
            user.update({"first_name": self.first_name, "email": self.suntek_email, "send_welcome_email": 1})
            user.flags.ignore_mandatory = True
            user.flags.ignore_permissions = True
            user.insert(ignore_mandatory=True)

            self.db_set('linked_user', user.name)
            self.db_set('is_user_created', 1)

            return user.name

        except Exception as e:
            frappe.log_error(str(e), "User Creation Error")
            frappe.throw(str(e))
