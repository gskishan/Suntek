frappe.ui.form.on("Customer", {
    onload: function(frm) {
        if (frm.doc.opportunity_name) {
            frappe.call({
                method: "frappe.client.get_value",
                args: {
                    doctype: "Opportunity",
                    filters: {
                        name: frm.doc.opportunity_name

                    },
                    fieldname: ["custom_customer_category"]
                },
                callback: function(res) {
                    frm.set_value("customer_group", res.message.custom_customer_category)
                }
            })



        }
    },

})
