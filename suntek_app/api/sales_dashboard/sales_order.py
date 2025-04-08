from collections import defaultdict

import frappe

from suntek_app.suntek.utils.api_handler import create_api_response


@frappe.whitelist()
def get_sales_order_data():
    from_date = frappe.request.args.get("from_date")
    to_date = frappe.request.args.get("to_date")
    territory = frappe.request.args.get("territory")
    type_of_case = frappe.request.args.get("type_of_case")
    limit = frappe.request.args.get("limit")

    filters = {"from_date": from_date, "to_date": to_date, "territory": territory, "type_of_case": type_of_case}

    sales_orders = _get_sales_orders(filters, limit)

    return create_api_response(200, "success", "Sales Orders Fetched", sales_orders)


def _get_sales_orders(filters=None, limit=100):
    where_clause = "1=1"

    if filters:
        if filters.get("from_date"):
            where_clause += f" AND creation >= '{filters['from_date']}'"
        if filters.get("to_date"):
            where_clause += f" AND creation <= '{filters['to_date']}'"
        if filters.get("territory"):
            where_clause += f" AND territory = '{filters['territory']}'"
        if filters.get("type_of_case"):
            where_clause += f" AND custom_type_of_case = '{filters['type_of_case']}'"

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
        status
    FROM
        `tabSales Order`
    WHERE
        {where_clause}
    ORDER BY
        creation DESC
    """

    if limit:
        query += f" LIMIT {limit}"
    else:
        query += " LIMIT 100"

    sales_orders = frappe.db.sql(
        query,
        as_dict=1,
    )

    grouped_data = defaultdict(
        lambda: {
            "total_amount": 0,
            "count": 0,
            "states": defaultdict(
                lambda: {
                    "total_amount": 0,
                    "count": 0,
                    "cities": defaultdict(
                        lambda: {
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
        territory = order.get("territory", "Unknown Territory")
        state = order.get("state", "Unknown State")
        city = order.get("city", "Unknown City")
        district = order.get("district", "Unknown District")
        district_name = order.get("district_name", "Unknown District")

        grouped_data[territory]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[territory]["count"] += 1

        grouped_data[territory]["states"][state]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[territory]["states"][state]["count"] += 1

        grouped_data[territory]["states"][state]["cities"][city]["total_amount"] += float(order.get("grand_total", 0))
        grouped_data[territory]["states"][state]["cities"][city]["count"] += 1

        grouped_data[territory]["states"][state]["cities"][city]["districts"][district]["district"] = district
        grouped_data[territory]["states"][state]["cities"][city]["districts"][district]["district_name"] = district_name
        grouped_data[territory]["states"][state]["cities"][city]["districts"][district]["total_amount"] += float(
            order.get("grand_total", 0)
        )
        grouped_data[territory]["states"][state]["cities"][city]["districts"][district]["count"] += 1
        grouped_data[territory]["states"][state]["cities"][city]["districts"][district]["orders"].append(order)

    result = []
    for territory, territory_data in grouped_data.items():
        territory_entry = {
            "territory": territory,
            "total_amount": territory_data["total_amount"],
            "count": territory_data["count"],
            "states": [],
        }

        if not territory_data["states"]:
            territory_data["states"]["Unknown State"] = {
                "total_amount": territory_data["total_amount"],
                "count": territory_data["count"],
                "cities": defaultdict(
                    lambda: {
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

        for state, state_data in territory_data["states"].items():
            state_entry = {
                "state": state,
                "total_amount": state_data["total_amount"],
                "count": state_data["count"],
                "cities": [],
            }

            if not state_data["cities"]:
                state_data["cities"]["Unknown City"] = {
                    "total_amount": state_data["total_amount"],
                    "count": state_data["count"],
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

            for city, city_data in state_data["cities"].items():
                city_entry = {
                    "city": city,
                    "total_amount": city_data["total_amount"],
                    "count": city_data["count"],
                    "districts": [],
                }

                if not city_data["districts"]:
                    city_data["districts"]["Unknown District"] = {
                        "district": None,
                        "district_name": None,
                        "total_amount": city_data["total_amount"],
                        "count": city_data["count"],
                        "orders": [],
                    }

                for district, district_data in city_data["districts"].items():
                    district_entry = {
                        "district": district_data["district"],
                        "district_name": district_data["district_name"],
                        "total_amount": district_data["total_amount"],
                        "count": district_data["count"],
                        "orders": district_data["orders"],
                    }
                    city_entry["districts"].append(district_entry)

                state_entry["cities"].append(city_entry)

            territory_entry["states"].append(state_entry)

        result.append(territory_entry)

    return result
