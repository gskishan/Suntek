
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

        raw_material_qty = row.get("raw_material_qty") or 0
        order_qty = row.get("order_qty") or 0
        required_qty = raw_material_qty * order_qty
        curr_row["required_qty"] = required_qty

        available_qty = row.get("available_qty") or 0
        shortage_qty = available_qty - required_qty
        curr_row["shortage_surplus"] = shortage_qty

        if shortage_qty < 0:
            curr_row["status"] = "Shortage"
        elif shortage_qty == 0 and required_qty > 0:
            curr_row["status"] = "Exact"
        elif required_qty == 0:
            curr_row["status"] = "No Requirement"
        else:
            curr_row["status"] = "Surplus"

        if previous_so and row["sales_order_no"] == previous_so:
            curr_row["sales_order_no"] = ""
            curr_row["customer"] = ""
            curr_row["project"] = ""
            curr_row["custom_department"] = ""
            curr_row["delivery_date"] = ""
            curr_row["delivery_status"] = ""
            curr_row["billing_status"] = ""

            if previous_item and row["finished_item_code"] == previous_item:
                curr_row["finished_item_code"] = ""
                curr_row["finished_item_name"] = ""
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
            "fieldtype": "Link",
            "options": "Department",
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
            "label": _("Warehouse"),
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
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
            "label": _("Is Semi-Finished Good"),
            "fieldname": "is_sfg",
            "fieldtype": "Check",
            "width": 130,
        },
        {
            "label": _("Required Qty"),
            "fieldname": "required_qty",
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
            "label": _("Available Qty"),
            "fieldname": "available_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Shortage/Surplus"),
            "fieldname": "shortage_surplus",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "label": _("Transferred Qty"),
            "fieldname": "transferred_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Consumed Qty"),
            "fieldname": "consumed_qty",
            "fieldtype": "Float",
            "width": 120,
        },
        {
            "label": _("Work Order"),
            "fieldname": "work_order",
            "fieldtype": "Link",
            "options": "Work Order",
            "width": 130,
        },
        {
            "label": _("Work Order Status"),
            "fieldname": "work_order_status",
            "fieldtype": "Data",
            "width": 140,
        },
    ]


@frappe.whitelist()
def get_data(filters):
    if isinstance(filters, str):
        filters = json.loads(filters)
    return get_data_internal(filters)


