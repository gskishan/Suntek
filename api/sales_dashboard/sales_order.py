import json
import re
import urllib.parse
from collections import defaultdict

import frappe

from suntek_app.suntek.utils.api_handler import create_api_response


def _get_sales_orders_by_department(filters=None, limit=100):
    where_clause = "1=1"
    show_sql = filters.pop("show_sql", False) if filters else False

    frappe.logger().info(f"_get_sales_orders_by_department called with filters: {filters}")

    if filters:
        if filters.get("from_date"):
            where_clause += f" AND creation >= '{filters['from_date']}'"
        if filters.get("to_date"):
            where_clause += f" AND creation <= '{filters['to_date']}'"
        if filters.get("territory"):
            territory_values = filters["territory"].split(",")
            territory_list = ", ".join([f"'{t}'" for t in territory_values])
            where_clause += f" AND territory IN ({territory_list})"
        if filters.get("state"):
            state_values = filters["state"].split(",")
            state_list = ", ".join([f"'{s}'" for s in state_values])
            where_clause += f" AND custom_suntek_state IN ({state_list})"
        if filters.get("department"):
            department_values = filters["department"].split(",")
            department_list = ", ".join([f"'{d}'" for d in department_values])
            where_clause += f" AND custom_department IN ({department_list})"
        if filters.get("status"):
            status = filters["status"]
            # Handle status as a comma-separated list like other filters
            if "," in status:
                status_values = status.split(",")
                status_list = ", ".join([f"'{s}'" for s in status_values])
                where_clause += f" AND status IN ({status_list})"
                frappe.logger().info(f"Applying multiple status filter with values: {status_values}")
            else:
                where_clause += f" AND status = '{status}'"
                frappe.logger().info(f"Applying single status filter: {status}")
        if filters.get("type_of_case"):
            where_clause += f" AND custom_type_of_case = '{filters['type_of_case']}'"


def _get_sales_orders(filters=None, limit=100):
    frappe.logger().info(f"DEBUG STATE FILTER: Called _get_sales_orders with filters: {filters}")
    if filters and filters.get("state"):
        frappe.logger().info(f"DEBUG STATE FILTER: Filter includes state: {filters.get('state')}")

    where_clause = "1=1"
    show_sql = filters.pop("show_sql", False) if filters else False

    frappe.logger().info(f"_get_sales_orders called with filters: {filters}")

    if filters:
        if filters.get("from_date"):
            where_clause += f" AND creation >= '{filters['from_date']}'"
        if filters.get("to_date"):
            where_clause += f" AND creation <= '{filters['to_date']}'"
        if filters.get("territory"):
            territory_values = filters["territory"].split(",")
            territory_list = ", ".join([f"'{t}'" for t in territory_values])
            where_clause += f" AND territory IN ({territory_list})"
        if filters.get("state"):
            state_values = filters["state"].split(",")
            state_list = ", ".join([f"'{s}'" for s in state_values])
            frappe.logger().info(f"Applying state filter with values: {state_values}")
            where_clause += f" AND custom_suntek_state IN ({state_list})"
        if filters.get("city"):
            city_values = filters["city"].split(",")
            city_list = ", ".join([f"'{c}'" for c in city_values])
            where_clause += f" AND custom_suntek_city IN ({city_list})"
        if filters.get("district"):
            district_values = filters["district"].split(",")
            district_list = ", ".join([f"'{d}'" for d in district_values])
            where_clause += f" AND custom_suntek_district IN ({district_list})"
        if filters.get("department"):
            where_clause += f" AND custom_department = '{filters['department']}'"
        if filters.get("status"):
            status = filters["status"]
            # Handle status as a comma-separated list like other filters
            if "," in status:
                status_values = status.split(",")
                status_list = ", ".join([f"'{s}'" for s in status_values])
                where_clause += f" AND status IN ({status_list})"
                frappe.logger().info(f"Applying multiple status filter with values: {status_values}")
            else:
                where_clause += f" AND status = '{status}'"
                frappe.logger().info(f"Applying single status filter: {status}")
        if filters.get("type_of_case"):
            where_clause += f" AND custom_type_of_case = '{filters['type_of_case']}'"


