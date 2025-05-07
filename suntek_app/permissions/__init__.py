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


def is_document_shared(doc_name, user, doctype=None):
    """Check if document is shared with the user"""
    return frappe.get_all(
        "DocShare",
        filters={"share_name": doc_name, "user": user, "read": 1},
        limit=1,
    )


def is_document_assigned(doc_name, user, doctype):
    """Check if document is assigned to the user"""
    return frappe.get_all(
        "ToDo",
        filters={"reference_type": doctype, "reference_name": doc_name, "owner": user},
        limit=1,
    )


def base_permission_query_conditions(user, doctype, special_owner_field=None):
    """Generate base permission query conditions that apply to all doctypes"""
    shared_condition = f"""EXISTS (SELECT 1 FROM `tabDocShare`
                          WHERE `tabDocShare`.share_name = `tab{doctype}`.name
                          AND `tabDocShare`.user = {frappe.db.escape(user)}
                          AND `tabDocShare`.read = 1)"""

    assigned_condition = f"""EXISTS (SELECT 1 FROM `tabToDo`
                           WHERE `tabToDo`.reference_type = {frappe.db.escape(doctype)}
                           AND `tabToDo`.reference_name = `tab{doctype}`.name
                           AND `tabToDo`.owner = {frappe.db.escape(user)})"""

    # owner_condition = f"`owner` = {frappe.db.escape(user)}"
    owner_condition = f"`tab{doctype}`.`owner` = {frappe.db.escape(user)}"

    special_owner_condition = ""
    if special_owner_field:
        special_owner_condition = f" OR `{special_owner_field}` = {frappe.db.escape(user)}"

    base_conditions = f"({owner_condition}{special_owner_condition} OR {shared_condition} OR {assigned_condition})"
    return base_conditions


def get_subordinate_conditions(user, doctype, special_owner_field=None):
    """Generate subordinate-related conditions for permission queries"""
    employee = get_user_employee(user)
    if not employee:
        return ""

    subordinate_employees = get_subordinates(employee, include_self=False)
    if not subordinate_employees:
        return ""

    subordinate_users = []
    for emp in subordinate_employees:
        emp_user = get_employee_user(emp)
        if emp_user:
            subordinate_users.append(emp_user)

    if not subordinate_users:
        return ""

    subordinate_conditions = []

    if subordinate_users:
        quoted_users = [frappe.db.escape(u) for u in subordinate_users]
        # subordinate_conditions.append(f"`owner` in ({', '.join(quoted_users)})")
        subordinate_conditions.append(f"`tab{doctype}`.`owner` in ({', '.join(quoted_users)})")

    if special_owner_field and subordinate_users:
        quoted_users = [frappe.db.escape(u) for u in subordinate_users]
        subordinate_conditions.append(f"`{special_owner_field}` in ({', '.join(quoted_users)})")

    if subordinate_conditions:
        return f" OR ({' OR '.join(subordinate_conditions)})"
    return ""


def get_employee_from_sales_person(sales_person):
    if not sales_person:
        return None
    return frappe.db.get_value("Sales Person", sales_person, "employee")
