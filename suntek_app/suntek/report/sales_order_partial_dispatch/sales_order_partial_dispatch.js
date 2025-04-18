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
            fieldname: "bom",
            label: __("BOM"),
            fieldtype: "Link",
            options: "BOM",
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
            options: "\nNot Started\nPartial\nCompleted\nNo BOM",
        },
        {
            fieldname: "only_bom_projects",
            label: __("Show Only BOM Projects"),
            fieldtype: "Check",
            default: 0,
        },
    ],

    onload: function (report) {
        report.page.add_inner_button(__("Refresh Chart"), function () {
            report.refresh();
        });
    },
};
