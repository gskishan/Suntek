import frappe
from frappe.model.document import Document


class SiteEngineer(Document):
    def before_save(self):
        site_employee = frappe.db.get_value(
            "Employee",
            self.employee,
            [
                "name",
                "first_name",
                "last_name",
                "department",
                "employee_name",
            ],
            as_dict=1,
        )

        self.first_name = site_employee.get("first_name")
        self.last_name = site_employee.get("last_name")
        self.full_name = f"{site_employee.get('first_name').strip} {site_employee.get('last_name').strip()}"
        self.department = site_employee.get("department")
