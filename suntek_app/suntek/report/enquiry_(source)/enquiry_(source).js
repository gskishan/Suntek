frappe.query_reports["Enquiry (Source)"] = {
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
			fieldname: "source",
			label: __("Source"),
			fieldtype: "Link",
			options: "Lead Source",
		},
		{
			fieldname: "status",
			label: __("Status"),
			fieldtype: "Select",
			options: ["", "Open", "Converted"],
		},
	],

	// Refresh whenever filters change
	onload: function (report) {
		report.page.add_inner_button(__("Refresh"), function () {
			report.refresh();
		});
	},

	// Format the data
	formatter: function (value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);

		if (column.fieldname == "conversion_rate") {
			value = value + "%";
		}

		return value;
	},
};
