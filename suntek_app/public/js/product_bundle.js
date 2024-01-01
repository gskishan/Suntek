   frappe.ui.form.on('Product Bundle Item', {
    item_code: function(frm,cdt,cdn){

        console.log(frm.doc.items)
        frm.doc.items.forEach(function(item){
            console.log(item)
            if (item.item_code){
                frappe.call({
                    method:"frappe.client.get_value",
                    args:{
                        doctype:"Item Price",
                        filters:{
                            item_code:item.item_code,
                            price_list: "Standard Buying"

                        },
                        fieldname:["price_list_rate"]
                        
                     },
                     callback:function(res){
                        if (res.message){
                            console.log(res.message)
                            // frm.fields_dict["items"].grid.get_field("custom_buying_rate").get_query = function(doc,cdt,cdn){
                            //     return{
                            //         filters:{
                            //             item_code:item.item_code
                            //         }
                                    
                            //     }
                            // };
                            frappe.model.set_value(cdt,cdn,"custom_buying_rate",res.message.price_list_rate)
                        } else {
                            frappe.model.set_value(cdt,cdn,"custom_buying_rate",0)
                       
                     }
                     } 

                 

                })
                

            }
        })
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
