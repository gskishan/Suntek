# Copyright (c) 2023, kishan and contributors
# For license information, please see license.txt
import frappe
from frappe.model.document import Document

class SiteSurvey(Document):
    def onload(self):
        if self.docstatus == 1:
            self.update_site_survery_status()

    def before_save(self):
        self.update_site_survey_status_on_save()

    def on_submit(self):
        self.update_site_survery_status()
        self.update_opportunity_status_section()

    def update_site_survey_status_on_save(self):
        self.site_survey_status = "Site Survey Assigned"
        


    def update_site_survery_status(self):
        self.site_survey_status = "Site Survey Completed"
       

    def update_opportunity_status_section(self):
        if not self.opportunity_name:
            return

        opportunity_doc = frappe.get_doc("Opportunity", self.opportunity_name)

        opportunity_doc.custom_site_survey_number = self.name
        opportunity_doc.custom_site_survey_engineer = self.site_engineer
        opportunity_doc.custom_site_survey_engineer_name = self.site_engineer_name
        opportunity_doc.custom_site_survey_status = self.site_survey_status
        opportunity_doc.save()

		
	
	


