import frappe
from frappe.desk.form.assign_to import notify_assignment
@frappe.whitelist()
def get_emp(user):
	sql="""select e.cell_number,s.name from `tabEmployee` e inner join `tabSales Person` s on e.name=s.employee where user_id="{0}" """.format(user)
	data=(frappe.db.sql(sql,as_dict=True))
	if data:
		return data

@frappe.whitelist()
def on_update(self,method):
	from frappe.utils import nowdate

	data=get_salesman_user(self)
	if data:
		if data[0].user_id:
			filters = {
				"reference_type": self.doctype,
				"reference_name": self.name,
				"status": "Open",
				"allocated_to": data[0].user_id,
				}
			if not frappe.get_all("ToDo", filters=filters):
				frappe.share.add_docshare(
						self.doctype, self.name,data[0].user_id , write=1, share=1, flags={"ignore_share_permission": True}
					)

				# d = frappe.get_doc(
	   #                          {
	   #                              "doctype": "ToDo",
	   #                              "allocated_to": data[0].user_id,
	   #                              "reference_type": self.doctype,
	   #                              "reference_name": self.name,
	   #                              "description":self.customer_name,
	   #                              "priority": "Medium",
	   #                              "status": "Open",
	   #                              "date": nowdate(),
	   #                              "assigned_by": frappe.session.user,
	   #                              "assignment_rule": "",
	   #                          }
	   #                      ).insert(ignore_permissions=True)

			# 	notify_assignment(
			# 	frappe.session.user,
			# 	data[0].user_id,
			# 	self.doctype,
			# 	self.name,
			# 	action="ASSIGN",
			# 	description=self.customer_name,
			# )
	  
def get_salesman_user(self):
	sql="""select  e.name , user_id from `tabSales Person` s inner join `tabEmployee` e on s.employee=e.name where s.employee 
 is not null and s.name="{0}" and e.user_id is not null """.format(self.custom_sales_excecutive)
	return frappe.db.sql(sql, as_dict=True)



	
