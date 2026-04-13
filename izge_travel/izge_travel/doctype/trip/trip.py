import frappe
from frappe import _, utils
from frappe.model.document import Document

class Trip(Document):
	def validate(self):
		if self.departure_date and self.return_date:
			if utils.get_datetime(self.return_date) < utils.get_datetime(self.departure_date):
				frappe.throw(_("Return Date cannot be before Departure Date."))
		
		# Validation: Check if primary traveler belongs to the selected customer
		if self.primary_traveler and self.customer:
			traveler_customer = frappe.db.get_value("Traveler", self.primary_traveler, "customer")
			if traveler_customer != self.customer:
				frappe.msgprint(_("Warning: Primary Traveler belongs to a different customer ({0})").format(traveler_customer))
		
		# Validation: Warning for empty location on completed/cancelled trips
		if self.trip_status in ["Completed", "Cancelled"]:
			if not self.last_confirmed_location:
				frappe.msgprint(_("Warning: Last confirmed location is empty for a completed/cancelled trip."))
