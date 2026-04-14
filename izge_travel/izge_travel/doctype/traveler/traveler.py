import frappe
from frappe import _, utils
from frappe.model.document import Document


class Traveler(Document):
	def validate(self):
		if not self.full_name:
			frappe.throw(_("Full Name cannot be empty."))

		if self.passport_expiry_date:
			if utils.get_datetime(self.passport_expiry_date) < utils.get_datetime(utils.today()):
				frappe.msgprint(
					_("Warning: Passport has expired on {0}").format(self.passport_expiry_date),
					indicator="orange",
					alert=True
				)

		if self.date_of_birth:
			if utils.get_datetime(self.date_of_birth) > utils.get_datetime(utils.today()):
				frappe.throw(_("Date of Birth cannot be in the future."))
