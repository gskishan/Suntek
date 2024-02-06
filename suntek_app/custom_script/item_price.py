import frappe

@frappe.whitelist()
def validate(self, method):
    if self.percentage != 0:
        change_rate = self.price_list_rate + (self.price_list_rate * (self.percentage / 100))
        self.db_set("price_list_rate", change_rate)
