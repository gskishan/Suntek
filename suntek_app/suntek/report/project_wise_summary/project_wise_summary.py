import frappe
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
        condition += " AND SO.customer = '{0}' ".format(filters.get("customer"))
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
            'fieldname': 'total_paid_amount',
            'label': _('Total Amount Received Via Payment Entry'),
            'fieldtype': 'Float',
            'width': 180
        },
        {
            'fieldname': 'remaining_amount',
            'label': _('Remaining Balance Amount'),
            'fieldtype': 'Float',
            'width': 180
        },
        {
            'fieldname': 'sales_order_status',
            'label': _('Sales Order Status'),
            'fieldtype': 'Data',
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
        IFNULL(SUM(payment.paid_amount), 0) AS total_paid_amount,
        IFNULL(SO.grand_total, 0) - IFNULL(SUM(payment.paid_amount), 0) AS remaining_amount,
        SO.status AS sales_order_status
    FROM 
        `tabProject` project
    INNER JOIN 
        `tabSales Order` SO ON project.name = SO.project 
    LEFT JOIN 
        `tabPayment Entry` payment ON SO.name = payment.sales_order 
        AND payment.docstatus = 1
    WHERE 
        project.docstatus = 0 {0}
    GROUP BY 
        SO.name, project.name
    """.format(condition)

    frappe.errprint(sql)
    return frappe.db.sql(sql, as_dict=1)
