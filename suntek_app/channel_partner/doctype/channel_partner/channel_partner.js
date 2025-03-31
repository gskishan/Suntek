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
  },

  channel_partner_firm: function (frm) {
    if (frm.doc.channel_partner_firm) {
      frappe.db
        .get_doc("Channel Partner Firm", frm.doc.channel_partner_firm)
        .then((firm) => {
          if (firm.address) {
            frappe.confirm(
              `Do you want to use the address from ${firm.firm_name}?`,
              () => {
                frappe.db.get_value(
                  "Address",
                  firm.address,
                  [
                    "name",
                    "address_line1",
                    "address_line2",
                    "city",
                    "state",
                    "country",
                    "pincode",
                  ],
                  (r) => {
                    if (r) {
                      frm.set_value("channel_partner_address", r.name);
                    }
                  }
                );
              }
            );
          }
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
        }
      );
    }
  },
});
