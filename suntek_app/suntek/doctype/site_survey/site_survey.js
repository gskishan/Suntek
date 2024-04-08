frappe.ui.form.on("Site Survey", {
    refresh: function (frm) {
        if (frm.is_new()){

            frappe.call({
                method: "get_opportunity_details",
                doc: frm.doc,
                callback: function (e) {
                    cur_frm.refresh_fields()
                }
            })
        }
    
    
        frm.add_custom_button(__('Designing'), function () {

        frappe.model.with_doctype('Designing', function () {
            var DesigningDoc = frappe.model.get_new_doc('Designing');
            console.log(frm.doc.site_engineer)
            DesigningDoc.designer = frm.doc.site_engineer
            DesigningDoc.site_survey = frm.doc.name;
            DesigningDoc.opportunity_name = frm.doc.opportunity_name;
            DesigningDoc.designing_status = "Open"

            
            DesigningDoc.customer_name=frm.doc.customer_name
            DesigningDoc.customer_number=frm.doc.customer_number
            DesigningDoc.opportuniy_owner=frm.doc.opportunity_owner
            DesigningDoc.sales_person=frm.doc.sales_person
            DesigningDoc.poc_name=frm.doc.poc_name
            DesigningDoc.poc_contact=frm.doc.poc_contact


            // Open the Site Survey document for editing
            frappe.set_route('Form', 'Designing', DesigningDoc.name);

        });
    }, __('Create'));
    frm.fields_dict['site_engineer'].get_query = function (doc, cdt, cdn) {
        return {
            filters: {
                'department': frm.doc.department
            }
        };
    };
    frm.fields_dict['department'].df.onchange = function () {
        frm.set_value('site_engineer', '');
        frm.refresh_field('site_engineer');
    };
},
   
});


