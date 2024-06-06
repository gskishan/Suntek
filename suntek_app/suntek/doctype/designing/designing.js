// Copyright (c) 2023, kishan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Designing', {
	refresh: function (frm) {
		if (frm.is_new()) {

			frappe.call({
				method: "get_opportunity_details",
				doc: frm.doc,
				callback: function (e) {
					cur_frm.refresh_fields()
				}
			})
		}
	},
	setup: function (frm) {
		cur_frm.set_query("designer", function (frm) {
			return {
				filters: [
					['Employee', 'designation', 'in', ["Autocad draft man", "Autocad Draft Woman"]]
				]
			}
		});
	}



});

frappe.ui.form.on('Designing Item', {
	rate: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		calculate_amount(child);
	},

	qty: function (frm, cdt, cdn) {
		var child = locals[cdt][cdn];
		calculate_amount(child);
	}
});

function calculate_amount(child) {
	child.amount = flt(child.rate) * flt(child.qty);
	refresh_field('amount', child.name, 'bom');
}
