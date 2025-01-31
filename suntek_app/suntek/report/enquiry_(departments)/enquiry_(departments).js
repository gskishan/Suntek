frappe.query_reports["Enquiry (Departments)"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options:
				"\nLead\nOpen\nReplied\nOpportunity\nQuotation\nLost Quotation\nInterested\nConverted\nDo Not Contact",
		},
		{
			fieldname: "custom_department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "lead_owner",
			label: __("Lead Owner"),
			fieldtype: "Link",
			options: "User",
		},
	],
};
