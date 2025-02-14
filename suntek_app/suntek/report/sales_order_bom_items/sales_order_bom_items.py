from __future__ import unicode_literals

import json

import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}
    if isinstance(filters, str):
        filters = json.loads(filters)
    columns = get_columns()
    raw_data = get_data(filters)
    data = process_data_for_display(raw_data)
    return columns, data


def process_data_for_display(raw_data):
    processed_data = []
    previous_so = None
    previous_item = None

    for row in raw_data:
        curr_row = row.copy()

        if previous_so and row["sales_order_no"] == previous_so:
            curr_row["sales_order_no"] = ""
            curr_row["customer"] = ""
            curr_row["project"] = ""
            curr_row["custom_department"] = ""
            curr_row["delivery_date"] = ""
            curr_row["delivery_status"] = ""
            curr_row["billing_status"] = ""
            curr_row["custom_remarks"] = ""

            if previous_item and row["finished_item_code"] == previous_item:
                curr_row["finished_item_code"] = ""
                curr_row["finished_item_name"] = ""
                curr_row["order_qty"] = ""
                curr_row["bom_no"] = ""

        processed_data.append(curr_row)
        previous_so = row["sales_order_no"]
        previous_item = row["finished_item_code"]

    return processed_data


def get_columns():
    return [
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order_no",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 130,
        },
        {
            "label": _("Customer"),
            "fieldname": "customer",
            "fieldtype": "Link",
            "options": "Customer",
            "width": 100,
        },
        {
            "label": _("Project ID"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 100,
        },
        {
            "label": _("Department"),
            "fieldname": "custom_department",
            "fieldtype": "Select",
            "options": "\nDomestic (Residential) Sales Team - SESP\nChannel Partner - SESP\nCommercial & Industrial (C&I) - SESP",
            "width": 150,
        },
        {
            "label": _("Dispatch Due Date"),
            "fieldname": "delivery_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": _("Delivery Status"),
            "fieldname": "delivery_status",
            "fieldtype": "Select",
            "options": "\nNot Delivered\nFully Delivered\nPartly Delivered\nClosed\nNot Applicable",
            "width": 140,
        },
        {
            "fieldname": "billing_status",
            "label": _("Billing Status"),
            "fieldtype": "Select",
            "options": "\nNot Billed\nFully Billed\nPartly Bileld\nClosed",
        },
        {
            "label": _("Finished Item Code"),
            "fieldname": "finished_item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 130,
        },
        {
            "label": _("Finished Item Name"),
            "fieldname": "finished_item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Order Qty"),
            "fieldname": "order_qty",
            "fieldtype": "Float",
            "width": 100,
        },
        {
            "label": _("BOM No"),
            "fieldname": "bom_no",
            "fieldtype": "Link",
            "options": "BOM",
            "width": 130,
        },
        {
            "label": _("Raw Material Code"),
            "fieldname": "raw_material_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 130,
        },
        {
            "label": _("Raw Material Name"),
            "fieldname": "raw_material_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Raw Material Qty"),
            "fieldname": "raw_material_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("UOM"),
            "fieldname": "raw_material_uom",
            "fieldtype": "Link",
            "options": "UOM",
            "width": 80,
        },
        {
            "label": _("Remarks"),
            "fieldname": "custom_remarks",
            "fieldtype": "Text Editor",
            "width": 200,
        },
    ]


@frappe.whitelist()
def get_data(filters):
    if isinstance(filters, str):
        filters = json.loads(filters)
    return get_data_internal(filters)


def get_data_internal(filters):
    conditions = get_conditions(filters)
    query = """
        SELECT 
            so.name as sales_order_no,
            so.customer,
            so.project,
            so.custom_department,
            so.delivery_date,
            so.delivery_status,
            so.billing_status,
            so.custom_remarks,
            soi.item_code as finished_item_code,
            soi.item_name as finished_item_name,
            soi.qty as order_qty,
            soi.bom_no,
            bom_item.item_code as raw_material_code,
            bom_item.item_name as raw_material_name,
            bom_item.qty as raw_material_qty,
            bom_item.uom as raw_material_uom
        FROM 
            `tabSales Order` so
        INNER JOIN 
            `tabSales Order Item` soi ON so.name = soi.parent
        LEFT JOIN 
            `tabBOM Item` bom_item ON soi.bom_no = bom_item.parent
        WHERE 
            so.docstatus = 1
            {conditions}
        ORDER BY 
            so.name, soi.idx, bom_item.idx
    """.format(conditions=conditions)

    try:
        return frappe.db.sql(query, filters, as_dict=1)
    except Exception as e:
        frappe.log_error(
            frappe.get_traceback(), f"Sales Order BOM Items Report Error: {str(e)}"
        )
        return []


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
    if filters.get("sales_order"):
        conditions.append("so.name = %(sales_order)s")
    if filters.get("delivery_status"):
        conditions.append("so.delivery_status = %(delivery_status)s")
    if filters.get("billing_status"):
        conditions.append("so.billing_status = %(billing_status)s")
    if filters.get("order_type"):
        conditions.append("so.order_type = %(order_type)s")

    return " AND " + " AND ".join(conditions) if conditions else ""
