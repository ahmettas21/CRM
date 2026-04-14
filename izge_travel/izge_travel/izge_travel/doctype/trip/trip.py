import frappe
from frappe import _
from frappe.model.document import Document


class Trip(Document):
	def validate(self):
		self.calculate_totals()

	def calculate_totals(self):
		"""Sum up all financial fields from flight, hotel, and charge child tables."""
		self.cost_amount = 0
		self.base_service_amount = 0
		self.extra_amount = 0
		self.total_sale_amount = 0

		# List of child table reference explicitly
		children = []
		if self.get("trip_flight_segments"):
			children.extend(self.get("trip_flight_segments"))
		if self.get("trip_hotel_stays"):
			children.extend(self.get("trip_hotel_stays"))
		if self.get("trip_service_items"):
			children.extend(self.get("trip_service_items"))
		if self.get("trip_charges"):
			children.extend(self.get("trip_charges"))

		for row in children:
			self.cost_amount += row.cost_amount or 0
			self.base_service_amount += row.service_amount or 0
			self.extra_amount += row.extra_amount or 0
			self.total_sale_amount += row.sale_amount or 0

		# Profit
		self.profit = self.total_sale_amount - self.cost_amount

	def on_submit(self):
		if getattr(self, "customer", None):
			self.create_sales_invoice()
		
	def on_cancel(self):
		self.cancel_sales_invoice()

	def create_sales_invoice(self):
		"""Creat a draft Sales Invoice pulling financial data from Trip."""
		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.remarks = f"Auto-generated from Trip: {self.name}"
		si.set_posting_time = 1

		# Add line items based on child tables
		self._add_invoice_items(si)

		# Insert if items exist
		if len(si.get("items")) > 0:
			si.set_missing_values()
			si.insert(ignore_permissions=True)
			frappe.msgprint(_("Draft Sales Invoice {0} created.").format(si.name))
			self.add_comment("Info", f"Draft Sales Invoice created: {si.name}")
		else:
			frappe.msgprint(_("No sales amounts found. Sales Invoice was not created."))

	def cancel_sales_invoice(self):
		"""Cancel or Delete associated Sales Invoices upon Trip cancellation."""
		sis = frappe.get_all("Sales Invoice", filters={"remarks": ["like", f"%{self.name}%"], "docstatus": ["<", 2]})
		for si_data in sis:
			si = frappe.get_doc("Sales Invoice", si_data.name)
			if si.docstatus == 0:
				frappe.delete_doc("Sales Invoice", si.name, ignore_permissions=True)
			elif si.docstatus == 1:
				si.cancel()
				frappe.msgprint(_("Sales Invoice {0} cancelled.").format(si.name))

	def _add_invoice_items(self, si):
		# 1. Flights
		for seg in self.get("trip_flight_segments", []):
			if seg.sale_amount:
				si.append("items", {
					"item_code": "YURTICI-UCAK",
					"qty": 1,
					"rate": seg.sale_amount,
					"description": f"Flight: PNR {seg.pnr or 'N/A'} - Route: {seg.departure_airport or ''} to {seg.arrival_airport or ''}"
				})
		
		# 2. Hotels
		for hotel in self.get("trip_hotel_stays", []):
			if hotel.sale_amount:
				self._ensure_item("OTEL-KONAKLAMA", "Otel Konaklama", "Otel")
				si.append("items", {
					"item_code": "OTEL-KONAKLAMA",
					"qty": 1,
					"rate": hotel.sale_amount,
					"description": f"Hotel: {hotel.hotel_name or 'N/A'}"
				})
		
		# 3. Service Items
		for srv in self.get("trip_service_items", []):
			if srv.sale_amount:
				self._ensure_item("ACENTE-KOMISYONU-GELIR", "Acente Komisyonu (Gelir)", "Hizmet Bedeli")
				si.append("items", {
					"item_code": "ACENTE-KOMISYONU-GELIR",
					"qty": 1,
					"rate": srv.sale_amount,
					"description": f"Service: {srv.service or 'General'}"
				})

		# 4. Charges
		for charge in self.get("trip_charges", []):
			if charge.sale_amount:
				self._ensure_item("HAVALIMANI-VERGISI", "Havalimanı Vergisi", "Vergi ve Harçlar")
				si.append("items", {
					"item_code": "HAVALIMANI-VERGISI",
					"qty": 1,
					"rate": charge.sale_amount,
					"description": f"Charge: {charge.charge_type or 'Extra'}"
				})

	def _ensure_item(self, item_code, item_name, item_group):
		"""Create item dynamically if it doesn't exist yet before attaching to invoice."""
		if not frappe.db.exists("Item", item_code):
			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_name = item_name
			doc.item_group = item_group
			doc.is_stock_item = 0
			doc.is_sales_item = 1
			doc.insert(ignore_permissions=True)
			# No commit here so it rolls back if Trip submit fails
