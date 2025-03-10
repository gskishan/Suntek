frappe.ui.form.on("Channel Partner", {
  refresh(frm) {
    if (
      frm.doc.status === "Active" &&
      !frm.doc.is_user_created &&
      frm.doc.suntek_email
    ) {
      frm.add_custom_button(__("Create User"), function () {
        frm.call({
          doc: frm.doc,
          method: "create_user",
          callback: function (r) {
            if (r.message) {
              frappe.show_alert({
                message: __("User created and linked successfully"),
                indicator: "green",
              });
              frm.reload_doc();
            }
          },
        });
      });
    }

    if (
      frm.doc.status === "Active" &&
      !frm.doc.__is_local &&
      !frm.doc.linked_customer
    ) {
      frm.add_custom_button(__("Create Customer"), function () {
        frm.call({
          doc: frm.doc,
          method: "create_customer",
          callbacl: function (r) {
            if (r.message) {
              frappe.show_alert({
                message: __("Customer created successfully"),
                indicator: "green",
              });
              frm.reload_doc();
            }
          },
        });
      });
    }

    if (
      frm.doc.status === "Active" &&
      frm.doc.is_user_created &&
      !frm.doc.warehouse
    ) {
      frm.add_custom_button(__("Create Warehouse"), function () {
        frm.call({
          doc: frm.doc,
          method: "create_channel_partner_warehouse",
          callback: function (r) {
            if (r.message) {
              frappe.show_alert({
                message: __("Warehouse created successfully"),
                indicator: "green",
              });
              frm.reload_doc();
            }
          },
        });
      });
    }
  },
});

frappe.ui.form.on("District PIN Code Table", {
  pin_code: function (frm, cdt, cdn) {
    let row = locals[cdt][cdn];
    if (row.pin_code) {
      frappe.db.get_value(
        "District PIN Code",
        row.pin_code,
        ["district", "city"],
        (response) => {
          if (response) {
            frappe.model.set_value(cdt, cdn, "district", response.district);
            frappe.model.set_value(cdt, cdn, "city", response.city);
          }
        },
      );
    }
  },
});
