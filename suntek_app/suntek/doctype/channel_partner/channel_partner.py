import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

from suntek_app.suntek.utils.validation_utils import validate_mobile_number


class ChannelPartner(Document):
    """Channel Partner Doctype"""

    def validate(self):
        self.handle_user_status()
        self.validate_mobile_numbers()
        self.make_channel_partner_name()
        self.channel_partner_code = self.name

    def autoname(self):
        if self.state_code and self.district_snake_case:
            self.name = make_autoname(
                f"{self.state_code}-{self.district_snake_case}-.#####"
            )

    def before_save(self):
        self.set_channel_partner_code()

    def set_channel_partner_code(self):
        if not self.channel_partner_code:
            self.channel_partner_code = self.name

    def make_channel_partner_name(self):
        self.channel_partner_name = (
            f"{self.first_name}{' ' + self.last_name if self.last_name else ''}"
        )

    def validate_mobile_numbers(self):
        if self.mobile_number and not validate_mobile_number(self.mobile_number):
            frappe.throw(
                "Invalid mobile number. Mobile number should be 10 digits and start with 6-9"
            )

        if self.suntek_mobile_number and not validate_mobile_number(
            self.suntek_mobile_number
        ):
            frappe.throw(
                "Invalid Suntek mobile number. Mobile number should be 10 digits and start with 6-9"
            )

    def handle_user_status(self):
        if self.linked_user:
            user = frappe.get_doc("User", self.linked_user)

            if self.status == "Inactive" and user.enabled:
                user.enabled = 0
                user.save(ignore_permissions=True)
                frappe.db.commit()
            elif self.status == "Active" and not user.enabled:
                user.enabled = 1
                user.save(ignore_permissions=True)
                frappe.db.commit()

    @frappe.whitelist()
    def create_user(self):
        """
        Create a User account for the Channel Partner.
        This is enabled if the Channel Partner is Active.
        """
        try:
            user = frappe.new_doc("User")
            user.update(
                {
                    "first_name": self.first_name,
                    "email": self.suntek_email,
                    "send_welcome_email": 0,
                }
            )
            user.flags.ignore_mandatory = True
            user.flags.ignore_permissions = True
            user.insert(ignore_mandatory=True)

            user.add_roles("Stock User", "System Manager")
            user.save()
            frappe.db.commit()

            self.db_set("linked_user", user.name)
            self.db_set("is_user_created", 1)

            return user.name

        except Exception as e:
            frappe.log_error(str(e), "User Creation Error")
            frappe.throw(str(e))