import re
from collections import defaultdict

import frappe

from suntek_app.permissions.sales_order import get_permission_query_conditions
from suntek_app.suntek.utils.api_handler import create_api_response


def extract_capacity_number(capacity_str):
    if not capacity_str or capacity_str == "":
        return None

    capacity_str = str(capacity_str)

    matches = re.findall(r"(\d+\.?\d*)", capacity_str)
    if matches:
        return float(matches[0])
    return None


def get_department_abbreviation(department_name):
    if not department_name:
        return "Unknown"

    if "Domestic (Residential) Sales Team" in department_name:
        return "Domestic"
    elif "Channel Partner" in department_name:
        return "CHP"
    elif "Commercial & Industrial" in department_name or "C&I" in department_name:
        return "C&I"
    else:
        base_department = re.sub(r"\s*[-–—]\s*(SESP|S)$", "", department_name)

        abbr = "".join([word[0] for word in base_department.split() if word])
        return abbr


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

        from_date = form_dict.get("from_date")
        to_date = form_dict.get("to_date")
        territory = form_dict.get("territory")
        state = form_dict.get("state")
        city = form_dict.get("city")
        district = form_dict.get("district")
        department = form_dict.get("department")
        status = form_dict.get("status")
        type_of_case = form_dict.get("type_of_case")
        type_of_structure = form_dict.get("type_of_structure")
        min_capacity = form_dict.get("min_capacity")
        max_capacity = form_dict.get("max_capacity")
        sales_person = form_dict.get("sales_person")
        limit = form_dict.get("limit", 100)
        try:
            if limit == "all":
                limit = None
        except (ValueError, TypeError):
            limit = 100

    except Exception:
        from_date = frappe.request.args.get("from_date")
        to_date = frappe.request.args.get("to_date")
        territory = frappe.request.args.get("territory")
        state = frappe.request.args.get("state")
        city = frappe.request.args.get("city")
        district = frappe.request.args.get("district")
        department = frappe.request.args.get("department")
        status = frappe.request.args.get("status")
        type_of_case = frappe.request.args.get("type_of_case")
        type_of_structure = frappe.request.args.get("type_of_structure")
        min_capacity = frappe.request.args.get("min_capacity")
        max_capacity = frappe.request.args.get("max_capacity")
        sales_person = frappe.request.args.get("sales_person")
        limit = frappe.request.args.get("limit", 100)
        try:
            if limit == "all":
                limit = None
        except (ValueError, TypeError):
            limit = 100

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
    }

    filters = {
        k: v
        for k, v in filters.items()
        if v is not None and (k not in ["state", "territory", "city", "district"] or v != "all")
    }

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

        from_date = form_dict.get("from_date")
        to_date = form_dict.get("to_date")
        territory = form_dict.get("territory")
        state = form_dict.get("state")
        department = form_dict.get("department")
        status = form_dict.get("status")
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

    except Exception:
        from_date = frappe.request.args.get("from_date")
        to_date = frappe.request.args.get("to_date")
        territory = frappe.request.args.get("territory")
        state = frappe.request.args.get("state")
        department = frappe.request.args.get("department")
        status = frappe.request.args.get("status")
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
    }

    filters = {
        k: v
        for k, v in filters.items()
        if v is not None and (k not in ["state", "territory", "department"] or v != "all")
    }

    sales_orders = _get_sales_orders_by_department(filters, limit)

    return create_api_response(200, "success", "Sales Orders By Department Fetched", sales_orders)


