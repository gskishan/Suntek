frappe.ui.form.on("Channel Partner Purchase Order", {
	refresh: function (frm) {
		if (
			frm.doc.docstatus === 1 &&
			!frm.doc.sales_order &&
			frm.doc.type_of_case !== "Subsidy" &&
			frappe.user.has_role(["Sales Manager", "System Manager"])
		) {
			frm.add_custom_button(
				__("Create Sales Order"),
				function () {
					frappe.confirm(
						__("Create a Sales Order with the Channel Partner as the customer?"),
						function () {
							frm.call({
								method: "create_sales_order",
								doc: frm.doc,
								freeze: true,
								callback: function (r) {
									if (r.message) {
										frappe.show_alert({
											message: __("Sales Order {0} created", [r.message]),
											indicator: "green",
										});
										frm.reload_doc();
									}
								},
							});
						}
					);
				},
				__("Actions")
			);
		}

		if (frm.doc.sales_order) {
			frm.add_custom_button(
				__("View Sales Order"),
				function () {
					frappe.set_route("Form", "Sales Order", frm.doc.sales_order);
				},
				__("Actions")
			);
		}

		if (frm.doc.type_of_case === "Subsidy") {
			frm.set_intro(
				__(
					"Note: Channel Partner Purchase Orders are not typically needed for Subsidy cases. " +
						"For subsidy cases, regular sales process is followed."
				),
				"red"
			);
		}

		if (frm.doc.type_of_case !== "Subsidy" && frm.doc.docstatus === 1 && !frm.doc.sales_order) {
			frm.set_intro(
				__(
					"This purchase order is awaiting review. Once approved, a Sales Order will be created " +
						"with the Channel Partner as the customer."
				)
			);
		}

		if (frm.doc.sales_order) {
			frm.set_intro(
				__(
					"A Sales Order has been created from this purchase order. " +
						"The Channel Partner is set as the customer."
				),
				"green"
			);
		}

		partner;
		frm.set_query("project", function () {
			return {
				filters: {
					custom_channel_partner: frm.doc.channel_partner,
				},
			};
		});
	},

	onload: function (frm) {
		frm.add_fetch("project", "custom_type_of_case", "type_of_case");

		if (frm.doc.grand_total) {
			let advance = frm.doc.advance_amount || 0;
			frm.set_value("balance_amount", frm.doc.grand_total - advance);
		}

		partner;
		frm.set_query("project", function () {
			return {
				filters: {
					custom_channel_partner: frm.doc.channel_partner,
				},
			};
		});
	},

	channel_partner: function (frm) {
		if (frm.doc.project && frm.doc.channel_partner) {
			frappe.db.get_value("Project", frm.doc.project, "custom_channel_partner", function (r) {
				if (r && r.custom_channel_partner !== frm.doc.channel_partner) {
					frm.set_value("project", "");
				}
			});
		}
	},

	project: function (frm) {
		if (frm.doc.project) {
			frappe.db.get_value("Project", frm.doc.project, "custom_type_of_case", function (r) {
				if (r && r.custom_type_of_case) {
					frm.set_value("type_of_case", r.custom_type_of_case);

					if (r.custom_type_of_case === "Subsidy") {
						frappe.show_alert({
							message: __(
								"Channel Partner Purchase Orders are typically not needed for Subsidy cases."
							),
							indicator: "orange",
						});
					}
				}
			});

			if (frm.doc.project) {
				frappe.call({
					method: "fetch_details_from_project_sales_order",
					doc: frm.doc,
					args: {
						project: frm.doc.project,
					},
					callback: function (r) {
						if (r.message) {
							if (frm.doc.items && frm.doc.items.length > 0) {
								frappe.confirm(
									__(
										"This will replace the current items, taxes and terms with those from the Sales Order. Continue?"
									),
									function () {
										populate_from_sales_order(frm, r.message);
									}
								);
							} else {
								populate_from_sales_order(frm, r.message);
							}
						}
					},
				});
			}
		}
	},

	type_of_case: function (frm) {
		if (frm.doc.type_of_case === "Subsidy") {
			frappe.show_alert({
				message: __("Channel Partner Purchase Orders are typically not needed for Subsidy cases."),
				indicator: "orange",
			});
		}
	},

	taxes_and_charges_template: function (frm) {
		if (frm.doc.taxes_and_charges_template) {
			frm.clear_table("taxes");
			frappe.model.with_doc(
				"Sales Taxes and Charges Template",
				frm.doc.taxes_and_charges_template,
				function () {
					var taxes_template = frappe.get_doc(
						"Sales Taxes and Charges Template",
						frm.doc.taxes_and_charges_template
					);

					$.each(taxes_template.taxes || [], function (i, tax) {
						var row = frm.add_child("taxes");
						row.charge_type = tax.charge_type;
						row.account_head = tax.account_head;
						row.description = tax.description;
						row.rate = tax.rate;
					});

					frm.refresh_field("taxes");
				}
			);
		}
	},

	advance_amount: function (frm) {
		if (frm.doc.grand_total && frm.doc.advance_amount !== undefined) {
			let balance = frm.doc.grand_total - frm.doc.advance_amount;
			frm.set_value("balance_amount", balance);
		} else {
			frm.set_value("balance_amount", frm.doc.grand_total || 0);
		}
	},

	grand_total: function (frm) {
		if (frm.doc.grand_total) {
			let advance = frm.doc.advance_amount || 0;
			frm.set_value("balance_amount", frm.doc.grand_total - advance);
		}
	},

	calculate_total: function (frm) {
		let total = 0;
		let total_qty = 0;

		(frm.doc.items || []).forEach(function (item) {
			total += item.amount || 0;
			total_qty += item.qty || 0;
		});

		frm.set_value("total", total);
		frm.set_value("total_qty", total_qty);

		if (frm.doc.taxes_and_charges) {
			frm.trigger("taxes_and_charges");
		}
	},
});

