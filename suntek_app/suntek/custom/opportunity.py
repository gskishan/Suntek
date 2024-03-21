import frappe

def change_opportunity_status(doc,method):
    pass
    

def set_opportunity_name(doc,method):

    if doc.name:
        doc.custom_opportunity_name = doc.name


@frappe.whitelist()
def custom_make_customer(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.opportunity_name = source.name

		if source.opportunity_from == "Lead":
			target.lead_name = source.party_name

	doclist = get_mapped_doc(
		"Opportunity",
		source_name,
		{
			"Opportunity": {
				"doctype": "Customer",
				"field_map": {"currency": "default_currency", "customer_name": "customer_name"},
			}
		},
		target_doc,
		set_missing_values,
	)

	return doclist
