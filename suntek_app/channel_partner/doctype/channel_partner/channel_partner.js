frappe.ui.form.on("Channel Partner", {
	refresh(frm) {
		if (frm.doc.status === "Active" && !frm.doc.is_user_created && frm.doc.suntek_email) {
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

		if (frm.doc.status === "Active" && !frm.doc.__is_local && !frm.doc.linked_customer) {
			// frm.add_custom_button(__("Create Customer"), function () {
			//   frm.call({
			//     doc: frm.doc,
			//     method: "create_customer",
			//     callbacl: function (r) {
			//       if (r.message) {
			//         frappe.show_alert({
			//           message: __("Customer created successfully"),
			//           indicator: "green",
			//         });
			//         frm.reload_doc();
			//       }
			//     },
			//   });
			// });
		}

		if (frm.doc.status === "Active" && frm.doc.is_user_created && !frm.doc.warehouse) {
			// frm.add_custom_button(__("Create Warehouse"), function () {
			//   frm.call({
			//     doc: frm.doc,
			//     method: "create_channel_partner_warehouse",
			//     callback: function (r) {
			//       if (r.message) {
			//         frappe.show_alert({
			//           message: __("Warehouse created successfully"),
			//           indicator: "green",
			//         });
			//         frm.reload_doc();
			//       }
			//     },
			//   });
			// });
		}
	},

	channel_partner_firm: function (frm) {
		// When firm changes, fetch address and contact info from firm
		if (frm.doc.channel_partner_firm) {
			frappe.db.get_doc("Channel Partner Firm", frm.doc.channel_partner_firm).then((firm) => {
				// If firm has an address, suggest using it
				if (firm.address) {
					frappe.confirm(`Do you want to use the address from ${firm.firm_name}?`, () => {
						// Yes, use the firm's address
						frappe.db.get_value(
							"Address",
							firm.address,
							["name", "address_line1", "address_line2", "city", "state", "country", "pincode"],
							(r) => {
								if (r) {
									// Create a new address for the channel partner, linked to the same physical address
									frm.set_value("channel_partner_address", r.name);
								}
							}
						);
					});
				}
			});
		}
	},
});

frappe.ui.form.on("District PIN Code Table", {
	pin_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.pin_code) {
			frappe.db.get_value("District PIN Code", row.pin_code, ["district", "city"], (response) => {
				if (response) {
					frappe.model.set_value(cdt, cdn, "district", response.district);
					frappe.model.set_value(cdt, cdn, "city", response.city);
				}
			});
		}
	},
});
