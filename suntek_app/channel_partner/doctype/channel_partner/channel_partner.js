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

    if (frm.doc.channel_partner_firm) {
      frm.add_custom_button(
        __("View Firm"),
        function () {
          frappe.set_route(
            "Form",
            "Channel Partner Firm",
            frm.doc.channel_partner_firm,
          );
        },
        __("Firm"),
      );

      frm.add_custom_button(
        __("Set as Primary Contact"),
        function () {
          frappe.call({
            method: "frappe.client.get",
            args: {
              doctype: "Channel Partner Firm",
              name: frm.doc.channel_partner_firm,
            },
            callback: function (r) {
              if (r.message) {
                let firm = r.message;
                let partnerExists = false;
                let isPrimary = false;

                // Check if partner already exists in the list
                if (firm.channel_partners) {
                  for (let i = 0; i < firm.channel_partners.length; i++) {
                    let p = firm.channel_partners[i];

                    if (p.channel_partner === frm.doc.name) {
                      partnerExists = true;
                      isPrimary = p.is_primary;

                      if (!isPrimary) {
                        // Update to primary
                        frappe.db
                          .set_value(
                            "Channel Partner Link",
                            p.name,
                            "is_primary",
                            1,
                          )
                          .then(() => {
                            frappe.show_alert({
                              message: __(
                                "Set as primary contact for the firm",
                              ),
                              indicator: "green",
                            });
                          });
                      }
                    } else if (p.is_primary) {
                      // Unset other primary contacts
                      frappe.db.set_value(
                        "Channel Partner Link",
                        p.name,
                        "is_primary",
                        0,
                      );
                    }
                  }
                }

                if (!partnerExists) {
                  // Add this partner to the firm and set as primary
                  frappe.call({
                    method:
                      "suntek_app.channel_partner.doctype.channel_partner_firm.channel_partner_firm.add_channel_partner_to_firm",
                    args: {
                      firm: frm.doc.channel_partner_firm,
                      partner: frm.doc.name,
                      is_primary: 1,
                    },
                    callback: function (r) {
                      if (r.message) {
                        frappe.show_alert({
                          message: __("Added as primary contact for the firm"),
                          indicator: "green",
                        });
                      }
                    },
                  });
                } else if (isPrimary) {
                  frappe.show_alert({
                    message: __("Already the primary contact"),
                    indicator: "blue",
                  });
                }
              }
            },
          });
        },
        __("Firm"),
      );
    }
  },

  channel_partner_firm: function (frm) {
    // When firm changes, fetch address and contact info from firm
    if (frm.doc.channel_partner_firm) {
      frappe.db
        .get_doc("Channel Partner Firm", frm.doc.channel_partner_firm)
        .then((firm) => {
          // If firm has an address, suggest using it
          if (firm.address) {
            frappe.confirm(
              `Do you want to use the address from ${firm.firm_name}?`,
              () => {
                // Yes, use the firm's address
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
                      // Create a new address for the channel partner, linked to the same physical address
                      frm.set_value("channel_partner_address", r.name);
                    }
                  },
                );
              },
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
        },
      );
    }
  },
});
