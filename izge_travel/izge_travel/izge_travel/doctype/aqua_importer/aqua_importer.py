import frappe
from frappe.model.document import Document
import csv
import io

class AquaImporter(Document):
	def process_import(self):
		if not self.import_file:
			frappe.throw("Please attach a file first.")
			
		self.db_set("status", "In Progress")
		
		# Get file content
		file_doc = frappe.get_doc("File", {"file_url": self.import_file})
		file_content = file_doc.get_content()
		filename = file_doc.file_name.lower()
		
		try:
			# Import utility dynamically
			from izge_travel.izge_travel.utils.aqua_parser import parse_aqua_file
			data_rows = parse_aqua_file(file_content, filename)
			
			if not data_rows:
				self.db_set("status", "Failed")
				self.db_set("log_details", "No valid rows parsed from the file.")
				return
			
			# Group by PNR
			pnrs = {}
			for row in data_rows:
				pnr = str(row.get("Pnr.No", "")).strip()
				if not pnr:
					continue
				if pnr not in pnrs:
					pnrs[pnr] = []
				pnrs[pnr].append(row)
				
			total_pnrs = len(pnrs)
			success = 0
			errors = []
			
			# Process each PNR group
			for pnr, rows in pnrs.items():
				try:
					self._process_pnr_group(pnr, rows)
					success += 1
				except Exception as e:
					frappe.db.rollback()
					errors.append(f"<b>PNR {pnr} Failed:</b> {str(e)}")
					
			log_text = f"Processed {total_pnrs} unique PNRs.<br>"
			log_text += f"{success} created/updated successfully.<br>"
			if errors:
				log_text += f"{len(errors)} failed:<br>" + "<hr>".join(errors)
				self.db_set("status", "Partially Failed")
			else:
				self.db_set("status", "Success")
				
			self.db_set("log_details", log_text)
			
		except Exception as e:
			frappe.db.rollback()
			self.db_set("status", "Failed")
			self.db_set("log_details", f"Critical Error parsing file: {str(e)}")


	def _process_pnr_group(self, pnr, rows):
		"""
		Takes all rows for a given PNR and creates/updates a Trip document.
		If Trip exists, it will delete existing segments to refresh.
		"""
		if not rows:
			return
			
		first_row = rows[0]
		customer_name = str(first_row.get("Müşteri", "")).strip()
		
		# 1. Resolve Customer
		if customer_name and not frappe.db.exists("Customer", customer_name):
			cust_group = frappe.db.get_value("Customer Group", {}, "name") or "Commercial"
			territory = frappe.db.get_value("Territory", {}, "name") or "All Territories"
			
			cust = frappe.new_doc("Customer")
			cust.customer_name = customer_name
			cust.customer_group = cust_group
			cust.territory = territory
			cust.customer_type = "Company"
			cust.insert(ignore_permissions=True)
				
		# Check if Trip exists
		trip_name = frappe.db.get_value("Trip", {"booking_reference": pnr}, "name")
		if trip_name:
			trip = frappe.get_doc("Trip", trip_name)
			# UPSERT: Clear old children
			trip.set("trip_flight_segments", [])
			trip.set("trip_hotel_stays", [])
			trip.set("trip_charges", [])
		else:
			trip = frappe.new_doc("Trip")
			trip.booking_reference = pnr
			
		# Map Header info
		trip.customer = customer_name
		trip.booking_date = self._parse_date(first_row.get("Kayıt Tarihi"))
		trip.supplier_pnr = str(first_row.get("Op.Pnr.No", "")).strip()
		trip.customer_invoice_no = str(first_row.get("Müşteri Fat.No", "")).strip()
		trip.supplier_invoice_no = str(first_row.get("Operatör Fat. No", "")).strip()
		
		# Try to resolve Sales Owner
		sales_owner_raw = str(first_row.get("Rez.Yapan", "")).strip()
		trip.sales_owner = "" # default
		if sales_owner_raw:
			# simple matching on full name
			user = frappe.db.get_value("User", {"full_name": sales_owner_raw}, "name")
			if user:
				trip.sales_owner = user
				
		ofis = str(first_row.get("OFİS", "")).strip()
		if "SANCAKTEPE" in ofis.upper():
			trip.office = "SANCAKTEPE 2018"
		else:
			trip.office = "İZGE TURİZM 2018"

		# Determine product type & scope mostly by counting rows or looking at first row
		is_hotel = any(str(r.get("Modül", "")).upper() == "OTEL" for r in rows)
		is_flight = any(str(r.get("Modül", "")).upper() == "UÇAK" for r in rows)
		
		if is_hotel and is_flight:
			trip.product_type = "Other" # Mixed
		elif is_hotel:
			trip.product_type = "Hotel"
		else:
			trip.product_type = "Flight"
			
		trip_scope = str(first_row.get("Gelir Türü", "")).upper()
		if "DIŞ" in trip_scope or "DIS" in trip_scope:
			trip.trip_scope = "International"
		else:
			trip.trip_scope = "Domestic"
			
		trip.status = "Confirmed"
		trip.currency = "TRY"
		
		primary_traveler_name = None
		# 2. Process rows
		valid_pax_count = 0
		for r in rows:
			modul = str(r.get("Modül", "")).upper()
			raw_yolcu = str(r.get("Yolcu", r.get("Misafir", ""))).strip()
			
			traveler_id = None
			if self._is_actual_traveler(raw_yolcu):
				traveler_id = self._resolve_traveler(raw_yolcu, customer_name)
				if traveler_id and not primary_traveler_name:
					primary_traveler_name = traveler_id
					
				if traveler_id:
					valid_pax_count += 1
			
			c_amount = self._parse_amount(r.get("Tedarikçiye Ödenen", r.get("Operatöre Ödenen", "0")))
			s_amount = self._parse_amount(r.get("Hizmet Bedeli", "0"))
			e_amount = self._parse_amount(r.get("Ekstra Bedel", "0"))
			total_sale = self._parse_amount(r.get("Satış", "0"))
			
			is_charge = not self._is_actual_traveler(raw_yolcu)
			
			if is_charge:
				# Ortak Charge mantığı (Eğer yolcu ismi bagaj/CIP/ceza ise)
				trip.append("trip_charges", {
					"charge_type": "Other",
					"description": raw_yolcu if raw_yolcu else modul,
					"cost_amount": c_amount,
					"service_amount": s_amount,
					"extra_amount": e_amount,
					"sale_amount": total_sale,
					"related_traveler": traveler_id
				})
			elif modul == "UÇAK":
				direction = "Outbound" if str(r.get("Yön Durum", "")).upper() == "GIDIS" else "Return"
				supplier_name_raw = str(r.get("Operatör", r.get("Tedarikçi", ""))).strip()
				supplier_id = self._ensure_supplier(supplier_name_raw)

				trip.append("trip_flight_segments", {
					"traveler": traveler_id,
					"direction": direction,
					"flight_no": str(r.get("Uçuş No", "")).strip(),
					"origin": str(r.get("Nereden", "")).strip(),
					"destination": str(r.get("Nereye", "")).strip(),
					"airline": str(r.get("Havayolu", "")).strip(),
					"operator": str(r.get("Operatör", "")).strip(),
					"supplier": supplier_id,
					"supplier_locator": str(r.get("Ted.Pnr.No", "")).strip(),
					"ticket_no": str(r.get("Bilet No", "")).strip(),
					"departure_date": self._parse_date(r.get("Uçuş Tarihi")),
					"departure_time": self._parse_time(r.get("Kalkış Saati")),
					"arrival_time": self._parse_time(r.get("İniş Saati")),
					"cost_amount": c_amount,
					"service_amount": s_amount,
					"extra_amount": e_amount,
					"sale_amount": total_sale
				})
			elif modul == "OTEL":
				supplier_name_raw = str(r.get("Tedarikçi", r.get("Operatör", ""))).strip()
				supplier_id = self._ensure_supplier(supplier_name_raw)

				trip.append("trip_hotel_stays", {
					"traveler": traveler_id,
					"hotel_name": str(r.get("Otel Adı", "")).strip(),
					"supplier": supplier_id,
					"supplier_locator": str(r.get("Ted.Pnr.No", "")).strip(),
					"voucher_no": str(r.get("Voucher No", "")).strip(),
					"check_in_date": self._parse_date(r.get("Giriş Tarihi")),
					"check_in_time": self._parse_time(r.get("Giriş Saati")),
					"check_out_date": self._parse_date(r.get("Çıkış Tarihi")),
					"check_out_time": self._parse_time(r.get("Çıkış Saati")),
					"cost_amount": c_amount,
					"service_amount": s_amount,
					"extra_amount": e_amount,
					"sale_amount": total_sale
				})
			else:
				# Vize, Transfer, Tur, Araç, Sigorta vs.
				trip_scope_upper = str(r.get("Gelir Türü", "")).upper()
				mapping = {
					"VIZE": "Visa", "VİZE": "Visa",
					"TRANSFER": "Transfer",
					"TUR": "Tour",
					"KİRALAMA": "Car Rental", "ARAÇ": "Car Rental", "ARAC": "Car Rental",
					"SİGORTA": "Insurance", "SIGORTA": "Insurance",
					"TREN": "Train",
					"OTOBÜS": "Bus", "OTOBUS": "Bus",
					"GEMİ": "Cruise", "CRUISE": "Cruise",
					"JET": "Private Jet"
				}
				
				category = "Other"
				for tr_kw, en_val in mapping.items():
					if tr_kw in trip_scope_upper or tr_kw in modul:
						category = en_val
						break
				
				svc_name = str(r.get("Nereden", "")).strip() if category == "Visa" else str(r.get("Havayolu", "")).strip()
				if not svc_name: svc_name = modul
				
				origin = str(r.get("Nereden", "")).strip() if category != "Visa" else ""
				destination = str(r.get("Nereye", "")).strip()
				
				supplier_name_raw = str(r.get("Operatör", r.get("Tedarikçi", ""))).strip()
				supplier_id = self._ensure_supplier(supplier_name_raw)

				trip.append("trip_service_items", {
					"traveler": traveler_id,
					"service_category": category,
					"service_name": svc_name,
					"supplier": supplier_id,
					"supplier_locator": str(r.get("Ted.Pnr.No", "")).strip(),
					"start_date": self._parse_date(r.get("Uçuş Tarihi", r.get("Giriş Tarihi", ""))),
					"start_time": self._parse_time(r.get("Kalkış Saati", r.get("Giriş Saati", ""))),
					"end_date": self._parse_date(r.get("Çıkış Tarihi", "")),
					"end_time": self._parse_time(r.get("İniş Saati", r.get("Çıkış Saati", ""))),
					"origin": origin,
					"destination": destination,
					"cost_amount": c_amount,
					"service_amount": s_amount,
					"extra_amount": e_amount,
					"sale_amount": total_sale
				})
				
		trip.pax_count = valid_pax_count if valid_pax_count > 0 else 1
		if primary_traveler_name:
			trip.primary_traveler = primary_traveler_name
			
		trip.calculate_totals()
		trip.save(ignore_permissions=True)
		
	def _is_actual_traveler(self, text):
		text = text.upper()
		charge_kw = ['BEDEL', 'KOLTUK', 'UCRET', 'CIP', 'BNDL', 'BAGAJ', 'TRANSFER', 'EKS']
		return not any(kw in text for kw in charge_kw)
		
	def _ensure_supplier(self, supplier_name):
		"""
		Checks if supplier exists by name. 
		If exists, returns its ID (name). 
		If not, creates it and returns the new ID.
		"""
		if not supplier_name: return None
		
		# Check if supplier exists by supplier_name
		existing_id = frappe.db.get_value("Supplier", {"supplier_name": supplier_name}, "name")
		if existing_id:
			return existing_id
			
		# Else create new
		sup_group = frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"
		sup = frappe.new_doc("Supplier")
		sup.supplier_name = supplier_name
		sup.supplier_group = sup_group
		sup.supplier_type = "Company"
		sup.insert(ignore_permissions=True)
		
		return sup.name
			
	def _resolve_traveler(self, full_text, customer):
		"""Splits MR/MRS prefix and creates traveler if missing"""
		if not full_text: return None
		full_text = full_text.strip().replace("\xa0", " ")
		parts = full_text.split(" ", 1)
		
		prefix = ""
		name = full_text
		if len(parts) > 1 and parts[0].upper() in ["MR", "MRS", "CHD", "INF"]:
			prefix = parts[0].upper()
			name = parts[1].strip()
			
		if not name: return None
		
		# Does traveler exist? (Wait, exact match on name might be tricky if formatting changes)
		# Will do exact match
		tvl_name = frappe.db.get_value("Traveler", {"full_name": name, "customer": customer}, "name")
		if tvl_name:
			return tvl_name
			
		# Create
		tvl = frappe.new_doc("Traveler")
		tvl.full_name = name
		tvl.title_prefix = prefix
		tvl.customer = customer
		tvl.insert(ignore_permissions=True)
		return tvl.name
		
	def _parse_amount(self, val):
		if not val or val == "-": return 0.0
		# "5.351,00" -> 5351.00
		s = str(val).replace(".", "").replace(",", ".")
		try:
			return float(s)
		except:
			return 0.0
			
	def _parse_date(self, val):
		if not val or val == "0-0" or str(val).lower() == "nan": return None
		try:
			val = str(val).strip().split(" ")[0] # Saati ayır
			d,m,y = val.split(".")
			return f"{y}-{m}-{d}"
		except:
			return None
			
	def _parse_time(self, val):
		if not val or str(val).lower() == "nan": return None
		# "00:00" -> "00:00:00"
		return str(val) + ":00"

@frappe.whitelist()
def trigger_import(docname):
	doc = frappe.get_doc("Aqua Importer", docname)
	doc.process_import()
	return "Success"
