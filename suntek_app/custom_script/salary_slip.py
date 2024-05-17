import frappe
from frappe import _
from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
from hrms.payroll.doctype.salary_slip.salary_slip import *
from frappe.utils import flt
from hrms.hr.utils import  validate_active_employee

class CustomSalarySlip(SalarySlip):
	def validate(self):
		self.status = self.get_status()
		validate_active_employee(self.employee)
		self.validate_dates()
		self.check_existing()
		frappe.errprint(len(self.deductions))
		if not self.salary_slip_based_on_timesheet:
			self.get_date_details()

		if not (len(self.get("earnings")) or len(self.get("deductions"))):
			# get details from salary structure
			frappe.errprint(len(self.deductions))
			self.get_emp_and_working_day_details()
			frappe.errprint(len(self.deductions))
		else:
			self.get_working_days_details(lwp=self.leave_without_pay)
		frappe.errprint(len(self.deductions))
		self.calculate_net_pay()
		self.compute_year_to_date()
		self.compute_month_to_date()
		self.compute_component_wise_year_to_date()
		self.add_leave_balances()
		self.compute_income_tax_breakup()

		if frappe.db.get_single_value("Payroll Settings", "max_working_hours_against_timesheet"):
			max_working_hours = frappe.db.get_single_value(
				"Payroll Settings", "max_working_hours_against_timesheet"
			)
			if self.salary_slip_based_on_timesheet and (self.total_working_hours > int(max_working_hours)):
				frappe.msgprint(
					_("Total working hours should not be greater than max working hours {0}").format(
						max_working_hours
					),
					alert=True,
				)


	@frappe.whitelist()
	def pull_sal_struct(self):
		from hrms.payroll.doctype.salary_structure.salary_structure import make_salary_slip

		if self.salary_slip_based_on_timesheet:
			self.salary_structure = self._salary_structure_doc.name
			self.total_working_hours = sum([d.working_hours or 0.0 for d in self.timesheets]) or 0.0
			make_salary_slip(self._salary_structure_doc.name, self)
			deduction=0
			for d in self.deductions:
				if d.salary_component=='Provident Fund Employee' or  d.salary_component=='ESIC Employer':
					deduction+=d.amount
			base=get_base_amount(self.employee)-deduction
			rt = ((base / self.total_working_days) / 8.5)
			self.hour_rate = rt
			self.base_hour_rate = flt(self.hour_rate) * flt(self.exchange_rate)
			wages_amount = self.hour_rate * self.total_working_hours
			self.add_earning_for_hourly_wages(
				self, self._salary_structure_doc.salary_component, wages_amount
			)
			frappe.errprint([len(self.deductions),"1"])

		make_salary_slip(self._salary_structure_doc.name, self)
		frappe.errprint([len(self.deductions),"2"])
		if self.salary_slip_based_on_timesheet:
			base=get_base_amount(self.employee)
			rt = ((base / self.total_working_days) / 8.5)
			self.hour_rate = rt
		
		

def get_base_amount(employee):
	sql="""select base from `tabSalary Structure Assignment` where employee="{0}" """.format(employee)
	base=frappe.db.sql(sql,as_dict=True)
	if base:
		return base[0].base
	else:
		frappe.msgprint("issue in finding salary assigment")
		return 0
