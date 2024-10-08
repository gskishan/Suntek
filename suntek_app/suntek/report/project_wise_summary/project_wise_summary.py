import frappe
import json
from frappe import _

def execute(filters=None):
    condition = data_condition(filters)
    data = get_data(condition)
    columns = get_columns()
    return columns, data

def data_condition(filters):
    condition = ""
    if filters.get("from_date") and filters.get("to_date"):
        condition += " AND SO.transaction_date BETWEEN '{0}' AND '{1}' ".format(filters.get("from_date"), filters.get("to_date"))
    if filters.get("project"):
        condition += " AND project.name = '{0}' ".format(filters.get("project"))
    if filters.get("company"):
        condition += " AND project.company = '{0}' ".format(filters.get("company"))
    if filters.get("customer"):
        condition += " AND SO.customer = '{0}' ".format(filters.get("customr"))
    return condition

def get_columns():
    columns = [
        {
            'fieldname': 'project',
            'label': _('Project'),
            'fieldtype': 'Link',
            'options': 'Project',
            'width': 200
        },
        {
            'fieldname': 'custom_type_of_case',
            'label': _('Custom Type Of Case'),
            'fieldtype': 'Data',
            'width': 200
        },
        {
            'fieldname': 'customer',
            'label': _('Customer'),
            'fieldtype': 'Link',
            'options': 'Customer',
            'width': 200
        },
        {
            'fieldname': 'sales_order_amount',
            'label': _('Sales Order Amount'),
            'fieldtype': 'Float',
            'width': 160
        },
        {
            'fieldname': 'discom_status',
            'label': _('Discom Status'),
            'fieldtype': 'Data',
            'width': 180
        },
        {
            'fieldname': 'in_principle_date_received',
            'label': _('In Principle Date Received'),
            'fieldtype': 'Date',
            'width': 180
        },
        {
            'fieldname': 'paid_amount',
            'label': _('Amount Received Via Payment Entry'),
            'fieldtype': 'Float',
            'width': 180
        },
        {
            'fieldname': 'remaining_amount',
            'label': _('Remaining Balance Amount'),
            'fieldtype': 'Float',
            'width': 180
        }
    ]
    return columns

def get_data(condition=None):
    sql = """
        SELECT 
            project.name AS project,
            IFNULL(SO.grand_total, 0) AS sales_order_amount,
            SO.custom_type_of_case,
            SO.customer,
            subsidy.name AS subsidy,
            subsidy.custom_in_principle_date_received AS in_principle_date_received,
            discom.discom_status AS discom_status,
            IFNULL(SUM(payment.paid_amount), 0) AS paid_amount,
            IFNULL(SO.grand_total, 0) - IFNULL(SUM(payment.paid_amount), 0) AS remaining_amount
        FROM 
            `tabProject` project
        INNER JOIN 
            `tabSales Order` SO ON project.name = SO.project 
        LEFT JOIN 
            `tabSubsidy` subsidy ON subsidy.project_name = project.name
        LEFT JOIN 
            `tabDiscom` discom ON discom.project_name = project.name
        LEFT JOIN 
            `tabPayment Entry` payment ON project.name = payment.project AND payment.docstatus = 1
        WHERE 
            project.docstatus = 0 {0}
        GROUP BY 
            project.name
    """.format(condition)
    
    frappe.errprint(sql)
    return frappe.db.sql(sql, as_dict=1)
