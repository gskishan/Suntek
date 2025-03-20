import frappe
from frappe.contacts.address_and_contact import load_address_and_contact
from frappe.model.document import Document


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

            # Add a dynamic link to this firm
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

            # Add a dynamic link to this firm
            contact.append(
                "links",
                {"link_doctype": "Channel Partner Firm", "link_name": self.name},
            )

            contact.insert(ignore_permissions=True)
            return contact.name
        except Exception as e:
            frappe.log_error(f"Failed to create contact for firm {self.name}: {str(e)}")
            frappe.throw(str(e))
