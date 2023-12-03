frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
         
        setTimeout(() => {
            
            frm.remove_custom_button('Supplier Quotation', 'Create');
            frm.remove_custom_button('Request For Quotation', 'Create');
            frm.remove_custom_button('Quotation', 'Create');
            frm.remove_custom_button('Opportunity', 'Create');
            }, 10);

        frm.add_custom_button(__('Site Survey'), function() {
    
            frappe.model.with_doctype('Site Survey', function() {
                console.log(frm.doc.__onload["addr_list"][0])
                var siteSurveyDoc = frappe.model.get_new_doc('Site Survey');

                siteSurveyDoc.opportunity_name = frm.doc.name; // Change 'opportunity_name' to the actual fieldname

                // Remove <br> tags and set address field
                var formattedAddress = frm.doc.__onload["addr_list"][0]
            
                siteSurveyDoc.site_location = formattedAddress.name + '\n' + formattedAddress.address_line1 + '\n' + formattedAddress.address_line2 + '\n' + formattedAddress.city + '\n' + formattedAddress.state + '\n' + formattedAddress.pincode + '\n' + formattedAddress.country;


                // Open the Site Survey document for editing
                frappe.set_route('Form', 'Site Survey', siteSurveyDoc.name);

            });
        }, __('Create'));
    }
});

frappe.ui.form.on("Opportunity", {
    custom_consumption: function(frm){
        if (frm.doc.custom_consumption == "Detailed"){
            frm.set_df_property('custom_details', 'hidden', 0)
            var DetailedTable = [
                {'month': 'January'},
                {'month': 'February'},
                {'month': 'March'},
                {'month': 'April'},
                {'month': 'May'},
                {'month': 'June'},
                {'month': 'July'},
                {'month': 'August'},
                {'month': 'September'},
                {'month': 'October'},
                {'month': 'November'},
                {'month': 'December'},
                {'month':"Average Consumtion (Sum/no of month)"}
    
            ]
           
            if(frm.is_new()){
                $.each(DetailedTable,function(i,r){
                    console.log(r)
                    var DetailedTable_add = cur_frm.add_child("custom_details");
                    DetailedTable_add.month = r.month
                    
                    
                });
                frm.refresh_fields("custom_details");
            }
            else if (frm.doc.custom_proposed_action.length == 0){
                $.each(DetailedTable,function(i,r){
                
                    var DetailedTable_add = cur_frm.add_child("custom_details");
                    DetailedTable_add.month = r.month
    
                });
                frm.refresh_fields("custom_details");
            }

        }
    
		
	},
    validate: function(frm) {
        if (frm.doc.custom_consumption == "Detailed") {
            console.log("innnnnnnnnnnnnn")
            // Calculate the sum and average
            var totalSum = 0;
            var nonZeroCount = 0;

            $.each(frm.doc.custom_details || [], function(i, row) {
                if (row.month !== "Average Consumption (Sum/no of month)") {
                    var qty = flt(row.qty || 0);
                    if (qty > 0) {
                        totalSum += qty;
                        nonZeroCount += 1;
                    }
                }
            });

            // Calculate average and set it in the last row
            var average = nonZeroCount > 0 ? totalSum / nonZeroCount : 0;
            frm.doc.custom_details[frm.doc.custom_details.length - 1].qty = average;

            frm.refresh_fields("custom_details");
        }
        else if (frm.doc.custom_consumption == "Average Consumption") {
            var averageConsumption = frm.doc.custom_average_consumption
            // Assuming there is a field named 'custom_recommended_capacity_uom'
            frm.set_value('custom_recommended_capacity_uom', averageConsumption / 120);
        }
    },
  
	
})
