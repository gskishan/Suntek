import frappe
from frappe import _


def execute(filters=None):
    # Get all UOMs from Lead/Enquiry
    uom_list = frappe.db.sql(
        """
        SELECT DISTINCT custom_uom 
        FROM `tabLead` 
        WHERE custom_uom IS NOT NULL 
        AND custom_uom != ''
        AND TRIM(custom_uom) != ''
        AND custom_uom = 'kWp'  # First get kWp
        UNION ALL
        SELECT DISTINCT custom_uom 
        FROM `tabLead` 
        WHERE custom_uom IS NOT NULL 
        AND custom_uom != ''
        AND TRIM(custom_uom) != ''
        AND custom_uom != 'kWp'  # Then get other UOMs
        """,
        as_dict=1,
    )

    # Define statuses
    statuses = [
        "Open",
        "Replied",
        "Opportunity",
        "Quotation",
        "Interested",
        "Converted",
        "Lost Quotation",
        "Do Not Contact",
    ]

    # Define base columns with conversion rate moved up
    columns = [
        {
            "fieldname": "source",
            "label": _("Source"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "total_leads",
            "label": _("Total Leads"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "total_capacity",
            "label": _("Overall Capacity"),
            "fieldtype": "Float",
            "width": 170,
        },
        {
            "fieldname": "conversion_rate",
            "label": _("Conversion Rate %"),
            "fieldtype": "Percent",
            "width": 150,
        },
    ]

    # First add all kWp specific columns
    for status in statuses:
        status_key = status.lower().replace(" ", "_")
        columns.append(
            {
                "fieldname": f"{status_key}_kwp",
                "label": _(f"{status} (kWp)"),
                "fieldtype": "Float",
                "width": 150,
            }
        )

    # Add status columns with counts
    for status in statuses:
        status_key = status.lower().replace(" ", "_")
        columns.append(
            {
                "fieldname": f"{status_key}_leads",
                "label": _(f"{status} (Nos)"),
                "fieldtype": "Int",
                "width": 150,
            }
        )

    # Group remaining columns by other UOMs
    for uom in uom_list:
        uom_name = uom.custom_uom
        if uom_name != "kWp":  # Skip kWp as it's already added
            # Add all status columns for this UOM together
            for status in statuses:
                status_key = status.lower().replace(" ", "_")
                columns.append(
                    {
                        "fieldname": f"{status_key}_{uom_name.lower().replace(' ', '_')}",
                        "label": _(f"{status} ({uom_name})"),
                        "fieldtype": "Float",
                        "width": 150,
                    }
                )

    # Build conditions based on filters
    conditions = "1=1"
    if filters:
        if filters.get("from_date"):
            conditions += f" AND custom_enquiry_date >= '{filters.get('from_date')}'"
        if filters.get("to_date"):
            conditions += f" AND custom_enquiry_date <= '{filters.get('to_date')}'"
        if filters.get("department"):
            conditions += f" AND custom_department = {frappe.db.escape(filters.get('department'))}"
        if filters.get("source"):
            conditions += f" AND source = {frappe.db.escape(filters.get('source'))}"
        if filters.get("status"):
            conditions += f" AND status = {frappe.db.escape(filters.get('status'))}"

    # Dynamic SQL query construction
    select_clauses = ["source"]

    # Add total leads and capacity calculations
    select_clauses.extend(
        [
            "COUNT(*) as total_leads",
            """SUM(CASE 
            WHEN custom_capacity REGEXP '^[0-9]+(\.[0-9]+)?$'
            THEN CAST(custom_capacity AS DECIMAL(10,2)) 
            ELSE 0 
        END) as total_capacity""",
        ]
    )

    # Add kWp calculations first
    for status in statuses:
        status_key = status.lower().replace(" ", "_")
        select_clauses.append(
            f"""
            SUM(CASE 
                WHEN status = '{status}' 
                AND custom_uom = 'kWp' 
                AND custom_capacity REGEXP '^[0-9]+(\.[0-9]+)?$'
                THEN CAST(custom_capacity AS DECIMAL(10,2)) 
                ELSE 0 
            END) as {status_key}_kwp
            """
        )

    # Add status counts
    for status in statuses:
        status_key = status.lower().replace(" ", "_")
        select_clauses.append(f"SUM(CASE WHEN status = '{status}' THEN 1 ELSE 0 END) as {status_key}_leads")

    # Add other UOM calculations
    for uom in uom_list:
        uom_name = uom.custom_uom
        if uom_name != "kWp":
            uom_key = uom_name.lower().replace(" ", "_")
            for status in statuses:
                status_key = status.lower().replace(" ", "_")
                select_clauses.append(
                    f"""
                    SUM(CASE 
                        WHEN status = '{status}' 
                        AND custom_uom = '{uom_name}' 
                        AND custom_capacity REGEXP '^[0-9]+(\.[0-9]+)?$'
                        THEN CAST(custom_capacity AS DECIMAL(10,2)) 
                        ELSE 0 
                    END) as {status_key}_{uom_key}
                    """
                )

    # Get data from database
    data = frappe.db.sql(
        f"""
        SELECT 
            {", ".join(select_clauses)}
        FROM `tabLead`
        WHERE {conditions}
        GROUP BY source
        ORDER BY total_leads DESC
        """,
        as_dict=1,
    )

    # Calculate conversion rates
    for row in data:
        row["conversion_rate"] = (row["converted_leads"] / row["total_leads"] * 100) if row["total_leads"] > 0 else 0

    return columns, data


def get_filters():
    return [
        {
            "fieldname": "from_date",
            "label": _("From Date"),
            "fieldtype": "Date",
            "default": frappe.utils.add_months(frappe.utils.nowdate(), -1),
            "reqd": 1,
        },
        {
            "fieldname": "to_date",
            "label": _("To Date"),
            "fieldtype": "Date",
            "default": frappe.utils.nowdate(),
            "reqd": 1,
        },
        {
            "fieldname": "department",
            "label": _("Department"),
            "fieldtype": "Link",
            "options": "Department",
        },
        {
            "fieldname": "source",
            "label": _("Source"),
            "fieldtype": "Link",
            "options": "Lead Source",
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Select",
            "options": (
                "\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact"
            ),
        },
    ]
