frappe.query_reports["Sales Order BOM Items"] = {
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
      fieldname: "custom_department",
      label: __("Department"),
      fieldtype: "Link",
      options: "Department",
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
      default: "Hyderabad Central Warehouse - SESP",
      reqd: 1,
      get_query: function () {
        return {
          filters: {
            is_group: 0,
          },
        };
      },
    },
    {
      fieldname: "delivery_status",
      label: __("Delivery Status"),
      fieldtype: "Select",
      options:
        "\nNot Delivered\nFully Delivered\nPartly Delivered\nClosed\nNot Applicable",
    },
    {
      fieldname: "billing_status",
      label: __("Billing Status"),
      fieldtype: "Select",
      options: "\nNot Billed\nFully Billed\nPartly Billed\nClosed",
    },
    {
      fieldname: "order_type",
      label: __("Order Type"),
      fieldtype: "Select",
      options: "\nSales\nMaintenance\nShopping Card",
      width: "100px",
    },
    {
      fieldname: "limit_results",
      label: __("Show All Results"),
      fieldtype: "Check",
      default: 0,
      description: __(
        "Warning: Showing all results may be slow for large datasets"
      ),
    },
  ],
  formatter: function (value, row, column, data, default_formatter) {
    if (column.fieldname == "available_qty") {
      const reqQty = data.raw_material_qty || 0;
      const availQty = value || 0;

      value = default_formatter(value, row, column, data);

      if (availQty < reqQty) {
        value = `<span style="color: red; font-weight: bold">${value}</span>`;
      } else {
        value = `<span style="color: green; font-weight: bold">${value}</span>`;
      }

      return value;
    }
    return default_formatter(value, row, column, data);
  },
  onload: function (report) {
    report.page.add_inner_button(__("Export Report"), function () {
      frappe.msgprint({
        title: __("Starting Export"),
        indicator: "blue",
        message: __(
          "Preparing export. This may take a while for large datasets..."
        ),
      });

      const filters = report.get_values();

      filters.limit_results = 1;

      frappe.call({
        method:
          "suntek_app.suntek.report.sales_order_bom_items.sales_order_bom_items.export_data",
        args: {
          filters: filters,
        },
        callback: function (r) {
          if (r.message) {
            let rows = [];

            const headers = [
              "Sales Order",
              "Customer",
              "Project ID",
              "Department",
              "Dispatch Due Date",
              "Delivery Status",
              "Billing Status",
              "Finished Item Code",
              "Finished Item Name",
              "BOM No",
              "Raw Material Code",
              "Raw Material Name",
              "Raw Material Qty",
              "UOM",
              "Required Qty",
              "Available Qty",
              "Shortage/Surplus",
              "Status",
              "Transferred Qty",
              "Consumed Qty",
              "Work Order",
              "Work Order Status",
            ];
            rows.push(headers);

            r.message.forEach((row) => {
              rows.push([
                row.sales_order_no,
                row.customer,
                row.project,
                row.custom_department,
                row.delivery_date,
                row.delivery_status,
                row.billing_status,
                row.finished_item_code,
                row.finished_item_name,
                row.bom_no,
                row.raw_material_code,
                row.raw_material_name,
                row.raw_material_qty,
                row.raw_material_uom,
                row.required_qty,
                row.available_qty,
                row.shortage_surplus,
                row.status,
                row.transferred_qty,
                row.consumed_qty,
                row.work_order,
                row.work_order_status,
              ]);
            });

            frappe.tools.downloadify(rows, null, "Sales Order BOM Items");
          }
        },
      });
    });
  },
};
