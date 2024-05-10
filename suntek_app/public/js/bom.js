frappe.ui.form.on("BOM", {
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
 

    //     }
    // }


})
