import frappe
@frappe.whitelist()
def get_emp(user):
  sql="""select e.cell_number,s.name from `tabEmployee` e inner join `tabSales Person` s on e.name=s.employee where user_id="{0}" """.format(user)
  data=(frappe.db.sql(sql,as_dict=True))
  if data:
    return data
    
