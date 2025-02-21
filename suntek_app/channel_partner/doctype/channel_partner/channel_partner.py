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

    def create_warehouse_permission(self, warehouse):
        try:
            user_permission = frappe.new_doc("User Permission")
            user_permission.update(
                {
                    "user": self.linked_user,
                    "allow": "Warehouse",
                    "for_value": warehouse.name,
                    "apply_to_all_doctypes": 1,
                }
            )

            user_permission.flags.ignore_permissions = True
            user_permission.insert()

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Warehouse Permission Creation Error")
            frappe.throw(str(e))

    def create_user_permissions(self):
        restricted_doctypes = [
            "Lead",
            "Opportunity",
            "Quotation",
            "Sales Order",
            "Site Survey",
            "Designing",
            "Project",
            "Discom",
            "Subsidy",
            "Sales Invoice",
            "Delivery Note",
            "Installation Note",
            "Purchase Order",
            "Purchase Invoice",
        ]

        try:
            for doctype in restricted_doctypes:
                user_permission = frappe.new_doc("User Permission")

                user_permission.user = self.linked_user
                user_permission.allow = "Channel Partner"
                user_permission.for_value = self.name
                user_permission.apply_to_all_doctypes = 0
                user_permission.applicable_for = doctype

                user_permission.save()

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Channel Partner User Permission Creation Error")

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

            user.add_roles("Channel Partner", "Stock User", "System Manager")
            user.save()
            frappe.db.commit()

            self.db_set("linked_user", user.name)
            self.db_set("is_user_created", 1)

            self.create_user_permissions()

            return user.name

        except Exception as e:
            frappe.log_error(str(e), "User Creation Error")
            frappe.throw(str(e))

    @frappe.whitelist()
    def create_channel_partner_warehouse(self):
        """
        Creates a warehouse linked to the channel partner
        """

        try:
            parent_warehouse = "Channel Partner Parent - SESP"

            if not frappe.db.exists("Warehouse", parent_warehouse):
                frappe.throw(f"Parent Warehouse '{parent_warehouse}' does not exist")

            warehouse = frappe.new_doc("Warehouse")

            warehouse_name = f"CP-{self.channel_partner_code} - SESP"

            warehouse.update(
                {
                    "warehouse_name": warehouse_name,
                    "parent_warehouse": parent_warehouse,
                    "company": "Suntek Energy Systems Pvt. Ltd.",
                }
            )

            warehouse.flags.ignore_permissions = True
            warehouse.insert()

            self.db_set("warehouse", warehouse.name)

            frappe.db.commit()

            if self.linked_user and self.warehouse:
                self.create_warehouse_permission(warehouse=warehouse)

            return warehouse.name

        except Exception as e:
            frappe.log_error(str(e), "Warehouse creation error")
            frappe.throw(str(e))
