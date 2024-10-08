
frappe.query_reports["Project Wise Summary"] = {
	"filters": [
		{
			"fieldname":"company",
			"label": __("Company"),
			"fieldtype": "Link",
			"options": "Company",
			"default": frappe.defaults.get_user_default("Company"),
			"reqd": 1
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default":frappe.datetime.add_months(frappe.datetime.get_today(), -1),
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today(),
			
		},
		
		{
			"fieldname":"project",
			"label": __("Project"),
			"fieldtype": "Link",
			"options": "Project",
            
		},
        {
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Link",
			"options": "Customer",
            
		},
		
	
		

]
};
