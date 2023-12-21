frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        // Iterate through each item in the Quotation
        if (frm.doc.custom_opportunity_name){
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Opportunity",
                    name: frm.doc.custom_opportunity_name,
                },
                callback(r) {
                    if(r.message) {
                        var opportunity_task = r.message;
                        if (opportunity_task.custom_enquiry_status != "Customer Confirmed"){
                            setTimeout(() => {
            
                                frm.remove_custom_button('Sales Order', 'Create');
                                frm.remove_custom_button('Subscription', 'Create');
            
                                }, 10);

                        }
                        
                    }
                }
            });


        }

    }
});
