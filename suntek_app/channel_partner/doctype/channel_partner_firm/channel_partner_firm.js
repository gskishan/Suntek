frappe.ui.form.on("Channel Partner Firm", {
  refresh: function (frm) {
    // Standard Address and Contact creation
    frm.trigger("render_address_and_contact");

    // Buttons to create Channel Partners
    if (!frm.is_new()) {
      frm.add_custom_button(__("Create Channel Partner"), function () {
        frappe.new_doc("Channel Partner", {
          channel_partner_firm: frm.doc.name,
        });
      });

      // Button to view similar firms
      frm.add_custom_button(
        __("Show Similar Firms"),
        function () {
          frappe.set_route("List", "Channel Partner Firm", {
            firm_name: ["like", "%" + frm.doc.firm_name + "%"],
          });
        },
        __("View"),
      );
    }

    // Only set creation fields when the document is new
    if (frm.is_new()) {
      frm.set_value("created_by", frappe.session.user);
      frm.set_value("creation_date", frappe.datetime.now_datetime());
    }
  },

  render_address_and_contact: function (frm) {
    // Render address and contact section using standard ERPNext utilities
    frappe.contacts.render_address_and_contact(frm);
  },

  validate: function (frm) {
    // Validate firm_code format
    if (frm.doc.firm_code) {
      let valid_format = /^[A-Z0-9]{2,10}$/.test(frm.doc.firm_code);
      if (!valid_format) {
        frappe.msgprint(
          __(
            "Firm Code should be 2-10 characters containing only uppercase letters and numbers.",
          ),
        );
        frappe.validated = false;
      }
    }

    // Set modification details only when we're actually saving
    frm.set_value("modified_by", frappe.session.user);
    frm.set_value("modified_date", frappe.datetime.now_datetime());
  },
});
