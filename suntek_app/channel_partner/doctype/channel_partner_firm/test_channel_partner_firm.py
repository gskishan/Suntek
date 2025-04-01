import unittest

import frappe

from suntek_app.channel_partner.doctype.channel_partner_firm.channel_partner_firm import ChannelPartnerFirm
from suntek_app.suntek.utils.validation_utils import validate_mobile_number, validate_pan_number


class TestChannelPartnerFirm(unittest.TestCase):
    def setUp(self):
        self.test_firm_data = {
            "doctype": "Channel Partner Firm",
            "firm_name": "_Test CP Firm",
            "status": "Active",
            "pan_number": "ABCDE1234F",
        }

    def tearDown(self):
        frappe.db.rollback()

    def test_pass(self):
        self.assertTrue(True)

    def test_pan_validation(self):
        validate_pan_number("ABCDE1234F")

        with self.assertRaises(frappe.exceptions.ValidationError):
            validate_pan_number("INVALID")

    def test_mobile_validation(self):
        self.assertTrue(validate_mobile_number("9876543210"))
        self.assertTrue(validate_mobile_number("+919876543210"))
        self.assertTrue(validate_mobile_number("+91-9876543210"))

        self.assertFalse(validate_mobile_number("987654321"))
        self.assertFalse(validate_mobile_number("98765432100"))
        self.assertFalse(validate_mobile_number("5876543210"))
        self.assertFalse(validate_mobile_number("987654 3210"))

    def test_is_active_method(self):
        firm = ChannelPartnerFirm(self.test_firm_data)
        self.assertTrue(firm.is_active())

        firm.status = "Inactive"
        self.assertFalse(firm.is_active())

        firm.status = "Pending Approval"
        self.assertFalse(firm.is_active())

    def test_autoname_format(self):
        firm = ChannelPartnerFirm(self.test_firm_data)

        self.assertTrue(hasattr(firm, "autoname"))

    def test_duplicate_firm_name_warning(self):
        firm = ChannelPartnerFirm(self.test_firm_data)

        class MockDoc:
            def __init__(self, name):
                self.name = name

        original_get_all = frappe.get_all
        original_msgprint = frappe.msgprint

        try:

            def mock_get_all(*args, **kwargs):
                if args[0] == "Channel Partner Firm" and kwargs.get("filters", {}).get("firm_name") == "_Test CP Firm":
                    return [MockDoc("CP-FIRM-00001")]
                return original_get_all(*args, **kwargs)

            msgprint_called = [False]

            def mock_msgprint(*args, **kwargs):
                msgprint_called[0] = True
                return None

            frappe.get_all = mock_get_all
            frappe.msgprint = mock_msgprint

            firm.validate_duplicate_firm_name()

            self.assertTrue(msgprint_called[0], "Warning message for duplicate firm name not shown")

        finally:
            frappe.get_all = original_get_all
            frappe.msgprint = original_msgprint

    def test_set_address_display(self):
        firm = ChannelPartnerFirm(self.test_firm_data)

        firm.address = "TEST-ADDRESS-001"

        class MockAddress:
            def __init__(self):
                self.address_line1 = "123 Test Street"
                self.address_line2 = "Test Area"
                self.city = "Test City"
                self.state = "Test State"
                self.country = "Test Country"
                self.pincode = "123456"

        original_get_doc = frappe.get_doc

        try:

            def mock_get_doc(doctype, name):
                if doctype == "Address" and name == "TEST-ADDRESS-001":
                    return MockAddress()
                return original_get_doc(doctype, name)

            frappe.get_doc = mock_get_doc

            firm.set_address_display()

            expected_display = "123 Test Street \nTest Area \nTest City \nTest State \nTest Country \n123456"
            self.assertEqual(firm.address_display, expected_display)

        finally:
            frappe.get_doc = original_get_doc

    def test_update_channel_partner_details(self):
        class MockChannelPartner:
            def __init__(self, name):
                self.name = name
                self.channel_partner_customer = None
                self.default_selling_list = None
                self.flags = frappe._dict()
                self.save_called = False

            def save(self, ignore_permissions=False):
                self.save_called = True

        class MockCustomer:
            def __init__(self):
                self.name = "TEST-CUSTOMER-001"
                self.customer_name = "Test Customer"

        firm = ChannelPartnerFirm(self.test_firm_data)
        firm.name = "TEST-CP-FIRM-001"
        firm.selling_price_list = "Standard Selling"
        firm.customer = "TEST-CUSTOMER-001"

        test_cp_1 = MockChannelPartner("TEST-CP-001")
        test_cp_2 = MockChannelPartner("TEST-CP-002")

        mock_objects = {
            "Customer": {"TEST-CUSTOMER-001": MockCustomer()},
            "Channel Partner": {"TEST-CP-001": test_cp_1, "TEST-CP-002": test_cp_2},
        }

        original_get_all = frappe.get_all
        original_get_doc = frappe.get_doc
        original_db_commit = frappe.db.commit

        try:

            def mock_get_all(*args, **kwargs):
                if (
                    args[0] == "Channel Partner"
                    and kwargs.get("filters", {}).get("channel_partner_firm") == "TEST-CP-FIRM-001"
                ):

                    class MockDict:
                        def __init__(self, name):
                            self.name = name

                    return [MockDict("TEST-CP-001"), MockDict("TEST-CP-002")]
                return original_get_all(*args, **kwargs)

            def mock_get_doc(doctype, name):
                if doctype in mock_objects and name in mock_objects[doctype]:
                    return mock_objects[doctype][name]
                return original_get_doc(doctype, name)

            def mock_db_commit():
                pass

            frappe.get_all = mock_get_all
            frappe.get_doc = mock_get_doc
            frappe.db.commit = mock_db_commit

            firm.update_channel_partner_details()

            self.assertTrue(test_cp_1.save_called, "First partner was not saved")
            self.assertTrue(test_cp_2.save_called, "Second partner was not saved")

            self.assertEqual(test_cp_1.channel_partner_customer, "TEST-CUSTOMER-001")
            self.assertEqual(test_cp_1.default_selling_list, "Standard Selling")
            self.assertEqual(test_cp_2.channel_partner_customer, "TEST-CUSTOMER-001")
            self.assertEqual(test_cp_2.default_selling_list, "Standard Selling")

        finally:
            frappe.get_all = original_get_all
            frappe.get_doc = original_get_doc
            frappe.db.commit = original_db_commit

    def test_create_sales_partner_method(self):
        firm = ChannelPartnerFirm(self.test_firm_data)
        firm.name = "TEST-CP-FIRM-001"
        firm.firm_name = "_Test CP Firm"
        firm.commission_rate = 10.0
        firm.territory = "Test Territory"

        class MockSalesPartner:
            def __init__(self):
                self.name = "SP-TEST-001"
                self.flags = frappe._dict()
                self.update_called = False
                self.partner_name = None
                self.partner_type = None
                self.commission_rate = None
                self.territory = None

            def update(self, data):
                for key, value in data.items():
                    setattr(self, key, value)
                self.update_called = True

            def insert(self):
                pass

        original_new_doc = frappe.new_doc
        original_db_exists = frappe.db.exists
        original_db_commit = frappe.db.commit
        original_msgprint = frappe.msgprint
        original_log_error = frappe.log_error

        try:
            sales_partner = MockSalesPartner()

            def mock_new_doc(doctype):
                if doctype == "Sales Partner":
                    return sales_partner
                return original_new_doc(doctype)

            def mock_db_exists(doctype, filters):
                if doctype == "Sales Partner Type" and filters == "Channel Partner":
                    return True
                return False

            def mock_db_commit():
                pass

            msgprint_called = [False]

            def mock_msgprint(*args, **kwargs):
                msgprint_called[0] = True

            def mock_log_error(*args, **kwargs):
                pass

            frappe.new_doc = mock_new_doc
            frappe.db.exists = mock_db_exists
            frappe.db.commit = mock_db_commit
            frappe.msgprint = mock_msgprint
            frappe.log_error = mock_log_error

            original_db_set = getattr(firm, "db_set", None)
            firm.db_set = lambda field, value: setattr(firm, field, value)

            result = firm.create_sales_partner()

            self.assertEqual(result, "SP-TEST-001")
            self.assertEqual(firm.linked_sales_partner, "SP-TEST-001")
            self.assertTrue(msgprint_called[0])

            self.assertTrue(sales_partner.update_called)
            self.assertEqual(sales_partner.partner_name, "_Test CP Firm")
            self.assertEqual(sales_partner.partner_type, "Channel Partner")
            self.assertEqual(sales_partner.commission_rate, 10.0)
            self.assertEqual(sales_partner.territory, "Test Territory")

        finally:
            frappe.new_doc = original_new_doc
            frappe.db.exists = original_db_exists
            frappe.db.commit = original_db_commit
            frappe.msgprint = original_msgprint
            frappe.log_error = original_log_error
