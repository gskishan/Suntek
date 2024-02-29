import frappe
@frappe.whitelist()
def get_emp(user):
  sql="""select e.cell_number,s.name from `tabEmployee` e inner join `tabSales Person` s on e.name=s.employee where user_id="{0}" """.format(user)
  data=(frappe.db.sql(sql,as_dict=True))
  if data:
    return data

@frappe.whitelist()
def on_update(self,method):
  from frappe.utils import nowdate
  if self.opportunity_owner:
    filters = {
			"reference_type": self.doctype,
			"reference_name": self.name,
			"status": "Open",
			"allocated_to": self.opportunity_owner,
		}
    if not frappe.get_all("ToDo", filters=filters):
      d = frappe.get_doc(
				{
					"doctype": "ToDo",
					"allocated_to": self.opportunity_owner,
					"reference_type": self.doctype,
					"reference_name": self.name,
					"description":self.customer_name,
					"priority": "Medium",
					"status": "Open",
					"date": nowdate(),
					"assigned_by": frappe.session.user,
					"assignment_rule": "",
				}
			).insert(ignore_permissions=True)
    
