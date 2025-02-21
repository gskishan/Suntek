frappe.ui.form.on("Sales Order", {
  custom_customer_id: function (frm) {
    frm.set_value("custom_customer_id", frm.doc.customer);
  },

  refresh: function (frm) {
    frm.set_value("custom_customer_id", frm.doc.customer);
    if (frm.doc.custom_opportunity_name) {
      // Fetch the Opportunity document
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Opportunity",
          name: frm.doc.custom_opportunity_name,
        },
        callback: function (response) {
          if (response.message) {
            var opportunity_doc = response.message;

            frm.set_value(
              "custom_type_of_case",
              opportunity_doc.custom_type_of_case,
            );
            frm.set_value(
              "custom_product_category",
              opportunity_doc.custom_product_category,
            );
          }
        },
      });
    }
    var hasSystemManager = frappe.user.has_role("System Manager");
    if (!hasSystemManager) {
      cur_frm.set_df_property("terms", "read_only", 1);
    }

    if (frm.doc.docstatus === 1) {
      if (frm.doc.status !== "Closed" && frm.doc.status !== "On Hold") {
        if (
          flt(frm.doc.per_billed) < 100 &&
          frappe.model.can_create("Sales Invoice")
        ) {
          frm.add_custom_button(
            __("Sales Invoice Custom"),
            () => {
              frappe.call({
                method: "suntek_app.overrides.sales_order.make_sales_invoice",
                args: {
                  source_name: frm.doc.name,
                },
                callback: function (r) {
                  if (!r.exc) {
                    var doc = frappe.model.sync(r.message);
                    frappe.set_route("Form", r.message.doctype, r.message.name);
                  }
                },
              });
            },
            __("Create"),
          );
        }
      }
    }
  },

  onload: function (frm) {
    frm.set_value("custom_customer_id", frm.doc.customer);
    if (frm.doc.custom_opportunity_name) {
      // Fetch the Opportunity document
      frappe.call({
        method: "frappe.client.get",
        args: {
          doctype: "Opportunity",
          name: frm.doc.custom_opportunity_name,
        },
        callback: function (response) {
          if (response.message) {
            var opportunity_doc = response.message;

            frm.set_value(
              "custom_type_of_case",
              opportunity_doc.custom_type_of_case,
            );
            frm.set_value(
              "custom_product_category",
              opportunity_doc.custom_product_category,
            );
          }
        },
      });
    }
  },
});
