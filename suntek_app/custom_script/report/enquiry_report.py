import frappe
from frappe import _
from frappe.utils import getdate, cint

def execute(filters=None):
    columns, data = [], []

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    
    columns = get_columns()
    data = get_data(start_date, end_date)
    
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "enquiry_owner",
            "label": _("Enquiry Owner"),
            "fieldtype": "Data",
            "width": 150
        },
        {
            "fieldname": "interested",
            "label": _("Interested"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "opportunity",
            "label": _("Opportunity"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "open",
            "label": _("Open"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "quotation",
            "label": _("Quotation"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "converted",
            "label": _("Converted"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "do_not_contact",
            "label": _("Do Not Contact"),
            "fieldtype": "Int",
            "width": 150
        }
    ]

def get_data(start_date, end_date):
    query = """
        SELECT 
            `custom_enquiry_owner_name` AS `enquiry_owner`,
            COUNT(CASE WHEN `status` = 'Interested' THEN 1 END) AS `interested`,
            COUNT(CASE WHEN `status` = 'Opportunity' THEN 1 END) AS `opportunity`,
            COUNT(CASE WHEN `status` = 'Open' THEN 1 END) AS `open`,
            COUNT(CASE WHEN `status` = 'Quotation' THEN 1 END) AS `quotation`,
            COUNT(CASE WHEN `status` = 'Converted' THEN 1 END) AS `converted`,
            COUNT(CASE WHEN `status` = 'Do Not Contact' THEN 1 END) AS `do_not_contact`
        FROM 
            `tabLead`
        WHERE 
            `creation_date` BETWEEN %(start_date)s AND %(end_date)s
        GROUP BY 
            `custom_enquiry_owner_name`
    """

    data = frappe.db.sql(query, {"start_date": start_date, "end_date": end_date}, as_dict=1)
    
    return data
