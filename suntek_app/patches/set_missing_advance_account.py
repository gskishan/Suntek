import frappe


def execute():
    try:
        advances_without_advance_account = frappe.db.get_list(
            "Employee Advance",
            filters={
                "advance_account": "",
                "docstatus": ["!=", 2],
            },
            pluck="name",
        )

        if not advances_without_advance_account:
            print("No Employee Advances found without advance account.")
            return

        default_other_expenses_account = frappe.db.get_value(
            "Company",
            "Suntek Energy Systems Pvt. Ltd.",
            "custom_default_employee_other_expense_account",
        )

        if not default_other_expenses_account:
            print("No default other expenses account found for the company.")
            return

        count = 0

        for advance in advances_without_advance_account:
            try:
                frappe.db.set_value(
                    "Employee Advance",
                    advance,
                    "advance_account",
                    default_other_expenses_account,
                    update_modified=False,
                )

                count += 1
                print(f"Updated {advance}")
            except Exception as e:
                print(f"Error updating advance account for {advance}: {e}")
                frappe.log_error(title="Error updating advance account", message=str(e))

        frappe.db.commit()

    except Exception as e:
        print(f"Error in set_missing_advance_account: {e}")

        frappe.db.rollback()
        frappe.log_error(title="Error in patch set_missing_advance_account", message=str(e))
