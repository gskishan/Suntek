import frappe
from frappe import _
@frappe.whitelist()
def on_update(self,method):
	if self.user_id:
		u=frappe.get_doc("User",self.user_id)
		u.db_set("mobile_no",self.cell_number, update_modified=False)



@frappe.whitelist()
def on_mobile_for_old():
	sql="""select * from `tabEmployee` where (user_id is not null or user_id !="") """
	for i in frappe.db.sql(sql,as_dict=1):
		emp=frappe.get_doc("Employee",i.name)
		if emp.user_id:
			u=frappe.get_doc("User",emp.user_id)
			u.db_set("mobile_no",emp.cell_number, update_modified=False)
