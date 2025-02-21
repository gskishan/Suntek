import frappe


def execute():
    sfg_items = frappe.db.get_list("Item", filters={"custom_is_sfg": 1}, pluck="name")

    if not sfg_items:
        return

    frappe.db.sql(
        """
        UPDATE `tabBOM Item`
        SET `custom_is_sfg` = 1
        WHERE item_code IN %(items)s
        """,
        {"items": sfg_items},
    )

    frappe.db.commit()
