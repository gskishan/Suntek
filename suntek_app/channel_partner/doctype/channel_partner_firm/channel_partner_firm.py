import frappe
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.document import Document

from suntek_app.suntek.utils.validation_utils import validate_pan_number


class ChannelPartnerFirm(Document):
    """Channel Partner Firm represents a company or business entity that has channel partners."""

    def autoname(self):
        """Autoname CP Firm in format CP-FIRM-00000"""
        from frappe.model.naming import make_autoname

        self.name = make_autoname("CP-FIRM-.#####")

    def onload(self):
        """Load address and contact info when the document loads"""
        load_address_and_contact(self)

    def validate(self):
        """Validate document before saving"""
        self.validate_duplicate_firm_name()

        validate_pan_number(self.pan_number)

    def on_update(self):
        self.update_channel_partner_details()
        self.set_address_display()

    def is_active(self):
        """Check if the firm is active"""
        return self.status == "Active"

    def set_address_display(self):
        if self.address:
            address = frappe.get_doc("Address", self.address)

            address_line1 = address.address_line1 or ""
            address_line2 = address.address_line2 or ""
            city = address.city or ""
            state = address.state or ""
            country = address.country or ""
            pincode = address.pincode or ""
            self.address_display = f"{address_line1} \n{address_line2} \n{city} \n{state} \n{country} \n{pincode}"

    def validate_duplicate_firm_name(self):
        """Check for duplicate firm names and warn the user"""
        if self.firm_name:
            duplicate_firms = frappe.get_all(
                "Channel Partner Firm",
                filters={
                    "firm_name": self.firm_name,
                    "name": ("!=", self.name if not self.is_new() else ""),
                },
                fields=["name"],
            )

            if duplicate_firms:
                duplicate_info = ", ".join([d.name for d in duplicate_firms])
                frappe.msgprint(
                    f"Warning: Firms with similar names already exist: {duplicate_info}",
                    title="Possible Duplicate Firm",
                    indicator="orange",
                )

    def update_channel_partner_details(self):
        channel_partners = frappe.get_all("Channel Partner", filters={"channel_partner_firm": self.name})

        customer = frappe.get_doc("Customer", self.customer) if self.customer else None

        for channel_partner in channel_partners:
            channel_partner_doc = frappe.get_doc("Channel Partner", channel_partner.name)
            updated = False

            if customer and not channel_partner_doc.channel_partner_customer:
                channel_partner_doc.channel_partner_customer = customer.name
                updated = True

            if self.selling_price_list and not channel_partner_doc.default_selling_list:
                channel_partner_doc.default_selling_list = self.selling_price_list
                updated = True

            if updated:
                channel_partner_doc.flags.ignore_mandatory = True
                channel_partner_doc.save(ignore_permissions=True)

                frappe.db.commit()

    def _set_customer_in_channel_partners(self):
        customer = frappe.get_doc("Customer", self.customer) if self.customer else None
        if customer:
            channel_partners = frappe.get_all("Channel Partner", filters={"channel_partner_firm": self.name})
            for channel_partner in channel_partners:
                channel_partner_doc = frappe.get_doc("Channel Partner", channel_partner.name)
                if not channel_partner_doc.channel_partner_customer:
                    channel_partner_doc.channel_partner_customer = customer.name

                    channel_partner_doc.flags.ignore_mandatory = True
                    channel_partner_doc.save(ignore_permissions=True)

    @frappe.whitelist()
    def create_sales_partner(self):
        try:
            territory = self.territory if self.territory else "India"

            sales_partner = frappe.new_doc("Sales Partner")

            sales_partner.update(
                {
                    "partner_name": self.firm_name,
                    "partner_type": "Channel Partner"
                    if frappe.db.exists("Sales Partner Type", "Channel Partner")
                    else None,
                    "commission_rate": self.commission_rate,
                    "territory": territory,
                }
            )

            sales_partner.flags.ignore_permissions = True
            sales_partner.insert()

            self.db_set("linked_sales_partner", sales_partner.name)

            frappe.db.commit()

            frappe.msgprint(f"Sales Partner created successfully: {sales_partner.name}")
            return sales_partner.name

        except Exception as e:
            frappe.log_error(
                title="Sales Partner Creation Error",
                message=str(e),
                reference_doctype="Channel Partner Firm",
                reference_name=self.name,
            )

    @frappe.whitelist()
    def get_channel_partners(self):
        """Fetch all channel partners associated with this firm"""
        return frappe.get_all(
            "Channel Partner",
            filters={"channel_partner_firm": self.name},
            fields=[
                "name",
                "channel_partner_name",
                "mobile_number",
                "status",
                "linked_user",
            ],
        )

    @frappe.whitelist()
    def create_address(self, address_data):
        """Create an address linked to this firm"""
        try:
            address = frappe.new_doc("Address")
            address.update(address_data)

            address.append(
                "links",
                {"link_doctype": "Channel Partner Firm", "link_name": self.name},
            )

            address.insert(ignore_permissions=True)
            return address.name
        except Exception as e:
            frappe.log_error(f"Failed to create address for firm {self.name}: {str(e)}")
            frappe.throw(str(e))

    @frappe.whitelist()
    def create_contact(self, contact_data):
        """Create a contact linked to this firm"""
        try:
            contact = frappe.new_doc("Contact")
            contact.update(contact_data)

            contact.append(
                "links",
                {"link_doctype": "Channel Partner Firm", "link_name": self.name},
            )

            contact.insert(ignore_permissions=True)
            return contact.name
        except Exception as e:
            frappe.log_error(f"Failed to create contact for firm {self.name}: {str(e)}")
            frappe.throw(str(e))
