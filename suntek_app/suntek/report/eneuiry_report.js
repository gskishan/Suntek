// Copyright (c) 2024, Patel Asif Khan and contributors
// For license information, please see license.txt

frappe.query_reports["Enquiry Owner Count"] = {
	"filters": [
		{
			"fieldname":"lead_owner",
			"label": __("Enquiry Owner"),
			"fieldtype": "Link",
			"options": "User"
		},
		{
			"fieldname":"from_date",
			"label": __("Start Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.nowdate(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("End Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.nowdate(),
		}
	]
};
