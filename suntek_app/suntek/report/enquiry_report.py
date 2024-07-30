import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)

    return columns, data

def get_columns(filters=None):
    return [
        {"label": _("Enquiry Owner"), "fieldname": "enquiry_owner", "fieldtype": "Data", "width": 150},
        {"label": _("Total Enquiry's"), "fieldname": "total_enquiries", "fieldtype": "Int", "width": 120},
        {"label": _("Interested"), "fieldname": "interested", "fieldtype": "Int", "width": 100},
        {"label": _("Opportunity"), "fieldname": "opportunity", "fieldtype": "Int", "width": 100},
        {"label": _("Open"), "fieldname": "open", "fieldtype": "Int", "width": 100},
        {"label": _("Quotation"), "fieldname": "quotation", "fieldtype": "Int", "width": 100},
        {"label": _("Converted"), "fieldname": "converted", "fieldtype": "Int", "width": 100},
        {"label": _("Do Not Contact"), "fieldname": "do_not_contact", "fieldtype": "Int", "width": 120},
        {"label": _("Lost"), "fieldname": "lost", "fieldtype": "Int", "width": 100},
    ]

def get_data(filters=None):
    data = frappe.db.sql("""
        SELECT 
            `custom_enquiry_owner_name` AS `enquiry_owner`,
            COUNT(*) AS `total_enquiries`,
            COUNT(CASE WHEN `status` = 'Interested' THEN 1 END) AS `interested`,
            COUNT(CASE WHEN `status` = 'Opportunity' THEN 1 END) AS `opportunity`,
            COUNT(CASE WHEN `status` = 'Open' THEN 1 END) AS `open`,
            COUNT(CASE WHEN `status` = 'Quotation' THEN 1 END) AS `quotation`,
            COUNT(CASE WHEN `status` = 'Converted' THEN 1 END) AS `converted`,
            COUNT(CASE WHEN `status` = 'Do Not Contact' THEN 1 END) AS `do_not_contact`,
            COUNT(CASE WHEN `status` = 'Lost' THEN 1 END) AS `lost`
        FROM 
            `tabLead`
        GROUP BY 
            `custom_enquiry_owner_name`
    """, as_dict=1)

    return data
