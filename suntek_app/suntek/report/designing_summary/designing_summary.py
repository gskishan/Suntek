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
  
    if filters.get("project"):
        condition += " AND p.project = '{0}' ".format(filters.get("project"))
    if filters.get("designing"):
        condition += " AND p.against_designing = '{0}' ".format(filters.get("designing"))
  
    return condition

def get_columns():
    columns = [
        {
            'fieldname': 'against_designing',
            'label': _('Designing'),
            'fieldtype': 'Link',
            'options': 'Designing',
            'width': 200
        },
          {
            'fieldname': 'stock_entry',
            'label': _('Stock Entry'),
            'fieldtype': 'Link',
            'options': 'Stock Entry',
            'width': 200
        },
        {
            'fieldname': 'item_code',
            'label': _('Item Code'),
            'fieldtype': 'Link',
            'options': 'Item',
            'width': 200
        },
        {
            'fieldname': 'item_name',
            'label': _('Item Name'),
            'fieldtype': 'Data',
            'width': 200
        },
       
        {
            'fieldname': 'qty',
            'label': _('Quantiity'),
            'fieldtype': 'Float',
            'width': 160
        },
       
      
        {
            'fieldname': 'transferred',
            'label': _('Transferred'),
            'fieldtype': 'Float',
            'width': 180
        },
        {
            'fieldname': 'pending_qty',
            'label': _('Balance Quantity'),
            'fieldtype': 'Float',
            'width': 180
        }
    ]
    return columns

def get_data(condition=None):
    sql = """  SELECT  p.against_designing,
    p.name stock_entry,item_code,item_name,qty,transferred,qty-transferred as pending_qty
FROM 
    `tabStock Entry` p
inner JOIN 
    `tabDesigning Item` c ON c.parent = p.against_designing
where p.docstatus=1 {}
    """.format(condition)
    
    frappe.errprint(sql)
    return frappe.db.sql(sql, as_dict=1)
