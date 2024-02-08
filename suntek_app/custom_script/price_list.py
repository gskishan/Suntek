import frappe

@frappe.whitelist()
def validate(self, method):
	frappe.errprint("working")
	if self.percentage != 0:
		sql="""select * from `tabItem Price` where price_list="{0}" """.format(self.name)
		data=frappe.db.sql(sql,as_dict=True)
		frappe.errprint(data)
		if len(data)>100:
			frappe.enqueue(update_rate, queue='long', param1=self, param2=data)
		else:
			update_rate(self,data)
	   


def update_rate(self,data):
	frappe.errprint([len(data),"da])
	for d in data:
		doc=frappe.get_doc("Item Price",d.name)
		change_rate = doc.price_list_rate + (doc.price_list_rate * (self.percentage / 100))
		doc.db_set("price_list_rate", change_rate)
