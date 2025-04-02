"""Test the test setup functions."""

import unittest

import frappe

from .create_test_data import (
    create_channel_partner,
    create_channel_partner_firm,
    create_channel_partner_firm_with_attachments,
    create_channel_partner_firm_with_sales_partner,
)


class TestSetupFunctions(unittest.TestCase):
    """Test the test setup functions."""

    def tearDown(self):
        """Clean up after each test."""
        frappe.db.delete("Channel Partner", {"channel_partner_name": "_Test Channel Partner 001"})
        frappe.db.delete("Channel Partner Firm", {"firm_name": "_Test Firm 001"})
        frappe.db.delete("Sales Partner", {"partner_name": "_Test Firm 001"})
        frappe.db.delete("Customer", {"customer_name": "_Test Firm 001"})
        frappe.db.delete("User", {"first_name": "_Test Channel Partner 001"})
        frappe.db.delete("Warehouse", {"warehouse_name": "CP-_Test Channel Partner 001-Sales - SESP"})
        frappe.db.delete("Warehouse", {"warehouse_name": "CP-_Test Channel Partner 001-Subsidy - SESP"})
        frappe.db.commit()

    def test_create_channel_partner_firm(self):
        """Test creating a channel partner firm."""
        firm = create_channel_partner_firm("_Test Firm 001")
        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.address)
        self.assertIsNotNone(firm.contact_person)
        self.assertIsNotNone(firm.customer)

    def test_create_channel_partner_firm_with_attachments(self):
        """Test creating a channel partner firm with attachments."""
        firm = create_channel_partner_firm_with_attachments("_Test Firm 001")
        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.business_registration)
        self.assertIsNotNone(firm.agreement)
        self.assertIsNotNone(firm.noc_for_stock)
        self.assertIsNotNone(firm.address_proof)

    def test_create_channel_partner_firm_with_sales_partner(self):
        """Test creating a channel partner firm with a sales partner."""
        firm = create_channel_partner_firm_with_sales_partner("_Test Firm 001", 10.0, "India")
        self.assertEqual(firm.firm_name, "_Test Firm 001")
        self.assertIsNotNone(firm.linked_sales_partner)
        sales_partner = frappe.get_doc("Sales Partner", firm.linked_sales_partner)
        self.assertEqual(sales_partner.commission_rate, 10.0)

    def test_create_channel_partner(self):
        """Test creating a channel partner."""
        channel_partner = create_channel_partner("_Test Channel Partner 001", fill_mandatory=True)
        self.assertEqual(channel_partner.channel_partner_name, "_Test Channel Partner 001")
        self.assertEqual(channel_partner.status, "Pending Approval")
        self.assertIsNotNone(channel_partner.channel_partner_firm)
        self.assertIsNotNone(channel_partner.contact)
        self.assertIsNotNone(channel_partner.channel_partner_address)
