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

                

                siteSurveyDoc.opportunity_name = frm.doc.name;
                console.log(siteSurveyDoc.opportunity_name)

                siteSurveyDoc.site_survey_status = "Site Survey Assigned"

                // Remove <br> tags and set address field
                if (frm.doc.__onload["addr_list"][0]){
                    var formattedAddress = frm.doc.__onload["addr_list"][0]

                    siteSurveyDoc.site_location = formattedAddress.name + '\n' + formattedAddress.address_line1 + '\n' + formattedAddress.address_line2 + '\n' + formattedAddress.city + '\n' + formattedAddress.state + '\n' + formattedAddress.pincode + '\n' + formattedAddress.country;

                }

                // Open the Site Survey document for editing
                frappe.set_route('Form', 'Site Survey', siteSurveyDoc.name);

            });
        }, __('Create'));
    },
    custom_average_consumption: function(frm) {
        var averageConsumption = frm.doc.custom_average_consumption;
        var recommendedCapacityUOM = averageConsumption / 120;
        frm.set_value('custom_recommended_capacity_uom', recommendedCapacityUOM.toFixed(2));
    },
    custom_consumption: function(frm, cdt, cdn) {
        if (frm.doc.custom_consumption == "Detailed"){
            autopopulate_month(frm);
        }
    },
    custom_capacity_kw:function(frm){
        updateProposalField(frm);

    },
    custom_capacity_mts:function(frm){
        updateProposalField(frm);

    },
    custom_capacity_watts:function(frm){
        updateProposalField(frm);

    },
    custom_capacity_lpd:function(frm){
        updateProposalField(frm);

    },
    custom_product_category:function(frm){
        updateProposalField(frm);

    },
    custom_product_type:function(frm){
        updateProposalField(frm);

    },
    custom_product_types:function(frm){
        updateProposalField(frm);

    },
    custom_product_typ:function(frm){
        updateProposalField(frm);

    },
    custom_product_typo:function(frm){
        updateProposalField(frm);

    },
    custom_type_of_case:function(frm){
        updateProposalField(frm);

    }
});


function updateProposalField(frm) {
    var capacity_kw = frm.doc.custom_capacity_kw ? frm.doc.custom_capacity_kw + " kw" : '';
    var capacity_mts = frm.doc.custom_capacity_mts ? frm.doc.custom_capacity_mts + " mts" : '';
    var capacity_watt = frm.doc.custom_capacity_watts ? frm.doc.custom_capacity_watts + " watt" : '';
    var capacity_lpd = frm.doc.custom_capacity_lpd ? frm.doc.custom_capacity_lpd + " lpd" : '';
    var product_category = frm.doc.custom_product_category ? frm.doc.custom_product_category + " " : '';
    var product_type_one = frm.doc.custom_product_type ? frm.doc.custom_product_type + " " : '';
    var product_type_two = frm.doc.custom_product_types ? frm.doc.custom_product_types + " " : '';
    var product_type_three = frm.doc.custom_product_typ ? frm.doc.custom_product_typ + " " : '';
    var product_type_four = frm.doc.custom_product_typo ? frm.doc.custom_product_typo + " " : '';
    var type_of_case = frm.doc.custom_type_of_case ? frm.doc.custom_type_of_case + " " : '';

    var proposal = "Proposal for " + capacity_kw + capacity_mts + capacity_watt + capacity_lpd + product_category 
    + "Under " + product_type_one + product_type_two + product_type_three + product_type_four + type_of_case;

    frm.set_value('custom_proposal', proposal);
}





var Month = ["January","February","March","April","May","June","July","August","September","October","November","December"]

function autopopulate_month(frm){
   
    for (var i=0; i < Month.length; i++){
		var d = frm.add_child("custom_details")

		d.month = Month[i];
	}
	frm.refresh_fields("custom_details");

}

frappe.ui.form.on('Month Details', {
        qty:function(frm,cdt,cdn){
            var uniqueMonths = [];
            var totalQty = 0;
        

            frm.doc.custom_details.forEach(function(row) {
                if (row.qty > 0 && row.month && !uniqueMonths.includes(row.month)) {
                    totalQty += row.qty;
                    console.log(totalQty)
                    uniqueMonths.push(row.month);
                }
            });
        
            var averageConsumption = uniqueMonths.length > 0 ? totalQty / uniqueMonths.length : 0;
        
            frm.set_value('custom_average', averageConsumption.toFixed(2));
        
            var RecommendedCapUom = averageConsumption/120
        
            frm.set_value('custom_recommended_cap_uom', RecommendedCapUom.toFixed(2));
        },

})



