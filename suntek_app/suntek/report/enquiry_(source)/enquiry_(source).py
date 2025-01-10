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
        """,
        as_dict=1,
    )

    # Define columns for the report
    columns = [
        {"fieldname": "source", "label": _("Source"), "fieldtype": "Data", "width": 180},
        {"fieldname": "total_leads", "label": _("Total Leads"), "fieldtype": "Int", "width": 100},
        {"fieldname": "total_capacity", "label": _("Overall Capacity"), "fieldtype": "Float", "width": 170},
        {"fieldname": "open_leads_capacity_kwp", "label": _("Capacity (Open - kWp)"), "fieldtype": "Float", "width": 210},
        {"fieldname": "converted_leads_capacity_kwp", "label": _("Capacity (Converted - kWp)"), "fieldtype": "Float", "width": 210},
    ]

    # Add UOM specific columns
    for uom in uom_list:
        uom_name = uom.custom_uom
        columns.extend(
            [
                {
                    "fieldname": f"total_leads_{uom_name.lower().replace(' ', '_')}",
                    "label": _(f"Total Leads ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 150,
                },
                {"fieldname": "open_leads", "label": _("Open"), "fieldtype": "Int", "width": 100},
                {"fieldname": "replied_leads", "label": _("Replied"), "fieldtype": "Int", "width": 100},
                {"fieldname": "opportunity_leads", "label": _("Opportunity"), "fieldtype": "Int", "width": 120},
                {"fieldname": "quotation_leads", "label": _("Quotation"), "fieldtype": "Int", "width": 120},
                {"fieldname": "interested_leads", "label": _("Interested"), "fieldtype": "Int", "width": 120},
                {"fieldname": "converted_leads", "label": _("Converted"), "fieldtype": "Int", "width": 120},
                {"fieldname": "lost_quotation_leads", "label": _("Lost Quotation"), "fieldtype": "Int", "width": 130},
                {"fieldname": "do_not_contact_leads", "label": _("Do Not Contact"), "fieldtype": "Int", "width": 130},
                {"fieldname": "conversion_rate", "label": _("Conversion Rate %"), "fieldtype": "Percent", "width": 150},
                {
                    "fieldname": f"total_capacity_{uom_name.lower().replace(' ', '_')}",
                    "label": _(f"Total Capacity ({uom_name})"),
                    "fieldtype": "Float",
                    "width": 170,
                },
            ]
        )

    # Add other columns
    columns.extend(
        [
            {"fieldname": "open_leads", "label": _("Open"), "fieldtype": "Int", "width": 120},
            {"fieldname": "converted_leads", "label": _("Converted"), "fieldtype": "Int", "width": 140},
            {"fieldname": "conversion_rate", "label": _("Conversion Rate %"), "fieldtype": "Percent", "width": 160},
        ]
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
            WHEN custom_capacity REGEXP '^[0-9]+(\\.[0-9]+)?$'
            THEN CAST(custom_capacity AS DECIMAL(10,2)) 
            ELSE 0 
        END) as total_capacity""",
            """SUM(CASE 
            WHEN status = 'Open' 
            AND custom_uom = 'kWp'
            AND custom_capacity REGEXP '^[0-9]+(\\.[0-9]+)?$'
            THEN CAST(custom_capacity AS DECIMAL(10,2)) 
            ELSE 0 
        END) as open_leads_capacity_kwp""",
            """SUM(CASE 
            WHEN status = 'Converted'
            AND custom_uom = 'kWp'
            AND custom_capacity REGEXP '^[0-9]+(\\.[0-9]+)?$'
            THEN CAST(custom_capacity AS DECIMAL(10,2)) 
            ELSE 0 
        END) as converted_leads_capacity_kwp""",
        ]
    )

    # Add UOM specific calculations
    for uom in uom_list:
        uom_name = uom.custom_uom
        field_name = uom_name.lower().replace(" ", "_")

        select_clauses.extend(
            [
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' THEN 1 ELSE 0 END) 
                as total_leads_{field_name}""",
                f"""SUM(CASE 
                WHEN custom_uom = '{uom_name}' AND custom_capacity REGEXP '^[0-9]+(\\.[0-9]+)?$'
                THEN CAST(custom_capacity AS DECIMAL(10,2)) 
                ELSE 0 
            END) as total_capacity_{field_name}""",
            ]
        )

    # Add status calculations
    select_clauses.extend(
        [
            "SUM(CASE WHEN status = 'Open' THEN 1 ELSE 0 END) as open_leads",
            "SUM(CASE WHEN status = 'Replied' THEN 1 ELSE 0 END) as replied_leads",
            "SUM(CASE WHEN status = 'Opportunity' THEN 1 ELSE 0 END) as opportunity_leads",
            "SUM(CASE WHEN status = 'Quotation' THEN 1 ELSE 0 END) as quotation_leads",
            "SUM(CASE WHEN status = 'Interested' THEN 1 ELSE 0 END) as interested_leads",
            "SUM(CASE WHEN status = 'Converted' THEN 1 ELSE 0 END) as converted_leads",
            "SUM(CASE WHEN status = 'Lost Quotation' THEN 1 ELSE 0 END) as lost_quotation_leads",
            "SUM(CASE WHEN status = 'Do Not Contact' THEN 1 ELSE 0 END) as do_not_contact_leads",
        ]
    )

    # Get data from database
    data = frappe.db.sql(
        f"""
        SELECT 
            {', '.join(select_clauses)}
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
            "options": "\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact",
        },
    ]
