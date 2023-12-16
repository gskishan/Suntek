from frappe import _



# def update_opportunity_dashboard(data):
#     return {
#         "fieldname": "opportunity_name",
#         "internal_links": {
# 			"Quotation": ["items", "prevdoc_docname"],
# 		},
#         "transactions": [
#             {"label": _("Site Survey"), "items":["Site Survey"]},
#             {"label": _("Designing"), "items":["Designing"]},
            
#         ], 
    
#     }

def update_opportunity_dashboard(data):
	return {
		"fieldname": "opportunity_name",
		"non_standard_fieldnames": {
			"Quotation": "prevdoc_docname"
		},
        "transactions": [
            {"label": _("Site Survey"), "items":["Site Survey"]},
            {"label": _("Designing"), "items":["Designing"]},
            {"label": _("Quotation"), "items":["Quotation"]},
            
        ]
	
	}

def update_enquiry_dashboard(data):
	return{
		"fieldname":"party_name",
	"transactions": [
		{"label": _("Opportunity"), "items":["Opportunity"]},
	]

	}





