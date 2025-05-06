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
    user = user or frappe.session.user

    if user == "Administrator":
        return True
    if "System Manager" in frappe.get_roles(user):
        return True
    if doc.owner == user:
        return True

    if doc.get("lead_owner") == user:
        return True

    if is_document_shared(doc.name, user) or is_document_assigned(doc.name, user, doc.doctype):
        return True

    employee = get_user_employee(user)

    if not employee:
        return False

    user_subordinates = get_subordinates(employee)
    doc_creator_employee = get_user_employee(employee)

    if doc_creator_employee and doc_creator_employee in user_subordinates:
        return True

    doc_owner_employee = get_user_employee(doc.get("lead_owner"))
    if doc_owner_employee and doc_owner_employee in user_subordinates:
        return True

    return False


def get_permission_query_conditions(user):
    if user == "Administrator":
        return ""

    if "System Manager" in frappe.get_roles(user):
        return ""

    special_owner_field = "lead_owner"

    base_conditions = base_permission_query_conditions(user, "Lead", special_owner_field)
    subordinate_conditions = get_subordinate_conditions(user, "Lead", special_owner_field)

    return f"({base_conditions}{subordinate_conditions})"
