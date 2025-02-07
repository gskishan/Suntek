from frappe.model.document import Document


class District(Document):

    def before_insert(self):
        self.set_district_snake_case()

    def set_district_snake_case(self):
        district_name = self.district
        district_words = district_name.split(" ")

        print(district_words)

        self.district_snake_case = "_".join(district_words).upper()
