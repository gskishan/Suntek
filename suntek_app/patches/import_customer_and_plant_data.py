import json

import frappe


def format_customer_name(first_name, last_name):
    if not first_name and not last_name:
        return ""

    def capitalize_name(name):
        if not name:
            return ""
        words = name.strip().split()
        return " ".join(word[0].upper() + word[1:].lower() for word in words)

    first = capitalize_name(first_name)
    last = capitalize_name(last_name)

    return f"{first} {last}".strip()


def import_customers():
    customer_count = 0

    try:
        with open("../apps/suntek_app/suntek_app/patches/plant_data.json", "r") as f:
            data_str = f.read()
            data = json.loads(data_str)

            for row in data:
                phone = row["c4"].replace("+91", "")
                customer_name = format_customer_name(
                    row["c2"].strip(), row["c3"].strip()
                )

                if not frappe.db.exists("Customer", {"mobile_no": phone}):
                    try:
                        customer = frappe.get_doc(
                            {
                                "doctype": "Customer",
                                "customer_name": customer_name,
                                "mobile_no": phone,
                            }
                        )
                        customer.insert(ignore_permissions=True)
                        frappe.db.commit()
                        customer_count += 1
                        print(f"{customer_count}: Created customer: {customer_name}")
                    except Exception as e:
                        print(f"Error creating customer {customer_name}: {str(e)}")
                        frappe.db.rollback()

    except Exception as e:
        print(f"Error reading file: {str(e)}")

    print(f"\nTotal customers created: {customer_count}")


def import_solar_plants():
    plant_count = 0

    try:
        with open("../apps/suntek_app/suntek_app/patches/plant_data.json", "r") as f:
            data_str = f.read()
            data = json.loads(data_str)

            for row in data:
                phone = row["c4"].replace("+91", "")
                customer = frappe.get_value("Customer", {"mobile_no": phone}, "name")

                if customer:
                    try:
                        if not frappe.db.exists(
                            "Solar Power Plants", {"plant_id": row["c0"]}
                        ):
                            plant = frappe.get_doc(
                                {
                                    "doctype": "Solar Power Plants",
                                    "plant_id": row["c0"],
                                    "plant_name": row["c1"].strip(),
                                    "oem": "Growatt",
                                    "customer": customer,
                                }
                            )
                            plant.insert(ignore_permissions=True)
                            frappe.db.commit()
                            plant_count += 1
                            print(
                                f"{plant_count}: Created plant: {plant.plant_name} for customer {customer}"
                            )
                    except Exception as e:
                        print(f"Error creating plant {row['c1']}: {str(e)}")
                        frappe.db.rollback()
                else:
                    print(
                        f"Customer not found for plant {row['c1']} with phone {phone}"
                    )

    except Exception as e:
        print(f"Error reading file: {str(e)}")

    print(f"\nTotal plants created: {plant_count}")


def execute():
    print("Starting customer import...")
    import_customers()
    print("\nStarting plant import...")
    import_solar_plants()
    print("\nImport completed!")
