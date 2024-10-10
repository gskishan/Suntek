
frappe.query_reports["Designing Summary"] = {
    "filters": [

        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",

        },
        {
            "fieldname": "designing",
            "label": __("Designing"),
            "fieldtype": "Link",
            "options": "Designing",
            get_query: function () {
                let project = frappe.query_report.get_filter_value("project");
                if (!project) return;

                return {
                    query: "suntek_app.suntek.report.designing_summary.designing_summary.get_designing_options",
                    filters: {
                        project: project
                    }
                };
            }
        }




    ]
};
