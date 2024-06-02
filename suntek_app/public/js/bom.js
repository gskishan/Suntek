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
                        method: "suntek_app.suntek.doctype.designing.designing.make_bom",
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
        setTimeout(function () {

            if (frm.is_new() && cur_frm.doc.project) {
                frappe.db.get_doc('Project', cur_frm.doc.project)
                    .then(doc => {
                        if (doc.sales_order) {

                            frappe.db.get_doc('Sales Order', doc.sales_order)
                                .then(so => {
                                    cur_frm.set_value("item", so.items[0].item_code)
                                    cur_frm.set_value("quantity", doc.custom_capacity)
                                    cur_frm.set_value("custom_customer", doc.customer)


                                })

                        }


                    })
            }
        }, 400);
    },



})
