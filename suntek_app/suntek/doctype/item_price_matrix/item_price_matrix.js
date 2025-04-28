// Copyright (c) 2025, kishan and contributors
// For license information, please see license.txt

frappe.ui.form.on("Item Price Matrix", {
    refresh(frm) {
        if (frm.doc.docstatus == 0) {
            frm.add_custom_button(
                __("Refresh Prices"),
                function () {
                    frappe.show_alert({
                        message: __("Refreshing prices..."),
                        indicator: "blue",
                    });

                    frm.call({
                        method: "fetch_item_price_from_price_list",
                        doc: frm.doc,
                        callback: function (r) {
                            if (r.message) {
                                frm.reload_doc();
                                frappe.show_alert({
                                    message: __("Prices updated successfully"),
                                    indicator: "green",
                                });
                            }
                        },
                    });
                },
                __("Actions"),
            );
        }

        // Set default checkboxes for new form
        if (frm.is_new()) {
            frm.set_value("selling", 1);
            frm.set_value("buying", 0);
        }

        if (!frm.doc.item_price) {
            frm.call({
                method: "fetch_item_price_from_price_list",
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        frm.reload_doc();
                    }
                },
            });
        }
    },

    validate(frm) {
        if (!frm.is_new()) {
            frm.call({
                method: "validate_checkboxes",
                doc: frm.doc,
            });
        }
    },
});