@frappe.whitelist()
def get_sales_order_data():
    if not frappe.has_permission("Sales Order", "read"):
        return create_api_response(403, "error", "Access Denied: Insufficient permissions to view sales data", {})

    user_roles = frappe.get_roles(frappe.session.user)
    allowed_roles = ["System Manager", "Sales Manager"]

    if not any(role in user_roles for role in allowed_roles):
        return create_api_response(403, "error", "Access Denied: Requires System Manager or Sales Manager role", {})

    try:
        form_dict = frappe.local.form_dict
        frappe.logger().info(f"Form dict: {form_dict}")

        from_date = form_dict.get("from_date")
        to_date = form_dict.get("to_date")
        territory = form_dict.get("territory")
        state = form_dict.get("state")
        city = form_dict.get("city")
        district = form_dict.get("district")
        department = form_dict.get("department")
        status = form_dict.get("status")
        # No special JSON handling needed for status - will be processed like other filters

        type_of_case = form_dict.get("type_of_case")
        type_of_structure = form_dict.get("type_of_structure")
        min_capacity = form_dict.get("min_capacity")
        max_capacity = form_dict.get("max_capacity")
        sales_person = form_dict.get("sales_person")
        limit = form_dict.get("limit", 100)
        try:
            if limit == "all":
                limit = None
            else:
                limit = int(limit)
        except (ValueError, TypeError):
            limit = 100
        show_sql = form_dict.get("show_sql") == "1"

    except Exception as e:
        frappe.logger().error(f"Error getting parameters: {e}")

        # Fallback to request.args if form_dict fails
        from_date = frappe.request.args.get("from_date")
        to_date = frappe.request.args.get("to_date")
        territory = frappe.request.args.get("territory")
        state = frappe.request.args.get("state")
        city = frappe.request.args.get("city")
        district = frappe.request.args.get("district")
        department = frappe.request.args.get("department")
        status = frappe.request.args.get("status")
        # No special JSON handling needed for status - will be processed like other filters

        type_of_case = frappe.request.args.get("type_of_case")
        type_of_structure = frappe.request.args.get("type_of_structure")
        min_capacity = frappe.request.args.get("min_capacity")
        max_capacity = frappe.request.args.get("max_capacity")
        sales_person = frappe.request.args.get("sales_person")
        limit = frappe.request.args.get("limit", 100)
        try:
            if limit == "all":
                limit = None
            else:
                limit = int(limit)
        except (ValueError, TypeError):
            limit = 100
        show_sql = frappe.request.args.get("show_sql") == "1"

    filters = {
        "from_date": from_date,
        "to_date": to_date,
        "territory": territory,
        "state": state,
        "city": city,
        "district": district,
        "department": department,
        "status": status,
        "type_of_case": type_of_case,
        "type_of_structure": type_of_structure,
        "min_capacity": min_capacity,
        "max_capacity": max_capacity,
        "sales_person": sales_person,
        "show_sql": show_sql,
    }

    filters = {
        k: v
        for k, v in filters.items()
        if v is not None and (k not in ["state", "territory", "city", "district"] or v != "all")
    }

    frappe.logger().info(f"Processed Filters: {filters}")

    sales_orders = _get_sales_orders(filters, limit)

    return create_api_response(200, "success", "Sales Orders Fetched", sales_orders)


@frappe.whitelist()
def get_sales_order_data_by_department():
    if not frappe.has_permission("Sales Order", "read"):
        return create_api_response(403, "error", "Access Denied: Insufficient permissions to view sales data", {})

    user_roles = frappe.get_roles(frappe.session.user)
    allowed_roles = ["System Manager", "Sales Manager"]

    if not any(role in user_roles for role in allowed_roles):
        return create_api_response(403, "error", "Access Denied: Requires System Manager or Sales Manager role", {})

    try:
        form_dict = frappe.local.form_dict
        frappe.logger().info(f"Form dict: {form_dict}")

        from_date = form_dict.get("from_date")
        to_date = form_dict.get("to_date")
        territory = form_dict.get("territory")
        state = form_dict.get("state")
        department = form_dict.get("department")
        status = form_dict.get("status")
        # No special JSON handling needed for status - will be processed like other filters

        type_of_case = form_dict.get("type_of_case")
        type_of_structure = form_dict.get("type_of_structure")
        min_capacity = form_dict.get("min_capacity")
        max_capacity = form_dict.get("max_capacity")
        sales_person = form_dict.get("sales_person")
        limit = form_dict.get("limit", 100)
        try:
            if limit == "all":
                limit = None
            else:
                limit = int(limit)
        except (ValueError, TypeError):
            limit = 100
        show_sql = form_dict.get("show_sql") == "1"

    except Exception as e:
        frappe.logger().error(f"Error getting parameters: {e}")

        # Fallback to request.args if form_dict fails
        from_date = frappe.request.args.get("from_date")
        to_date = frappe.request.args.get("to_date")
        territory = frappe.request.args.get("territory")
        state = frappe.request.args.get("state")
        department = frappe.request.args.get("department")
        status = frappe.request.args.get("status")
        # No special JSON handling needed for status - will be processed like other filters

        type_of_case = frappe.request.args.get("type_of_case")
        type_of_structure = frappe.request.args.get("type_of_structure")
        min_capacity = frappe.request.args.get("min_capacity")
        max_capacity = frappe.request.args.get("max_capacity")
        sales_person = frappe.request.args.get("sales_person")
        limit = frappe.request.args.get("limit", 100)
        try:
            if limit == "all":
                limit = None
            else:
                limit = int(limit)
        except (ValueError, TypeError):
            limit = 100
        show_sql = frappe.request.args.get("show_sql") == "1"

    filters = {
        "from_date": from_date,
        "to_date": to_date,
        "territory": territory,
        "state": state,
        "department": department,
        "status": status,
        "type_of_case": type_of_case,
        "type_of_structure": type_of_structure,
        "min_capacity": min_capacity,
        "max_capacity": max_capacity,
        "sales_person": sales_person,
        "show_sql": show_sql,
    }

    filters = {
        k: v
        for k, v in filters.items()
        if v is not None and (k not in ["state", "territory", "department"] or v != "all")
    }

    frappe.logger().info(f"Department View - Processed Filters: {filters}")

    sales_orders = _get_sales_orders_by_department(filters, limit)

    return create_api_response(200, "success", "Sales Orders By Department Fetched", sales_orders)
