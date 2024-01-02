   frappe.ui.form.on('Product Bundle Item', {
    item_code: function(frm,cdt,cdn){
        var child = locals[cdt][cdn];

            if (child.item_code){
                frappe.model.set_value(cdt,cdn,"rate", null)
                frappe.model.set_value(cdt,cdn,"custom_buying_rate", null)
                
                frappe.call({
                    method:"suntek_app.suntek.custom.product_bundle.update_product_bundle_rate_price",
                    args:{
                            item_code:child.item_code,
                     },
                     callback:function(res){
                        if (res.message){
                            console.log(res.message)
                            if (res.message[0]){
                                frappe.model.set_value(cdt,cdn,"rate", res.message[0])
                            }
                            if (res.message[1]){
                                frappe.model.set_value(cdt,cdn,"custom_buying_rate", res.message[1])
                            }
            
                        }
                     }

                })
                

            }
    },


    rate: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_selling_amount(child);
    },

    qty: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_selling_amount(child);
        calculate_buying_amount(child);
    },
    custom_buying_rate: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        calculate_buying_amount(child);
    },
});

function calculate_selling_amount(child) {
    child.custom_amount = flt(child.rate) * flt(child.qty);
    refresh_field('custom_amount', child.name, 'items');
}

function calculate_buying_amount(child) {
    child.custom_buying_amount = flt(child.custom_buying_rate) * flt(child.qty);

    refresh_field('custom_buying_amount', child.name, 'items');
}
