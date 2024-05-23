import frappe
from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_link_to_form
import re

def change_enquiry_status(doc, method):
    duplicate_check(doc) 
    if doc.custom_enquiry_status:
        doc.status = doc.custom_enquiry_status
    if not validate_mobile_number(doc.mobile_no):
        frappe.throw("Invalid mobile number! Please enter a 10-digit number starting with 6, 7, 8, or 9, optionally prefixed by +91 or +91-.")

def set_enquiry_name(doc, method):
    if doc.name:
        doc.custom_enquiry_name = doc.name

def validate_mobile_number(number):
    # Ensure number is a string before matching
    number = str(number)
    pattern = r'^(\+91[-]?)?[6-9]\d{9}$'
    if re.match(pattern, number):
        return True
    else:
        return False

@frappe.whitelist()
def custom_make_opportunity(source_name, target_doc=None):
    def set_missing_values(source, target):
        _set_missing_values(source, target)
        target.custom_enquiry_status = "Open"
        target.custom_company_name = source.company_name

    target_doc = get_mapped_doc(
        "Lead",
        source_name,
        {
            "Lead": {
                "doctype": "Opportunity",
                "field_map": {
                    "campaign_name": "campaign",
                    "doctype": "opportunity_from",
                    "name": "party_name",
                    "lead_name": "contact_display",
                    "company_name": "customer_name",
                    "email_id": "contact_email",
                    "mobile_no": "contact_mobile",
                    "lead_owner": "opportunity_owner",
                    "custom_enquiry_owner_name": "custom_opportunity_owner_name",
                    "notes": "notes",
                },
            }
        },
        target_doc,
        set_missing_values,
    )

    return target_doc

def _set_missing_values(source, target):
    address = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Address",
        },
        ["parent"],
        limit=1,
    )

    contact = frappe.get_all(
        "Dynamic Link",
        {
            "link_doctype": source.doctype,
            "link_name": source.name,
            "parenttype": "Contact",
        },
        ["parent"],
        limit=1,
    )

    if address:
        target.customer_address = address[0].parent

    if contact:
        target.contact_person = contact[0].parent

def duplicate_check(doc):
    mobile_no = str(doc.mobile_no)  # Ensure mobile_no is a string
    sql = """select * from `tabLead` where mobile_no="{0}" and name!="{1}" """.format(mobile_no, doc.name)
    data = frappe.db.sql(sql, as_dict=True)
    if data:
        frappe.errprint(data)
        frappe.throw("Duplicate mobile no {} already linked to <b>{}</b> ".format(mobile_no, data[0].custom_enquiry_owner_name))
