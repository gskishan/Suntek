import frappe

def change_enquiry_status(doc,method):
    
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status
    duplicate_check(doc)

def set_enquiry_name(doc,method):

    if doc.name:
        doc.custom_enquiry_name = doc.name
        
def duplicate_check(doc):
    sql="""select * from  `tabLead` where name!="{0}" and mobile_no="{1}" """.format(doc.name,doc.mobile_no)
    if frappe.db.sql(sql,as_dict=1):
        frappe.errprint(sql)
        frappe.throw("Duplicate Mobile no {0}".format(doc.mobile_no))
