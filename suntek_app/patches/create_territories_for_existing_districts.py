def execute():
    import frappe

    districts = frappe.get_all("District", fields=["name"])

    created_count = 0
    for district_data in districts:
        try:
            # This line has the error - you're using frappe.new_doc which creates a new document
            # Instead, you should use frappe.get_doc to retrieve existing document
            district = frappe.get_doc("District", district_data.name)

            if not district.territory:
                result = district.create_territory()
                if result:
                    created_count += 1

        except Exception as e:
            frappe.log_error(
                f"Error creating territory for district {district_data.name}: {str(e)}",
                "Territory Migration Error",
            )

    print(f"Created territories for {created_count} districts")
