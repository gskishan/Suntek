frappe.ui.form.on('Lead', {
    refresh: function(frm) {
       
        var status = frm.doc.custom_enquiry_status;
    
        setTimeout(() => {
            
            frm.remove_custom_button('Customer', 'Create');
            frm.remove_custom_button('Prospect', 'Create');
            frm.remove_custom_button('Quotation', 'Create');
            }, 10);
        
        if (status != "Interested") {
            
            setTimeout(() => {
                frm.remove_custom_button('Opportunity', 'Create');
               
                
            }, 10);
        }
    },
    
    
});



