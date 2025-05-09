import frappe
from frappe.utils import flt
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip


class CustomSalarySlip(SalarySlip):
    @frappe.whitelist()
    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import (
            make_salary_slip,
        )

        rt = 0
        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            make_salary_slip(self._salary_structure_doc.name, self)

            self.set("earnings", [])
            self.set("deductions", [])
            base = get_base_amount(self.employee)
            rt = (base / self.total_working_days) / 8.5
            self.hour_rate = rt
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
            wages_amount = self.hour_rate * self.total_working_hours
            self.add_earning_for_hourly_wages(self, self._salary_structure_doc.salary_component, wages_amount)

        make_salary_slip(self._salary_structure_doc.name, self)
        if self.salary_slip_based_on_timesheet:
            self.hour_rate = rt


def get_base_amount(employee):
    sql = f"""select base from `tabSalary Structure Assignment` where employee="{employee}" """
    base = frappe.db.sql(sql, as_dict=True)
    if base:
        return base[0].base
    else:
        frappe.msgprint("issue in finding salary assigment")
        return 0
