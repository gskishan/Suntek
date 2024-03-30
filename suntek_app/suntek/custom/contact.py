
from frappe.contacts.doctype.contact.contact import Contact
from frappe.contacts.doctype.contact.contact import *
from frappe.utils import cstr
import frappe
from frappe import _
from frappe.model.naming import append_number_if_name_exists
class CustomContact(Contact):
	def autoname(self):
		# concat first and last name
		self.name = " ".join(filter(None, [cstr(self.get(f)).strip() for f in ["first_name", "last_name"]]))

		if frappe.db.exists("Contact", self.name):
			self.name = append_number_if_name_exists("Contact", self.name)
