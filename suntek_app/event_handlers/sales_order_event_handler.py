import frappe
from frappe import _


def update_cppo_from_sales_order(doc, method=None):
    if doc.get("__islocal"):
        return

    if (
        not hasattr(doc, "custom_to_channel_partner")
        or not doc.custom_to_channel_partner
    ):
        return

    try:
        linked_cppo = frappe.get_doc(
            "Channel Partner Purchase Order", {"sales_order": doc.name}
        )

        if not linked_cppo:
            return

        update_required = False
        update_fields = {}

        items_updated = update_cppo_items(linked_cppo, doc)
        if items_updated:
            update_required = True
            update_fields.update(
                {
                    "total": doc.total,
                    "total_qty": sum(item.qty for item in doc.items),
                }
            )

        taxes_updated = update_cppo_taxes(linked_cppo, doc)
        if taxes_updated:
            update_required = True
            update_fields.update(
                {
                    "total_taxes_and_charges": doc.total_taxes_and_charges,
                }
            )

        terms_updated = update_cppo_terms(linked_cppo, doc)
        if terms_updated:
            update_required = True

        if update_required:
            update_fields.update(
                {
                    "grand_total": doc.grand_total,
                    "balance_amount": doc.grand_total
                    - (linked_cppo.advance_amount or 0),
                }
            )

            if update_fields:
                for field, value in update_fields.items():
                    linked_cppo.db_set(field, value, update_modified=False)

                frappe.get_doc(
                    {
                        "doctype": "Comment",
                        "comment_type": "Info",
                        "reference_doctype": "Channel Partner Purchase Order",
                        "reference_name": linked_cppo.name,
                        "content": f"Updated automatically from Sales Order {doc.name}",
                    }
                ).insert(ignore_permissions=True)

                frappe.msgprint(
                    _(
                        "Channel Partner Purchase Order {0} has been updated to match changes in Sales Order {1}"
                    ).format(linked_cppo.name, doc.name),
                    alert=True,
                    indicator="green",
                )

    except Exception as e:
        frappe.log_error(
            f"Error updating CPPO from Sales Order: {str(e)}", "CPPO Update Error"
        )


def update_cppo_items(cppo, sales_order):
    """
    Update items in Channel Partner Purchase Order from Sales Order.
    Returns True if items were updated, False otherwise.
    """

    so_items = get_so_items(sales_order)

    if not items_changed(cppo.items, so_items):
        return False

    frappe.db.sql(
        """DELETE FROM `tabChannel Partner Purchase Order Item` 
                     WHERE parent = %s""",
        cppo.name,
    )

    for item in so_items:
        cppo_item = frappe.new_doc(
            "Channel Partner Purchase Order Item", parent_doc=cppo
        )

        cppo_item.update(
            {
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "description": item["description"],
                "qty": item["qty"],
                "uom": item["uom"],
                "rate": item["rate"],
                "amount": item["amount"],
                "parenttype": "Channel Partner Purchase Order",
                "parentfield": "items",
                "parent": cppo.name,
            }
        )
        cppo_item.db_insert()

    return True


def update_cppo_taxes(cppo, sales_order):
    """
    Update taxes in Channel Partner Purchase Order from Sales Order.
    Returns True if taxes were updated, False otherwise.
    """

    so_taxes = get_so_taxes(sales_order)

    if not taxes_changed(cppo.get("taxes", []), so_taxes):
        return False

    frappe.db.sql(
        """DELETE FROM `tabSales Taxes and Charges` 
                     WHERE parent = %s AND parenttype = 'Channel Partner Purchase Order'""",
        cppo.name,
    )

    for tax in so_taxes:
        cppo_tax = frappe.new_doc("Sales Taxes and Charges", parent_doc=cppo)

        cppo_tax.update(
            {
                "charge_type": tax["charge_type"],
                "account_head": tax["account_head"],
                "description": tax["description"],
                "rate": tax["rate"],
                "tax_amount": tax["tax_amount"],
                "total": tax["total"],
                "parenttype": "Channel Partner Purchase Order",
                "parentfield": "taxes",
                "parent": cppo.name,
            }
        )
        cppo_tax.db_insert()

    if hasattr(sales_order, "taxes_and_charges") and sales_order.taxes_and_charges:
        cppo.db_set(
            "taxes_and_charges_template",
            sales_order.taxes_and_charges,
            update_modified=False,
        )

    return True


def update_cppo_terms(cppo, sales_order):
    """
    Update terms & conditions in Channel Partner Purchase Order from Sales Order.
    Returns True if terms were updated, False otherwise.
    """

    cppo_tc_name = cppo.terms_and_conditions or ""
    so_tc_name = getattr(sales_order, "tc_name", "") or ""

    cppo_terms = cppo.terms_and_conditions_details or ""
    so_terms = getattr(sales_order, "terms", "") or ""

    if cppo_tc_name != so_tc_name or cppo_terms != so_terms:
        cppo.db_set("terms_and_conditions", so_tc_name, update_modified=False)
        cppo.db_set("terms_and_conditions_details", so_terms, update_modified=False)
        return True

    return False


def get_so_items(sales_order):
    items = []
    for item in sales_order.items:
        items.append(
            {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": item.amount,
            }
        )
    return items


