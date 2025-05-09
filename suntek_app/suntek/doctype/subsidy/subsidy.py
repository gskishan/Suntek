from datetime import datetime

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Subsidy(Document):
    def autoname(self):
        current_year = datetime.now().year
        self.name = make_autoname(f"SES-SUBSIDY-{current_year}-.#####")

    def before_insert(self):
        self.get_channel_partner_data_on_create()

    def after_insert(self):
        self.update_project_on_save()

    def after_save(self):
        self.update_project_on_save()

    def on_submit(self):
        self.update_project_on_submit()

    def on_validate(self):
        self.update_status_on_project()

    def update_status_on_project(self):
        if self.project_name:
            project = frappe.get_doc("Project", self.project_name)
            project.db_set("custom_subsidy_status", self.subsidy_status, update_modified=False)

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

    def update_project_on_save(self):
        # Check if the Discom document is linked to a Project
        if self.project_name:
            project = frappe.get_doc("Project", self.project_name)
            project.custom_subsidy_id = self.name
            project.custom_subsidy_status = self.subsidy_status
            project.custom_tsredco_transaction_no = self.tsredco_transaction_no
            project.custom_tsredco_transaction_date = self.tsredco_transaction_date
            project.custom_proposal_submission_date = self.proposal_submission_date
            project.custom_tracking_number = self.tracking_number
            project.custom_mnre_sanction_no = self.mnre_sanction_no
            project.custom_pcr_submit_date = self.pcr_submit_date
            project.custom_subsidy_cheque_upload = self.subsidy_cheque_upload
            project.custom_subsidy_cheque_no = self.subsidy_cheque_no
            project.custom_transaction_amount = self.transaction_amount
            project.custom_transaction_bank_and_branch = self.transaction_bank_and_branch
            project.custom_in_principle_no = self.in_principle_no
            project.custom_in_principle_date = self.in_principle_date
            project.custom_tsredco_inspection = self.tsredco_inspection
            project.custom_tsredco_inspection_photos = self.tsredco_inspection_photos
            project.custom_subsidy_cheque_date = self.subsidy_cheque_date
            project.custom_pcr_submission_target_date = self.pcr_submission_target_date
            project.save()

    def update_project_on_submit(self):
        # Similar to update_project_on_save, check if the Discom document is linked to a Project
        if self.project_name:
            project = frappe.get_doc("Project", self.project_name)
            project.custom_subsidy_id = self.name
            project.custom_subsidy_status = self.subsidy_status
            project.custom_tsredco_transaction_no = self.tsredco_transaction_no
            project.custom_tsredco_transaction_date = self.tsredco_transaction_date
            project.custom_proposal_submission_date = self.proposal_submission_date
            project.custom_tracking_number = self.tracking_number
            project.custom_mnre_sanction_no = self.mnre_sanction_no
            project.custom_pcr_submit_date = self.pcr_submit_date
            project.custom_subsidy_cheque_upload = self.subsidy_cheque_upload
            project.custom_subsidy_cheque_no = self.subsidy_cheque_no
            project.custom_transaction_amount = self.transaction_amount
            project.custom_transaction_bank_and_branch = self.transaction_bank_and_branch
            project.custom_in_principle_no = self.in_principle_no
            project.custom_in_principle_date = self.in_principle_date
            project.custom_tsredco_inspection = self.tsredco_inspection
            project.custom_tsredco_inspection_photos = self.tsredco_inspection_photos
            project.custom_subsidy_cheque_date = self.subsidy_cheque_date
            project.custom_pcr_submission_target_date = self.pcr_submission_target_date
            project.save()
