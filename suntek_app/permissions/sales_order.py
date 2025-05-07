import frappe

from suntek_app.permissions import (
    base_permission_query_conditions,
    get_employee_from_sales_person,
    get_subordinate_conditions,
    get_subordinates,
    get_user_employee,
    is_document_assigned,
    is_document_shared,
)


def has_permission(doc, ptype="read", user=None):
    """Custom permission check for Sales Order doctype"""
    user = user or frappe.session.user

    if user == "Administrator":
        return True

    if "System Manager" in frappe.get_roles(user):
        return True
    if "Sales Master Manager" in frappe.get_roles(user):
        return True

    if doc.owner == user:
        return True

    if is_document_shared(doc.name, user) or is_document_assigned(doc.name, user, doc.doctype):
        return True

    employee = get_user_employee(user)
    if not employee:
        return False

    sales_person = doc.get("sales_person")
    if sales_person:
        sales_person_employee = get_employee_from_sales_person(sales_person)
        if sales_person_employee and sales_person_employee == employee:
            return True

    user_subordinates = get_subordinates(employee)

    doc_creator_employee = get_user_employee(doc.owner)
    if doc_creator_employee and doc_creator_employee in user_subordinates:
        return True

    if sales_person:
        sales_person_employee = get_employee_from_sales_person(sales_person)
        if sales_person_employee and sales_person_employee in user_subordinates:
            return True

    return False


def get_permission_query_conditions(user):
    """Permission query conditions for Sales Order doctype"""
    if user == "Administrator":
        return ""

    if "System Manager" in frappe.get_roles(user):
        return ""

    if "Sales Master Manager" in frappe.get_roles(user):
        return ""

    base_conditions = base_permission_query_conditions(user, "Sales Order")
    subordinate_conditions = get_subordinate_conditions(user, "Sales Order")

    employee = get_user_employee(user)
    sales_person_condition = ""

    if employee:
        sales_person_condition = f""" OR EXISTS (
            SELECT 1 FROM `tabSales Person`
            WHERE `tabSales Person`.employee = {frappe.db.escape(employee)}
            AND `tabSales Person`.name = `tabSales Order`.sales_person
        )"""

        subordinate_employees = get_subordinates(employee, include_self=False)

        if subordinate_employees:
            quoted_employees = ", ".join([frappe.db.escape(e) for e in subordinate_employees])
            sales_person_condition += f""" OR EXISTS (
                SELECT 1 from `tabSales Person`
                WHERE `tabSales Person`.employee IN ({quoted_employees})
                AND `tabSales Person`.name = `tabSales Order`.sales_person
            )"""

    return f"({base_conditions}{subordinate_conditions}{sales_person_condition})"
