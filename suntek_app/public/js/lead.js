frappe.ui.form.on("Lead", {
	refresh: function (frm) {
		var status = frm.doc.custom_enquiry_status;

		setTimeout(() => {
			frm.remove_custom_button("Customer", "Create");
			frm.remove_custom_button("Prospect", "Create");
			frm.remove_custom_button("Quotation", "Create");
			frm.remove_custom_button("Opportunity", "Create");
		}, 10);

		if (status == "Interested") {
			frm.add_custom_button("Opportunity", function () {
				frm.trigger("custom_make_opportunity");
			});
		}
	},

	source: function (frm) {
		// Only set department automatically if it's not already set
		if (frm.doc.source === "Digital Marketing" && !frm.doc.custom_department) {
			frm.set_value("custom_department", "Tele Sales - SESP");
		}
	},

	setup: function (frm) {
		if (frm.is_new()) {
			if (frm.doc.source === "Digital Marketing" && !frm.doc.custom_department) {
				frm.set_value("custom_department", "Tele Sales - SESP");
			}
		}
	},

	organization_section: function (frm) {
		let show_section =
			frm.doc.custom_customer_category &&
			["Apartments", "Gated Communities", "Government", "C & I"].includes(
				frm.doc.custom_customer_category
			);
		frm.toggle_display("organization_section", show_section);
	},

	industry: function (frm) {
		let show_industry =
			frm.doc.custom_customer_category == "C & I" ||
			frm.doc.custom_customer_category == "Government";
		frm.toggle_display("industry", show_industry);
	},

	custom_customer_category: function (frm) {
		// Trigger both checks when category changes
		frm.trigger("organization_section");
		frm.trigger("industry");
	},
	custom_make_opportunity: async function (frm) {
		let existing_prospect = (
			await frappe.db.get_value(
				"Prospect Lead",
				{
					lead: frm.doc.name,
				},
				"name",
				null,
				"Prospect"
			)
		).message.name;
		let fields = [];
		if (!existing_prospect) {
			fields = [
				{
					label: "Create Prospect",
					fieldname: "create_prospect",
					fieldtype: "Check",
					default: 1,
				},
				{
					label: "Prospect Name",
					fieldname: "prospect_name",
					fieldtype: "Data",
					default: frm.doc.company_name,
					depends_on: "create_prospect",
				},
			];
		}
		let existing_contact = (
			await frappe.db.get_value(
				"Contact",
				{
					first_name: frm.doc.first_name || frm.doc.lead_name,
					last_name: frm.doc.last_name,
				},
				"name"
			)
		).message.name;

		if (!existing_contact) {
			fields.push({
				label: "Create Contact",
				fieldname: "create_contact",
				fieldtype: "Check",
				default: "1",
			});
		}

		if (fields) {
			var d = new frappe.ui.Dialog({
				title: __("Create Opportunity"),
				fields: fields,
				primary_action: function () {
					var data = d.get_values();
					frappe.call({
						method: "create_prospect_and_contact",
						doc: frm.doc,
						args: {
							data: data,
						},
						freeze: true,
						callback: function (r) {
							if (!r.exc) {
								frappe.model.open_mapped_doc({
									method: "suntek_app.suntek.custom.lead.custom_make_opportunity",
									frm: frm,
								});
							}
							d.hide();
						},
					});
				},
				primary_action_label: __("Create"),
			});
			d.show();
		} else {
			frappe.model.open_mapped_doc({
				method: "suntek_app.suntek.custom.lead.custom_make_opportunity",
				frm: frm,
			});
		}
	},
	custom_company_name: function (frm) {
		if (frm.doc.custom_company_name) {
			cur_frm.set_value("company_name", cur_frm.doc.custom_company_name);
		}
	},
});

frappe.ui.form.on("Neodove Dispose Details", {
	call_recording: function (frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		if (row.call_recording_url) {
			window.open(row.call_recording_url, "_blank");
		}
	},
});
