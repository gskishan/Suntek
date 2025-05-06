import frappe

from suntek_app.permissions import (
    base_permission_query_conditions,
    get_subordinate_conditions,
    get_subordinates,
    get_user_employee,
    is_document_assigned,
    is_document_shared,
)


def has_permission(doc, ptype="read", user=None):
    """Custom permission check for Quotation doctype"""
    user = user or frappe.session.user

    if user == "Administrator":
        return True

    if "System Manager" in frappe.get_roles(user):
        return True

    if doc.owner == user:
        return True

    if is_document_shared(doc.name, user) or is_document_assigned(doc.name, user, doc.doctype):
        return True

    employee = get_user_employee(user)
    if not employee:
        return False

    user_subordinates = get_subordinates(employee)

    doc_creator_employee = get_user_employee(doc.owner)
    if doc_creator_employee and doc_creator_employee in user_subordinates:
        return True

    return False


def get_permission_query_conditions(user):
    """Permission query conditions for Quotation doctype"""
    if user == "Administrator":
        return ""

    if "System Manager" in frappe.get_roles(user):
        return ""

    base_conditions = base_permission_query_conditions(user, "Quotation")
    subordinate_conditions = get_subordinate_conditions(user, "Quotation")

    return f"({base_conditions}{subordinate_conditions})"
