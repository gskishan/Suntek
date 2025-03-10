import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class District(Document):
    def before_insert(self):
        self.set_district_snake_case()
        self.set_state_data()

    def autoname(self):
        dis_3 = self.district[0:3].upper()
        self.name = make_autoname(f"{dis_3}-{self.state_code}-.#####")

    def set_district_snake_case(self):
        district_name = self.district
        district_words = district_name.split(" ")
        self.district_snake_case = "_".join(district_words).upper()

    def set_state_data(self):
        city = frappe.db.get_value(
            "City",
            {"name": self.city},
            ["name", "state", "state_code", "country"],
            as_dict=1,
        )
        self.state = city.state
        self.state_code = city.state_code
        self.country = city.country

    def create_territory(self):
        try:
            territory_name = self.district

            existing_territory = frappe.db.exists("Territory", territory_name)

            if existing_territory:
                self.db_set("territory", existing_territory)
                return existing_territory

            parent_territory = self.state
            if not frappe.db.exists("Territory", parent_territory):
                country_territory = self.country
                if not frappe.db.exists("Territory", country_territory):
                    country_doc = frappe.get_doc(
                        {
                            "doctype": "Territory",
                            "territory_name": self.country,
                            "parent_territory": "All Territories",
                            "is_group": 1,
                        }
                    )
                    country_doc.insert(ignore_permissions=True)
                state_doc = frappe.get_doc(
                    {
                        "doctype": "Territory",
                        "territory_name": self.state,
                        "parent_territory": self.country,
                        "is_group": 1,
                    }
                )
                state_doc.insert(ignore_permissions=True)

            new_territory = frappe.get_doc(
                {
                    "doctype": "Territory",
                    "territory_name": territory_name,
                    "parent_territory": self.state,
                    "is_group": 0,
                }
            )
            new_territory.insert(ignore_permissions=True)

            self.db_set("territory", new_territory.name)

            frappe.msgprint(f"Territory {territory_name} created successfully")
            return new_territory.name

        except Exception as e:
            frappe.log_error(str(e), "Customer Creation Error")
            frappe.msgprint(f"Could not create Territory: {str(e)}")
