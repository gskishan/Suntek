import frappe


def create_states():
    states = [
        {"state": "Andhra Pradesh", "state_code": "AP", "country": "India"},
        {"state": "Arunachal Pradesh", "state_code": "AR", "country": "India"},
        {"state": "Assam", "state_code": "AS", "country": "India"},
        {"state": "Bihar", "state_code": "BR", "country": "India"},
        {"state": "Chhattisgarh", "state_code": "CG", "country": "India"},
        {"state": "Goa", "state_code": "GA", "country": "India"},
        {"state": "Gujarat", "state_code": "GJ", "country": "India"},
        {"state": "Haryana", "state_code": "HR", "country": "India"},
        {"state": "Himachal Pradesh", "state_code": "HP", "country": "India"},
        {"state": "Jammu and Kashmir", "state_code": "JK", "country": "India"},
        {"state": "Jharkhand", "state_code": "JH", "country": "India"},
        {"state": "Karnataka", "state_code": "KA", "country": "India"},
        {"state": "Kerala", "state_code": "KL", "country": "India"},
        {"state": "Madhya Pradesh", "state_code": "MP", "country": "India"},
        {"state": "Maharashtra", "state_code": "MH", "country": "India"},
        {"state": "Manipur", "state_code": "MN", "country": "India"},
        {"state": "Meghalaya", "state_code": "ML", "country": "India"},
        {"state": "Mizoram", "state_code": "MZ", "country": "India"},
        {"state": "Nagaland", "state_code": "NL", "country": "India"},
        {"state": "Orissa", "state_code": "OR", "country": "India"},
        {"state": "Punjab", "state_code": "PB", "country": "India"},
        {"state": "Rajasthan", "state_code": "RJ", "country": "India"},
        {"state": "Sikkim", "state_code": "SK", "country": "India"},
        {"state": "Tamil Nadu", "state_code": "TN", "country": "India"},
        {"state": "Tripura", "state_code": "TR", "country": "India"},
        {"state": "Uttarakhand", "state_code": "UK", "country": "India"},
        {"state": "Uttar Pradesh", "state_code": "UP", "country": "India"},
        {"state": "West Bengal", "state_code": "WB", "country": "India"},
        {
            "state": "Andaman and Nicobar Islands",
            "state_code": "AN",
            "country": "India",
        },
        {"state": "Chandigarh", "state_code": "CH", "country": "India"},
        {"state": "Dadra and Nagar Haveli", "state_code": "DH", "country": "India"},
        {"state": "Daman and Diu", "state_code": "DD", "country": "India"},
        {"state": "Delhi", "state_code": "DL", "country": "India"},
        {"state": "Lakshadweep", "state_code": "LD", "country": "India"},
        {"state": "Pondicherry", "state_code": "PY", "country": "India"},
        {"state": "Telangana", "state_code": "TS", "country": "India"},
    ]

    states_added = 0

    for state_data in states:
        if not frappe.db.exists(
            "State", {"state": state_data["state"], "country": state_data["country"]}
        ):
            try:
                state = frappe.get_doc(
                    {
                        "doctype": "State",
                        "state": state_data["state"],
                        "state_code": state_data["state_code"],
                        "country": state_data["country"],
                    }
                )
                state.insert(ignore_permissions=True)
                states_added += 1
                print(f"Added state: {state_data['state']}")
            except Exception as e:
                print(f"Error adding state {state_data['state']}: {str(e)}")
                frappe.db.rollback()
        else:
            print(f"State {state_data['state']} already exists")

    frappe.db.commit()
    print(f"\nTotal states added: {states_added}")


def add_cities():
    cities = [
        {"city": "Mumbai", "state": "Maharashtra", "country": "India"},
        {"city": "Delhi", "state": "Delhi", "country": "India"},
        {"city": "Bangalore", "state": "Karnataka", "country": "India"},
        {"city": "Hyderabad", "state": "Telangana", "country": "India"},
        {"city": "Chennai", "state": "Tamil Nadu", "country": "India"},
        {"city": "Kolkata", "state": "West Bengal", "country": "India"},
        {"city": "Ahmedabad", "state": "Gujarat", "country": "India"},
        {"city": "Pune", "state": "Maharashtra", "country": "India"},
        {"city": "Jaipur", "state": "Rajasthan", "country": "India"},
        {"city": "Lucknow", "state": "Uttar Pradesh", "country": "India"},
        {"city": "Chandigarh", "state": "Chandigarh", "country": "India"},
        {"city": "Surat", "state": "Gujarat", "country": "India"},
        {"city": "Kochi", "state": "Kerala", "country": "India"},
        {"city": "Bhopal", "state": "Madhya Pradesh", "country": "India"},
        {"city": "Indore", "state": "Madhya Pradesh", "country": "India"},
        {"city": "Patna", "state": "Bihar", "country": "India"},
        {"city": "Vadodara", "state": "Gujarat", "country": "India"},
        {"city": "Coimbatore", "state": "Tamil Nadu", "country": "India"},
        {"city": "Nagpur", "state": "Maharashtra", "country": "India"},
        {"city": "Visakhapatnam", "state": "Andhra Pradesh", "country": "India"},
        {"city": "Ludhiana", "state": "Punjab", "country": "India"},
        {"city": "Madurai", "state": "Tamil Nadu", "country": "India"},
        {"city": "Kanpur", "state": "Uttar Pradesh", "country": "India"},
        {"city": "Agra", "state": "Uttar Pradesh", "country": "India"},
        {"city": "Noida", "state": "Uttar Pradesh", "country": "India"},
        {"city": "Vijayawada", "state": "Andhra Pradesh", "country": "India"},
        {"city": "Raipur", "state": "Chhattisgarh", "country": "India"},
        {"city": "Ranchi", "state": "Jharkhand", "country": "India"},
        {"city": "Gurgaon", "state": "Haryana", "country": "India"},
        {"city": "Shivamogga", "state": "Karnataka", "country": "India"},
        {"city": "Thiruvananthapuram", "state": "Kerala", "country": "India"},
        {"city": "Jammu", "state": "Jammu and Kashmir", "country": "India"},
        {"city": "Nashik", "state": "Maharashtra", "country": "India"},
        {"city": "Dehradun", "state": "Uttarakhand", "country": "India"},
        {"city": "Shimla", "state": "Himachal Pradesh", "country": "India"},
        {"city": "Mysore", "state": "Karnataka", "country": "India"},
        {"city": "Aligarh", "state": "Uttar Pradesh", "country": "India"},
        {"city": "Dhanbad", "state": "Jharkhand", "country": "India"},
    ]

    cities_added = 0

    for city_data in cities:
        if not frappe.db.exists("City", city_data["city"]):
            try:
                state_code = frappe.get_value("State", city_data["state"], "state_code")

                city = frappe.get_doc(
                    {
                        "doctype": "City",
                        "city": city_data["city"],
                        "state": city_data["state"],
                        "state_code": state_code,
                    }
                )
                city.insert(ignore_permissions=True)
                cities_added += 1
                print(f"Added city: {city_data['city']}, {city_data['state']}")
            except Exception as e:
                print(f"Error adding city {city_data['city']}: {str(e)}")
                frappe.db.rollback()
        else:
            print(f"City {city_data['city']} already exists")

    frappe.db.commit()
    return cities_added


def execute():
    print("Starting state import...")

    create_states()
    print("\nStarting city import...")
    add_cities()

    print("\nImport completed!")
