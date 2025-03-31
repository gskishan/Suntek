frappe.ui.form.on("Channel Partner Firm", {
  refresh: function (frm) {
    frm.trigger("render_address_and_contact");

    if (!frm.is_new()) {
      frm.add_custom_button(__("Create Channel Partner"), function () {
        frappe.new_doc("Channel Partner", {
          channel_partner_firm: frm.doc.name,
        });
      });

      frm.add_custom_button(
        __("Show Similar Firms"),
        function () {
          frappe.set_route("List", "Channel Partner Firm", {
            firm_name: ["like", "%" + frm.doc.firm_name + "%"],
          });
        },
        __("View")
      );
    }
  },

  render_address_and_contact: function (frm) {
    frappe.contacts.render_address_and_contact(frm);
  },

  validate: function (frm) {
    if (frm.doc.firm_code) {
      let valid_format = /^[A-Z0-9]{2,10}$/.test(frm.doc.firm_code);
      if (!valid_format) {
        frappe.msgprint(
          __(
            "Firm Code should be 2-10 characters containing only uppercase letters and numbers."
          )
        );
        frappe.validated = false;
      }
    }
  },
});
