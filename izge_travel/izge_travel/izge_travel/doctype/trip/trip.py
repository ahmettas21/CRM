import frappe
from frappe import _
from frappe.model.document import Document


class Trip(Document):
	def validate(self):
		self.calculate_totals()
		self.calculate_cc_commission()
		self.check_margin_guardrail()

	def check_margin_guardrail(self):
		"""SOP Guardrail: Zararına satış engellemesi (Sales < Cost)."""
		from frappe.utils import flt
		if flt(self.total_sale_amount) < flt(self.cost_amount) and self.status not in ["Cancelled", "Refunded", "Void"]:
			frappe.throw(
				_("SOP-GUARDRAIL: Toplam satış tutarı ({0}) maliyetten ({1}) düşük olamaz! Lütfen kârlılığı kontrol edin.")
				.format(self.total_sale_amount, self.cost_amount)
			)

	def calculate_totals(self):
		"""Sum up all financial fields from flight, hotel, and charge child tables."""
		from frappe.utils import flt
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
				self.cost_amount += flt(row.cost_amount)
				self.base_service_amount += flt(row.service_amount)
				self.extra_amount += flt(row.extra_amount)
				self.total_sale_amount += flt(row.sale_amount)
				self.total_tax_amount += flt(getattr(row, 'tax_amount', 0))

		# Profit
		self.profit = self.total_sale_amount - self.cost_amount

	def calculate_cc_commission(self):
		"""Calculate credit card commission amount if payment method is Credit Card."""
		from frappe.utils import flt
		if self.payment_method == "Credit Card" and flt(self.cc_commission_rate) > 0:
			self.cc_commission_amount = flt(
				self.total_sale_amount * flt(self.cc_commission_rate) / 100, 2
			)
		else:
			self.cc_commission_amount = 0

	def on_submit(self):
		# Muhasebe hareketi için Sales Invoice otomatik oluşmasın, 
		# Kullanıcı 'Make Invoice' butonuyla (API) kendisi tetikleyecek.
		# Ancak submit anında maliyetlerin Purchase Invoice olarak oluşması vizyonunu koruyalım.
		self.create_purchase_invoices()
		
		# CC Commission Journal Entry
		if self.payment_method == "Credit Card" and self.cc_commission_amount > 0:
			self.create_cc_commission_entry()

	def on_cancel(self):
		"""Cancel all associated Sales and Purchase Invoices."""
		self.cancel_sales_invoice()
		self.cancel_purchase_invoices()

	@frappe.whitelist()
	def make_sales_invoice(self):
		"""
		SOP Trigger: Create a draft Sales Invoice from Trip screen manually.
		Trip controller muhasebenin sahibi değil, kural motorudur.
		"""
		if self.docstatus != 1:
			frappe.throw(_("Fatura oluşturmak için önce Trip kaydını Submit etmelisiniz."))
			
		if self.customer_invoice_no:
			frappe.throw(_("Bu Trip için zaten bir fatura oluşturulmuş: {0}").format(self.customer_invoice_no))

		si_name = self.create_sales_invoice()
		if si_name:
			self.db_set("customer_invoice_no", si_name)
			return si_name
		return None

	def create_sales_invoice(self):
		si = frappe.new_doc("Sales Invoice")
		si.customer = self.customer
		si.remarks = f"Booking Ref: {self.booking_reference or 'N/A'} | Trip: {self.name}"
		si.set_posting_time = 1
		si.due_date = self.payment_due_date or frappe.utils.today()
		
		# Attach Payment Terms if set
		if hasattr(self, "payment_terms_template") and self.payment_terms_template:
			si.payment_terms_template = self.payment_terms_template

		# Seçilen senaryoya göre vergi şablonu ata
		if self.product_type == "Hotel":
			si.taxes_and_charges = "TAX-DOMESTIC-PACKAGE"
		elif self.product_type in ["Package", "Tour"] and self.trip_scope == "International":
			si.taxes_and_charges = "TAX-OUTGOING-PACKAGE"
		elif self.product_type == "Service":
			si.taxes_and_charges = "TAX-SERVICE-PACKAGE"

		# Add line items based on child tables and display preferences
		self._add_invoice_items(si)

		# Insert if items exist
		if len(si.get("items")) > 0:
			si.set_missing_values()
			si.insert(ignore_permissions=True)
			frappe.msgprint(_("Draft Sales Invoice {0} created for Customer.").format(si.name))
			self.add_comment("Info", f"Draft Sales Invoice created: {si.name}")
			return si.name
		return None

	def cancel_sales_invoice(self):
		"""Cancel associated Sales Invoices."""
		sis = frappe.get_all("Sales Invoice", filters={
			"remarks": ["like", f"%{self.name}%"],
			"docstatus": ["<", 2]
		})
		if not sis:
			# Fallback for old records or reference based lookup
			sis = frappe.get_all("Sales Invoice", filters={
				"remarks": ["like", f"%{self.booking_reference}%"],
				"docstatus": ["<", 2]
			})

		for si_data in sis:
			si = frappe.get_doc("Sales Invoice", si_data.name)
			if si.docstatus == 0:
				frappe.delete_doc("Sales Invoice", si.name, ignore_permissions=True)
			elif si.docstatus == 1:
				si.cancel()
		
		self.db_set("customer_invoice_no", "")

	def create_purchase_invoices(self):
		"""
		Identifies all unique suppliers in the Trip and creates a separate 
		Purchase Invoice for each supplier's cost.
		"""
		suppliers = {}  # {supplier_name: [list of segment rows]}
		
		# Collect all rows with cost and supplier
		all_rows = []
		for table in ["trip_flight_segments", "trip_hotel_stays", "trip_service_items", "trip_charges"]:
			all_rows.extend(self.get(table))

		for row in all_rows:
			if row.cost_amount and getattr(row, "supplier", None):
				if row.supplier not in suppliers:
					suppliers[row.supplier] = []
				suppliers[row.supplier].append(row)

		pi_names = []
		for supplier, rows in suppliers.items():
			pi_name = self._create_single_purchase_invoice(supplier, rows)
			if pi_name:
				pi_names.append(pi_name)
		
		if pi_names:
			self.db_set("supplier_invoice_no", ", ".join(pi_names))

	def _create_single_purchase_invoice(self, supplier, rows):
		"""Creates one Purchase Invoice for a specific supplier."""
		from frappe.utils import flt
		pi = frappe.new_doc("Purchase Invoice")
		pi.supplier = supplier
		pi.remarks = f"Trip Cost: {self.booking_reference or self.name}"
		pi.due_date = self.payment_due_date or frappe.utils.today()
		
		for row in rows:
			item_code = "BILET-MALIYETI"
			item_name = "Bilet/Hizmet Maliyeti"
			
			if hasattr(row, 'hotel_name'):
				item_code = "KONAKLAMA-MALIYETI"
				item_name = "Konaklama Maliyeti"
			elif hasattr(row, 'service_category'):
				cat = getattr(row, 'service_category', 'Genel')
				item_code = f"{cat.upper()}-MALIYETI" if cat else "GENEL-MALIYET"
				item_name = f"{cat or 'Genel'} Maliyeti"
			elif hasattr(row, 'charge_type'):
				item_code = "EK-MASRAF"
				item_name = "Ek Masraf"
			
			self._ensure_item(item_code, item_name, "Maliyetler", is_purchase=True)
			
			pi.append("items", {
				"item_code": item_code,
				"qty": 1,
				"rate": flt(row.cost_amount),
				"description": f"PNR: {self.booking_reference} - {getattr(row, 'traveler', getattr(row, 'related_traveler', 'N/A'))}"
			})
			
		if len(pi.get("items")) > 0:
			pi.set_missing_values()
			pi.insert(ignore_permissions=True)
			frappe.msgprint(_("Draft Purchase Invoice {0} created for {1}.").format(pi.name, supplier))
			return pi.name
		return None

	def cancel_purchase_invoices(self):
		"""Cancel associated Purchase Invoices."""
		pis = frappe.get_all("Purchase Invoice", filters={
			"remarks": ["like", f"%{self.booking_reference}%"],
			"docstatus": ["<", 2]
		})
		for pi_data in pis:
			pi = frappe.get_doc("Purchase Invoice", pi_data.name)
			if pi.docstatus == 0:
				frappe.delete_doc("Purchase Invoice", pi.name, ignore_permissions=True)
			elif pi.docstatus == 1:
				pi.cancel()
		
		self.db_set("supplier_invoice_no", "")

	def create_cc_commission_entry(self):
		"""Create a Journal Entry for credit card POS commission expense."""
		from frappe.utils import flt
		
		if not flt(self.cc_commission_amount):
			return
			
		company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
		if not company:
			return
		
		# Try to find or create CC Commission expense account
		expense_account = frappe.db.get_value("Account", {
			"account_name": "Kredi Kartı Komisyon Gideri",
			"company": company
		}, "name")
		
		if not expense_account:
			# We'll skip creating the JE if no dedicated account exists
			# User should set this up in Chart of Accounts
			frappe.msgprint(
				_("CC commission account 'Kredi Kartı Komisyon Gideri' not found. Please set up in Chart of Accounts."),
				indicator="orange", alert=True
			)
			return
		
		bank_account = frappe.db.get_value("Account", {
			"account_type": "Bank",
			"is_group": 0,
			"company": company
		}, "name")
		
		if not bank_account:
			return
			
		je = frappe.new_doc("Journal Entry")
		je.voucher_type = "Journal Entry"
		je.posting_date = frappe.utils.today()
		je.remark = f"CC Commission - {self.cc_bank or 'N/A'} - Trip: {self.booking_reference}"
		
		je.append("accounts", {
			"account": expense_account,
			"debit_in_account_currency": flt(self.cc_commission_amount)
		})
		je.append("accounts", {
			"account": bank_account,
			"credit_in_account_currency": flt(self.cc_commission_amount)
		})
		
		je.insert(ignore_permissions=True)
		frappe.msgprint(_("CC Commission Journal Entry {0} created.").format(je.name))

	def _add_invoice_items(self, si):
		"""Maps child tables to Sales Invoice items based on Product Type and Item Segmentation."""
		from frappe.utils import flt

		# 1. PACKAGE / TOUR (Kombine Mantık)
		if self.product_type in ["Package", "Tour"]:
			if self.cost_amount > 0:
				self._ensure_item("YURTDISI-MALIYET-YANSITMA", "Yurtdışı Maliyet Yansıtma", "Hizmetler")
				si.append("items", {
					"item_code": "YURTDISI-MALIYET-YANSITMA",
					"qty": 1,
					"rate": flt(self.cost_amount),
					"description": f"Tur Maliyet Yansıtması - {self.booking_reference}"
				})
			
			if self.profit > 0 or self.base_service_amount > 0:
				fee = flt(self.total_sale_amount) - flt(self.cost_amount)
				self._ensure_item("HIZMET-BEDELI", "Acente Hizmet Bedeli", "Servis")
				si.append("items", {
					"item_code": "HIZMET-BEDELI",
					"qty": 1,
					"rate": fee,
					"description": f"Acente Hizmet Bedeli - {self.booking_reference}"
				})
			return

		# 2. HOTEL (Item Segmentation)
		if self.product_type == "Hotel":
			for hotel in self.get("trip_hotel_stays", []):
				if hotel.cost_amount > 0:
					self._ensure_item("KONAKLAMA-MALIYETI", "Konaklama Maliyeti", "Hizmetler")
					si.append("items", {
						"item_code": "KONAKLAMA-MALIYETI",
						"qty": 1,
						"rate": flt(hotel.cost_amount),
						"description": f"Otel Maliyet: {hotel.hotel_name}"
					})
				if flt(hotel.sale_amount) > flt(hotel.cost_amount):
					fee = flt(hotel.sale_amount) - flt(hotel.cost_amount)
					self._ensure_item("HIZMET-BEDELI", "Hizmet Bedeli", "Servis")
					si.append("items", {
						"item_code": "HIZMET-BEDELI",
						"qty": 1,
						"rate": fee,
						"description": f"Konaklama Hizmet Kârı: {hotel.hotel_name}"
					})
			return

		# 3. SERVICE (Visa, vb.)
		if self.product_type == "Service":
			for srv in self.get("trip_service_items", []):
				# Vize Harcı gibi passthrough (Kâr sıfır) olanları ayrı satır bas
				if flt(srv.sale_amount) == flt(srv.cost_amount) and flt(srv.cost_amount) > 0:
					item_code = "VIZE-HARCI" if srv.service_category == "Visa" else "HIZMET-HARCI"
					self._ensure_item(item_code, f"{srv.service_category or 'Hizmet'} Harcı/Maliyeti", "Hizmetler")
					si.append("items", {
						"item_code": item_code,
						"qty": 1,
						"rate": flt(srv.sale_amount),
						"description": f"Pass-through Harç: {srv.service_name}"
					})
				# Kâr varsa ayrı hizmet satırı
				elif flt(srv.sale_amount) > flt(srv.cost_amount):
					item_code = "VIZE-DANISMANLIK" if srv.service_category == "Visa" else f"{srv.service_category.upper()}-HIZMETI"
					cost = flt(srv.cost_amount)
					fee = flt(srv.sale_amount) - cost
					
					if cost > 0:
						self._ensure_item(f"{item_code}-MALIYET", f"{srv.service_category} Maliyet", "Hizmetler")
						si.append("items", {
							"item_code": f"{item_code}-MALIYET",
							"qty": 1,
							"rate": cost,
							"description": f"{srv.service_name} (Maliyet)"
						})
					
					self._ensure_item(item_code, f"{srv.service_category} Bedeli", "Servis")
					si.append("items", {
						"item_code": item_code,
						"qty": 1,
						"rate": fee,
						"description": f"{srv.service_name} (Danışmanlık/Hizmet)"
					})
			return

		# Default Flight / Diğer davranışları (Eski yapıyı koru)
		display_hidden = (getattr(self, "service_fee_display", "Visible") == "Hidden")
		for seg in self.get("trip_flight_segments", []):
			if seg.sale_amount:
				self._ensure_item("UCAK-BILETI", "Uçak Bileti", "Hizmetler")
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

	def _ensure_item(self, item_code, item_name, item_group, is_purchase=False):
		"""Create item dynamically if it doesn't exist yet."""
		if not frappe.db.exists("Item", item_code):
			# Ensure Item Group exists
			if not frappe.db.exists("Item Group", item_group):
				root_ig = frappe.db.get_value("Item Group", {"is_group": 1, "parent_item_group": ["is", "not set"]}, "name") or "All Item Groups"
				ig = frappe.new_doc("Item Group")
				ig.item_group_name = item_group
				ig.parent_item_group = root_ig
				ig.insert(ignore_permissions=True)

			doc = frappe.new_doc("Item")
			doc.item_code = item_code
			doc.item_name = item_name
			doc.item_group = item_group
			doc.is_stock_item = 0
			doc.is_sales_item = 1
			doc.is_purchase_item = 1 if is_purchase else 0
			doc.insert(ignore_permissions=True)

			# No commit here so it rolls back if Trip submit fails
