// suntek/suntek/doctype/suntek_settings/suntek_settings.js

frappe.ui.form.on("Suntek Settings", {
	generate_neodove_webhook_secret: function (frm) {
		frappe.call({
			method: "suntek_app.suntek.doctype.suntek_settings.suntek_settings.generate_webhook_secret",
			callback: function (r) {
				if (r.message) {
					let d = new frappe.ui.Dialog({
						title: "New Webhook Token",
						fields: [
							{
								fieldname: "token",
								fieldtype: "Code",
								label: "HMAC Token",
								read_only: 1,
								default: r.message,
							},
						],
						primary_action_label: "Copy",
						primary_action: function () {
							navigator.clipboard.writeText(r.message).then(function () {
								frappe.show_alert({
									message: __("Token copied to clipboard"),
									indicator: "green",
								});
								d.hide();
							});
						},
					});
					d.show();
				}
			},
		});
	},
	generate_ambassador_api_key: function (frm) {
		frappe.call({
			method:
				"suntek_app.suntek.doctype.suntek_settings.suntek_settings.generate_solar_ambassador_api_token",
			callback: function (r) {
				if (r.message) {
					let d = new frappe.ui.Dialog({
						title: "New Solar Ambassador API Key",
						fields: [
							{
								fieldname: "token",
								fieldtype: "Code",
								label: "API Key",
								read_only: 1,
								default: r.message,
							},
						],
						primary_action_label: "Copy",
						primary_action: function () {
							navigator.clipboard.writeText(r.message).then(function () {
								frappe.show_alert({
									message: __("API Key copied to clipboard"),
									indicator: "green",
								});
								d.hide();
							});
						},
					});
					d.show();
				}
			},
		});
	},
});
