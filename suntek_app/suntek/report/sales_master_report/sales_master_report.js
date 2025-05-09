frappe.query_reports["Sales Master Report"] = {
    filters: [
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
            default: frappe.datetime.add_months(frappe.datetime.get_today(), -3),
            reqd: 0,
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
            default: frappe.datetime.get_today(),
            reqd: 0,
        },
        {
            fieldname: "lead_owner",
            label: __("Lead Owner"),
            fieldtype: "Link",
            options: "User",
        },
        {
            fieldname: "source",
            label: __("Lead Source"),
            fieldtype: "Link",
            options: "Lead Source",
        },
        {
            fieldname: "state",
            label: __("State"),
            fieldtype: "Link",
            options: "State",
        },
        {
            fieldname: "customer_category",
            label: __("Customer Category"),
            fieldtype: "Select",
            options: "\nIndividual\nC & I",
        },
        {
            fieldname: "type_of_case",
            label: __("Type of Case"),
            fieldtype: "Select",
            options: "\nSubsidy\nNon Subsidy\nDiscom",
        },
        {
            fieldname: "sales_executive",
            label: __("Field Sales Executive"),
            fieldtype: "Link",
            options: "Employee",
        },
        {
            fieldname: "branch",
            label: __("Branch"),
            fieldtype: "Data",
        },
    ],
};
