import frappe
from frappe import _


def execute(filters=None):
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

    columns = [
        {
            "fieldname": "reference_by",
            "label": _("Reference By"),
            "fieldtype": "Data",
            "width": 120,
        },
        {
            "fieldname": "reference_name",
            "label": _("Reference Name"),
            "fieldtype": "Data",
            "width": 180,
        },
        {
            "fieldname": "reference_details",
            "label": _("Reference Details"),
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
    ]

    for uom in uom_list:
        uom_name = uom.custom_uom
        field_name = uom_name.lower().replace(" ", "_")

        columns.extend(
            [
                {
                    "fieldname": f"total_leads_{field_name}",
                    "label": _(f"Total Leads ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 150,
                },
                {
                    "fieldname": f"total_capacity_{field_name}",
                    "label": _(f"Total Capacity ({uom_name})"),
                    "fieldtype": "Float",
                    "width": 170,
                },
                {
                    "fieldname": f"open_leads_{field_name}",
                    "label": _(f"Open ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"replied_leads_{field_name}",
                    "label": _(f"Replied ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"opportunity_leads_{field_name}",
                    "label": _(f"Opportunity ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"quotation_leads_{field_name}",
                    "label": _(f"Quotation ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"interested_leads_{field_name}",
                    "label": _(f"Interested ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"converted_leads_{field_name}",
                    "label": _(f"Converted ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 120,
                },
                {
                    "fieldname": f"lost_quotation_leads_{field_name}",
                    "label": _(f"Lost Quotation ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 130,
                },
                {
                    "fieldname": f"do_not_contact_leads_{field_name}",
                    "label": _(f"Do Not Contact ({uom_name})"),
                    "fieldtype": "Int",
                    "width": 130,
                },
                {
                    "fieldname": f"conversion_rate_{field_name}",
                    "label": _(f"Conversion Rate % ({uom_name})"),
                    "fieldtype": "Percent",
                    "width": 150,
                },
            ]
        )

    conditions = "custom_reference_by IS NOT NULL"
    if filters:
        if filters.get("from_date"):
            conditions += f" AND custom_enquiry_date >= '{filters.get('from_date')}'"
        if filters.get("to_date"):
            conditions += f" AND custom_enquiry_date <= '{filters.get('to_date')}'"
        if filters.get("department"):
            conditions += f" AND custom_department = '{filters.get('department')}'"
        if filters.get("reference_by"):
            conditions += f" AND custom_reference_by = '{filters.get('reference_by')}'"
        if filters.get("status"):
            conditions += f" AND status = '{filters.get('status')}'"

    select_clauses = [
        "custom_reference_by as reference_by",
        """CASE 
            WHEN custom_reference_by = 'Employee' THEN custom_employee_name
            WHEN custom_reference_by = 'Customer' THEN custom_customer_name
            ELSE ''
        END as reference_name""",
        """CASE 
            WHEN custom_reference_by = 'Employee' THEN custom_employee_mobile_no
            WHEN custom_reference_by = 'Customer' THEN custom_customer_mobile_no
            ELSE ''
        END as reference_details""",
        "COUNT(*) as total_leads",
        """SUM(CASE 
            WHEN custom_capacity REGEXP '^[0-9]+(\\.[0-9]+)?$'
            THEN CAST(custom_capacity AS DECIMAL(10,2)) 
            ELSE 0 
        END) as total_capacity""",
    ]

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
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Open' THEN 1 ELSE 0 END) 
            as open_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Replied' THEN 1 ELSE 0 END) 
            as replied_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Opportunity' THEN 1 ELSE 0 END) 
            as opportunity_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Quotation' THEN 1 ELSE 0 END) 
            as quotation_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Interested' THEN 1 ELSE 0 END) 
            as interested_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Converted' THEN 1 ELSE 0 END) 
            as converted_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Lost Quotation' THEN 1 ELSE 0 END) 
            as lost_quotation_leads_{field_name}""",
                f"""SUM(CASE WHEN custom_uom = '{uom_name}' AND status = 'Do Not Contact' THEN 1 ELSE 0 END) 
            as do_not_contact_leads_{field_name}""",
            ]
        )

    data = frappe.db.sql(
        f"""
        SELECT 
            {", ".join(select_clauses)}
        FROM `tabLead`
        WHERE {conditions}
        GROUP BY custom_reference_by, 
            CASE 
                WHEN custom_reference_by = 'Employee' THEN custom_employee
                WHEN custom_reference_by = 'Customer' THEN custom_customer
                ELSE ''
            END
        ORDER BY total_leads DESC
        """,
        as_dict=1,
    )

    for row in data:
        for uom in uom_list:
            uom_name = uom.custom_uom
            field_name = uom_name.lower().replace(" ", "_")
            total_leads_field = f"total_leads_{field_name}"
            converted_leads_field = f"converted_leads_{field_name}"
            conversion_rate_field = f"conversion_rate_{field_name}"

            row[conversion_rate_field] = (
                (row[converted_leads_field] / row[total_leads_field] * 100)
                if row[total_leads_field] > 0
                else 0
            )

    return columns, data
