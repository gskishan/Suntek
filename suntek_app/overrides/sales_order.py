import frappe


@frappe.whitelist()
def make_sales_invoice(source_name, target_doc=None):
    from erpnext.selling.doctype.sales_order.sales_order import (
        make_sales_invoice as _make_sales_invoice,
    )

    si = _make_sales_invoice(source_name, target_doc)

    sales_order = frappe.get_doc("Sales Order", source_name)

    if sales_order.get("custom_channel_partner"):
        si.custom_channel_partner = sales_order.custom_channel_partner

        if si.custom_channel_partner:
            channel_partner = frappe.get_doc("Channel Partner", si.custom_channel_partner)

            si.custom_channel_partner_name = channel_partner.channel_partner_name
            si.custom_channel_partner_mobile = channel_partner.suntek_mobile_number

    return si
