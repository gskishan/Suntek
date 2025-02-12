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
    data = get_data(filters)
    return columns, data


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
    ]


def get_data(filters):
    conditions = get_conditions(filters)

    query = """
        SELECT 
            so.name as sales_order_no,
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

    return " AND " + " AND ".join(conditions) if conditions else ""
