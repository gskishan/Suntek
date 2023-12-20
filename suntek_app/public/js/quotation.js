frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        // Iterate through each item in the Quotation
        $.each(frm.doc.items, function(i, r) {
            // Check if the item has a reference to an Opportunity
            if (r.prevdoc_docname) {
                frappe.call({
                    method: "frappe.client.get",
                    args: {
                        doctype: "Opportunity",
                        name: r.prevdoc_docname,
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
        });
    }
});
