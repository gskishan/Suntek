import json

import frappe
from erpnext.stock.get_item_details import apply_price_list as erpnext_apply_price_list

from suntek_app.suntek.doctype.solar_panel_pricing_rule.solar_panel_pricing_rule import (
    get_price_from_solar_panel_pricing_rule,
)


@frappe.whitelist()
def apply_price_list_for_solar_panel(args, as_doc=False, doc=None):
    result = erpnext_apply_price_list(args, as_doc=as_doc, doc=doc)

    if isinstance(args, str):
        args = json.loads(args)
    if isinstance(args, dict):
        args = frappe._dict(args)

    height = None
    items = []

    if doc:
        if isinstance(doc, str):
            try:
                doc = json.loads(doc)
                items = doc.get("items", [])
                if isinstance(doc, dict):
                    height = doc.get("custom_height")
            except Exception:
                pass

        elif hasattr(doc, "get"):
            items = doc.get("items", [])
            height = doc.get("custom_height")
        elif isinstance(doc, dict):
            items = doc.get("items", [])
            height = doc.get("custom_height")
    if height and result and isinstance(result, dict) and "children" in result:
        for child in result["children"]:
            item_name = child.get("name")

            for item in items:
                if item.get("name") == item_name:
                    item_code = item.get("item_code")
                    kwp = item.get("qty", 1)

                    solar_panel_price = get_price_from_solar_panel_pricing_rule(
                        item_code=item_code,
                        kwp=kwp,
                        height=height,
                    )

                    if solar_panel_price:
                        child["price_list_rate"] = solar_panel_price
                    break

    return result
