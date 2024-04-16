import frappe
from frappe.model.mapper import get_mapped_doc
def change_opportunity_status(doc,method):
	pass
	

def set_opportunity_name(doc,method):
	if doc.name:
		doc.custom_opportunity_name = doc.name
	if doc.contact_person:
		doc.customer_name=doc.contact_person
	if doc.custom_customer_category=='C & I':
		doc.customer_name=doc.custom_company_name
	vaidate_address(doc)

def vaidate_address(doc):
	sql="""select name from `tabDynamic Link` where link_doctype="Lead" and link_name="{0}" """.format(doc.party_name)
	if not frappe.db.sql(sql,as_dict=True):
		frappe.throw("Address missing")
		

@frappe.whitelist()
def custom_make_customer(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.opportunity_name = source.name
		target.custom_company_name = source.custom_company_name

		if source.opportunity_from == "Lead":
			target.lead_name = source.party_name
		if source.custom_customer_category=='C & I':
			target.customer_name=source.custom_company_name
		if source.custom_customer_category=='Individual':
			target.customer_name=source.contact_person

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
