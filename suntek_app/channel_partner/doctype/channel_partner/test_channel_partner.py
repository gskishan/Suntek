import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from suntek_app.channel_partner.test_setup.create_test_data import create_channel_partner


class TestChannelPartner(FrappeTestCase):
    def setUp(self):
        if not frappe.db.exists("Role", "Channel Partner"):
            role = frappe.new_doc("Role")
            role.role_name = "Channel Partner"
            role.desk_access = 1
            role.save(ignore_permissions=True)
            frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("Channel Partner", {"channel_partner_name": "_Test Channel Partner 001"})
        frappe.db.delete("User", {"first_name": "_Test Channel Partner 001"})
        frappe.db.delete("Warehouse", {"warehouse_name": "CP-_Test Channel Partner 001-Sales - SESP"})
        frappe.db.delete("Warehouse", {"warehouse_name": "CP-_Test Channel Partner 001-Subsidy - SESP"})
        frappe.db.commit()

    def test_channel_partner_creation(self):
        channel_partner = create_channel_partner("_Test Channel Partner 001", fill_mandatory=True)
        self.assertEqual(channel_partner.channel_partner_name, "_Test Channel Partner 001")
        self.assertEqual(channel_partner.status, "Pending Approval")
        self.assertIsNotNone(channel_partner.channel_partner_firm)
        self.assertIsNotNone(channel_partner.contact)
        self.assertIsNotNone(channel_partner.channel_partner_address)
        self.assertIsNotNone(channel_partner.district)
        self.assertIsNotNone(channel_partner.pan_number)
        self.assertIsNotNone(channel_partner.id_proof)
        self.assertIsNotNone(channel_partner.pan_card)
        self.assertIsNotNone(channel_partner.photograph)
        self.assertIsNotNone(channel_partner.electricity_bill)

    def test_channel_partner_mandatory_fields_missing(self):
        with self.assertRaises(ValidationError) as context:
            create_channel_partner("_Test Channel Partner 001", fill_mandatory=False)

        error_message = str(context.exception)
        self.assertIn("first_name", error_message)
        self.assertIn("email", error_message)
        self.assertIn("mobile_number", error_message)
        self.assertIn("contact", error_message)
        self.assertIn("channel_partner_address", error_message)
        self.assertIn("district", error_message)
        self.assertIn("pan_number", error_message)
        self.assertIn("id_proof", error_message)
        self.assertIn("pan_card", error_message)
        self.assertIn("photograph", error_message)
        self.assertIn("electricity_bill", error_message)

    def test_channel_partner_user_creation(self):
        channel_partner = create_channel_partner("_Test Channel Partner 001", fill_mandatory=True)
        frappe.db.commit()

        linked_user = channel_partner.create_user()
        frappe.db.commit()

        self.assertIsNotNone(linked_user)
        user = frappe.get_doc("User", linked_user)
        self.assertEqual(user.first_name, "_Test Channel Partner 001")
        self.assertEqual(user.email, "suntek.test@example.com")

        user_roles = frappe.get_all("Has Role", filters={"parent": linked_user}, fields=["role"])
        role_names = [r.role for r in user_roles]
        self.assertIn("Channel Partner", role_names)

        sales_warehouse = frappe.get_doc("Warehouse", channel_partner.default_sales_warehouse)
        self.assertEqual(sales_warehouse.warehouse_type, "Sales")
        self.assertEqual(sales_warehouse.company, "Suntek Energy Systems Pvt. Ltd.")

        subsidy_warehouse = frappe.get_doc("Warehouse", channel_partner.default_subsidy_warehouse)
        self.assertEqual(subsidy_warehouse.warehouse_type, "Subsidy")
        self.assertEqual(subsidy_warehouse.company, "Suntek Energy Systems Pvt. Ltd.")

        user_permissions = frappe.get_all(
            "User Permission", filters={"user": linked_user}, fields=["allow", "for_value", "apply_to_all_doctypes"]
        )

        permission_types = [p.allow for p in user_permissions]
        self.assertIn("User", permission_types)
        self.assertIn("Channel Partner", permission_types)
        self.assertIn("Warehouse", permission_types)
        self.assertIn("Department", permission_types)
        self.assertIn("Channel Partner Firm", permission_types)
