import frappe
@frappe.whitelist()
def get_emp(user):
  sql="""select * from `tabEmployee` e inner join `tabSales Person` s on e.name=s.employee where user_id="{0}" """.format(user)
  return(frappe.db.sql(sql,as_dict=True))
