import frappe
@frappe.whitelist()
def validate(self,method):
        frappe.errprint("working")
        if self.percentage !=0:
            change_rate=self.price_list_rate+ ( self.price_list_rate * self.price_list_rate)
            self.db_set("price_list_rate",change_rate)
