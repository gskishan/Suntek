from frappe.model.document import Document


class ChannelPartner(Document):
    def before_save(self):
        self.set_channel_partner_name()

    def set_channel_partner_name(self):
        salutation = self.salutation if self.salutation else ""
        first_name = self.first_name if self.first_name else ""
        last_name = self.last_name if self.last_name else ""

        self.channel_partner_name = " ".join(filter(None, [salutation, first_name, last_name]))
