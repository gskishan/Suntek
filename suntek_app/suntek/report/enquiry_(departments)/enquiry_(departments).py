import frappe


def execute(filters=None):
    columns = [
        {
            "fieldname": "name",
            "label": "Lead ID",
            "fieldtype": "Link",
            "options": "Lead",
            "width": 200,
        },
        {
            "fieldname": "lead_name",
            "label": "Lead Name",
            "fieldtype": "Data",
            "width": 160,
        },
        {
            "fieldname": "custom_department",
            "label": "Department",
            "fieldtype": "Data",
            "width": 160,
        },
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 140},
        {
            "fieldname": "lead_owner",
            "label": "Lead Owner",
            "fieldtype": "Link",
            "options": "User",
            "width": 160,
        },
        {
            "fieldname": "custom_enquiry_owner_name",
            "label": "Enquiry Owner Name",
            "fieldtype": "Data",
            "width": 190,
        },
        {
            "fieldname": "creation",
            "label": "Creation Date",
            "fieldtype": "Date",
            "width": 140,
        },
    ]

    conditions = ""
    if filters:
        if filters.get("status"):
            conditions += " and status = %(status)s"
        if filters.get("custom_department"):
            conditions += " and custom_department = %(custom_department)s"
        if filters.get("lead_owner"):
            conditions += " and lead_owner = %(lead_owner)s"
        if filters.get("from_date"):
            conditions += " and creation >= %(from_date)s"
        if filters.get("to_date"):
            conditions += " and creation <= %(to_date)s"

    data = frappe.db.sql(
        f"""
        SELECT
            name,
            lead_name,
            custom_department,
            status,
            lead_owner,
            custom_enquiry_owner_name,
            creation
        FROM tabLead
        WHERE 1=1 {conditions}
        ORDER BY creation desc
    """,
        filters,
        as_dict=1,
    )

    dept_data = frappe.db.sql(
        f"""
        SELECT 
            CASE 
                WHEN custom_department = 'Tele Sales - SESP' THEN 'Tele Sales'
                WHEN custom_department = 'Domestic (Residential) Sales Team - SESP' THEN 'Domestic (Residential)'
                WHEN custom_department = 'Channel Partner - SESP' THEN 'Channel Partner'
                WHEN custom_department = 'Commercial & Industrial (C&I) - SESP' THEN 'C&I'
                ELSE 'Others'
            END as department,
            COUNT(*) as count
        FROM tabLead
        WHERE 1=1 {conditions}
        GROUP BY 
            CASE 
                WHEN custom_department = 'Tele Sales - SESP' THEN 'Tele Sales'
                WHEN custom_department = 'Domestic (Residential) Sales Team - SESP' THEN 'Domestic (Residential)'
                WHEN custom_department = 'Channel Partner - SESP' THEN 'Channel Partner'
                WHEN custom_department = 'Commercial & Industrial (C&I) - SESP' THEN 'C&I'
                ELSE 'Others'
            END
    """,
        filters,
        as_dict=1,
    )

    chart = {
        "type": "pie",
        "data": {
            "labels": [d.department for d in dept_data],
            "datasets": [{"values": [d.count for d in dept_data]}],
        },
    }

    return columns, data, None, chart
