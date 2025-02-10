import frappe
from frappe.model.document import Document


class DistrictPINCode(Document):
    def before_save(self):
        self.set_district_data()

    def set_district_data(self):
        district = frappe.db.get_value(
            "District",
            {"name": self.district},
            ["city", "state", "district_snake_case", "state_code"],
            as_dict=1,
        )

        self.city = district.city
        self.state = district.state
        self.district_snake_case = district.district_snake_case
        self.state_code = district.state_code
