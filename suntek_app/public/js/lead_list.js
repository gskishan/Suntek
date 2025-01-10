frappe.listview_settings["Lead"] = {
  onload: function (listview) {
    listview.page.add_inner_button(__("Assign Telecallers"), function () {
      frappe.call({
        method: "suntek_app.suntek.custom.lead.bulk_assign_unassigned_leads",
        callback: function (r) {
          listview.refresh();
        },
      });
    });
  },
};
