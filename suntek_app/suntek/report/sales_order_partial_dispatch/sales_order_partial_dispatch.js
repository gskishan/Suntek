frappe.query_reports["Sales Order Partial Dispatch"] = {
    filters: [
        {
            fieldname: "sales_order",
            label: __("Sales Order"),
            fieldtype: "Link",
            options: "Sales Order",
            get_query: function () {
                return {
                    filters: {
                        docstatus: 1,
                    },
                };
            },
        },
        {
            fieldname: "project",
            label: __("Project"),
            fieldtype: "Link",
            options: "Project",
        },
        {
            fieldname: "design",
            label: __("Design"),
            fieldtype: "Link",
            options: "Designing",
            get_query: function () {
                return {
                    filters: {
                        docstatus: 1,
                    },
                };
            },
        },
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
            options: "\nNot Started\nPartial\nCompleted\nNo Design",
        },
        {
            fieldname: "only_design_projects",
            label: __("Ignore Projects without Design"),
            fieldtype: "Check",
            default: 1,
        },
    ],

    onload: function (report) {
        report.page.add_inner_button(__("Refresh Chart"), function () {
            report.refresh();
        });
    },
};
