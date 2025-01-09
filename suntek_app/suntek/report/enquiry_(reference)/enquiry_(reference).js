// Copyright (c) 2025, kishan and contributors
// For license information, please see license.txt

// Copyright (c) 2025, kishan and contributors
// For license information, please see license.txt

frappe.query_reports["Enquiry (Reference)"] = {
	filters: [
		{
			fieldname: "from_date",
			label: __("From Date"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1,
		},
		{
			fieldname: "to_date",
			label: __("To Date"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1,
		},
		{
			fieldname: "department",
			label: __("Department"),
			fieldtype: "Link",
			options: "Department",
		},
		{
			fieldname: "reference_by",
			label: __("Reference By"),
			fieldtype: "Select",
			options: "\nEmployee\nCustomer",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: [
				"",
				"Lead",
				"Open",
				"Replied",
				"Opportunity",
				"Quotation",
				"Lost Quotation",
				"Interested",
				"Converted",
				"Do Not Contact",
			],
		},
	],

	onload: function (report) {
		report.page.add_inner_button(__("Refresh"), function () {
			report.refresh();
		});
	},

	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "conversion_rate") {
			value = value + "%";
		}

		return value;
	},
};
