from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Discom(Document):
    def autoname(self):
        current_year = datetime.now().year
        self.name = make_autoname(f"SES-DISCOM-{current_year}-.#####")

    def before_insert(self):
        self.get_channel_partner_data_on_create()

    def after_insert(self):
        self.update_project_on_save()

    def after_save(self):
        self.update_project_on_save()

    def on_validate(self):
        self.update_project_status()

    def update_project_status(self):
        if self.project_name:
            project = frappe.get_doc(
                "Project", self.project_name, update_modified=False
            )
            project.db_set(
                "custom_discom_status", self.discom_status, update_modified=False
            )

    def get_channel_partner_data_on_create(self):
        try:
            if self.project_name:
                project = frappe.get_doc("Project", self.project_name)

            if project and project.custom_channel_partner:
                self.channel_partner = project.custom_channel_partner
                self.channel_partner_name = project.custom_channel_partner_name
                self.channel_partner_mobile = project.custom_channel_partner_mobile

        except Exception as e:
            frappe.log_error(str(e), "Error fetching channel partner data in Discom")
            frappe.throw(str(e))

    def on_submit(self):
        self.update_project_on_submit()

    def update_project_on_save(self):
        if self.project_name:
            project = frappe.get_doc("Project", self.project_name)
            project.custom_discom_id = self.name
            project.custom_discom_status = self.discom_status
            project.custom_net_meter_reg_no = self.net_meter_reg_no
            project.custom_application_date = self.application_date
            project.custom_ade_office = self.ade_office
            project.custom_feasibility_report = self.feasibility_report
            project.custom_meter_requisition_letter = self.meter_requisition_letter
            project.custom_pending_for_ade_inspection = self.pending_for_ade_inspection
            project.custom_meter_fitting_date = self.meter_fitting_date
            project.custom_synchronization_report = self.synchronization_report
            project.custom_net_meter_reg_doc = self.net_meter_reg_doc
            project.custom_feasibility_release_date = self.feasibility_release_date
            project.custom_adede_contact_no = self.adede_contact_no
            project.custom_work_completion_report_submission_date = (
                self.work_completion_report_submission_date
            )
            project.custom_meter_drawn_date = self.meter_drawn_date
            project.custom_material_gatepass_of_meter = self.material_gatepass_of_meter
            project.custom_net_meter_bill_revise_status = (
                self.net_meter_bill_revise_status
            )
            project.custom_revised_bill_copy = self.revised_bill_copy
            project.save()

    def update_project_on_submit(self):
        if self.project_name:
            project = frappe.get_doc("Project", self.project_name)
            project.custom_discom_id = self.name
            project.custom_discom_status = self.discom_status
            project.custom_net_meter_reg_no = self.net_meter_reg_no
            project.custom_application_date = self.application_date
            project.custom_ade_office = self.ade_office
            project.custom_feasibility_report = self.feasibility_report
            project.custom_meter_requisition_letter = self.meter_requisition_letter
            project.custom_pending_for_ade_inspection = self.pending_for_ade_inspection
            project.custom_meter_fitting_date = self.meter_fitting_date
            project.custom_synchronization_report = self.synchronization_report
            project.custom_net_meter_reg_doc = self.net_meter_reg_doc
            project.custom_feasibility_release_date = self.feasibility_release_date
            project.custom_adede_contact_no = self.adede_contact_no
            project.custom_work_completion_report_submission_date = (
                self.work_completion_report_submission_date
            )
            project.custom_meter_drawn_date = self.meter_drawn_date
            project.custom_material_gatepass_of_meter = self.material_gatepass_of_meter
            project.custom_net_meter_bill_revise_status = (
                self.net_meter_bill_revise_status
            )
            project.custom_revised_bill_copy = self.revised_bill_copy
            project.save()
