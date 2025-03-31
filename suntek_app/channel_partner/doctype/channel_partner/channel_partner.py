import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname

from suntek_app.suntek.utils.validation_utils import validate_mobile_number, validate_pan_number


class ChannelPartner(Document):
    def before_insert(self):
        self.validate_channel_partner_firm()

    def autoname(self):
        if self.state_code and self.district_snake_case:
            self.name = make_autoname(f"{self.state_code}-{self.district_snake_case}-.#####")

    def before_save(self):
        self.update_channel_partner_firm()
        self.set_channel_partner_code()

        self.channel_partner_code = self.name

    def validate(self):
        self.handle_user_status()
        self.validate_mobile_numbers()
        self.make_channel_partner_name()

        validate_pan_number(self.pan_number)

    def after_insert(self):
        self.update_channel_partner_firm()

    def validate_channel_partner_firm(self):
        if not self.channel_partner_firm:
            return
        firm = frappe.get_doc("Channel Partner Firm", self.channel_partner_firm)
        if not firm.is_active():
            frappe.throw(
                f"Channel Partner Firm {self.channel_partner_firm} is inactive. Cannot create channel partner."
            )

    def update_channel_partner_firm(self):
        old_firm = None
        if not self.is_new():
            old_firm = frappe.db.get_value("Channel Partner", self.name, "channel_partner_firm")

        if old_firm and old_firm != self.channel_partner_firm:
            old_firm_doc = frappe.get_doc("Channel Partner Firm", old_firm)

            for i, cp in enumerate(old_firm_doc.channel_partners):
                if cp.channel_partner == self.name:
                    old_firm_doc.channel_partners.pop(i)
                    break

            if old_firm_doc.docstatus == 1:
                old_firm_doc.flags.ignore_validate_update_after_submit = True
            old_firm_doc.flags.ignore_permissions = True
            old_firm_doc.save()

        if self.channel_partner_firm:
            firm = frappe.get_doc("Channel Partner Firm", self.channel_partner_firm)

            partner_exists = False
            for cp in firm.channel_partners:
                if cp.channel_partner == self.name:
                    partner_exists = True
                    break

            if not partner_exists:
                firm.append(
                    "channel_partners",
                    {
                        "channel_partner": self.name,
                        "channel_partner_name": self.channel_partner_name,
                    },
                )

                if firm.docstatus == 1:
                    firm.flags.ignore_validate_update_after_submit = True
                    firm.flags.ignore_permissions = True
                    firm.save()

    def set_channel_partner_code(self):
        if not self.channel_partner_code:
            self.channel_partner_code = self.name

    def make_channel_partner_name(self):
        if self.last_name:
            self.channel_partner_name = f"{self.first_name} {self.last_name}"
        else:
            self.channel_partner_name = self.first_name

    def validate_mobile_numbers(self):
        if self.mobile_number and not validate_mobile_number(self.mobile_number):
            frappe.throw("Invalid mobile number. Mobile number should be 10 digits and start with 6-9")

        if self.suntek_mobile_number and not validate_mobile_number(self.suntek_mobile_number):
            frappe.throw("Invalid Suntek mobile number. Mobile number should be 10 digits and start with 6-9")

    def handle_user_status(self):
        if self.linked_user:
            user = frappe.get_doc("User", self.linked_user)

            if (self.status == "Inactive" and user.enabled) or (self.status == "Active" and not user.enabled):
                user.enabled = 1 if self.status == "Active" else 0
                user.save(ignore_permissions=True)
                frappe.db.commit()

    def create_user_permissions(self, doctype, for_value, applicable_for=None, apply_to_all_doctypes=0):
        if not self.linked_user:
            frappe.throw("Cannot create permission: No linked user found")

        if not for_value:
            frappe.throw(f"Cannot create {doctype} permission: Missing for_value")

        try:
            existing = frappe.db.exists(
                "User Permission",
                {
                    "user": self.linked_user,
                    "allow": doctype,
                    "for_value": for_value,
                },
            )

            if existing:
                return existing

            user_permission = frappe.new_doc("User Permission")
            user_permission.update(
                {
                    "user": self.linked_user,
                    "allow": doctype,
                    "for_value": for_value,
                    "apply_to_all_doctypes": apply_to_all_doctypes,
                    "applicable_for": applicable_for,
                }
            )

            user_permission.flags.ignore_permissions = True
            user_permission.insert()

            return user_permission.name

        except Exception as e:
            frappe.log_error(
                title=f"Error creating {doctype} permission",
                message=str(e),
                reference_doctype="Channel Partner",
                reference_name=self.name,
            )
            frappe.throw(f"Failed to create {doctype} permission: {str(e)}")

    def create_firm_permission(self):
        try:
            user_permission = frappe.new_doc("User Permission")
            user_permission.update(
                {
                    "user": self.linked_user,
                    "allow": "Channel Partner Firm",
                    "for_value": self.channel_partner_firm,
                    "apply_to_all_doctypes": 1,
                }
            )

            user_permission.save()
            frappe.db.commit()
        except Exception as e:
            frappe.log_error(
                title="Channel Partner Permission Creation Error",
                message=str(e),
                reference_doctype="Channel Partner",
            )

    @frappe.whitelist()
    def create_user(self):
        frappe.db.begin()

        try:
            linked_user = None
            default_sales_warehouse = None
            default_subsidy_warehouse = None

            warehouses_created = False
            permissions_created = []

            user = frappe.new_doc("User")
            user.update(
                {
                    "first_name": self.first_name,
                    "email": self.suntek_email,
                    "send_welcome_email": 0,
                    "module_profile": "Channel Partner"
                    if frappe.db.exists("Module Profile", "Channel Partner")
                    else None,
                }
            )
            user.flags.ignore_mandatory = True
            user.flags.ignore_permissions = True
            user.insert(ignore_mandatory=True)

            user.add_roles("Channel Partner")
            user.save()

            linked_user = user.name

            if not self.default_sales_warehouse or not self.default_subsidy_warehouse:
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

                default_sales_warehouse = sales_warehouse.name
                default_subsidy_warehouse = subsidy_warehouse.name
                warehouses_created = True

            if linked_user:
                cp_perm = self._create_user_permissions(
                    user=linked_user, doctype="Channel Partner", for_value=self.name, apply_to_all_doctypes=1
                )
                if cp_perm:
                    permissions_created.append("Channel Partner")

                if default_sales_warehouse or self.default_sales_warehouse:
                    warehouse_value = default_sales_warehouse or self.default_sales_warehouse
                    sales_perm = self._create_user_permissions(
                        user=linked_user,
                        doctype="Warehouse",
                        for_value=warehouse_value,
                        applicable_for="Warehouse",
                    )
                    if sales_perm:
                        permissions_created.append("Sales Warehouse")

                if default_subsidy_warehouse or self.default_subsidy_warehouse:
                    warehouse_value = default_subsidy_warehouse or self.default_subsidy_warehouse
                    subsidy_perm = self._create_user_permissions(
                        user=linked_user,
                        doctype="Warehouse",
                        for_value=warehouse_value,
                        applicable_for="Warehouse",
                    )
                    if subsidy_perm:
                        permissions_created.append("Subsidy Warehouse")

                dept_perm = self._create_user_permissions(
                    user=linked_user,
                    doctype="Department",
                    for_value="Channel Partner - SESP",
                    apply_to_all_doctypes=1,
                )
                if dept_perm:
                    permissions_created.append("Department")

                if self.channel_partner_firm:
                    firm_perm = self._create_user_permissions(
                        user=linked_user,
                        doctype="Channel Partner Firm",
                        for_value=self.channel_partner_firm,
                        apply_to_all_doctypes=1,
                    )
                    if firm_perm:
                        permissions_created.append("Channel Partner Firm")

            self.linked_user = linked_user
            self.is_user_created = 1

            if warehouses_created:
                self.default_sales_warehouse = default_sales_warehouse
                self.default_subsidy_warehouse = default_subsidy_warehouse
                self.warehouse = default_sales_warehouse

            self.flags.ignore_mandatory = True
            self.save()

            frappe.db.commit()

            success_message = f"Successfully created user account for {self.channel_partner_name}"
            if warehouses_created:
                success_message += "\nCreated Sales and Subsidy warehouses"

            success_message += f"\nCreated permissions: {', '.join(permissions_created)}"

            frappe.msgprint(success_message)
            return linked_user

        except Exception as e:
            frappe.db.rollback()

            error_message = f"Failed to complete Channel Partner setup: {str(e)}"
            frappe.log_error(
                title=f"Channel Partner Setup Error - {self.name}",
                message=error_message,
                reference_doctype="Channel Partner",
                reference_name=self.name,
            )

            frappe.msgprint(
                f"Setup process failed and was rolled back. Error: {str(e)}",
                indicator="red",
            )
            frappe.throw(error_message)

    def _create_user_permissions(self, user, doctype, for_value, applicable_for=None, apply_to_all_doctypes=0):
        if not user:
            frappe.throw("Cannot create permission: No user provided")

        if not for_value:
            frappe.throw(f"Cannot create {doctype} permission: Missing for_value")

        try:
            existing = frappe.db.exists(
                "User Permission",
                {
                    "user": user,
                    "allow": doctype,
                    "for_value": for_value,
                },
            )

            if existing:
                return existing

            user_permission = frappe.new_doc("User Permission")
            user_permission.update(
                {
                    "user": user,
                    "allow": doctype,
                    "for_value": for_value,
                    "apply_to_all_doctypes": apply_to_all_doctypes,
                    "applicable_for": applicable_for,
                }
            )

            user_permission.flags.ignore_permissions = True
            user_permission.insert()

            return user_permission.name

        except Exception as e:
            frappe.log_error(
                title=f"Error creating {doctype} permission",
                message=str(e),
                reference_doctype="Channel Partner",
                reference_name=self.name,
            )
            frappe.throw(f"Failed to create {doctype} permission: {str(e)}")

    def _create_customer(self, linked_user):
        try:
            if self.linked_customer:
                frappe.msgprint(f"Customer {self.linked_customer} is already linked to this Channel Partner")
                linked_customer = frappe.get_doc("Customer", {"name": self.linked_customer})
                return linked_customer.name

            territory = "India"
            if hasattr(self, "district") and self.district:
                district_territory = frappe.db.get_value("District", self.district, "territory")
                if district_territory:
                    territory = district_territory
                else:
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

                new_address.append(
                    "links",
                    {
                        "link_doctype": "Customer",
                        "link_name": customer.name,
                    },
                )

                new_address.flags.ignore_permissions = True
                new_address.insert()

            return customer.name

        except Exception as e:
            frappe.log_error(str(e), "Customer Creation Error")
            frappe.throw(str(e))

    def create_customer(self):
        try:
            if self.linked_customer:
                frappe.msgprint(f"Customer {self.linked_customer} is already linked to this Channel Partner")

                linked_customer = frappe.get_doc("Customer", {"name": self.linked_customer})

                return linked_customer.name

            territory = "India"
            if hasattr(self, "district") and self.district:
                district_territory = frappe.db.get_value("District", self.district, "territory")
                if district_territory:
                    territory = district_territory
                else:
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

                new_address.append(
                    "links",
                    {
                        "link_doctype": "Customer",
                        "link_name": customer.name,
                    },
                )

                new_address.flags.ignore_permissions = True
                new_address.insert()

            return customer.name

        except Exception as e:
            frappe.log_error(str(e), "Customer Creation Error")
            frappe.throw(str(e))


@frappe.whitelist()
def get_channel_partner_data_from_project(project_id):
    project = frappe.get_doc("Project", project_id)

    return project.custom_channel_partner if project.custom_channel_partner else None
