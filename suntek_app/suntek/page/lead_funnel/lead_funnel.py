import frappe
from frappe import _


def validate_filters(from_date, to_date, company):
    if from_date and to_date and (from_date >= to_date):
        frappe.throw(_("To Date must be greater than From Date"))
    if not company:
        frappe.throw(_("Please Select a Company"))


@frappe.whitelist()
def get_funnel_data(from_date, to_date, company):
    validate_filters(from_date, to_date, company)

    main_stages = [
        {"status": "Open", "color": "#16A085"},
        {"status": "Interested", "color": "#27AE60"},
        {"status": "Quotation", "color": "#8E44AD"},
        {"status": "Converted", "color": "#2ECC71"},
        {"status": "Do Not Contact", "color": "#7F8C8D"},
    ]

    data = []
    others_count = 0

    others_count = frappe.db.sql(
        """
        SELECT COUNT(*) as count 
        FROM `tabLead`
        WHERE status NOT IN ('Open', 'Interested', 'Quotation', 'Converted', 'Do Not Contact')
        AND (date(`creation`) between %s and %s)
        AND company = %s
    """,
        (from_date, to_date, company),
    )[0][0]

    for stage in main_stages:
        count = frappe.db.sql(
            """
            SELECT COUNT(*) as count 
            FROM `tabLead`
            WHERE status = %s 
            AND (date(`creation`) between %s and %s)
            AND company = %s
        """,
            (stage["status"], from_date, to_date, company),
        )[0][0]

        if count:
            data.append({"title": _(stage["status"]), "value": count, "color": stage["color"]})

    if others_count:
        data.append({"title": _("Others"), "value": others_count, "color": "#E67E22"})

    return data
