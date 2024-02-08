import frappe

@frappe.whitelist()
def validate(self, method):
    # if self.percentage != 0:
    #     change_rate = self.price_list_rate + (self.price_list_rate * (self.percentage / 100))
    #     self.db_set("price_list_rate", change_rate)
    if self.is_new() and self.price_list=="Standard Buying":
        ss=frappe.get_doc("Price List","Standard Selling")
        new=frappe.new_doc("Item Price")
        new.price_list="Standard Selling"
        new.item_code=self.item_code
        new.price_list_rate=self.price_list_rate + (self.price_list_rate * (ss.percentage / 100))
        new.save()