def _get_sales_orders_by_department(filters=None, limit=100):
    where_clause = "1=1"

    permission_conditions = get_permission_query_conditions(frappe.session.user)
    if permission_conditions:
        where_clause += f" AND ({permission_conditions})"

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
            if "," in filters["status"]:
                status_values = filters["status"].split(",")
                status_list = ", ".join([f"'{s}'" for s in status_values])
                where_clause += f" AND status IN ({status_list})"
            else:
                where_clause += f" AND status = '{filters['status']}'"
        if filters.get("type_of_case"):
            where_clause += f" AND custom_type_of_case = '{filters['type_of_case']}'"
        if filters.get("type_of_structure"):
            where_clause += f" AND custom_type_of_structure = '{filters['type_of_structure']}'"
        if filters.get("min_capacity"):
            where_clause += f" AND CAST(REGEXP_REPLACE(custom_capacity, '[^0-9.]', '') AS DECIMAL(10,2)) >= {float(filters['min_capacity'])}"
        if filters.get("max_capacity"):
            where_clause += f" AND CAST(REGEXP_REPLACE(custom_capacity, '[^0-9.]', '') AS DECIMAL(10,2)) <= {float(filters['max_capacity'])}"
        if filters.get("sales_person"):
            sales_person_values = filters["sales_person"].split(",")
            sales_person_list = ", ".join([f"'{s}'" for s in sales_person_values])
            where_clause += f" AND sales_person IN ({sales_person_list})"

    query = f"""
    SELECT
        name,
        grand_total,
        territory,
        creation,
        customer,
        custom_suntek_state as state,
        custom_department as department,
        custom_type_of_case as type_of_case,
        custom_type_of_structure as type_of_structure,
        custom_capacity as capacity,
        status,
        sales_person
    FROM
        `tabSales Order`
    WHERE
        {where_clause}
    ORDER BY
        creation DESC
    """

    if limit:
        query += f" LIMIT {limit}"

    sales_orders = frappe.db.sql(
        query,
        as_dict=1,
    )

    for order in sales_orders:
        if "type_of_case" in order and (order["type_of_case"] == "" or order["type_of_case"] is None):
            order["type_of_case"] = "No Type of Case"
        if "department" in order and (order["department"] == "" or order["department"] is None):
            order["department"] = "Unassigned Department"

        if "capacity" in order:
            order["capacity_raw"] = order["capacity"]
            order["capacity_value"] = extract_capacity_number(order["capacity"])

        if "department" in order and order["department"]:
            order["department_abbr"] = get_department_abbreviation(order["department"])

    grouped_data = defaultdict(
        lambda: {
            "state": None,
            "total_amount": 0,
            "count": 0,
            "territories": defaultdict(
                lambda: {
                    "territory": None,
                    "total_amount": 0,
                    "count": 0,
                    "departments": defaultdict(
                        lambda: {
                            "department": None,
                            "total_amount": 0,
                            "count": 0,
                            "orders": [],
                        }
                    ),
                }
            ),
        }
    )

    for order in sales_orders:
        state = order.get("state", "Unknown State")
        territory = order.get("territory", "Unknown Territory")
        department = order.get("department", "Unassigned Department")

        grouped_data[state]["state"] = state
        grouped_data[state]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[state]["count"] += 1

        grouped_data[state]["territories"][territory]["territory"] = territory
        grouped_data[state]["territories"][territory]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[state]["territories"][territory]["count"] += 1

        grouped_data[state]["territories"][territory]["departments"][department]["department"] = department
        grouped_data[state]["territories"][territory]["departments"][department]["total_amount"] += float(
            order.get("grand_total", 0)
        )
        grouped_data[state]["territories"][territory]["departments"][department]["count"] += 1
        grouped_data[state]["territories"][territory]["departments"][department]["orders"].append(order)

    result = []
    for _, state_data in grouped_data.items():
        state_entry = {
            "state": state_data["state"],
            "total_amount": state_data["total_amount"],
            "count": state_data["count"],
            "territories": [],
        }

        for _, territory_data in state_data["territories"].items():
            territory_entry = {
                "territory": territory_data["territory"],
                "total_amount": territory_data["total_amount"],
                "count": territory_data["count"],
                "departments": [],
            }

            for _, department_data in territory_data["departments"].items():
                dept_abbr = get_department_abbreviation(department_data["department"])

                for order in department_data["orders"]:
                    if "department" in order and order["department"]:
                        if "department_abbr" not in order or not order["department_abbr"]:
                            order["department_abbr"] = get_department_abbreviation(order["department"])

                department_entry = {
                    "department": department_data["department"],
                    "department_abbr": dept_abbr,
                    "total_amount": department_data["total_amount"],
                    "count": department_data["count"],
                    "orders": department_data["orders"],
                }
                territory_entry["departments"].append(department_entry)

            state_entry["territories"].append(territory_entry)

        result.append(state_entry)

    return result


