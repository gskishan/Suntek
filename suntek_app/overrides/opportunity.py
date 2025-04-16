import frappe


def get_permission_query_conditions(user=None, doctype=None):
    """
    Permission query conditions for Opportunity doctype.
    If user is Sales Manager, they can see all opportunities.
    Otherwise, users can only see opportunities where:
    1. They are the opportunity_owner
    2. The document is shared with them via DocShare
    """
    if not user:
        user = frappe.session.user

    if "System Manager" in frappe.get_roles(user):
        return ""

    if "Sales Manager" in frappe.get_roles(user):
        return ""

    if not frappe.has_permission("Opportunity", "read", user=user):
        return "1=0"

    shared_opportunities = frappe.db.sql_list(
        """
        SELECT DISTINCT share_name
        FROM `tabDocShare`
        WHERE user=%s AND share_doctype='Opportunity' AND `read`=1
    """,
        user,
    )

    conditions = []

    conditions.append(f"(`tabOpportunity`.`opportunity_owner` = '{user}')")

    if shared_opportunities:
        shared_opps_str = "', '".join(shared_opportunities)
        conditions.append(f"(`tabOpportunity`.`name` IN ('{shared_opps_str}'))")

    if conditions:
        return "(" + " OR ".join(conditions) + ")"
    else:
        return "1=0"


def has_permission(doc, user=None, permission_type=None):
    """
    Permission check for Opportunity.
    If user is Sales Manager, they have permissions.
    Otherwise, users only have permissions on opportunities where:
    1. They are the opportunity_owner
    2. The document is shared with them via DocShare
    """
    if not user:
        user = frappe.session.user

    log_permission_check(doc, user, permission_type)

    if "System Manager" in frappe.get_roles(user):
        return True

    if "Sales Manager" in frappe.get_roles(user):
        return True

    if permission_type == "create":
        return True

    if getattr(doc, "is_new", None) or not doc.name:
        return True

    if doc.opportunity_owner == user:
        return True

    filters = {"share_doctype": "Opportunity", "share_name": doc.name, "user": user}

    if permission_type:
        filters[permission_type] = 1

    if frappe.db.exists("DocShare", filters):
        return True

    return False


def log_permission_check(doc, user, permission_type):
    """Log permission check details for debugging"""
    try:
        if permission_type == "create":
            frappe.logger().info(f"PERMISSION CHECK: User {user} requesting {permission_type} for Opportunity")
            frappe.logger().info(f"User roles: {frappe.get_roles(user)}")
            frappe.logger().info(
                f"Doc details: is_new={getattr(doc, 'is_new', None)}, name={doc.name if hasattr(doc, 'name') else 'None'}"
            )
            frappe.logger().info(
                f"Has standard permission: {frappe.has_permission('Opportunity', permission_type, user=user)}"
            )
    except Exception as e:
        frappe.logger().error(f"Error in permission logging: {e}")
