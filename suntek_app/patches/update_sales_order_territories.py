def execute():
    import random

    import frappe
    from frappe.utils import cstr

    print("Starting to update territories in Sales Orders...")

    # Create territories for each state
    telangana_territories = ["Telangana Region 1", "Telangana Region 2"]
    andhra_territories = ["Andhra Pradesh Region 1", "Andhra Pradesh Region 2"]
    karnataka_territories = ["Karnataka Region 1", "Karnataka Region 2"]
    madhya_pradesh_territories = ["Madhya Pradesh Region 1", "Madhya Pradesh Region 2"]

    all_territories = telangana_territories + andhra_territories + karnataka_territories + madhya_pradesh_territories

    # Create territories if they don't exist
    for territory_name in all_territories:
        if not frappe.db.exists("Territory", territory_name):
            territory = frappe.new_doc("Territory")
            territory.territory_name = territory_name
            territory.parent_territory = "India"
            territory.is_group = 0
            territory.save()
            print(f"Created territory: {territory_name}")

    # Get all states and cities for reference
    states = {s.name for s in frappe.get_all("State", fields=["name"])}

    print(f"Found {len(states)} states in the system")

    # Get all sales orders
    sales_orders = frappe.db.sql(
        """
        SELECT name, customer, territory, custom_suntek_state, custom_suntek_city, shipping_address_name
        FROM `tabSales Order`
        WHERE docstatus = 1
    """,
        as_dict=1,
    )

    updated_count = 0
    skipped_count = 0
    states_updated = 0
    cities_updated = 0

    # States we want to explicitly handle
    target_states = ["Telangana", "Andhra Pradesh", "Karnataka", "Madhya Pradesh", "Maharashtra"]
    # Cities we want to explicitly handle
    target_cities = {"hyderabad": "Hyderabad", "bengaluru": "Bengaluru", "bangalore": "Bengaluru"}

    for so_data in sales_orders:
        # Get the Sales Order document
        so = frappe.get_doc("Sales Order", so_data.name)

        # First check if custom_suntek_state is set
        state = so_data.custom_suntek_state
        city = so_data.custom_suntek_city
        address_state = None
        address_city = None
        territory_to_set = None

        # Get the shipping address directly from the Sales Order
        address_name = so_data.shipping_address_name

        # If shipping_address_name is not available, skip this record
        if not address_name:
            print(f"Skipping Sales Order {so.name}: No shipping address found")
            skipped_count += 1
            continue

        # Get the address document
        if frappe.db.exists("Address", address_name):
            address = frappe.get_doc("Address", address_name)
            address_state = address.state
            address_city = address.city

            # Update custom_suntek_state if state exists in State doctype and is one of our target states
            # Only set if it's not already set
            if (
                address_state
                and address_state in states
                and any(target in address_state for target in target_states)
                and not state
            ):
                so.db_set("custom_suntek_state", address_state)
                print(f"Updated Sales Order {so.name}: Set custom_suntek_state to {address_state}")
                states_updated += 1
                state = address_state  # Update state for territory assignment

            # Update custom_suntek_city ONLY for specific cities and only if not already set
            if address_city and not city:
                address_city_lower = address_city.lower()
                if address_city_lower in target_cities:
                    normalized_city = target_cities[address_city_lower]
                    so.db_set("custom_suntek_city", normalized_city)
                    print(f"Updated Sales Order {so.name}: Set custom_suntek_city to {normalized_city}")
                    cities_updated += 1

            # If state was not found but city is one of our target cities, set the corresponding state
            if not state and address_city:
                address_city_lower = address_city.lower()
                if address_city_lower in ["hyderabad"]:
                    so.db_set("custom_suntek_state", "Telangana")
                    print(
                        f"Updated Sales Order {so.name}: Set custom_suntek_state to Telangana (because city is Hyderabad)"
                    )
                    states_updated += 1
                    state = "Telangana"  # Update state for territory assignment
                elif address_city_lower in ["bengaluru", "bangalore"]:
                    so.db_set("custom_suntek_state", "Karnataka")
                    print(
                        f"Updated Sales Order {so.name}: Set custom_suntek_state to Karnataka (because city is Bengaluru)"
                    )
                    states_updated += 1
                    state = "Karnataka"  # Update state for territory assignment

        # Determine which territory to use based on state
        if state:
            if "Telangana" in state:
                territory_to_set = random.choice(telangana_territories)
            elif "Andhra" in state:
                territory_to_set = random.choice(andhra_territories)
            elif "Karnataka" in state:
                territory_to_set = random.choice(karnataka_territories)
            elif "Madhya Pradesh" in state:
                territory_to_set = random.choice(madhya_pradesh_territories)
            # Note: Maharashtra doesn't have territories, we just store the state

        # Update the territory if one was selected
        if territory_to_set:
            # Update the territory field using db_set to bypass workflow validation
            so.db_set("territory", territory_to_set)
            updated_count += 1
            print(f"Updated Sales Order {so.name}: Territory set to {territory_to_set} (State: {state})")
        else:
            skipped_count += 1

    frappe.db.commit()

    print(f"Completed updating territories in Sales Orders.")
    print(f"Updated: {updated_count}, Skipped: {skipped_count}")
    print(f"States updated: {states_updated}, Cities updated: {cities_updated}")
