frappe.ui.form.on('Site Survey', {
    refresh: function(frm) {

        frm.add_custom_button(__('Designing'), function() {
    
            frappe.model.with_doctype('Designing', function() {
                var DesigningDoc = frappe.model.get_new_doc('Designing');
				
				DesigningDoc.site_survey = frm.doc.name;
                DesigningDoc.opportunity_name = frm.doc.opportunity_name; 
                

                // Open the Site Survey document for editing
                frappe.set_route('Form', 'Designing', DesigningDoc.name);

            });
        }, __('Create'));
    }
});
