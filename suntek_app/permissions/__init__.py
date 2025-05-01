import frappe


"""
Direct Subordinate - An Employee whose `reports_to` is set to Employee 'x' directly reports to 'x'
Indirect Subordinate - An Employee whose `reports_to` is set to Employee 'x',
                       and Emplyee 'x''s `reports_to` is set to 'y' indirectly reports to 'y'
"""


def get_user_employee(user=None):
    """Get the Employee linked to a user"""
    user = user or frappe.session.user
    employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
    return employee


def get_employee_user(employee):
    """Get the User linked to an Employee"""
    return frappe.db.get_value("Employee", employee, "user_id")


def get_subordinates(employee, include_self=True):
    """Get all subordinates (direct and indirect) of an employee"""
    if not employee:
        return []

    subordinates = set()
    if include_self:
        subordinates.add(employee)

    direct_subordinates = frappe.get_all("Employee", filters={"reports_to": employee}, pluck="name")

    for subordinate in direct_subordinates:
        subordinates.add(subordinate)
        subordinates.update(get_subordinates(subordinate, include_self=False))

    return list(subordinates)


def get_subordinate_users(employee):
    """Get user IDs of all subordinates (direct and indirect) of an employee"""
    subordinate_employees = get_subordinates(employee)

    users = []
    for emp in subordinate_employees:
        user = get_employee_user(emp)
        if user:
            users.append(user)

    return users


def has_permission(doc, ptype="read", user=None):
    """
    Custom permission check function for document-level permissions
    Returns True if the user has permission, False otherwise
    """
    user = user or frappe.session.user

    print(f"Permission check for {doc.doctype} {doc.name} by {user}")

    if user == "Administrator":
        return True

    if "System Manager" in frappe.get_roles(user):
        return True

    if doc.doctype == "Lead":
        if doc.get("lead_owner") == user:
            return True

        if frappe.get_all(
            "DocShare",
            filters={"share_name": doc.name, "user": user, "read": 1},
            limit=1,
        ):
            return True

        if frappe.get_all(
            "ToDo",
            filters={"reference_type": doc.doctype, "reference_name": doc.name, "owner": user},
            limit=1,
        ):
            return True

        employee = get_user_employee(user)
        if employee:
            allowed_users = get_subordinate_users(employee)
            if doc.owner in allowed_users or doc.get("lead_owner") in allowed_users:
                return True

        return False

    if doc.doctype == "Opportunity" and doc.get("opportunity_owner") == user:
        return True

    if frappe.get_all(
        "DocShare",
        filters={"share_name": doc.name, "user": user, "read": 1},
        limit=1,
    ):
        return True

    if frappe.get_all(
        "ToDo",
        filters={"reference_type": doc.doctype, "reference_name": doc.name, "owner": user},
        limit=1,
    ):
        return True

    employee = get_user_employee(user)
    if not employee:
        return False

    allowed_users = get_subordinate_users(employee)
    allowed_users.append(user)

    if doc.owner in allowed_users:
        return True

    return False


def get_permission_query_conditions(user, doctype):
    """
    Returns query conditions for list views and reports
    This ensures users only see their own documents and their subordinates' documents in lists
    """
    if user == "Administrator":
        return ""

    if "System Manager" in frappe.get_roles(user):
        return ""

    special_owner_field = None
    if doctype == "Lead":
        special_owner_field = "lead_owner"
    elif doctype == "Opportunity":
        special_owner_field = "opportunity_owner"

    employee = get_user_employee(user)
    if not employee:
        shared_condition = f"""EXISTS (SELECT 1 FROM `tabDocShare`
                              WHERE `tabDocShare`.share_name = `tab{doctype}`.name
                              AND `tabDocShare`.user = {frappe.db.escape(user)}
                              AND `tabDocShare`.read = 1)"""

        assigned_condition = f"""EXISTS (SELECT 1 FROM `tabToDo`
                               WHERE `tabToDo`.reference_type = {frappe.db.escape(doctype)}
                               AND `tabToDo`.reference_name = `tab{doctype}`.name
                               AND `tabToDo`.owner = {frappe.db.escape(user)})"""

        special_owner_condition = ""
        if special_owner_field:
            special_owner_condition = f" OR `{special_owner_field}` = {frappe.db.escape(user)}"

        return f"({shared_condition} OR {assigned_condition}{special_owner_condition})"

    allowed_users = get_subordinate_users(employee)
    allowed_users.append(user)

    hierarchy_condition = ""
    if allowed_users:
        quoted_users = [frappe.db.escape(u) for u in allowed_users]
        hierarchy_condition = f"""`owner` in ({", ".join(quoted_users)})"""

        if special_owner_field:
            hierarchy_condition += f""" OR `{special_owner_field}` in ({", ".join(quoted_users)})"""

    shared_condition = f"""EXISTS (SELECT 1 FROM `tabDocShare`
                          WHERE `tabDocShare`.share_name = `tab{doctype}`.name
                          AND `tabDocShare`.user = {frappe.db.escape(user)}
                          AND `tabDocShare`.read = 1)"""

    assigned_condition = f"""EXISTS (SELECT 1 FROM `tabToDo`
                           WHERE `tabToDo`.reference_type = {frappe.db.escape(doctype)}
                           AND `tabToDo`.reference_name = `tab{doctype}`.name
                           AND `tabToDo`.owner = {frappe.db.escape(user)})"""

    return f"({hierarchy_condition} OR {shared_condition} OR {assigned_condition})"
