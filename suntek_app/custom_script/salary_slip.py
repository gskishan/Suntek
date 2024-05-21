import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from frappe.utils import flt
from hrms.hr.utils import validate_active_employee

class CustomSalarySlip(SalarySlip):

    @frappe.whitelist()
    def pull_sal_struct(self):
        from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

        rt = 0
        if self.salary_slip_based_on_timesheet:
            self.salary_structure = self._salary_structure_doc.name
            self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
            make_salary_slip(self._salary_structure_doc.name, self)

            adding = 0
            for e in self.earnings:
                if e.salary_component in ['Basic', 'Conveyance Allowance', 'House Rent Allowance', 'Medical Allowance']:
                    adding += e.amount

            self.set("earnings", [])
            self.set("deductions", [])

            # Calculate rt based only on adding
            if self.total_working_days > 0:
                rt = (adding / self.total_working_days) / 8.5
            else:
                frappe.throw(_("Total working days cannot be zero"))

            self.hour_rate = rt
            self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)

            wages_amount = self.hour_rate * self.total_working_hours
            self.add_earning_for_hourly_wages(
                self._salary_structure_doc.salary_component, wages_amount
            )

        make_salary_slip(self._salary_structure_doc.name, self)
        if self.salary_slip_based_on_timesheet:
            self.hour_rate = rt


def get_base_amount(employee):
    sql = """SELECT base FROM `tabSalary Structure Assignment` WHERE employee=%s"""
    base = frappe.db.sql(sql, employee, as_dict=True)
    if base:
        return base[0].base
    else:
        frappe.msgprint(_("Issue in finding salary assignment"))
        return 0
