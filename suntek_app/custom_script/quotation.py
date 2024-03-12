import frappe
@frappe.whitelist()
def validate(self,method):
    pass
    #for d in self.items:
        #d.custom_total_gst_rate=d.igst_rate+d.cgst_rate+d.sgst_rate
        #d.custom_total_gst_amount=d.igst_amount+d.cgst_amount+d.sgst_amount


@frappe.whitelist()
def get_grandtotal(quotation=None):
    if quotation:
        qt=frappe.get_doc("Quotation",quotation)
        gt_grand=qt.grand_total
        return gt_grand