def _get_sales_orders(filters=None, limit=100):
    where_clause = "1=1"

    permission_conditions = get_permission_query_conditions(frappe.session.user)
    if permission_conditions:
        where_clause += f" AND ({permission_conditions})"

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
            if "," in filters["status"]:
                status_values = filters["status"].split(",")
                status_list = ", ".join([f"'{s}'" for s in status_values])
                where_clause += f" AND status IN ({status_list})"
            else:
                where_clause += f" AND status = '{filters['status']}'"
        if filters.get("type_of_case"):
            where_clause += f" AND custom_type_of_case = '{filters['type_of_case']}'"
        if filters.get("type_of_structure"):
            where_clause += f" AND custom_type_of_structure = '{filters['type_of_structure']}'"
        if filters.get("min_capacity"):
            where_clause += f" AND CAST(REGEXP_REPLACE(custom_capacity, '[^0-9.]', '') AS DECIMAL(10,2)) >= {float(filters['min_capacity'])}"
        if filters.get("max_capacity"):
            where_clause += f" AND CAST(REGEXP_REPLACE(custom_capacity, '[^0-9.]', '') AS DECIMAL(10,2)) <= {float(filters['max_capacity'])}"
        if filters.get("sales_person"):
            sales_person_values = filters["sales_person"].split(",")
            sales_person_list = ", ".join([f"'{s}'" for s in sales_person_values])
            where_clause += f" AND sales_person IN ({sales_person_list})"

    query = f"""
    SELECT
        name,
        grand_total,
        territory,
        creation,
        customer,
        custom_suntek_district as district,
        custom_suntek_district_name as district_name,
        custom_suntek_state as state,
        custom_suntek_city as city,
        custom_type_of_case as type_of_case,
        custom_type_of_structure as type_of_structure,
        custom_department as department,
        custom_capacity as capacity,
        status,
        sales_person
    FROM
        `tabSales Order`
    WHERE
        {where_clause}
    ORDER BY
        creation DESC
    """

    if limit:
        query += f" LIMIT {limit}"

    sales_orders = frappe.db.sql(
        query,
        as_dict=1,
    )

    for order in sales_orders:
        if "type_of_case" in order and (order["type_of_case"] == "" or order["type_of_case"] is None):
            order["type_of_case"] = "No Type of Case"

        if "capacity" in order:
            order["capacity_raw"] = order["capacity"]
            order["capacity_value"] = extract_capacity_number(order["capacity"])

        if "department" in order and order["department"]:
            order["department_abbr"] = get_department_abbreviation(order["department"])

    grouped_data = defaultdict(
        lambda: {
            "state": None,
            "total_amount": 0,
            "count": 0,
            "territories": defaultdict(
                lambda: {
                    "territory": None,
                    "total_amount": 0,
                    "count": 0,
                    "cities": defaultdict(
                        lambda: {
                            "city": None,
                            "total_amount": 0,
                            "count": 0,
                            "districts": defaultdict(
                                lambda: {
                                    "district": None,
                                    "district_name": None,
                                    "total_amount": 0,
                                    "count": 0,
                                    "orders": [],
                                }
                            ),
                        }
                    ),
                }
            ),
        }
    )

    for order in sales_orders:
        state = order.get("state", "Unknown State")
        territory = order.get("territory", "Unknown Territory")
        city = order.get("city", "Unknown City")
        district = order.get("district", "Unknown District")
        district_name = order.get("district_name", "Unknown District")

        grouped_data[state]["state"] = state
        grouped_data[state]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[state]["count"] += 1

        grouped_data[state]["territories"][territory]["territory"] = territory
        grouped_data[state]["territories"][territory]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[state]["territories"][territory]["count"] += 1

        grouped_data[state]["territories"][territory]["cities"][city]["city"] = city
        grouped_data[state]["territories"][territory]["cities"][city]["total_amount"] += float(
            order.get("grand_total", 0)
        )
        grouped_data[state]["territories"][territory]["cities"][city]["count"] += 1

        grouped_data[state]["territories"][territory]["cities"][city]["districts"][district]["district"] = district
        grouped_data[state]["territories"][territory]["cities"][city]["districts"][district]["district_name"] = (
            district_name
        )
        grouped_data[state]["territories"][territory]["cities"][city]["districts"][district]["total_amount"] += float(
            order.get("grand_total", 0)
        )
        grouped_data[state]["territories"][territory]["cities"][city]["districts"][district]["count"] += 1
        grouped_data[state]["territories"][territory]["cities"][city]["districts"][district]["orders"].append(order)

    result = []
    for _, state_data in grouped_data.items():
        state_entry = {
            "state": state_data["state"],
            "total_amount": state_data["total_amount"],
            "count": state_data["count"],
            "territories": [],
        }

        for _, territory_data in state_data["territories"].items():
            territory_entry = {
                "territory": territory_data["territory"],
                "total_amount": territory_data["total_amount"],
                "count": territory_data["count"],
                "cities": [],
            }

            for _, city_data in territory_data["cities"].items():
                city_entry = {
                    "city": city_data["city"],
                    "total_amount": city_data["total_amount"],
                    "count": city_data["count"],
                    "districts": [],
                }

                for _, district_data in city_data["districts"].items():
                    for order in district_data["orders"]:
                        if "department" in order and order["department"]:
                            if "department_abbr" not in order or not order["department_abbr"]:
                                order["department_abbr"] = get_department_abbreviation(order["department"])

                    district_entry = {
                        "district": district_data["district"],
                        "district_name": district_data["district_name"],
                        "total_amount": district_data["total_amount"],
                        "count": district_data["count"],
                        "orders": district_data["orders"],
                    }
                    city_entry["districts"].append(district_entry)

                territory_entry["cities"].append(city_entry)

            state_entry["territories"].append(territory_entry)

        result.append(state_entry)

    return result
