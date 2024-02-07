import frappe

@frappe.whitelist()
def validate(self, method):
    if self.percentage != 0:
        change_rate = self.price_list_rate + (self.price_list_rate * (self.percentage / 100))
        self.db_set("price_list_rate", change_rate)
    if self.is_new() and self.price_list=="Standard Buying":
        new=frappe.new_doc("Item Price")
        new.price_list="Standard Selling"
        new.item_code=self.item_code
        new.price_list_rate=self.price_list_rate
        new.save()

@frappe.whitelist()
def on_save(self, method):
    pass

