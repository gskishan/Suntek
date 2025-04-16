import frappe


def get_permission_query_conditions(user=None, doctype=None):
    """
    Permission query conditions for Lead doctype.
    If user is Sales Manager, they can see all leads.
    Otherwise, users can only see leads where:
        1. They are the lead_owner
        2. The document is shared with them via DocShare
    """
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return ""

    if "Sales Manager" in frappe.get_roles(user):
        return ""

    if not frappe.has_permission("Lead", "read", user=user):
        return "1=0"

    shared_leads = frappe.db.sql_list(
        """
        SELECT DISTINCT share_name
        FROM `tabDocShare`
        WHERE user=%s AND share_doctype='Lead' AND `read`=1
    """,
        user,
    )

    conditions = []

    conditions.append(f"(`tabLead`.`lead_owner` = '{user}')")

    if shared_leads:
        shared_leads_str = "', '".join(shared_leads)
        conditions.append(f"(`tabLead`.`name` IN ('{shared_leads_str}'))")

    if conditions:
        return "(" + " OR ".join(conditions) + ")"
    else:
        return "1=0"


def has_permission(doc, user=None, permission_type=None):
    """
    Permission check for Lead.
    If user is Sales Manager, they have permissions.
    Otherwise, users only have permissions on leads where:
        1. They are the lead_owner
        2. The document is shared with them via DocShare
    """
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return True

    if "Sales Manager" in frappe.get_roles(user):
        return True

    if permission_type == "create":
        return True

    if getattr(doc, "is_new", None) or not doc.name:
        return True

    if doc.lead_owner == user:
        return True

    filters = {"share_doctype": "Lead", "share_name": doc.name, "user": user}

    if permission_type:
        filters[permission_type] = 1

    if frappe.db.exists("DocShare", filters):
        return True

    return False
