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
		self.total_tax_amount = 0

		# List of child tables to iterate
		child_tables = [
			"trip_flight_segments",
			"trip_hotel_stays",
			"trip_service_items",
			"trip_charges"
		]

		for table in child_tables:
			for row in self.get(table):
				self.cost_amount += row.cost_amount or 0
				self.base_service_amount += row.service_amount or 0
				self.extra_amount += row.extra_amount or 0
				self.total_sale_amount += row.sale_amount or 0
				self.total_tax_amount += row.tax_amount or 0

		# Profit
		self.profit = self.total_sale_amount - self.cost_amount

	def on_submit(self):
		if getattr(self, "customer", None):
			self.create_sales_invoice()
		
	def on_cancel(self):
		self.cancel_sales_invoice()

	def create_sales_invoice(self):
		"""Create a draft Sales Invoice pulling financial data from Trip."""
		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.remarks = f"Auto-generated from Trip: {self.name}"
		si.set_posting_time = 1
		si.due_date = frappe.utils.today()

		# Add line items based on child tables and display preferences
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
		"""
		Maps child tables to Sales Invoice items.
		If service_fee_display is 'Hidden', service_amount is bundled into the main product rate.
		"""
		display_hidden = (getattr(self, "service_fee_display", "Visible") == "Hidden")

		# 1. Flights
		for seg in self.get("trip_flight_segments", []):
			if seg.sale_amount:
				self._ensure_item("UCAK-BILETI", "Uçak Bileti", "Hizmetler")
				
				# Bundle rate if service fee is hidden
				# Formula: Sale Amount - Service Fee (already included in sale usually)
				# Actually in Aqua, 'Satış' includes everything. 
				# If Hidden, we use the row's total sale_amount as the rate.
				# If Visible, we use sale_amount - service_amount.
				
				rate = seg.sale_amount
				if not display_hidden:
					rate = seg.sale_amount - (seg.service_amount or 0)

				si.append("items", {
					"item_code": "UCAK-BILETI",
					"qty": 1,
					"rate": rate,
					"description": f"Uçak Bileti: {seg.traveler} - PNR: {seg.ticket_no or seg.supplier_locator or 'N/A'}"
				})
				
				if not display_hidden and seg.service_amount:
					self._ensure_item("HIZMET-BEDELI", "Hizmet Bedeli", "Servis")
					si.append("items", {
						"item_code": "HIZMET-BEDELI",
						"qty": 1,
						"rate": seg.service_amount,
						"description": f"Hizmet Bedeli (Bilet): {seg.traveler}"
					})

		# 2. Hotels
		for hotel in self.get("trip_hotel_stays", []):
			if hotel.sale_amount:
				self._ensure_item("OTEL-KONAKLAMA", "Otel Konaklama", "Hizmetler")
				
				rate = hotel.sale_amount
				if not display_hidden:
					rate = hotel.sale_amount - (hotel.service_amount or 0)

				si.append("items", {
					"item_code": "OTEL-KONAKLAMA",
					"qty": 1,
					"rate": rate,
					"description": f"Otel: {hotel.hotel_name} - Giriş: {hotel.check_in_date}"
				})

				if not display_hidden and hotel.service_amount:
					self._ensure_item("HIZMET-BEDELI", "Hizmet Bedeli", "Servis")
					si.append("items", {
						"item_code": "HIZMET-BEDELI",
						"qty": 1,
						"rate": hotel.service_amount,
						"description": f"Hizmet Bedeli (Konaklama): {hotel.hotel_name}"
					})

		# 3. Service Items (Visa, etc.)
		for srv in self.get("trip_service_items", []):
			if srv.sale_amount:
				item_code = f"{srv.service_category.upper()}-HIZMETI" if srv.service_category else "GENEL-HIZMET"
				self._ensure_item(item_code, f"{srv.service_category or 'Genel'} Hizmeti", "Hizmetler")
				
				rate = srv.sale_amount
				if not display_hidden:
					rate = srv.sale_amount - (srv.service_amount or 0)

				si.append("items", {
					"item_code": item_code,
					"qty": 1,
					"rate": rate,
					"description": f"{srv.service_category}: {srv.service_name}"
				})

				if not display_hidden and srv.service_amount:
					self._ensure_item("HIZMET-BEDELI", "Hizmet Bedeli", "Servis")
					si.append("items", {
						"item_code": "HIZMET-BEDELI",
						"qty": 1,
						"rate": srv.service_amount,
						"description": f"Hizmet Bedeli ({srv.service_category})"
					})

	def _ensure_item(self, item_code, item_name, item_group):
		"""Create item dynamically if it doesn't exist yet."""
		if not frappe.db.exists("Item", item_code):
			# Ensure Item Group exists
			if not frappe.db.exists("Item Group", item_group):
				ig = frappe.new_doc("Item Group")
				ig.item_group_name = item_group
				ig.parent_item_group = "All Item Groups"
				ig.insert(ignore_permissions=True)

			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_name = item_name
			doc.item_group = item_group
			doc.is_stock_item = 0
			doc.is_sales_item = 1
			doc.insert(ignore_permissions=True)

			# No commit here so it rolls back if Trip submit fails
