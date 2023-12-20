    frappe.ui.form.on('Product Bundle',{
            refresh: function(frm){
                frm.add_custom_button(__('Update Item Price'), function(){
                    frappe.call({
                        method:"suntek_app.suntek.custom.product_bundle.update_product_bundle_rate_price",
                        args:{
                            docname: frm.doc.name
                        },
                        callback: function(response) {
                            console.log(response)
                            if (response.message) {
                                console.log(response.message['rate'])
                                frm.refresh();
                            }
                        }
                    })
                },)
            }
    })

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
