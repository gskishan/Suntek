frappe.ui.form.on("Delivery Note", {
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
                    method: "suntek_app.suntek.doctype.designing.designing.get_item",
                    source_doctype: "Designing",
                    target: frm,
                    setters: {
                        project: frm.doc.project,
                    },
                    get_query_filters: {
                        customer: frm.doc.project,
                    },

                }) 
                }

            }, __("Get Items From"));

    },


})