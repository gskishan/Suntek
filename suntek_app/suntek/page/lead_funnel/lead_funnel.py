import frappe
from frappe import _


def validate_filters(from_date, to_date, company):
    if from_date and to_date and (from_date >= to_date):
        frappe.throw(_("To Date must be greater than From Date"))
    if not company:
        frappe.throw(_("Please Select a Company"))


@frappe.whitelist()
def get_funnel_data(from_date, to_date, company, lead_owner=None, source=None):
    validate_filters(from_date, to_date, company)

    main_stages = [
        {"status": "Open", "color": "#2C9BC8"},
        {"status": "Interested", "color": "#4CAF50"},
        {"status": "Quotation", "color": "#9C27B0"},
        {"status": "Converted", "color": "#28A745"},
        {"status": "Do Not Contact", "color": "#DC3545"},
    ]

    conditions = []
    values = [from_date, to_date, company]

    if lead_owner:
        conditions.append("lead_owner = %s")
        values.append(lead_owner)

    if source:
        conditions.append("source = %s")
        values.append(source)

    additional_conditions = " AND " + " AND ".join(conditions) if conditions else ""

    data = []
    others_count = frappe.db.sql(
        """
        SELECT COUNT(*) as count 
        FROM `tabLead` 
        WHERE status NOT IN ('Open', 'Interested', 'Quotation', 'Converted', 'Do Not Contact')
        AND (date(`creation`) between %s and %s)
        AND company = %s
        {}
    """.format(
            additional_conditions
        ),
        tuple(values),
    )[0][0]

    for stage in main_stages:
        count = frappe.db.sql(
            """
            SELECT COUNT(*) as count 
            FROM `tabLead`
            WHERE status = %s 
            AND (date(`creation`) between %s and %s)
            AND company = %s
            {}
        """.format(
                additional_conditions
            ),
            (stage["status"],) + tuple(values),
        )[0][0]

        if count:
            data.append({"title": _(stage["status"]), "value": count, "color": stage["color"]})

    if others_count:
        data.append({"title": _("Others"), "value": others_count, "color": "#FD7E14"})

    return data
