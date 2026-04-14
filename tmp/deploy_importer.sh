#!/bin/sh
set -e

APP_PATH="/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel"
APP_PKG="/home/frappe/bench/apps/izge_travel/izge_travel"
SITE="erpnext-production-1b2e.up.railway.app"

echo "=== PHASE 1: INSTALL BS4 ==="
su frappe -c "/home/frappe/bench/env/bin/pip install beautifulsoup4" || true

echo "=== PHASE 2: COPY UTILS ==="
mkdir -p $APP_PATH/utils
mkdir -p $APP_PKG/utils
cat > $APP_PKG/utils/__init__.py << 'EOF'
# Utils
EOF

cat > $APP_PKG/utils/aqua_parser.py << 'EOF_PARSER'
import csv
import io
import bs4

def parse_aqua_file(file_content, filename):
    data = []
    if filename.endswith(".xls") or filename.endswith(".html"):
        soup = bs4.BeautifulSoup(file_content, "html.parser")
        table = soup.find("table")
        if not table:
            raise ValueError("No HTML table found in the provided .xls file.")
        rows = table.find_all("tr")
        if not rows:
            return []
        headers = [th.get_text(strip=True) for th in rows[0].find_all(["th", "td"])]
        for row in rows[1:]:
            cells = row.find_all("td")
            if not cells:
                continue
            row_data = [cell.get_text(strip=True) for cell in cells]
            if len(row_data) != len(headers):
                row_data = row_data[:len(headers)] + [""] * (len(headers) - len(row_data))
            row_dict = dict(zip(headers, row_data))
            pnr_val = row_dict.get("Pnr.No", "")
            if pnr_val.startswith("-") or pnr_val == "Genel Toplam":
                continue
            data.append(row_dict)
    elif filename.endswith(".csv"):
        try:
            content_str = file_content.decode("utf-8-sig")
        except UnicodeDecodeError:
            try:
                content_str = file_content.decode("latin-1")
            except Exception:
                content_str = file_content.decode("utf-8", errors="ignore")
        reader = csv.DictReader(io.StringIO(content_str), delimiter=";")
        if not reader.fieldnames or len(reader.fieldnames) < 5:
            reader = csv.DictReader(io.StringIO(content_str), delimiter=",")
        for row_dict in reader:
             row_dict = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row_dict.items() if k}
             pnr_val = str(row_dict.get("Pnr.No", ""))
             if pnr_val.startswith("-") or pnr_val == "Genel Toplam":
                 continue
             data.append(row_dict)
    else:
        raise ValueError("Unsupported file format. Please upload .xls (HTML) or .csv")
    return data
EOF_PARSER
echo "  Utils created"

echo "=== PHASE 3: CREATE AQUA IMPORTER DOCTYPE ==="
mkdir -p $APP_PATH/doctype/aqua_importer
mkdir -p $APP_PKG/doctype/aqua_importer

