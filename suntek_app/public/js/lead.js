frappe.ui.form.on('Lead', {
    refresh: function(frm) {
       
        var status = frm.doc.custom_enquiry_status;
    
        setTimeout(() => {
            
            frm.remove_custom_button('Customer', 'Create');
            frm.remove_custom_button('Prospect', 'Create');
            frm.remove_custom_button('Quotation', 'Create');
            frm.remove_custom_button('Opportunity', 'Create');
            }, 10);
        
        if (status == "Interested") {
            
            setTimeout(() => {
                frm.add_custom_button('Opportunity', function() {
                    frappe.model.open_mapped_doc({
        			method: "suntek_app.suntek.custom.lead.custom_make_opportunity",
        			frm: cur_frm,

                   
               
                });
            }, 10);
        }
    }
});
