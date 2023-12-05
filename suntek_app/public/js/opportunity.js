frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
         
        setTimeout(() => {
            
            frm.remove_custom_button('Supplier Quotation', 'Create');
            frm.remove_custom_button('Request For Quotation', 'Create');
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
    },
    custom_average_consumption: function(frm) {
        var averageConsumption = frm.doc.custom_average_consumption;
        frm.set_value('custom_recommended_capacity_uom', averageConsumption / 120);
    },

    onload: function(frm) {
        if (frm.doc.party_name) {
            frappe.call({
                method: "frappe.client.get",
                args: {
                    doctype: "Lead",
                    name: frm.doc.party_name
                },
                callback: function(response) {
                    console.log(response)
                    var lead_doc = response.message;
                    if (lead_doc) {
                        // Clear existing items in the Opportunity
                        frm.clear_table('items');
                        
                        // Populate items from the Lead
                        lead_doc.custom_items.forEach(function(item) {
                            
                            var row = frappe.model.add_child(frm.doc, 'Opportunity Item', 'items');
                        
                            row.item_code = item.item_code
                            row.item_name = item.item_name
                            row.item_group = item.item_group
                            row.brand = item.brand
                            row.description = item.description
                            row.qty = item.qty
                            row.rate = item.rate
                            row.amount = item.amount
                            row.base_rate = item.base_rate
                            row.base_amount = item.base_amount
                            
                            // Add other fields as needed
                        });

                        // Refresh the form to reflect the changes
                        frm.refresh_fields();
                    }
                }
            });
        }
    }
});


frappe.ui.form.on('Month Details', {
    qty: function(frm, cdt, cdn) {
        calculateAverageConsumption(frm);
    },

    month: function(frm, cdt, cdn) {
        calculateAverageConsumption(frm);
    }
});

function calculateAverageConsumption(frm) {
    var uniqueMonths = [];
    var totalQty = 0;

    frm.doc.custom_details.forEach(function(row) {
        if (row.qty > 0 && row.month && !uniqueMonths.includes(row.month)) {
            totalQty += row.qty;
            uniqueMonths.push(row.month);
        }
    });

    var averageConsumption = uniqueMonths.length > 0 ? totalQty / uniqueMonths.length : 0;

    frm.set_value('custom_average', averageConsumption);

    var RecommendedCapUom = averageConsumption/120

    frm.set_value('custom_recommended_cap_uom', RecommendedCapUom);
}


