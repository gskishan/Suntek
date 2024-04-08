frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Remove existing buttons
        if (frm.doc.custom_type_of_case != "Subsidy" || frm.doc.custom_type_of_case != "Non Subsidy"){
            $('.document-link[data-doctype="Discom"] .btn[data-doctype="Discom"]').remove();
        }
           if (!frm.doc.custom_type_of_case == "Subsidy"){
               $('.document-link[data-doctype="Subsidy"] .btn[data-doctype="Subsidy"]').remove();
        }
        
        if(!frm.is_new() && frm.doc.custom_project_template){
            frm.set_df_property('custom_project_template', 'read_only', 1)

        }
        frm.clear_custom_buttons();

        if (frm.doc.custom_type_of_case == "Subsidy") {
            // Show both "Discom" and "Subsidy" buttons
            if (!frm.doc.custom_discom_id) {
                frm.add_custom_button(__('Discom'), function() {
                    frappe.model.with_doctype('Discom', function() {
                        var discomDoc = frappe.model.get_new_doc('Discom');
                            discomDoc.project_name = frm.doc.name
                            discomDoc.sales_order = frm.doc.sales_order
                            discomDoc.customer_name = frm.doc.customer
            
                        frappe.set_route('Form', 'Discom', discomDoc.name);
                    });
                }, __('Create'));
            }
            if (!frm.doc.custom_subsidy_id) {
                frm.add_custom_button(__('Subsidy'), function() {
                    frappe.model.with_doctype('Subsidy', function() {
                        var subsidyDoc = frappe.model.get_new_doc('Subsidy');
                        subsidyDoc.project_name = frm.doc.name
                        subsidyDoc.sales_order = frm.doc.sales_order
                        subsidyDoc.customer_name = frm.doc.customer
                        frappe.set_route('Form', 'Subsidy', subsidyDoc.name);
                    });
                }, __('Create'));
            }
        } else if (frm.doc.custom_type_of_case == "Non Subsidy") {
            if (!frm.doc.custom_discom_id) {
            // Show only "Discom" button
                frm.add_custom_button(__('Discom'), function() {
                    frappe.model.with_doctype('Discom', function() {
                        var discomDoc = frappe.model.get_new_doc('Discom');
                            discomDoc.project_name = frm.doc.name
                            discomDoc.sales_order = frm.doc.sales_order
                            discomDoc.customer_name = frm.doc.customer
                        frappe.set_route('Form', 'Discom', discomDoc.name);
                    });
                }, __('Create'));
            }
        }
        // No buttons for other cases
    }
});