cat > $APP_PKG/doctype/aqua_importer/aqua_importer.json << 'EOF_JSON'
{"actions":[],"allow_rename":1,"creation":"2026-04-14 04:00:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["import_file","status","process_button","log_details"],"fields":[{"fieldname":"import_file","fieldtype":"Attach","in_list_view":1,"label":"Import File (CSV/XLS)","reqd":1},{"default":"Pending","fieldname":"status","fieldtype":"Select","in_list_view":1,"label":"Status","options":"Pending\nIn Progress\nSuccess\nFailed\nPartially Failed","read_only":1},{"fieldname":"process_button","fieldtype":"Button","label":"Process Import","depends_on":"eval:doc.status == 'Pending' || doc.status == 'Failed' || doc.status == 'Partially Failed'"},{"fieldname":"log_details","fieldtype":"Text Editor","label":"Log Details","read_only":1}],"index_web_pages_for_search":1,"links":[],"modified":"2026-04-14 04:00:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Aqua Importer","naming_rule":"Expression","autoname":"format:AQUA-{YYYY}-{MM}-####","owner":"Administrator","permissions":[{"create":1,"delete":1,"email":1,"export":1,"print":1,"read":1,"report":1,"role":"System Manager","share":1,"write":1}],"sort_field":"modified","sort_order":"DESC","states":[]}
EOF_JSON

cat > $APP_PKG/doctype/aqua_importer/aqua_importer.js << 'EOF_JS'
frappe.ui.form.on('Aqua Importer', {
	process_button: function(frm) {
		if (!frm.doc.import_file) {
			frappe.msgprint(__('Please attach a file before processing.'));
			return;
		}
		frappe.confirm(__('Are you sure you want to process this file? Existing trips with same PNRs will be overwritten.'),
			function() {
				frm.set_df_property("process_button", "disabled", true);
				frappe.call({
					method: 'izge_travel.izge_travel.doctype.aqua_importer.aqua_importer.trigger_import',
					args: { docname: frm.doc.name },
					freeze: true,
					freeze_message: __('Processing Import... This might take a while.'),
					callback: function(r) {
						frm.reload_doc();
						if(!r.exc) {
							frappe.show_alert({message: __('Import processing completed.'), indicator: 'green'});
						}
					}
				});
			}
		);
	}
});
EOF_JS

cat > $APP_PKG/doctype/aqua_importer/aqua_importer.py << 'EOF_PY'
import frappe
from frappe.model.document import Document

class AquaImporter(Document):
	def process_import(self):
		if not self.import_file:
			frappe.throw("Please attach a file first.")
		self.db_set("status", "In Progress")
		file_doc = frappe.get_doc("File", {"file_url": self.import_file})
		file_content = file_doc.get_content()
		filename = file_doc.file_name.lower()
		try:
			from izge_travel.izge_travel.utils.aqua_parser import parse_aqua_file
			data_rows = parse_aqua_file(file_content, filename)
			if not data_rows:
				self.db_set("status", "Failed")
				self.db_set("log_details", "No valid rows parsed from the file.")
				return
			pnrs = {}
			for row in data_rows:
				pnr = str(row.get("Pnr.No", "")).strip()
				if not pnr: continue
				if pnr not in pnrs: pnrs[pnr] = []
				pnrs[pnr].append(row)
			total_pnrs = len(pnrs)
			success = 0
			errors = []
			for pnr, rows in pnrs.items():
				try:
					self._process_pnr_group(pnr, rows)
					success += 1
				except Exception as e:
					frappe.db.rollback()
					errors.append(f"<b>PNR {pnr} Failed:</b> {str(e)}")
			log_text = f"Processed {total_pnrs} unique PNRs.<br>{success} created/updated successfully.<br>"
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
		if not rows: return
		first_row = rows[0]
		customer_name = str(first_row.get(u"M\u00fc\u015fteri", "")).strip()
        
		if customer_name and not frappe.db.exists("Customer", customer_name):
			cust = frappe.new_doc("Customer")
			cust.customer_name = customer_name
			cust.customer_group = "Commercial"
			cust.territory = "All Territories"
			cust.customer_type = "Company"
			cust.insert(ignore_permissions=True)
			
		trip_name = frappe.db.get_value("Trip", {"booking_reference": pnr}, "name")
		if trip_name:
			trip = frappe.get_doc("Trip", trip_name)
			trip.set("trip_flight_segments", [])
			trip.set("trip_hotel_stays", [])
			trip.set("trip_charges", [])
		else:
			trip = frappe.new_doc("Trip")
			trip.booking_reference = pnr
			
		trip.customer = customer_name
		trip.booking_date = self._parse_date(first_row.get("Kay\u0131t Tarihi"))
		trip.supplier_pnr = str(first_row.get("Op.Pnr.No", "")).strip()
		trip.customer_invoice_no = str(first_row.get("M\u00fc\u015fteri Fat.No", "")).strip()
		trip.supplier_invoice_no = str(first_row.get("Operat\u00f6r Fat. No", "")).strip()
		
		sales_owner_raw = str(first_row.get("Rez.Yapan", "")).strip()
		trip.sales_owner = ""
		if sales_owner_raw:
			user = frappe.db.get_value("User", {"full_name": sales_owner_raw}, "name")
			if user: trip.sales_owner = user
				
		ofis = str(first_row.get("OF\u0130S", "")).strip()
		trip.office = "SANCAKTEPE 2018" if "SANCAKTEPE" in ofis.upper() else "\u0130ZGE TUR\u0130ZM 2018"

		is_hotel = any(str(r.get("Mod\u00fcl", "")).upper() == "OTEL" for r in rows)
		is_flight = any(str(r.get("Mod\u00fcl", "")).upper() == "U\u00c7AK" for r in rows)
		
		if is_hotel and is_flight: trip.product_type = "Other"
		elif is_hotel: trip.product_type = "Hotel"
		else: trip.product_type = "Flight"
			
		trip_scope = str(first_row.get("Gelir T\u00fcr\u00fc", "")).upper()
		trip.trip_scope = "International" if "DI\u015e" in trip_scope or "DIS" in trip_scope else "Domestic"
			
		trip.status = "Confirmed"
		trip.currency = "TRY"
		
		primary_traveler_name = None
		valid_pax_count = 0
		for r in rows:
			modul = str(r.get("Mod\u00fcl", "")).upper()
			raw_yolcu = str(r.get("Yolcu", r.get("Misafir", ""))).strip()
			
			traveler_id = None
			if self._is_actual_traveler(raw_yolcu):
				traveler_id = self._resolve_traveler(raw_yolcu, customer_name)
				if traveler_id and not primary_traveler_name:
					primary_traveler_name = traveler_id
				if traveler_id: valid_pax_count += 1
			
			c_amount = self._parse_amount(r.get("Tedarik\u00e7iye \u00d6denen", r.get("Operat\u00f6re \u00d6denen", "0")))
			s_amount = self._parse_amount(r.get("Hizmet Bedeli", "0"))
			e_amount = self._parse_amount(r.get("Ekstra Bedel", "0"))
			total_sale = self._parse_amount(r.get("Sat\u0131\u015f", "0"))
			
			if modul == "U\u00c7AK":
				if not self._is_actual_traveler(raw_yolcu):
					trip.append("trip_charges", {"charge_type": "Other", "description": raw_yolcu, "cost_amount": c_amount, "service_amount": s_amount, "extra_amount": e_amount, "sale_amount": total_sale, "related_traveler": traveler_id})
				else:
					direction = "Outbound" if str(r.get("Y\u00f6n Durum", "")).upper() == "GIDIS" else "Return"
					trip.append("trip_flight_segments", {"traveler": traveler_id, "direction": direction, "flight_no": str(r.get("U\u00e7u\u015f No", "")).strip(), "origin": str(r.get("Nereden", "")).strip(), "destination": str(r.get("Nereye", "")).strip(), "airline": str(r.get("Havayolu", "")).strip(), "operator": str(r.get("Operat\u00f6r", "")).strip(), "supplier_locator": str(r.get("Ted.Pnr.No", "")).strip(), "ticket_no": str(r.get("Bilet No", "")).strip(), "departure_date": self._parse_date(r.get("U\u00e7u\u015f Tarihi")), "departure_time": self._parse_time(r.get("Kalk\u0131\u015f Saati")), "arrival_time": self._parse_time(r.get("\u0130ni\u015f Saati")), "cost_amount": c_amount, "service_amount": s_amount, "extra_amount": e_amount, "sale_amount": total_sale})
			elif modul == "OTEL":
				trip.append("trip_hotel_stays", {"traveler": traveler_id, "hotel_name": str(r.get("Otel Ad\u0131", "")).strip(), "supplier": str(r.get("Tedarik\u00e7i", "")).strip(), "supplier_locator": str(r.get("Ted.Pnr.No", "")).strip(), "voucher_no": str(r.get("Voucher No", "")).strip(), "check_in_date": self._parse_date(r.get("Giri\u015f Tarihi")), "check_in_time": self._parse_time(r.get("Giri\u015f Saati")), "check_out_date": self._parse_date(r.get("\u00c7\u0131k\u0131\u015f Tarihi")), "check_out_time": self._parse_time(r.get("\u00c7\u0131k\u0131\u015f Saati")), "cost_amount": c_amount, "service_amount": s_amount, "extra_amount": e_amount, "sale_amount": total_sale})
			else:
				trip.append("trip_charges", {"charge_type": "Other", "description": modul + " " + raw_yolcu, "cost_amount": c_amount, "service_amount": s_amount, "extra_amount": e_amount, "sale_amount": total_sale, "related_traveler": traveler_id})
				
		trip.pax_count = valid_pax_count if valid_pax_count > 0 else 1
		if primary_traveler_name: trip.primary_traveler = primary_traveler_name
		trip.calculate_totals()
		trip.save(ignore_permissions=True)
		
	def _is_actual_traveler(self, text):
		charge_kw = ['BEDEL', 'KOLTUK', 'UCRET', 'CIP', 'BNDL', 'BAGAJ', 'TRANSFER', 'EKS']
		return not any(kw in text.upper() for kw in charge_kw)
		
	def _resolve_traveler(self, full_text, customer):
		if not full_text: return None
		full_text = full_text.strip().replace("\xa0", " ")
		parts = full_text.split(" ", 1)
		prefix, name = "", full_text
		if len(parts) > 1 and parts[0].upper() in ["MR", "MRS", "CHD", "INF"]:
			prefix, name = parts[0].upper(), parts[1].strip()
		if not name: return None
		tvl_name = frappe.db.get_value("Traveler", {"full_name": name, "customer": customer}, "name")
		if tvl_name: return tvl_name
		tvl = frappe.new_doc("Traveler")
		tvl.full_name = name
		tvl.title_prefix = prefix
		tvl.customer = customer
		tvl.insert(ignore_permissions=True)
		return tvl.name
		
	def _parse_amount(self, val):
		if not val or val == "-": return 0.0
		try: return float(str(val).replace(".", "").replace(",", "."))
		except: return 0.0
			
	def _parse_date(self, val):
		if not val or val == "0-0" or str(val).lower() == "nan": return None
		try:
			d,m,y = str(val).split(".")
			return f"{y}-{m}-{d}"
		except: return None
			
	def _parse_time(self, val):
		if not val or str(val).lower() == "nan": return None
		return str(val).strip() + ":00"

@frappe.whitelist()
def trigger_import(docname):
	doc = frappe.get_doc("Aqua Importer", docname)
	doc.process_import()
	return "Success"
EOF_PY

touch $APP_PKG/doctype/aqua_importer/__init__.py
echo "  Aqua Importer created"

echo "=== PHASE 4: MIGRATE ==="
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel
cd /home/frappe/bench
su frappe -c "bench --site $SITE migrate" 2>&1 | tail -30
echo "  Migrate DONE"

echo "=== DEPLOY COMPLETE ==="
