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
            "label": _("Project Creation Date"),
            "fieldname": "project_creation_date",
            "fieldtype": "Date",
            "width": 120,
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
        {
            "label": _("Delivery Note"),
            "fieldname": "delivery_note",
            "fieldtype": "Link",
            "options": "Delivery Note",
            "width": 130,
        },
        {
            "label": _("Sales Invoice"),
            "fieldname": "sales_invoice",
            "fieldtype": "Link",
            "options": "Sales Invoice",
            "width": 130,
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

    design_filter = ""
    if filters.get("design"):
        design_filter = f" AND name = '{filters.get('design')}'"

    all_designs = frappe.db.sql(
        f"""
        SELECT
            name, custom_project
        FROM
            `tabDesigning`
        WHERE
            docstatus = 1
            {design_filter}
        """,
        as_dict=1,
    )

    project_to_designs = {}
    for design in all_designs:
        if design.custom_project not in project_to_designs:
            project_to_designs[design.custom_project] = []
        project_to_designs[design.custom_project].append(design.name)

    design_items_map = {}
    if all_designs:
        all_design_names = [d.name for d in all_designs]
        all_design_items = frappe.db.sql(
            """
            SELECT
                di.parent,
                di.item_code,
                di.item_name,
                di.qty as required_qty
            FROM
                `tabDesigning Item` di
            WHERE
                di.parent IN %s
            """,
            [tuple(all_design_names) if len(all_design_names) > 1 else ("'" + all_design_names[0] + "'")],
            as_dict=1,
        )

        for item in all_design_items:
            if item.parent not in design_items_map:
                design_items_map[item.parent] = []
            design_items_map[item.parent].append(item)

    transferred_qty_conditions = ""
    transferred_qty_values = {}

    if filters.get("from_date") and filters.get("to_date"):
        transferred_qty_conditions += " AND se.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        transferred_qty_values["from_date"] = filters.get("from_date")
        transferred_qty_values["to_date"] = filters.get("to_date")

    all_transferred_qtys = frappe.db.sql(
        f"""
        SELECT
            se.project,
            sed.item_code,
            SUM(sed.qty) as transferred_qty,
            MAX(se.posting_date) as last_transfer_date,
            GROUP_CONCAT(DISTINCT se.name ORDER BY se.posting_date DESC SEPARATOR ', ') as stock_entries
        FROM
            `tabStock Entry Detail` sed
        JOIN
            `tabStock Entry` se ON se.name = sed.parent
        WHERE
            se.docstatus = 1
            AND sed.t_warehouse IS NOT NULL
            AND se.stock_entry_type = 'Material Transfer to Customer'
            AND se.project IS NOT NULL
            {transferred_qty_conditions}
        GROUP BY
            se.project, sed.item_code
        """,
        transferred_qty_values,
        as_dict=1,
    )

    project_item_to_transferred = {}
    for tq in all_transferred_qtys:
        if tq.project not in project_item_to_transferred:
            project_item_to_transferred[tq.project] = {}
        project_item_to_transferred[tq.project][tq.item_code] = {
            "transferred_qty": tq.transferred_qty,
            "last_transfer_date": tq.last_transfer_date,
            "last_stock_entry": tq.stock_entries.split(", ")[0] if tq.stock_entries else None,
        }

    delivery_notes = frappe.db.sql(
        """
        SELECT
            dni.against_sales_order as sales_order,
            GROUP_CONCAT(DISTINCT dn.name ORDER BY dn.creation DESC SEPARATOR ', ') as delivery_notes
        FROM
            `tabDelivery Note` dn
        JOIN
            `tabDelivery Note Item` dni ON dn.name = dni.parent
        WHERE
            dn.docstatus = 1
        GROUP BY
            dni.against_sales_order
        """,
        as_dict=1,
    )

    so_to_dn = {}
    for dn in delivery_notes:
        if dn.sales_order:
            so_to_dn[dn.sales_order] = dn.delivery_notes.split(", ")[0] if dn.delivery_notes else None

    project_delivery_notes = frappe.db.sql(
        """
        SELECT
            dn.project,
            GROUP_CONCAT(DISTINCT dn.name ORDER BY dn.creation DESC SEPARATOR ', ') as delivery_notes
        FROM
            `tabDelivery Note` dn
        WHERE
            dn.docstatus = 1
            AND dn.project IS NOT NULL
        GROUP BY
            dn.project
        """,
        as_dict=1,
    )

    project_to_dn = {}
    for dn in project_delivery_notes:
        if dn.project:
            project_to_dn[dn.project] = dn.delivery_notes.split(", ")[0] if dn.delivery_notes else None

    sales_invoices = frappe.db.sql(
        """
        SELECT
            sii.sales_order,
            GROUP_CONCAT(DISTINCT si.name ORDER BY si.creation DESC SEPARATOR ', ') as sales_invoices
        FROM
            `tabSales Invoice` si
        JOIN
            `tabSales Invoice Item` sii ON si.name = sii.parent
        WHERE
            si.docstatus = 1
            AND sii.sales_order IS NOT NULL
        GROUP BY
            sii.sales_order
        """,
        as_dict=1,
    )

    so_to_si = {}
    for si in sales_invoices:
        if si.sales_order:
            so_to_si[si.sales_order] = si.sales_invoices.split(", ")[0] if si.sales_invoices else None

    project_sales_invoices = frappe.db.sql(
        """
        SELECT
            si.project,
            GROUP_CONCAT(DISTINCT si.name ORDER BY si.creation DESC SEPARATOR ', ') as sales_invoices
        FROM
            `tabSales Invoice` si
        WHERE
            si.docstatus = 1
            AND si.project IS NOT NULL
        GROUP BY
            si.project
        """,
        as_dict=1,
    )

    project_to_si = {}
    for si in project_sales_invoices:
        if si.project:
            project_to_si[si.project] = si.sales_invoices.split(", ")[0] if si.sales_invoices else None

    sales_orders = frappe.db.sql(
        f"""
        SELECT
            so.name as sales_order,
            so.project,
            p.creation as project_creation_date
        FROM
            `tabSales Order` so
        LEFT JOIN
            `tabProject` p ON p.name = so.project
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
        sales_order_id = so.sales_order

        delivery_note = so_to_dn.get(sales_order_id) or project_to_dn.get(project_id)

        sales_invoice = so_to_si.get(sales_order_id) or project_to_si.get(project_id)

        designs = project_to_designs.get(project_id, [])

        if designs:
            for design_id in designs:
                design_items = design_items_map.get(design_id, [])

                for item in design_items:
                    transferred_data = project_item_to_transferred.get(project_id, {}).get(item.item_code, {})
                    total_transferred = transferred_data.get("transferred_qty", 0)
                    last_stock_entry = transferred_data.get("last_stock_entry")
                    last_transfer_date = transferred_data.get("last_transfer_date")

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
                        "sales_order": sales_order_id,
                        "project": project_id,
                        "project_creation_date": so.project_creation_date,
                        "design": design_id,
                        "item_code": item.item_code,
                        "item_name": item.item_name,
                        "required_qty": item.required_qty,
                        "transferred_qty": total_transferred,
                        "pending_qty": pending_qty if pending_qty > 0 else 0,
                        "status": status,
                        "last_stock_entry": last_stock_entry,
                        "last_transfer_date": last_transfer_date,
                        "delivery_note": delivery_note,
                        "sales_invoice": sales_invoice,
                    }

                    data.append(row)
        else:
            if (not filters.get("status") or filters.get("status") == "No Design") and not filters.get(
                "only_design_projects"
            ):
                row = {
                    "sales_order": sales_order_id,
                    "project": project_id,
                    "project_creation_date": so.project_creation_date,
                    "design": "Design Unavailable",
                    "item_code": None,
                    "item_name": None,
                    "required_qty": 0,
                    "transferred_qty": 0,
                    "pending_qty": 0,
                    "status": "No Design",
                    "last_stock_entry": None,
                    "last_transfer_date": None,
                    "delivery_note": delivery_note,
                    "sales_invoice": sales_invoice,
                }

                data.append(row)

    return data
