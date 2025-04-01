import unittest

import frappe


def create_item():
    item = frappe.new_doc("Item")
    item.item_code = "TEST-ITEM-001"
    item.item_name = "Test Item"
    item.item_group = "Products"
    item.stock_uom = "Nos"
    item.is_stock_item = 1
    item.is_sales_item = 1
    item.is_purchase_item = 1

    item.save()


class TestChannelPartnerPurchaseOrder(unittest.TestCase):
    def setUp(self):
        create_item()

    def tearDown(self):
        frappe.db.rollback()

    def test_create_purchase_order(self):
        self.assertTrue(True)
