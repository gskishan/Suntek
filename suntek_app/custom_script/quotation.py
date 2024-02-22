import frappe
@frappe.whitelist()
def validate(self,method):
    pass
    #for d in self.items:
        #d.custom_total_gst_rate=d.igst_rate+d.cgst_rate+d.sgst_rate
        #d.custom_total_gst_amount=d.igst_amount+d.cgst_amount+d.sgst_amount
