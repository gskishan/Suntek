import json
import re
from collections import defaultdict

import frappe

from suntek_app.suntek.utils.api_handler import create_api_response


# Function to extract numeric value from capacity string
def extract_capacity_number(capacity_str):
    if not capacity_str or capacity_str == "":
        return None

    # Convert to string in case it's a number already
    capacity_str = str(capacity_str)

    # Extract numbers with optional decimal point
    matches = re.findall(r"(\d+\.?\d*)", capacity_str)
    if matches:
        return float(matches[0])
    return None


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
        type_of_case = form_dict.get("type_of_case")
        type_of_structure = form_dict.get("type_of_structure")
        min_capacity = form_dict.get("min_capacity")
        max_capacity = form_dict.get("max_capacity")
        sales_person = form_dict.get("sales_person")
        limit = form_dict.get("limit", 100)
        try:
            frappe.logger().info(f"Raw limit value: {limit}, type: {type(limit)}")
            if limit == "all":
                limit = None
                frappe.logger().info("Limit set to None for 'all' option")
            else:
                limit = int(limit)
                frappe.logger().info(f"Limit converted to int: {limit}")
        except (ValueError, TypeError) as e:
            frappe.logger().error(f"Error converting limit to int: {e}")
            limit = 100
            frappe.logger().info(f"Limit set to default: {limit}")
        show_sql = form_dict.get("show_sql") == "1"

        frappe.logger().info(
            f"Received state: {state}, territory: {territory}, city: {city}, district: {district}, limit: {limit}, min_capacity: {min_capacity}, max_capacity: {max_capacity}, type_of_structure: {type_of_structure}"
        )

    except Exception as e:
        frappe.logger().error(f"Error getting parameters: {e}")

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
            frappe.logger().info(f"Raw limit value: {limit}, type: {type(limit)}")
            if limit == "all":
                limit = None
                frappe.logger().info("Limit set to None for 'all' option")
            else:
                limit = int(limit)
                frappe.logger().info(f"Limit converted to int: {limit}")
        except (ValueError, TypeError) as e:
            frappe.logger().error(f"Error converting limit to int: {e}")
            limit = 100
            frappe.logger().info(f"Limit set to default: {limit}")
        show_sql = frappe.request.args.get("show_sql") == "1"

        frappe.logger().info(
            f"Using args: state: {state}, territory: {territory}, city: {city}, district: {district}, limit: {limit}, min_capacity: {min_capacity}, max_capacity: {max_capacity}, type_of_structure: {type_of_structure}"
        )

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
            # Check if status is a comma-separated list and handle multiple statuses
            if "," in filters["status"]:
                status_values = filters["status"].split(",")
                status_list = ", ".join([f"'{s}'" for s in status_values])
                where_clause += f" AND status IN ({status_list})"
                frappe.logger().info(f"Applying multiple status filter with values: {status_values}")
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
        frappe.logger().info(f"Added LIMIT {limit} to query")
    else:
        # No limit clause needed for "all" option
        frappe.logger().info("No LIMIT clause added to query (all items)")
        pass

    if filters and filters.get("state"):
        frappe.logger().info(f"SQL Query with state filter: {query}")
    elif show_sql:
        frappe.logger().info(f"SQL Query: {query}")

    sales_orders = frappe.db.sql(
        query,
        as_dict=1,
    )

    for order in sales_orders:
        if "type_of_case" in order and (order["type_of_case"] == "" or order["type_of_case"] is None):
            order["type_of_case"] = "No Type of Case"

        # Extract numeric capacity from the custom_capacity field
        if "capacity" in order:
            order["capacity_raw"] = order["capacity"]
            order["capacity_value"] = extract_capacity_number(order["capacity"])

    frappe.logger().info(f"Query returned {len(sales_orders)} sales orders")
    if limit:
        frappe.logger().info(f"Query was limited to {limit} records")
    else:
        frappe.logger().info("Query was not limited (all records)")

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
