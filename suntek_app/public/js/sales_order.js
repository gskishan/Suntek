frappe.ui.form.on('Sales Order', {
    custom_customer_id: function(frm) {
        frm.set_value("custom_customer_id",frm.doc.customer)
    },
    refresh: function(frm) {
        frm.set_value("custom_customer_id",frm.doc.customer)
    },

});
