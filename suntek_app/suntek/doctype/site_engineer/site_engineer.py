import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


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
        first_name = site_employee.get("first_name", "").strip()
        last_name = site_employee.get("last_name", "").strip()
        self.full_name = f"{first_name} {last_name}" if last_name else first_name
        self.department = site_employee.get("department")

    def autoname(self):
        employee = self.employee
        self.name = make_autoname(f"SES-SE-{employee}-.#####")
