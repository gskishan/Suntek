# import frappe

# @frappe.whitelist()
# def update_product_bundle_rate_price(docname):
#     product_bundle_doc = frappe.get_doc("Product Bundle", docname)

#     for item in product_bundle_doc.items:
#         item_price_rate = frappe.db.get_value("Item Price", {"item_code": item.item_code}, "price_list_rate")
         
#         if item_price_rate is not None:
        
#             calculated_amount = item.qty * item_price_rate

#             frappe.db.set_value("Product Bundle Item", item.name, "rate", item_price_rate)
#             frappe.db.set_value("Product Bundle Item", item.name, "custom_amount", calculated_amount)
#         else:
#             frappe.db.set_value("Product Bundle Item", item.name, "rate", 0)
#             frappe.db.set_value("Product Bundle Item", item.name, "custom_amount", 0)
    
#     return item

   
