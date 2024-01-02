from operator import itemgetter
import frappe


@frappe.whitelist()
def update_product_bundle_rate_price(item_code):
    selling_rate = 0
    buying_rate = 0
    if item_code:
        item_price_rate_selling = frappe.db.get_value("Item Price", {"item_code":item_code,"price_list":"Standard Selling"},["price_list_rate"])
        
        item_price_rate_buying = frappe.db.get_value("Item Price", {"item_code":item_code,"price_list":"Standard Buying"},["price_list_rate"])

    
        if item_price_rate_selling:
            selling_rate = item_price_rate_selling
        if item_price_rate_buying:
            buying_rate = item_price_rate_buying
        
    return selling_rate,buying_rate 

    
  

   
