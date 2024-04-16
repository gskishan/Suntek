frappe.ui.form.on("Stock Entry", {
    refresh: function (frm, doc, dt, dn) {
        frm.add_custom_button(__('Designing'),
            function () {
                if (!cur_frm.doc.project) {
                    frappe.throw({
                        title: __("Mandatory"),
                        message: __("Please Select a Project")
                    });
                }
                else {
                    erpnext.utils.map_current_doc({
                        method: "suntek_app.suntek.doctype.designing.designing.make_stock_entry",
                        source_doctype: "Designing",
                        target: frm,
                        setters: {
                            custom_project: frm.doc.project,
                        },
                        get_query_filters: {
                            custom_project: frm.doc.project,
                            docstatus: 1,
                        },

                    })
                }

            }, __("Get Items From"));

    },
    stock_entry_type: function (frm) {
        if (frm.doc.stock_entry_type == "Material Transfer to Customer" && frm.doc.project) {
            frappe.db.get_value('Project', cur_frm.doc.project, 'customer',)
                .then(r => {
                    if (r.message["customer"] !== null) {
                        frm.set_value("customer", r.message["customer"]);
                    }

                })


        }
    }


})
