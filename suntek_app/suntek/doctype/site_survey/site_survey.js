frappe.ui.form.on("Site Survey", {
    refresh: function(frm) {
    
        frm.add_custom_button(__('Designing'), function() {
    
            frappe.model.with_doctype('Designing', function() {
                var DesigningDoc = frappe.model.get_new_doc('Designing');
                console.log(frm.doc.site_engineer)
				DesigningDoc.designer = frm.doc.site_engineer
				DesigningDoc.site_survey = frm.doc.name;
                DesigningDoc.opportunity_name = frm.doc.opportunity_name;
                DesigningDoc.designing_status = "Open"
                

                // Open the Site Survey document for editing
                frappe.set_route('Form', 'Designing', DesigningDoc.name);

            });
        }, __('Create'));
        frm.fields_dict['site_engineer'].get_query = function(doc, cdt, cdn) {
            return {
                filters: {
                    'department': frm.doc.department
                }
            };
        };
        frm.fields_dict['department'].df.onchange = function() {
            frm.set_value('site_engineer', '');
            frm.refresh_field('site_engineer');
        };
    },
   
});


