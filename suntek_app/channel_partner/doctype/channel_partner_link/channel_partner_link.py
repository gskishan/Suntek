import frappe
from frappe.model.document import Document


class ChannelPartnerLink(Document):
    def validate(self):
        if self.is_primary:
            if hasattr(self, "parenttype") and self.parenttype == "Channel Partner Firm":
                parent = frappe.get_doc(self.parenttype, self.parent)

                for link in parent.channel_partners or []:
                    if link.name != self.name and link.is_primary:
                        link.is_primary = 0
