import frappe
from frappe import _
from frappe.model.document import Document

class TripSegment(Document):
	def validate(self):
		if self.start_datetime and self.end_datetime:
			if self.end_datetime < self.start_datetime:
				frappe.throw(_("End Datetime cannot be before Start Datetime."))
