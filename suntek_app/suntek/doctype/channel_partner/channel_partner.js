// Copyright (c) 2025, kishan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Channel Partner", {
	refresh(frm) {},
});

frappe.ui.form.on("Channel Partner PIN Code Table", {
	pin_code: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.pin_code) {
			frappe.db.get_value(
				"Channel Partner PIN Codes",
				row.pin_code,
				["district", "city"], // Added city to the fields to fetch
				(response) => {
					if (response) {
						frappe.model.set_value(cdt, cdn, "district", response.district);
						frappe.model.set_value(cdt, cdn, "city", response.city); // Setting the city value
					}
				}
			);
		}
	},
});
