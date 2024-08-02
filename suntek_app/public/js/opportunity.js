frappe.ui.form.on('Opportunity', {
    refresh: function(frm) {
        console.log("refreshd")

	    $("#opportunity-activities_tab-tab").css("display", "none");
	cur_frm.set_df_property("custom_enquiry_status", "options", ["Open",
			    "Closed",
			    "In Progress",
			    "New",
			    "Payment pending",
			    "PO send",
			    "Waiting on client approval",
			    "Rejected by client",
			    "Rejected by Suntek",
			    "Enquiry status 2",
			    "Quotation",
			    "Converted",
			    "Lost",
			    "Replied"]);
	if (cur_frm.doc.status=="Quotation" || cur_frm.doc.status=="Converted" ){
			cur_frm.set_df_property("custom_enquiry_status", "options", ["Open",
			    "Closed",
			    "Customer Confirmed",
			    "In Progress",
			    "New",
			    "Payment pending",
			    "PO send",
			    "Waiting on client approval",
			    "Rejected by client",
			    "Rejected by Suntek",
			    "Enquiry status 2",
			    "Quotation",
			    "Converted",
			    "Lost",
			    "Replied"]);
		}
     
         
        setTimeout(() => {
            
            frm.remove_custom_button('Supplier Quotation', 'Create');
            frm.remove_custom_button('Request For Quotation', 'Create');
            frm.remove_custom_button('Opportunity', 'Create');
	    frm.remove_custom_button('Customer', 'Create');
            }, 10);
	  setTimeout(() => {
		frm.add_custom_button(__(" Customer"),
		function () {
			frappe.model.open_mapped_doc({
			method: "suntek_app.suntek.custom.opportunity.custom_make_customer",
			frm: cur_frm,
		});
		},
		__("Create"));
	  }, 100);

        frm.add_custom_button(__('Site Survey'), function() {
    
            frappe.model.with_doctype('Site Survey', function() {
                console.log(frm.doc.__onload["addr_list"][0])
                var siteSurveyDoc = frappe.model.get_new_doc('Site Survey');

                

                siteSurveyDoc.opportunity_name = frm.doc.name;
                console.log(siteSurveyDoc.opportunity_name)
		if (frm.doc.custom_customer_category=="Individual"){
			siteSurveyDoc.customer_name=frm.doc.contact_person
		}
		if (frm.doc.custom_customer_category=='C & I'){
			siteSurveyDoc.customer_name=frm.doc.custom_company_name
		}
		siteSurveyDoc.customer_number=frm.doc.contact_mobile
		siteSurveyDoc.opportunity_owner=frm.doc.opportunity_owner
		siteSurveyDoc.sales_person=frm.doc.custom_sales_excecutive
		siteSurveyDoc.poc_name=frm.doc.custom_person_name
		siteSurveyDoc.poc_contact=frm.doc.custom_another_mobile_no
		    

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

    custom_product_category:function(frm){
        if (frm.doc.custom_product_category == ""){
            frm.fields_dict.custom_capacity.df.label = "Capacity";
            frm.set_df_property('custom_product_type', 'options', ['']); 
            
        }
        if (frm.doc.custom_product_category == "Solar Fencing"){
            frm.fields_dict.custom_capacity.df.label = "Capacity (Mts)";
            frm.set_df_property('custom_product_type', 'options', ['Ground Fencing', 'Wall Fencing']); 
            
            
        }
       
        if (frm.doc.custom_product_category == "Solar PV Power"){

            frm.fields_dict.custom_capacity.df.label = "Capacity (KW)";
            frm.set_df_property('custom_product_type', 'options', ['Hybrid', 'Off Grid','On Grid']); 
            frm.refresh_field('custom_product_type');
            
        }
       
        if (frm.doc.custom_product_category == "Solar Street Light"){

            frm.fields_dict.custom_capacity.df.label = "Capacity (Watts)";
            frm.set_df_property('custom_product_type', 'options', ['Semi Integrated', 'Stand Alone']); 
            frm.refresh_field('custom_product_type');
            
        }
       
        if (frm.doc.custom_product_category == "Solar Water Heater"){

            frm.fields_dict.custom_capacity.df.label = "Capacity (LPD)";
            frm.set_df_property('custom_product_type', 'options', ['ETC', 'FPC','FPC-P']); 
            frm.refresh_field('custom_product_type');
            
        }
       
        if (frm.doc.custom_product_category == "Heat Pump"){

            frm.fields_dict.custom_capacity.df.label = "Capacity (LPH)";
            frm.set_df_property('custom_product_type', 'options'); 
            
        }
        frm.refresh_field('custom_product_type');
        frm.refresh_field('custom_capacity');
        updateProposalField(frm);
        
    },

    custom_capacity:function(frm){
        
        updateProposalField(frm);

    },
    custom_product_type:function(frm){
        
        updateProposalField(frm);

    },
    custom_type_of_case:function(frm){
        updateProposalField(frm);

    },
	opportunity_owner: function (frm) {
		  if (frm.doc.opportunity_owner) {
			  frappe.call({
				  method: "suntek_app.custom_script.opportunity.get_emp",
				  args: {
					  "user": frm.doc.opportunity_owner,
  
				  }, callback: function (r) {
					if(r.message){
					
					  cur_frm.set_value("custom_sales_excecutive",r.message[0].name)
					  cur_frm.set_value("custom_mobile_no",r.message[0].cell_number)
					}
					  else{
						    cur_frm.set_value("custom_sales_excecutive","")
					  cur_frm.set_value("custom_mobile_no","")
					  }
					 
  
				  }
			  })
		  }
  
  
	  }
  

});


function updateProposalField(frm) {
    var product_category = frm.doc.custom_product_category ? frm.doc.custom_product_category + " " : '';
    var product_type = frm.doc.custom_product_type ? frm.doc.custom_product_type + " " : '';
    var type_of_case = frm.doc.custom_type_of_case ? frm.doc.custom_type_of_case + " " : '';



    if (frm.doc.custom_product_category == "Solar Fencing"){
        var capacity = frm.doc.custom_capacity ? frm.doc.custom_capacity + " Mts " : ''; 
       
    }
    if (frm.doc.custom_product_category == "Solar PV Power"){
        var capacity = frm.doc.custom_capacity ? frm.doc.custom_capacity + " KW " : ''; 
        
    }
    if (frm.doc.custom_product_category == "Solar Street Light"){
        var capacity = frm.doc.custom_capacity ? frm.doc.custom_capacity + " Watts " : ''; 
    }
    if (frm.doc.custom_product_category == "Solar Water Heater"){
        var capacity = frm.doc.custom_capacity ? frm.doc.custom_capacity + " LPD " : ''; 
    }
    if (frm.doc.custom_product_category == "Heat Pump"){
        var capacity = frm.doc.custom_capacity ? frm.doc.custom_capacity + " LPH " : ''; 
    }

    var proposal = '';

    if (product_category) {
        proposal = "Proposal for " + capacity + product_category +
            " Under " + product_type + type_of_case;
    }

    frm.set_value('custom_proposal', proposal.trim());
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