frappe.ui.form.on("Channel Partner Purchase Order Item", {
	qty: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.rate;
		frappe.model.set_value(cdt, cdn, "amount", row.amount);
		frm.trigger("calculate_total");
	},

	rate: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		row.amount = row.qty * row.rate;
		frappe.model.set_value(cdt, cdn, "amount", row.amount);
		frm.trigger("calculate_total");
	},

	item_code: function (frm, cdt, cdn) {
		var row = locals[cdt][cdn];
		if (row.item_code) {
			frappe.db.get_value(
				"Item",
				row.item_code,
				["item_name", "description", "stock_uom", "standard_rate"],
				function (r) {
					if (r) {
						frappe.model.set_value(cdt, cdn, "item_name", r.item_name);
						frappe.model.set_value(cdt, cdn, "description", r.description);
						frappe.model.set_value(cdt, cdn, "uom", r.stock_uom);
						if (!row.rate) {
							frappe.model.set_value(cdt, cdn, "rate", r.standard_rate);
						}
					}
				}
			);
		}
	},

	items_add: function (frm, cdt, cdn) {},

	items_remove: function (frm) {
		frm.trigger("calculate_total");
	},
});

function populate_from_sales_order(frm, data) {
	if (data.taxes_and_charges_template) {
		frm.set_value("taxes_and_charges_template", data.taxes_and_charges_template);
	}

	if (data.terms_and_conditions) {
		frm.set_value("terms_and_conditions", data.terms_and_conditions);
	}

	if (data.terms) {
		frm.set_value("terms_and_conditions_details", data.terms);
	}

	frm.clear_table("items");
	let total_amount = 0;
	let total_qty = 0;

	data.items.forEach(function (item) {
		var row = frm.add_child("items");
		row.item_code = item.item_code;
		row.item_name = item.item_name;
		row.description = item.description;
		row.qty = item.qty;
		row.uom = item.uom;
		row.rate = item.rate;
		row.warehouse = item.warehouse;

		if (item.amount) {
			row.amount = item.amount;
		} else {
			row.amount = item.rate * item.qty;
		}

		total_amount += flt(row.amount);
		total_qty += flt(item.qty);
	});

	frm.set_value("total", total_amount);
	frm.set_value("total_qty", total_qty);

	frm.clear_table("taxes");
	let total_taxes = 0;

	if (data.taxes && data.taxes.length) {
		frappe.show_alert({
			message: __("Fetching {0} tax entries", [data.taxes.length]),
			indicator: "blue",
		});

		data.taxes.forEach(function (tax) {
			var row = frm.add_child("taxes");
			row.charge_type = tax.charge_type;
			row.account_head = tax.account_head;
			row.description = tax.description;
			row.rate = tax.rate;

			if (tax.tax_amount) {
				row.tax_amount = flt(tax.tax_amount);
				total_taxes += flt(tax.tax_amount);
			} else if (tax.rate) {
				row.tax_amount = flt((total_amount * tax.rate) / 100);
				total_taxes += row.tax_amount;
			}
		});
	}

	frm.set_value("total_taxes_and_charges", total_taxes);

	let grand_total = flt(total_amount) + flt(total_taxes);
	frm.set_value("grand_total", grand_total);

	if (frm.doc.advance_amount) {
		frm.set_value("balance_amount", grand_total - flt(frm.doc.advance_amount));
	} else {
		frm.set_value("balance_amount", grand_total);
	}

	frm.refresh_fields([
		"items",
		"taxes",
		"taxes_and_charges",
		"terms_and_conditions",
		"terms",
		"total",
		"total_qty",
		"total_taxes_and_charges",
		"grand_total",
		"balance_amount",
	]);

	frappe.show_alert({
		message: __("Details fetched from Sales Order {0}", [data.sales_order]),
		indicator: "green",
	});
}
