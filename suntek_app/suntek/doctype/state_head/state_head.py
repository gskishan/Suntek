import frappe
from frappe.model.document import Document


class StateHead(Document):
    @frappe.whitelist()
    def fetch_employee_id_from_user(self):
        employee = None
        employee_data = None

        user = frappe.get_doc("User", self.state_head_user_id)

        if frappe.db.exists("Employee", {"user_id": user.name}):
            employee = frappe.get_doc("Employee", {"user_id": user.name})
            employee_data = self._fetch_employee_details(employee)

        return employee_data if employee_data else None

    def _fetch_employee_details(self, employee_doc):
        response = {}

        response["branch"] = employee_doc.branch
        response["employee_id"] = employee_doc.name
        response["department"] = employee_doc.department
        response["designation"] = employee_doc.designation
        response["status"] = employee_doc.status

        return response
