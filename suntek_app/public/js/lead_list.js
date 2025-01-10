frappe.listview_settings["Lead"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__("Assign Telecallers"), function () {
			frappe.confirm(
				"Are you sure you want to assign all unassigned leads to telecallers?",
				function () {
					frappe.show_alert({
						message: __("Assigning leads..."),
						indicator: "blue",
					});

					frappe.call({
						method: "suntek_app.suntek.custom.lead.bulk_assign_unassigned_leads",
						callback: function (r) {
							listview.refresh();
						},
					});
				}
			);
		});
	},
};
