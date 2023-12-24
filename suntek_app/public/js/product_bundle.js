   frappe.ui.form.on('Product Bundle Item', {
    rate: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_amount(child);
    },

    qty: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_amount(child);
    }
});

function calculate_amount(child) {
    child.custom_amount = flt(child.rate) * flt(child.qty);
    refresh_field('custom_amount', child.name, 'items');
}
