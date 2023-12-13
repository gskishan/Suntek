// Copyright (c) 2023, kishan and contributors
// For license information, please see license.txt



frappe.ui.form.on('Designing Item', {
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
    child.amount = flt(child.rate) * flt(child.qty);
    refresh_field('amount', child.name, 'bom');
}
