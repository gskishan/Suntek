import frappe
from frappe.exceptions import ValidationError
from frappe.tests.utils import FrappeTestCase

from suntek_app.channel_partner.test_setup.create_test_data import (
    create_channel_partner_firm,
    create_channel_partner_firm_with_attachments,
    create_channel_partner_firm_with_sales_partner,
)


class TestChannelPartnerFirm(FrappeTestCase):
    def tearDown(self):
        frappe.db.delete("Channel Partner Firm", {"firm_name": "_Test Firm 001"})
        frappe.db.delete("Sales Partner", {"partner_name": "_Test Firm 001"})
        frappe.db.commit()

    def test_channel_partner_firm_creation(self):
        firm = create_channel_partner_firm("_Test Firm 001")

        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.address)
        self.assertIsNotNone(firm.contact_person)
        self.assertIsNotNone(firm.customer)

    def test_channel_partner_firm_with_attachments(self):
        firm = create_channel_partner_firm_with_attachments("_Test Firm 001")

        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.address)
        self.assertIsNotNone(firm.contact_person)
        self.assertIsNotNone(firm.customer)
        self.assertIsNotNone(firm.business_registration)
        self.assertIsNotNone(firm.agreement)
        self.assertIsNotNone(firm.noc_for_stock)
        self.assertIsNotNone(firm.address_proof)

    def test_channel_partner_firm_mandatory_fields_missing(self):
        with self.assertRaises(ValidationError):
            firm = frappe.get_doc(
                {
                    "doctype": "Channel Partner Firm",
                    "firm_name": "_Test Firm 001",
                    "status": "Active",
                }
            )
            firm.insert()

    def test_channel_partner_firm_mandatory_fields_filled(self):
        firm = create_channel_partner_firm_with_attachments("_Test Firm 001", status="Active")
        self.assertEqual(firm.status, "Active")
        self.assertIsNotNone(firm.business_registration)
        self.assertIsNotNone(firm.agreement)
        self.assertIsNotNone(firm.noc_for_stock)
        self.assertIsNotNone(firm.address_proof)
        self.assertIsNotNone(firm.commission_rate)
        self.assertIsNotNone(firm.customer)
        self.assertIsNotNone(firm.contact_person)

    def test_channel_partner_firm_with_sales_partner(self):
        firm = create_channel_partner_firm_with_sales_partner("_Test Firm 001", 10.0, "India")

        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.address)
        self.assertIsNotNone(firm.contact_person)
        self.assertIsNotNone(firm.customer)
        self.assertIsNotNone(firm.linked_sales_partner)

        sales_partner = frappe.get_doc("Sales Partner", firm.linked_sales_partner)
        self.assertEqual(sales_partner.commission_rate, 10.0)
