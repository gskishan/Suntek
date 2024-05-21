import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from frappe.utils import flt

class CustomSalarySlip(SalarySlip):

    @frappe.whitelist()
    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip
        rt = 0
        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            make_salary_slip(self._salary_structure_doc.name, self)
            
            # Clear earnings and deductions
            self.set("earnings", [])
            self.set("deductions", [])

            # Calculate total relevant earnings
            relevant_earnings = self.calculate_relevant_earnings()
            if relevant_earnings > 0:
                rt = ((relevant_earnings / self.total_working_days) / 8.5)
            else:
                frappe.msgprint("No relevant earnings found to calculate hourly rate")

            self.hour_rate = rt
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            wages_amount = self.hour_rate * self.total_working_hours

            self.add_earning_for_hourly_wages(
                self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)
        if self.salary_slip_based_on_timesheet:
            self.hour_rate = rt

    def calculate_relevant_earnings(self):
        # Retrieve salary structure earnings
        earnings = frappe.get_all("Salary Detail",
                                  filters={"parent": self._salary_structure_doc.name, "parentfield": "earnings"},
                                  fields=["salary_component", "amount"])
        total_earnings = 0
        earnings_components = ['Basic', 'Conveyance Allowance', 'House Rent Allowance', 'Medical Allowance']
        for e in earnings:
            if e.salary_component in earnings_components:
                total_earnings += e.amount
                self.append("earnings", {
                    "salary_component": e.salary_component,
                    "amount": e.amount
                })
        return total_earnings

    def add_earning_for_hourly_wages(self, salary_component, wages_amount):
        self.append("earnings", {
            "salary_component": salary_component,
            "amount": wages_amount
        })

def get_base_amount(employee):
    sql = """SELECT base FROM `tabSalary Structure Assignment` WHERE employee=%s"""
    base = frappe.db.sql(sql, employee, as_dict=True)
    if base:
        return base[0].base
    else:
        frappe.msgprint("Issue in finding salary assignment")
        return 0
