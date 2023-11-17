frappe.ui.form.on('Lead', {
    refresh: function(frm) {

        frm.set_df_property('status', 'options', ["Lead","Open","Replied","Opportunity","Quotation","Lost Quotation","Interested","Converted","Not Interested"])
        
        var status = frm.doc.status;
       
        // Check if the status is "Interested"
        if (status != "Interested") {
        
            setTimeout(() => {
                frm.remove_custom_button('Opportunity', 'Create');
                }, 10);
        
        } 
    },
    
    
});



