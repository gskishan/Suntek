# Copyright (c) 2025, kishan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class City(Document):
    def before_save(self):
        self.set_state_code()

    def set_state_code(self):
        state = frappe.db.get_value(
            "State",
            {"name": self.state},
            ["name", "state_code"],
            as_dict=1,
        )
        self.state_code = state.state_code
