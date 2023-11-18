frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {

        frm.add_custom_button(__('Site Survey'), function() {
    
            frappe.model.with_doctype('Site Survey', function() {
                var siteSurveyDoc = frappe.model.get_new_doc('Site Survey');

                siteSurveyDoc.opportunity_name = frm.doc.name; // Change 'opportunity_name' to the actual fieldname

                // Remove <br> tags and set address field
                var formattedAddress = frm.doc.address_display.replace(/<br>/g, '\n');
                siteSurveyDoc.site_location = formattedAddress;

                // Open the Site Survey document for editing
                frappe.set_route('Form', 'Site Survey', siteSurveyDoc.name);

            });
        }, __('Create'));
    }
});