def get_so_taxes(sales_order):
    taxes = []

    if not hasattr(sales_order, "taxes") or not sales_order.taxes:
        return taxes

    for tax in sales_order.taxes:
        taxes.append(
            {
                "charge_type": tax.charge_type,
                "account_head": tax.account_head,
                "description": tax.description,
                "rate": tax.rate,
                "tax_amount": tax.tax_amount,
                "total": tax.total,
            }
        )

    return taxes


def items_changed(cppo_items, so_items):
    if len(cppo_items) != len(so_items):
        return True

    cppo_item_map = {}
    for item in cppo_items:
        key = f"{item.item_code}_{item.qty}_{item.rate}"
        cppo_item_map[key] = item

    for so_item in so_items:
        key = f"{so_item['item_code']}_{so_item['qty']}_{so_item['rate']}"
        if key not in cppo_item_map:
            return True

    return False


def taxes_changed(cppo_taxes, so_taxes):
    if len(cppo_taxes) != len(so_taxes):
        return True

    cppo_tax_map = {}
    for tax in cppo_taxes:
        key = f"{tax.account_head}_{tax.rate}"
        cppo_tax_map[key] = tax

    for so_tax in so_taxes:
        key = f"{so_tax['account_head']}_{so_tax['rate']}"
        if key not in cppo_tax_map:
            return True

    return False


def update_cppo_items(cppo, sales_order):
    so_items = get_so_items(sales_order)

    if not items_changed(cppo.items, so_items):
        return False

    frappe.db.sql(
        """DELETE FROM `tabChannel Partner Purchase Order Item` 
                     WHERE parent = %s""",
        cppo.name,
    )

    for item in so_items:
        cppo_item = frappe.new_doc(
            "Channel Partner Purchase Order Item", parent_doc=cppo
        )

        cppo_item.update(
            {
                "item_code": item["item_code"],
                "item_name": item["item_name"],
                "description": item["description"],
                "qty": item["qty"],
                "uom": item["uom"],
                "rate": item["rate"],
                "amount": item["amount"],
                "parenttype": "Channel Partner Purchase Order",
                "parentfield": "items",
                "parent": cppo.name,
            }
        )
        cppo_item.db_insert()

    return True


def update_cppo_taxes(cppo, sales_order):
    so_taxes = get_so_taxes(sales_order)

    if not taxes_changed(cppo.get("taxes", []), so_taxes):
        return False

    frappe.db.sql(
        """DELETE FROM `tabSales Taxes and Charges` 
                     WHERE parent = %s AND parenttype = 'Channel Partner Purchase Order'""",
        cppo.name,
    )

    for tax in so_taxes:
        cppo_tax = frappe.new_doc("Sales Taxes and Charges", parent_doc=cppo)

        cppo_tax.update(
            {
                "charge_type": tax["charge_type"],
                "account_head": tax["account_head"],
                "description": tax["description"],
                "rate": tax["rate"],
                "tax_amount": tax["tax_amount"],
                "total": tax["total"],
                "parenttype": "Channel Partner Purchase Order",
                "parentfield": "taxes",
                "parent": cppo.name,
            }
        )
        cppo_tax.db_insert()

    if hasattr(sales_order, "taxes_and_charges") and sales_order.taxes_and_charges:
        cppo.db_set(
            "taxes_and_charges_template",
            sales_order.taxes_and_charges,
            update_modified=False,
        )

    return True


def update_cppo_terms(cppo, sales_order):
    cppo_tc_name = cppo.terms_and_conditions or ""
    so_tc_name = getattr(sales_order, "tc_name", "") or ""

    cppo_terms = cppo.terms_and_conditions_details or ""
    so_terms = getattr(sales_order, "terms", "") or ""
    print(so_terms)

    if cppo_tc_name != so_tc_name or cppo_terms != so_terms:
        cppo.db_set("terms_and_conditions", so_tc_name, update_modified=False)
        cppo.db_set("terms_and_conditions_details", so_terms, update_modified=False)
        return True

    return False


def get_so_items(sales_order):
    items = []
    for item in sales_order.items:
        items.append(
            {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "description": item.description,
                "qty": item.qty,
                "uom": item.uom,
                "rate": item.rate,
                "amount": item.amount,
            }
        )
    return items


def get_so_taxes(sales_order):
    taxes = []

    if not hasattr(sales_order, "taxes") or not sales_order.taxes:
        return taxes

    for tax in sales_order.taxes:
        taxes.append(
            {
                "charge_type": tax.charge_type,
                "account_head": tax.account_head,
                "description": tax.description,
                "rate": tax.rate,
                "tax_amount": tax.tax_amount,
                "total": tax.total,
            }
        )

    return taxes


def items_changed(cppo_items, so_items):
    if len(cppo_items) != len(so_items):
        return True

    cppo_item_map = {}
    for item in cppo_items:
        key = f"{item.item_code}_{item.qty}_{item.rate}"
        cppo_item_map[key] = item

    for so_item in so_items:
        key = f"{so_item['item_code']}_{so_item['qty']}_{so_item['rate']}"
        if key not in cppo_item_map:
            return True

    return False


def taxes_changed(cppo_taxes, so_taxes):
    if len(cppo_taxes) != len(so_taxes):
        return True

    cppo_tax_map = {}
    for tax in cppo_taxes:
        key = f"{tax.account_head}_{tax.rate}"
        cppo_tax_map[key] = tax

    for so_tax in so_taxes:
        key = f"{so_tax['account_head']}_{so_tax['rate']}"
        if key not in cppo_tax_map:
            return True

    return False