def get_data_internal(filters):
    conditions = get_conditions(filters)

    warehouse = filters.get("warehouse") or "Hyderabad Central Warehouse - SESP"
    filters["warehouse"] = warehouse

    if filters.get("sales_order"):
        sales_order = filters.get("sales_order")

        work_orders_count = frappe.db.count(
            "Work Order", {"sales_order": sales_order, "docstatus": 1}
        )

        frappe.log_error(
            f"Direct Work Orders for SO {sales_order}: {work_orders_count}",
            "WO-Count-Debug",
        )

        boms_in_so = frappe.db.sql(
            """
            SELECT soi.bom_no, soi.item_code
            FROM `tabSales Order Item` soi
            WHERE soi.parent = %s AND soi.bom_no IS NOT NULL
            """,
            sales_order,
            as_dict=1,
        )

        bom_count = len(boms_in_so)
        frappe.log_error(
            f"SO {sales_order} has {bom_count} BOM items", "BOM-Count-Debug"
        )

        if bom_count > 0:
            for i, bom in enumerate(boms_in_so):
                if i < 3:
                    frappe.log_error(
                        f"BOM {i + 1}: {bom.bom_no}, Item: {bom.item_code}",
                        f"BOM-Detail-{i + 1}",
                    )

                    wo_count = frappe.db.count(
                        "Work Order", {"bom_no": bom.bom_no, "docstatus": 1}
                    )

                    frappe.log_error(
                        f"Found {wo_count} work orders for BOM {bom.bom_no}",
                        f"WO-BOM-Count-{i + 1}",
                    )

                    if wo_count > 0:
                        sample_wo = frappe.get_list(
                            "Work Order",
                            filters={"bom_no": bom.bom_no, "docstatus": 1},
                            fields=["name", "sales_order", "status"],
                            limit=1,
                        )
                        if sample_wo:
                            frappe.log_error(
                                f"Sample WO: {sample_wo[0].name}, SO: {sample_wo[0].sales_order}",
                                f"WO-Detail-{i + 1}",
                            )

    query = f"""
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
            bom_item.uom as raw_material_uom,
            bin.actual_qty as available_qty,
            bin.warehouse as warehouse,
            raw_item.custom_is_sfg as is_sfg,
            
            /* Use a subquery to find the most relevant work order */
            (SELECT wo.name 
             FROM `tabWork Order` wo 
             WHERE (wo.bom_no = soi.bom_no OR wo.production_item = soi.item_code)
             AND (wo.sales_order = so.name OR wo.project = so.project)
             AND wo.docstatus = 1
             LIMIT 1) as work_order,
             
            /* Get the work order status */
            (SELECT wo.status
             FROM `tabWork Order` wo 
             WHERE (wo.bom_no = soi.bom_no OR wo.production_item = soi.item_code)
             AND (wo.sales_order = so.name OR wo.project = so.project)
             AND wo.docstatus = 1
             LIMIT 1) as work_order_status,
             
            /* Calculate transferred quantity */
            (SELECT IFNULL(SUM(sed.qty), 0)
             FROM `tabStock Entry Detail` sed
             JOIN `tabStock Entry` se ON se.name = sed.parent
             JOIN `tabWork Order` wo ON se.work_order = wo.name 
             WHERE (wo.bom_no = soi.bom_no OR wo.production_item = soi.item_code)
             AND (wo.sales_order = so.name OR wo.project = so.project)
             AND sed.item_code = bom_item.item_code
             AND se.docstatus = 1
             AND se.stock_entry_type = 'Material Transfer for Manufacture'
            ) as transferred_qty,
             
            /* Calculate consumed quantity */
            (SELECT IFNULL(SUM(sed.qty), 0)
             FROM `tabStock Entry Detail` sed
             JOIN `tabStock Entry` se ON se.name = sed.parent
             JOIN `tabWork Order` wo ON se.work_order = wo.name 
             WHERE (wo.bom_no = soi.bom_no OR wo.production_item = soi.item_code)
             AND (wo.sales_order = so.name OR wo.project = so.project)
             AND sed.item_code = bom_item.item_code
             AND se.docstatus = 1
             AND se.stock_entry_type = 'Manufacture'
            ) as consumed_qty
             
        FROM 
            `tabSales Order` so
        INNER JOIN 
            `tabSales Order Item` soi ON so.name = soi.parent
        LEFT JOIN 
            `tabBOM Item` bom_item ON soi.bom_no = bom_item.parent
        LEFT JOIN
            `tabBin` bin ON bom_item.item_code = bin.item_code
            AND bin.warehouse = %(warehouse)s
        LEFT JOIN
            `tabItem` raw_item ON bom_item.item_code = raw_item.name
        WHERE 
            so.docstatus = 1
            {conditions}
        ORDER BY 
            so.name, soi.idx, bom_item.idx
    """

    try:
        results = frappe.db.sql(query, filters, as_dict=1)

        work_order_count = sum(1 for row in results if row.get("work_order"))
        total_rows = len(results)

        frappe.log_error(
            f"Results: {total_rows} rows, {work_order_count} with work orders",
            "Report-WO-Summary",
        )

        if results and work_order_count > 0:
            for row in results[:3]:
                if row.get("work_order"):
                    frappe.log_error(
                        f"WO: {row.get('work_order')}, Item: {row.get('raw_material_code')}, "
                        f"Req: {row.get('required_qty')}, Trans: {row.get('transferred_qty')}, "
                        f"Cons: {row.get('consumed_qty')}",
                        "Material-Movement-Sample",
                    )
                    break

        return results
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), f"Report Error: {str(e)}")
        return []


def get_conditions(filters):
    conditions = []
    if filters.get("from_date"):
        conditions.append("so.transaction_date >= %(from_date)s")
    if filters.get("to_date"):
        conditions.append("so.transaction_date <= %(to_date)s")
    if filters.get("sales_order"):
        conditions.append("so.name = %(sales_order)s")
    if filters.get("custom_department"):
        conditions.append("so.custom_department = %(custom_department)s")
    if filters.get("delivery_status"):
        conditions.append("so.delivery_status = %(delivery_status)s")
    if filters.get("billing_status"):
        conditions.append("so.billing_status = %(billing_status)s")
    if filters.get("order_type"):
        conditions.append("so.order_type = %(order_type)s")

    return " AND " + " AND ".join(conditions) if conditions else ""
