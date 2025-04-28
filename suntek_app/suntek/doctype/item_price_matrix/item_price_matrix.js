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
                                if (!frm.is_new()) {
                                    frm.reload_doc();
                                } else {
                                    frm.set_value("item_price", r.message);
                                }

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
    },

    item(frm) {
        if (frm.doc.item) {
            frm.call({
                method: "fetch_item_price_from_price_list",
                doc: frm.doc,
                callback: function (r) {
                    if (r.message) {
                        frm.set_value("item_base_price", r.message);

                        if (!frm.doc.final_item_price) {
                            frm.set_value("final_item_price", r.message);
                        }
                    }
                },
            });
        }
    },

    uom_category_1(frm) {
        if (frm.doc.uom_category_1) {
            frm.set_df_property("min_uom_1", "description", `Minimum value for ${frm.doc.uom_category_1}`);
            frm.set_df_property("max_uom_1", "description", `Maximum value for ${frm.doc.uom_category_1}`);
            frm.refresh_fields(["min_uom_1", "max_uom_1"]);
        }
    },

    uom_category_2(frm) {
        if (frm.doc.uom_category_2) {
            frm.set_df_property("min_uom_2", "description", `Minimum value for ${frm.doc.uom_category_2}`);
            frm.set_df_property("max_uom_2", "description", `Maximum value for ${frm.doc.uom_category_2}`);
            frm.refresh_fields(["min_uom_2", "max_uom_2"]);
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
