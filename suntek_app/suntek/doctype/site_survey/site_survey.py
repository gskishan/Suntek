import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class SiteSurvey(Document):
    def autoname(self):
        self.name = make_autoname("SITE-SURVEY-.#####")

    def onload(self):
        if self.docstatus == 1:
            self.update_site_survery_status()

    def validate(self):
        self.update_site_survey_status_on_save()

    def before_insert(self):
        self.get_channel_partner_from_opportunity()

    def before_save(self):
        self.get_channel_partner_from_opportunity()

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

    def get_channel_partner_from_opportunity(self):
        opportunity = frappe.get_doc("Opportunity", self.opportunity_name)

        if opportunity.custom_channel_partner:
            self.channel_partner = opportunity.custom_channel_partner

    @frappe.whitelist()
    def set_site_engineer(self):
        user = frappe.db.get_value("User", {"name": frappe.session.user}, "name", as_dict=1)
        employee = frappe.db.get_value("Employee", {"user_id": user.name}, "name", as_dict=1)

        response = {
            "user": user,
        }
        if employee:
            response["employee"] = employee

        return response

    @frappe.whitelist()
    def get_opportunity_details(self):
        data = None

        if self.is_new() and self.custom_project:
            project_doc = frappe.get_doc("Project", self.custom_project)
            so = project_doc.sales_order
            opportunity = frappe.db.get_value("Sales Order", so, "custom_opportunity_name")
            op = frappe.get_doc("Opportunity", opportunity)
            self.opportunity_name = op.name
            self.customer_name = project_doc.customer
            self.customer_number = project_doc.custom_customer_mobile
            self.opportunity_owner = op.opportunity_owner
            self.sales_person = op.custom_sales_excecutive
            self.poc_name = project_doc.custom_poc_person_name
            self.poc_contact = project_doc.custom_poc_mobile_no

            sql = """
                SELECT
                    parent
                FROM
                    `tabDynamic Link`
                WHERE
                    link_doctype = 'Lead'
                    AND link_name = %s
                    AND parenttype = 'Address'
            """
            data = frappe.db.sql(sql, as_dict=True)

        if data:
            formattedAddress = frappe.get_doc("Address", data[0].parent)
            lines = []

            if formattedAddress.name:
                lines.append(formattedAddress.name)
            if formattedAddress.address_line1:
                lines.append(formattedAddress.address_line1)
            if formattedAddress.address_line2:
                lines.append(formattedAddress.address_line2)
            if formattedAddress.city:
                lines.append(formattedAddress.city)
            if formattedAddress.state:
                lines.append(formattedAddress.state)
            if formattedAddress.pincode:
                lines.append(formattedAddress.pincode)
            if formattedAddress.country:
                lines.append(formattedAddress.country)

            self.site_location = "\n".join(lines)

    def update_opportunity_status_section(self):
        if not self.opportunity_name:
            return

        opportunity_doc = frappe.get_doc("Opportunity", self.opportunity_name)
        opportunity_doc.custom_site_survey_number = self.name
        opportunity_doc.custom_site_survey_engineer = self.site_engineer
        opportunity_doc.custom_site_survey_engineer_name = self.site_engineer_name
        opportunity_doc.custom_site_survey_status = self.site_survey_status
        opportunity_doc.save()
