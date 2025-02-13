frappe.query_reports["Sales Order BOM Items"] = {
    "filters": [
        {
            "fieldname": "sales_order",
            "label": __("Sales Order"),
            "fieldtype": "Link",
            "options": "Sales Order",
            "width": "100px"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "width": "100px"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "100px"
        },
        {
            "fieldname": "delivery_status",
            "label": __("Delivery Status"),
            "fieldtype": "Select",
            "options": "\nNot Delivered\nFully Delivered\nPartly Delivered\nClosed\nNot Applicable",
            "width": "100px",
        },
        {
            "fieldname": "billing_status",
            "label": __("Billing Status"),
            "fieldtype": "Select",
            "options": "\nNot Billed\nFully Billed\nPartly Bileld\nClosed"
        }
    ],
    onload: function(report) {
        report.page.add_inner_button(__('Export Report'), function() {
            const filters = report.get_values();

            frappe.call({
                method: 'suntek_app.suntek.report.sales_order_bom_items.sales_order_bom_items.get_data',
                args: {
                    filters: filters
                },
                callback: function(r) {
                    if (r.message) {
                        let rows = [];

                        const headers = [
                            "Sales Order", "Delivery Status", "Billing Status",
                            "Finished Item Code", "Finished Item Name", "Order Qty",
                            "BOM No", "Raw Material Code", "Raw Material Name",
                            "Raw Material Qty", "UOM"
                        ];
                        rows.push(headers);

                        r.message.forEach(row => {
                            rows.push([
                                row.sales_order_no,
                                row.delivery_status,
                                row.billing_status,
                                row.finished_item_code,
                                row.finished_item_name,
                                row.order_qty,
                                row.bom_no,
                                row.raw_material_code,
                                row.raw_material_name,
                                row.raw_material_qty,
                                row.raw_material_uom
                            ]);
                        });

                        frappe.tools.downloadify(rows, null, 'Sales Order BOM Items');
                    }
                }
            });
        });
    }
}
