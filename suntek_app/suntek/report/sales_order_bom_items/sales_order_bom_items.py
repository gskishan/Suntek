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

    warehouse = filters.get("warehouse") or "Hyderabad New Warehouse TGIIC - SESP"
    filters["warehouse"] = warehouse

    create_work_order_temp_table(filters)

    query = """
        SELECT /*+ MAX_EXECUTION_TIME(300000) */
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
            
            temp_wo.name as work_order,
            temp_wo.status as work_order_status,
            
            IFNULL(temp_wo.transferred_qty, 0) as transferred_qty,
            IFNULL(temp_wo.consumed_qty, 0) as consumed_qty
             
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
        LEFT JOIN
            `_temp_work_orders` temp_wo ON 
            (temp_wo.bom_no = soi.bom_no OR temp_wo.production_item = soi.item_code)
            AND (temp_wo.sales_order = so.name OR temp_wo.project = so.project)
            AND temp_wo.raw_material = bom_item.item_code
        WHERE 
            so.docstatus = 1
            {conditions}
        ORDER BY 
            so.name, soi.idx, bom_item.idx
    """.format(conditions=conditions)

    try:
        if not filters.get("sales_order") and not filters.get("limit_results"):
            frappe.msgprint(
                "Limiting results to 500 rows. Use filters to narrow your search or enable 'Show All Results'."
            )
            query += " LIMIT 500"
        elif filters.get("limit_results") == 0:
            query += " LIMIT 500"

        results = frappe.db.sql(query, filters, as_dict=1)

        frappe.db.sql("DROP TEMPORARY TABLE IF EXISTS `_temp_work_orders`")

        return results
    except Exception as e:
        frappe.db.sql("DROP TEMPORARY TABLE IF EXISTS `_temp_work_orders`")
        frappe.log_error(frappe.get_traceback(), f"Report Error: {str(e)}")
        return []


def create_work_order_temp_table(filters):
    """Create a temporary table with work orders and their consumed/transferred quantities"""
    try:
        frappe.db.sql("DROP TEMPORARY TABLE IF EXISTS `_temp_work_orders`")

        frappe.db.sql("""
            CREATE TEMPORARY TABLE `_temp_work_orders` (
                `name` varchar(140),
                `sales_order` varchar(140),
                `bom_no` varchar(140),
                `production_item` varchar(140),
                `project` varchar(140),
                `status` varchar(140),
                `raw_material` varchar(140),
                `transferred_qty` decimal(18,6),
                `consumed_qty` decimal(18,6),
                INDEX idx_name (`name`),
                INDEX idx_sales_order (`sales_order`),
                INDEX idx_bom (`bom_no`),
                INDEX idx_item (`production_item`),
                INDEX idx_raw_material (`raw_material`)
            )
        """)

        so_condition = ""
        so_params = []

        if filters.get("sales_order"):
            so_condition = "AND wo.sales_order = %s"
            so_params.append(filters.get("sales_order"))
        elif filters.get("from_date") and filters.get("to_date"):
            so_condition = """AND wo.sales_order IN (
                SELECT name FROM `tabSales Order`
                WHERE transaction_date BETWEEN %s AND %s
                AND docstatus = 1
            )"""
            so_params.extend([filters.get("from_date"), filters.get("to_date")])

        work_orders = frappe.db.sql(
            f"""
            SELECT 
                wo.name, wo.sales_order, wo.bom_no, wo.production_item, 
                wo.project, wo.status
            FROM 
                `tabWork Order` wo
            WHERE 
                wo.docstatus = 1
                {so_condition}
        """,
            so_params,
            as_dict=1,
        )

        if not work_orders:
            return

        wo_names = [wo["name"] for wo in work_orders]

        stock_entries = frappe.db.sql(
            """
            SELECT 
                se.work_order,
                sed.item_code as raw_material,
                SUM(CASE WHEN se.stock_entry_type = 'Material Transfer for Manufacture' THEN sed.qty ELSE 0 END) as transferred_qty,
                SUM(CASE WHEN se.stock_entry_type = 'Manufacture' THEN sed.qty ELSE 0 END) as consumed_qty
            FROM 
                `tabStock Entry Detail` sed
            JOIN 
                `tabStock Entry` se ON se.name = sed.parent
            WHERE 
                se.work_order IN %s
                AND se.docstatus = 1
            GROUP BY 
                se.work_order, sed.item_code
        """,
            [wo_names],
            as_dict=1,
        )

        stock_entry_data = {}
        for entry in stock_entries:
            key = (entry["work_order"], entry["raw_material"])
            stock_entry_data[key] = {
                "transferred_qty": entry["transferred_qty"] or 0,
                "consumed_qty": entry["consumed_qty"] or 0,
            }

        insert_data = []
        for wo in work_orders:
            bom_items = []
            if wo["bom_no"]:
                bom_items = frappe.db.sql(
                    """
                    SELECT item_code FROM `tabBOM Item` 
                    WHERE parent = %s
                """,
                    wo["bom_no"],
                    as_dict=1,
                )

            for bom_item in bom_items:
                raw_material = bom_item["item_code"]
                key = (wo["name"], raw_material)
                quantities = stock_entry_data.get(
                    key, {"transferred_qty": 0, "consumed_qty": 0}
                )

                insert_data.append(
                    (
                        wo["name"],
                        wo["sales_order"],
                        wo["bom_no"],
                        wo["production_item"],
                        wo["project"],
                        wo["status"],
                        raw_material,
                        quantities["transferred_qty"],
                        quantities["consumed_qty"],
                    )
                )

        batch_size = 1000
        for i in range(0, len(insert_data), batch_size):
            batch = insert_data[i : i + batch_size]
            if batch:
                frappe.db.sql(
                    """
                    INSERT INTO `_temp_work_orders`
                    (`name`, `sales_order`, `bom_no`, `production_item`, 
                    `project`, `status`, `raw_material`, `transferred_qty`, `consumed_qty`)
                    VALUES %s
                """
                    % (", ".join(["%s"] * len(batch))),
                    [item for sublist in batch for item in sublist],
                )

    except Exception as e:
        frappe.db.sql("DROP TEMPORARY TABLE IF EXISTS `_temp_work_orders`")
        frappe.log_error(frappe.get_traceback(), f"Temp table creation error: {str(e)}")


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


@frappe.whitelist()
def export_data(filters):
    if isinstance(filters, str):
        filters = json.loads(filters)

    filters["limit_results"] = 1

    raw_data = get_data(filters)
    data = process_data_for_display(raw_data)
    return data
