from frappe.model.document import Document


class Dealer(Document):
    def before_save(self):
        self.set_dealer_name()

    def set_dealer_name(self):
        salutation = self.salutation if self.salutation else ""
        first_name = self.first_name if self.first_name else ""
        last_name = self.last_name if self.last_name else ""

        self.dealer_name = " ".join(filter(None, [salutation, first_name, last_name]))
