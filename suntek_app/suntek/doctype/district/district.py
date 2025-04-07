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
