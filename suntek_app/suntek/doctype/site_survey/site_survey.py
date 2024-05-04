# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class SiteSurvey(Document):
    def onload(self):
        if self.docstatus == 1:
            self.update_site_survery_status()
    
    def validate(self):
        self.update_site_survey_status_on_save()


    def after_insert(self):
        self.update_site_survey_status_on_save()
        self.update_opportunity_status_section()

    def on_submit(self):
        self.update_site_survery_status()
        self.update_opportunity_status_section()

    def update_site_survey_status_on_save(self):
        self.site_survey_status = "Site Survey Assigned"

    def update_site_survery_status(self):
        self.site_survey_status = "Site Survey Completed"
        
    @frappe.whitelist()	
    def get_opportunity_details(self):
        if self.is_new() and self.custom_project:
            project_doc=frappe.get_doc("Project",self.custom_project)
            so= project_doc.sales_order
            opportunity= frappe.db.get_value('Sales Order', so, 'custom_opportunity_name')
            op=frappe.get_doc("Opportunity", opportunity)
            self.opportunity_name=op.name
            self.customer_name=project_doc.customer
            self.customer_number=project_doc.custom_customer_mobile
            self.opportunity_owner=op.opportunity_owner
            self.sales_person=op.custom_sales_excecutive
            self.poc_name=project_doc.custom_poc_person_name
            self.poc_contact=project_doc.custom_poc_mobile_no
            sql="""select parent from `tabDynamic Link` where link_doctype="Lead" and link_name="{0}" and parenttype="Address" """.format(op.party_name)
            data=frappe.db.sql(sql,as_dict=True)

            if data:
                formattedAddress=frappe.get_doc("Address",data[0].parent)
                self.site_location = (
                formattedAddress.name + '\n' + 
                formattedAddress.address_line1 + '\n' + 
                formattedAddress.address_line2 + '\n' + 
                formattedAddress.city + '\n' + 
                formattedAddress.state + '\n' + 
                formattedAddress.pincode + '\n' + 
                formattedAddress.country
                )

		    
            
       

    def update_opportunity_status_section(self):
        if not self.opportunity_name:
            return

        opportunity_doc = frappe.get_doc("Opportunity", self.opportunity_name)
        opportunity_doc.custom_site_survey_number = self.name
        opportunity_doc.custom_site_survey_engineer = self.site_engineer
        opportunity_doc.custom_site_survey_engineer_name = self.site_engineer_name
        opportunity_doc.custom_site_survey_status = self.site_survey_status
        opportunity_doc.save()
