import frappe


def execute():
    excluded_custom_fields = [
        "Company-custom_default_employee_other_expense_account",
        "Delivery Request-workflow_state1",
        "Delivery Payment-custom_sales_amount",
        "Employee Advance-custom_column_break_crsgc",
        "Delivery Request-custom_delivery_request_purpose",
        "Employee Advance-custom_advance_type",
        "Delivery Request-custom_approver",
        "Sales Order-custom_dispatch_status",
        "Sales Order-custom_outstanding",
        "Delivery Request-custom_payment_schedules",
        "Delivery Request-custom_advance",
        "Delivery Request-custom_payment_from_sales_order",
        "Sales Order-custom_advance_amount",
        "Sales Invoice-custom_advance_payment",
        "Project-custom_state",
        "Project-custom_branch",
        "Project-custom_branch",
        "Opportunity-custom_branch",
    ]
    excluded_property_setters = [
        "Employee Advance-advance_account-default",
        "Employee Advance-advance_account-fetch_from",
        "Employee Advance-advance_account-read_only",
        "Sales Order-payment_schedule-allow_on_submit",
        "Delivery Request-custom_approver-in_list_view",
        "Sales Order-custom_outstanding-in_list_view",
        "Sales Invoice-payment_schedule-allow_on_submit",
        "Opportunity-custom_suntek_state-reqd",
        "Sales Order-state-fetch_from",
        "Sales Order-branch-fetch_from",
        "Purchase Order-state-fetch_from",
        "Purchase Order-branch-fetch_from",
        "Purchase Receipt-state-fetch_from",
        "Purchase Receipt-branch-fetch_from",
        "Purchase Invoice-state-fetch_from",
        "Purchase Invoice-branch-fetch_from",
        "Delivery Note-state-fetch_from",
        "Delivery Note-branch-fetch_from",
        "Sales Invoice-state-fetch_from",
        "Sales Invoice-branch-fetch_from",
        "Purchase Order Item-state-fetch_from",
        "Purchase Order Item-branch-fetch_from",
        "Purchase Receipt Item-state-fetch_from",
        "Purchase Receipt Item-branch-fetch_from",
        "Purchase Invoice Item-state-fetch_from",
        "Purchase Invoice Item-branch-fetch_from",
        "Delivery Note Item-state-fetch_from",
        "Delivery Note Item-branch-fetch_from",
        "Sales Invoice Item-state-fetch_from",
        "Sales Invoice Item-branch-fetch_from",
        "Journal Entry Account-state-fetch_from",
        "Journal Entry Account-branch-fetch_from",
        "Stock Entry Detail-state-fetch_from",
        "Stock Entry Detail-branch-fetch_from",
        "Material Request Item-state-fetch_from",
        "Material Request Item-branch-fetch_from",
        "Payment Entry-state-fetch_from",
        "Payment Entry-branch-fetch_from",
        "Stock Entry-state-fetch_from",
        "Stock Entry-branch-fetch_from",
        "Expense Claim Detail-state-fetch_from",
        "Expense Claim Detail-branch-fetch_from",
        "Expense Claim-state-fetch_from",
        "Expense Claim-branch-fetch_from",
    ]

    excluded_cf_str = "', '".join(excluded_custom_fields)
    excluded_ps_str = "', '".join(excluded_property_setters)

    # Get counts before update
    pre_custom_fields = frappe.db.sql(f"""
        SELECT COUNT(*) 
        FROM `tabCustom Field`
        WHERE (module IS NULL OR module != 'suntek')
        AND name NOT IN ('{excluded_cf_str}')
    """)[0][0]

    pre_property_setters = frappe.db.sql(f"""
        SELECT COUNT(*) 
        FROM `tabProperty Setter`
        WHERE (module IS NULL OR module != 'suntek')
        AND name NOT IN ('{excluded_ps_str}')
    """)[0][0]

    # Update custom fields
    frappe.db.sql(f"""
        UPDATE `tabCustom Field`
        SET module = 'suntek'
        WHERE (module IS NULL OR module != 'suntek')
        AND name NOT IN ('{excluded_cf_str}')
    """)

    # Update property setters
    frappe.db.sql(f"""
        UPDATE `tabProperty Setter`
        SET module = 'suntek'
        WHERE (module IS NULL OR module != 'suntek')
        AND name NOT IN ('{excluded_ps_str}')
    """)

    frappe.db.commit()

    # Count how many were updated
    cf_count = pre_custom_fields
    ps_count = pre_property_setters

    print(f"Updated {cf_count} custom fields and {ps_count} property setters to module 'suntek'")

    # Check excluded fields
    cf_excluded = frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabCustom Field` WHERE name IN ('{excluded_cf_str}') AND (module IS NULL OR module != 'suntek')"
    )[0][0]
    ps_excluded = frappe.db.sql(
        f"SELECT COUNT(*) FROM `tabProperty Setter` WHERE name IN ('{excluded_ps_str}') AND (module IS NULL OR module != 'suntek')"
    )[0][0]

    print(
        f"Confirmed {cf_excluded}/{len(excluded_custom_fields)} excluded custom fields and {ps_excluded}/{len(excluded_property_setters)} excluded property setters were preserved"
    )
