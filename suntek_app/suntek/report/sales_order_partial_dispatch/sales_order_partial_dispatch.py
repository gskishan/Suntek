import frappe
from frappe import _


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    for row in data:
        if row.get("status") == "Completed":
            row["status_color"] = "green"
        elif row.get("status") == "Partial":
            row["status_color"] = "orange"
        elif row.get("status") == "Not Started":
            row["status_color"] = "red"
        elif row.get("status") == "No Design":
            row["status_color"] = "gray"

        if row.get("pending_qty") > 0:
            row["pending_color"] = "red"
        else:
            row["pending_color"] = ""

    return columns, data


def get_columns():
    """Define columns for the report"""
    return [
        {
            "label": _("Sales Order"),
            "fieldname": "sales_order",
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": 235,
        },
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 100,
        },
        {
            "label": _("Design"),
            "fieldname": "design",
            "fieldtype": "Link",
            "options": "Designing",
            "width": 220,
        },
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 151,
        },
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "label": _("Required Qty"),
            "fieldname": "required_qty",
            "fieldtype": "Float",
            "width": 80,
        },
        {
            "label": _("Transferred Qty"),
            "fieldname": "transferred_qty",
            "fieldtype": "Float",
            "width": 80,
        },
        {
            "label": _("Pending Qty"),
            "fieldname": "pending_qty",
            "fieldtype": "Float",
            "width": 80,
            "indicator": {"color_field": "pending_color"},
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100,
            "indicator": {"color_field": "status_color"},
        },
        {
            "label": _("Last Stock Entry"),
            "fieldname": "last_stock_entry",
            "fieldtype": "Link",
            "options": "Stock Entry",
            "width": 130,
        },
        {
            "label": _("Last Transfer Date"),
            "fieldname": "last_transfer_date",
            "fieldtype": "Date",
            "width": 120,
        },
    ]


def get_data(filters=None):
    """Fetch data for the report"""
    data = []

    conditions = ""
    values = {}

    if filters.get("sales_order"):
        conditions += " AND so.name = %(sales_order)s"
        values["sales_order"] = filters.get("sales_order")

    if filters.get("project"):
        conditions += " AND so.project = %(project)s"
        values["project"] = filters.get("project")

    if filters.get("from_date") and filters.get("to_date"):
        conditions += " AND so.transaction_date BETWEEN %(from_date)s AND %(to_date)s"
        values["from_date"] = filters.get("from_date")
        values["to_date"] = filters.get("to_date")

    sales_orders = frappe.db.sql(
        f"""
        SELECT 
            so.name as sales_order,
            so.project
        FROM 
            `tabSales Order` so
        WHERE 
            so.docstatus = 1
            AND so.project IS NOT NULL
            {conditions}
        ORDER BY 
            so.creation DESC
    """,
        values,
        as_dict=1,
    )

    for so in sales_orders:
        project_id = so.project

        # Get designing documents linked to the project
        design_conditions = ""
        design_values = {"project": project_id}

        if filters.get("design"):
            design_conditions += " AND name = %(design)s"
            design_values["design"] = filters.get("design")

        designs = frappe.db.sql(
            f"""
            SELECT 
                name
            FROM 
                `tabDesigning` 
            WHERE 
                custom_project = %(project)s 
                AND docstatus = 1
                {design_conditions}
            ORDER BY 
                modified DESC
            """,
            design_values,
            as_dict=1,
        )

        if designs and len(designs) > 0:
            for design in designs:
                design_id = design.name

                # Get items from designing document
                design_items = frappe.db.sql(
                    """
                    SELECT 
                        di.item_code,
                        di.item_name,
                        di.qty as required_qty
                    FROM 
                        `tabDesigning Item` di
                    WHERE 
                        di.parent = %s
                    """,
                    design_id,
                    as_dict=1,
                )

                for item in design_items:
                    # Get stock entries for this project and item
                    stock_entry_conditions = ""
                    stock_entry_values = {
                        "project": project_id,
                        "item_code": item.item_code,
                    }

                    if filters.get("from_date") and filters.get("to_date"):
                        stock_entry_conditions += (
                            " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"
                        )
                        stock_entry_values["from_date"] = filters.get("from_date")
                        stock_entry_values["to_date"] = filters.get("to_date")

                    transferred_items = frappe.db.sql(
                        f"""
                        SELECT 
                            se.name as stock_entry,
                            se.posting_date,
                            sed.qty
                        FROM 
                            `tabStock Entry Detail` sed
                        JOIN 
                            `tabStock Entry` se ON se.name = sed.parent
                        WHERE 
                            se.project = %(project)s
                            AND sed.item_code = %(item_code)s
                            AND se.docstatus = 1
                            AND sed.t_warehouse IS NOT NULL
                            AND se.stock_entry_type = 'Material Transfer to Customer'
                            {stock_entry_conditions}
                        ORDER BY 
                            se.posting_date DESC
                    """,
                        stock_entry_values,
                        as_dict=1,
                    )

                    total_transferred = 0
                    last_stock_entry = None
                    last_transfer_date = None

                    if transferred_items:
                        for transfer in transferred_items:
                            total_transferred += transfer.qty

                        last_stock_entry = transferred_items[0].stock_entry
                        last_transfer_date = transferred_items[0].posting_date

                    pending_qty = item.required_qty - total_transferred

                    if total_transferred <= 0:
                        status = "Not Started"
                    elif pending_qty <= 0:
                        status = "Completed"
                    else:
                        status = "Partial"

                    if filters.get("status") and filters.get("status") != status:
                        continue

                    row = {
                        "sales_order": so.sales_order,
                        "project": project_id,
                        "design": design_id,
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "required_qty": item.required_qty,
                        "transferred_qty": total_transferred,
                        "pending_qty": pending_qty if pending_qty > 0 else 0,
                        "status": status,
                        "last_stock_entry": last_stock_entry,
                        "last_transfer_date": last_transfer_date,
                    }

                    data.append(row)
        else:
            if (
                not filters.get("status") or filters.get("status") == "No Design"
            ) and not filters.get("only_design_projects"):
                row = {
                    "sales_order": so.sales_order,
                    "project": project_id,
                    "design": "Design Unavailable",
                    "item_code": None,
                    "item_name": None,
                    "required_qty": 0,
                    "transferred_qty": 0,
                    "pending_qty": 0,
                    "status": "No Design",
                    "last_stock_entry": None,
                    "last_transfer_date": None,
                }

                data.append(row)

    return data
