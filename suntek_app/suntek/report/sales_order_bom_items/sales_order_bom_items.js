frappe.query_reports["Sales Order BOM Items"] = {
  filters: [
    {
      fieldname: "sales_order",
      label: __("Sales Order"),
      fieldtype: "Link",
      options: "Sales Order",
      width: "100px",
    },
    {
      fieldname: "from_date",
      label: __("From Date"),
      fieldtype: "Date",
      default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
      width: "100px",
    },
    {
      fieldname: "to_date",
      label: __("To Date"),
      fieldtype: "Date",
      default: frappe.datetime.get_today(),
      width: "100px",
    },
    {
      fieldname: "delivery_status",
      label: __("Delivery Status"),
      fieldtype: "Select",
      options:
        "\nNot Delivered\nFully Delivered\nPartly Delivered\nClosed\nNot Applicable",
      width: "100px",
    },
    {
      fieldname: "billing_status",
      label: __("Billing Status"),
      fieldtype: "Select",
      options: "\nNot Billed\nFully Billed\nPartly Bileld\nClosed",
    },
    {
      fieldname: "order_type",
      label: __("Order Type"),
      fieldtype: "Select",
      options: "\nSales\nMaintenance\nShopping Card",
      width: "100px",
    },
    {
      fieldname: "warehouse",
      label: __("Warehouse"),
      fieldtype: "Link",
      options: "Warehouse",
      width: "100px",
    },
    {
      fieldname: "custom_department",
      label: __("Department"),
      fieldtype: "Select",
      options:
        "\nDomestic (Residential) Sales Team - SESP\nChannel Partner - SESP\nCommercial & Industrial (C&I) - SESP",
      width: "100px",
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
      const filters = report.get_values();

      frappe.call({
        method:
          "suntek_app.suntek.report.sales_order_bom_items.sales_order_bom_items.get_data",
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
              "Remarks",
              "Finished Item Code",
              "Finished Item Name",
              "Order Qty",
              "BOM No",
              "Raw Material Code",
              "Raw Material Name",
              "Raw Material Qty",
              "UOM",
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
                row.custom_remarks,
                row.finished_item_code,
                row.finished_item_name,
                row.order_qty,
                row.bom_no,
                row.raw_material_code,
                row.raw_material_name,
                row.raw_material_qty,
                row.raw_material_uom,
              ]);
            });

            frappe.tools.downloadify(rows, null, "Sales Order BOM Items");
          }
        },
      });
    });
  },
};
