frappe.ui.form.on("Solar Panel Pricing Rule", {
    onload(frm) {
        frm.call({
            method: "get_price_list",
            doc: frm.doc,
            callback: function (r) {
                if (r.message) {
                    frm.set_value("price_list", r.message);
                }
            },
        });
    },

    refresh(frm) {
        frm.add_custom_button(__("Refresh Prices"), function () {
            frappe.show_alert({
                message: __("Refreshing prices..."),
                indicator: "blue",
            });

            frm.call({
                method: "fetch_item_price_from_price_list",
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        if (!frm.is_new()) {
                            frm.reload_doc();
                        } else {
                            frm.set_value("base_price", r.message);
                        }

                        frappe.show_alert({
                            message: __("Prices updated successfully"),
                            indicator: "green",
                        });
                    }
                },
            });
        });
    },

    item(frm) {
        if (frm.doc.item) {
            frm.call({
                method: "fetch_item_price_from_price_list",
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        console.log(r.message);
                        frm.set_value("base_price", r.message);

                        if (!frm.doc.final_price) {
                            frm.set_value("final_price", r.message);
                        }
                    }
                },
            });
        }
    },
});
