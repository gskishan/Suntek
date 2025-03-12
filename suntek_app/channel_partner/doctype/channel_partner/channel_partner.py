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
                    "applicable_for": "Warehouse",
                }
            )

            user_permission.flags.ignore_permissions = True
            user_permission.insert()

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Warehouse Permission Creation Error")
            frappe.throw(str(e))

    def create_user_permissions(self):
        try:
            user_permission = frappe.new_doc("User Permission")

            user_permission.update(
                {
                    "user": self.linked_user,
                    "allow": "Channel Partner",
                    "for_value": self.name,
                    "apply_to_all_doctypes": 1,
                }
            )

            user_permission.save()

            frappe.db.commit()

            print(f"User Permission saved: {user_permission.name}")
        except Exception as e:
            frappe.log_error(str(e), "Channel Partner User Permission Creation Error")

    def create_department_permission(self):
        try:
            user_permission = frappe.new_doc("User Permission")

            user_permission.user = self.linked_user
            user_permission.allow = "Department"
            user_permission.for_value = "Channel Partner - SESP"
            user_permission.apply_to_all_doctypes = 1

            user_permission.save()

            frappe.db.commit()
        except Exception as e:
            frappe.log_error(str(e), "Channel Partner Department Permission created")

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

            user.add_roles("Channel Partner")
            user.save()
            frappe.db.commit()

            self.db_set("linked_user", user.name)
            self.db_set("is_user_created", 1)

            self.create_user_permissions()
            self.create_department_permission()

            return user.name

        except Exception as e:
            frappe.log_error(str(e), "User Creation Error")
            frappe.throw(str(e))

    @frappe.whitelist()
    def create_channel_partner_warehouse(self):
        try:
            parent_warehouse = "Channel Partner Parent - SESP"

            if not frappe.db.exists("Warehouse", parent_warehouse):
                frappe.throw(f"Parent Warehouse '{parent_warehouse}' does not exist")

            sales_warehouse = frappe.new_doc("Warehouse")
            sales_warehouse_name = f"CP-{self.channel_partner_code}-Sales - SESP"

            sales_warehouse.update(
                {
                    "warehouse_name": sales_warehouse_name,
                    "parent_warehouse": parent_warehouse,
                    "company": "Suntek Energy Systems Pvt. Ltd.",
                    "custom_suntek_district": self.district_name,
                    "custom_suntek_city": self.city,
                    "custom_suntek_state": self.state,
                    "warehouse_type": "Sales",
                }
            )

            sales_warehouse.flags.ignore_permissions = True
            sales_warehouse.insert()

            subsidy_warehouse = frappe.new_doc("Warehouse")
            subsidy_warehouse_name = f"CP-{self.channel_partner_code}-Subsidy - SESP"

            subsidy_warehouse.update(
                {
                    "warehouse_name": subsidy_warehouse_name,
                    "parent_warehouse": parent_warehouse,
                    "company": "Suntek Energy Systems Pvt. Ltd.",
                    "custom_suntek_district": self.district_name,
                    "custom_suntek_city": self.city,
                    "custom_suntek_state": self.state,
                    "warehouse_type": "Subsidy",
                }
            )

            subsidy_warehouse.flags.ignore_permissions = True
            subsidy_warehouse.insert()

            self.db_set("default_sales_warehouse", sales_warehouse.name)
            self.db_set("default_subsidy_warehouse", subsidy_warehouse.name)
            self.db_set("warehouse", sales_warehouse.name)

            frappe.db.commit()

            if self.linked_user:
                self.create_warehouse_permission(warehouse=sales_warehouse)
                self.create_warehouse_permission(warehouse=subsidy_warehouse)

            return {
                "sales_warehouse": sales_warehouse.name,
                "subsidy_warehouse": subsidy_warehouse.name,
            }

        except Exception as e:
            frappe.log_error(str(e), "Warehouse Crreation Error")
            frappe.throw(str(e))

    @frappe.whitelist()
    def create_customer(self):
        try:
            # Check if a customer already exists
            existing_customers = frappe.get_all(
                "Customer",
                filters={"custom_channel_partner": self.name},
                fields=["name"],
            )

            if existing_customers:
                frappe.msgprint(
                    f"Customer {existing_customers[0].name} already exists for this Channel Partner"
                )
                return existing_customers[0].name

            # Get territory from district if available
            territory = "India"  # Default
            if hasattr(self, "district") and self.district:
                # First try to get linked territory
                district_territory = frappe.db.get_value(
                    "District", self.district, "territory"
                )
                if district_territory:
                    territory = district_territory
                else:
                    # If no linked territory, use district name
                    territory = self.district

            customer = frappe.new_doc("Customer")
            customer.update(
                {
                    "customer_name": self.channel_partner_name,
                    "customer_type": "Partnership",
                    "customer_group": "Channel Partner",
                    "territory": territory,
                    "custom_channel_partner": self.name,
                    "mobile_no": self.mobile_number,
                    "email_id": self.email,
                    "tax_id": self.gst_number,
                    "default_currency": "INR",
                }
            )

            customer.flags.ignore_permissions = True
            customer.insert()

            if self.channel_partner_address:
                address_doc = frappe.get_doc("Address", self.channel_partner_address)
                new_address = frappe.new_doc("Address")
                new_address.address_title = self.channel_partner_name
                new_address.address_type = "Billing"
                new_address.address_line1 = address_doc.address_line1
                new_address.address_line2 = address_doc.address_line2
                new_address.city = self.city
                new_address.state = self.state
                new_address.country = self.country
                new_address.pincode = address_doc.pincode
                new_address.phone = self.mobile_number
                new_address.email_id = self.email
                new_address.gstin = self.gst_number

                new_address.append(
                    "links",
                    {
                        "link_doctype": "Customer",
                        "link_name": customer.name,
                    },
                )

                new_address.flags.ignore_permissions = True
                new_address.insert()

            self.db_set("linked_customer", customer.name)

            return customer.name

        except Exception as e:
            frappe.log_error(str(e), "Customer Creation Error")
            frappe.throw(str(e))


@frappe.whitelist()
def get_channel_partner_data_from_project(project_id):
    project = frappe.get_doc("Project", project_id)

    return project.custom_channel_partner if project.custom_channel_partner else None
