#!/bin/sh
set -e

APP_PATH="/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel"
APP_PKG="/home/frappe/bench/apps/izge_travel/izge_travel"
SITE="erpnext-production-1b2e.up.railway.app"

echo "=== PHASE 1: WRITE TRAVELER DOCTYPE ==="
mkdir -p $APP_PATH/doctype/traveler
cat > $APP_PATH/doctype/traveler/traveler.json << 'TRAVJSON'
{"actions":[],"allow_rename":1,"autoname":"naming_series:","creation":"2026-04-14 00:20:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["naming_series","title_prefix","full_name","customer","section_contact","email","mobile_phone","section_identity","nationality","passport_number","passport_expiry_date","date_of_birth","section_emergency","emergency_contacts","section_notes","notes"],"fields":[{"fieldname":"naming_series","fieldtype":"Select","label":"Naming Series","options":"TRAV-.YYYY.-.#####","reqd":1},{"fieldname":"title_prefix","fieldtype":"Select","label":"Title","options":"\nMR\nMRS\nCHD\nINF"},{"fieldname":"full_name","fieldtype":"Data","in_list_view":1,"in_standard_filter":1,"label":"Full Name","reqd":1},{"fieldname":"customer","fieldtype":"Link","in_list_view":1,"in_standard_filter":1,"label":"Customer","options":"Customer","reqd":1},{"fieldname":"section_contact","fieldtype":"Section Break","label":"Contact Information"},{"fieldname":"email","fieldtype":"Data","label":"Email","options":"Email"},{"fieldname":"mobile_phone","fieldtype":"Phone","in_list_view":1,"label":"Mobile Phone"},{"fieldname":"section_identity","fieldtype":"Section Break","label":"Identity & Travel Documents"},{"fieldname":"nationality","fieldtype":"Link","in_list_view":1,"label":"Nationality","options":"Country"},{"fieldname":"passport_number","fieldtype":"Data","label":"Passport Number"},{"fieldname":"passport_expiry_date","fieldtype":"Date","label":"Passport Expiry Date"},{"fieldname":"date_of_birth","fieldtype":"Date","label":"Date of Birth"},{"fieldname":"section_emergency","fieldtype":"Section Break","label":"Emergency Contacts"},{"fieldname":"emergency_contacts","fieldtype":"Table","label":"Emergency Contacts","options":"Traveler Emergency Contact"},{"fieldname":"section_notes","fieldtype":"Section Break","label":"Notes"},{"fieldname":"notes","fieldtype":"Small Text","label":"Notes"}],"index_web_pages_for_search":1,"links":[],"modified":"2026-04-14 03:45:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Traveler","naming_rule":"By \"Naming Series\" field","owner":"Administrator","permissions":[{"create":1,"delete":1,"email":1,"export":1,"print":1,"read":1,"report":1,"role":"System Manager","share":1,"write":1}],"sort_field":"modified","sort_order":"DESC","states":[],"title_field":"full_name","search_fields":"full_name,customer"}
TRAVJSON

cat > $APP_PATH/doctype/traveler/traveler.py << 'TRAVPY'
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
TRAVPY

touch $APP_PATH/doctype/traveler/__init__.py
echo "  Traveler DONE"

echo "=== PHASE 2: WRITE TRIP DOCTYPE ==="
mkdir -p $APP_PATH/doctype/trip
cat > $APP_PATH/doctype/trip/trip.json << 'TRIPJSON'
{"actions":[],"allow_rename":1,"autoname":"naming_series:","creation":"2026-04-14 00:20:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["naming_series","booking_reference","supplier_pnr","booking_date","column_break_basic","customer","primary_traveler","pax_count","section_classification","product_type","trip_scope","column_break_class","status","sales_owner","office","section_financial","cost_amount","base_service_amount","column_break_fin","extra_amount","total_sale_amount","column_break_fin2","profit","currency","section_invoicing","customer_invoice_no","column_break_inv","supplier_invoice_no","section_segments","trip_segments","section_charges","trip_charges"],"fields":[{"fieldname":"naming_series","fieldtype":"Select","label":"Naming Series","options":"TRIP-.YYYY.-.#####","reqd":1},{"fieldname":"booking_reference","fieldtype":"Data","in_list_view":1,"in_standard_filter":1,"label":"Booking Reference (PNR)","reqd":1,"unique":1},{"fieldname":"supplier_pnr","fieldtype":"Data","label":"Supplier PNR"},{"fieldname":"booking_date","fieldtype":"Date","in_list_view":1,"label":"Booking Date","reqd":1},{"fieldname":"column_break_basic","fieldtype":"Column Break"},{"fieldname":"customer","fieldtype":"Link","in_list_view":1,"in_standard_filter":1,"label":"Customer","options":"Customer","reqd":1},{"fieldname":"primary_traveler","fieldtype":"Link","in_list_view":1,"in_standard_filter":1,"label":"Primary Traveler","options":"Traveler"},{"fieldname":"pax_count","fieldtype":"Int","label":"Pax Count","default":"1"},{"fieldname":"section_classification","fieldtype":"Section Break","label":"Classification"},{"fieldname":"product_type","fieldtype":"Select","in_standard_filter":1,"label":"Product Type","options":"\nFlight\nHotel\nTransfer\nTrain\nOther"},{"fieldname":"trip_scope","fieldtype":"Select","in_standard_filter":1,"label":"Trip Scope","options":"\nDomestic\nInternational"},{"fieldname":"column_break_class","fieldtype":"Column Break"},{"default":"Draft","fieldname":"status","fieldtype":"Select","in_list_view":1,"in_standard_filter":1,"label":"Status","options":"Draft\nNormal\nConfirmed\nCompleted\nCancelled\nRefunded","reqd":1},{"fieldname":"sales_owner","fieldtype":"Link","in_standard_filter":1,"label":"Sales Owner","options":"User"},{"fieldname":"office","fieldtype":"Select","in_standard_filter":1,"label":"Office","options":"\nİZGE TURİZM 2018\nSANCAKTEPE 2018"},{"fieldname":"section_financial","fieldtype":"Section Break","label":"Financial Details"},{"fieldname":"cost_amount","fieldtype":"Currency","label":"Cost Amount (Paid to Supplier)","options":"currency"},{"fieldname":"base_service_amount","fieldtype":"Currency","label":"Service Fee","options":"currency"},{"fieldname":"column_break_fin","fieldtype":"Column Break"},{"fieldname":"extra_amount","fieldtype":"Currency","label":"Extra Amount","options":"currency"},{"fieldname":"total_sale_amount","fieldtype":"Currency","label":"Total Sale","options":"currency","in_list_view":1},{"fieldname":"column_break_fin2","fieldtype":"Column Break"},{"fieldname":"profit","fieldtype":"Currency","label":"Profit","options":"currency","read_only":1,"in_list_view":1},{"fieldname":"currency","fieldtype":"Link","label":"Currency","options":"Currency","default":"TRY"},{"fieldname":"section_invoicing","fieldtype":"Section Break","label":"Invoice References","collapsible":1},{"fieldname":"customer_invoice_no","fieldtype":"Data","label":"Customer Invoice No"},{"fieldname":"column_break_inv","fieldtype":"Column Break"},{"fieldname":"supplier_invoice_no","fieldtype":"Data","label":"Supplier Invoice No"},{"fieldname":"section_segments","fieldtype":"Section Break","label":"Trip Segments"},{"fieldname":"trip_segments","fieldtype":"Table","label":"Trip Segments","options":"Trip Segment"},{"fieldname":"section_charges","fieldtype":"Section Break","label":"Additional Charges","collapsible":1},{"fieldname":"trip_charges","fieldtype":"Table","label":"Trip Charges","options":"Trip Charge"}],"index_web_pages_for_search":1,"links":[],"modified":"2026-04-14 03:45:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip","naming_rule":"By \"Naming Series\" field","owner":"Administrator","permissions":[{"create":1,"delete":1,"email":1,"export":1,"print":1,"read":1,"report":1,"role":"System Manager","share":1,"write":1}],"sort_field":"modified","sort_order":"DESC","states":[],"title_field":"booking_reference","search_fields":"booking_reference,customer,primary_traveler"}
TRIPJSON

cat > $APP_PATH/doctype/trip/trip.py << 'TRIPPY'
import frappe
from frappe import _
from frappe.model.document import Document


class Trip(Document):
	def validate(self):
		self.calculate_profit()

	def calculate_profit(self):
		"""Calculate profit = total_sale_amount - cost_amount"""
		cost = self.cost_amount or 0
		total = self.total_sale_amount or 0
		self.profit = total - cost
TRIPPY

touch $APP_PATH/doctype/trip/__init__.py
echo "  Trip DONE"

echo "=== PHASE 3: WRITE TRIP SEGMENT DOCTYPE ==="
mkdir -p $APP_PATH/doctype/trip_segment
cat > $APP_PATH/doctype/trip_segment/trip_segment.json << 'SEGJSON'
{"actions":[],"allow_rename":1,"creation":"2026-04-14 00:20:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["direction","flight_no","departure_date","departure_time","arrival_time","origin","destination","airline","operator","supplier_locator","ticket_no","traveler"],"fields":[{"fieldname":"direction","fieldtype":"Select","in_list_view":1,"label":"Direction","options":"\nOutbound\nReturn","reqd":1},{"fieldname":"flight_no","fieldtype":"Data","in_list_view":1,"label":"Flight No"},{"fieldname":"departure_date","fieldtype":"Date","in_list_view":1,"label":"Departure Date","reqd":1},{"fieldname":"departure_time","fieldtype":"Time","label":"Departure Time"},{"fieldname":"arrival_time","fieldtype":"Time","label":"Arrival Time"},{"fieldname":"origin","fieldtype":"Data","in_list_view":1,"label":"Origin (IATA)","reqd":1},{"fieldname":"destination","fieldtype":"Data","in_list_view":1,"label":"Destination (IATA)","reqd":1},{"fieldname":"airline","fieldtype":"Data","in_list_view":1,"label":"Airline"},{"fieldname":"operator","fieldtype":"Data","label":"Operator"},{"fieldname":"supplier_locator","fieldtype":"Data","label":"Supplier Locator"},{"fieldname":"ticket_no","fieldtype":"Data","label":"Ticket No"},{"fieldname":"traveler","fieldtype":"Link","label":"Traveler","options":"Traveler"}],"index_web_pages_for_search":1,"istable":1,"links":[],"modified":"2026-04-14 03:45:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip Segment","naming_rule":"Random","owner":"Administrator","permissions":[],"sort_field":"modified","sort_order":"DESC","states":[]}
SEGJSON

cat > $APP_PATH/doctype/trip_segment/trip_segment.py << 'SEGPY'
import frappe
from frappe.model.document import Document


class TripSegment(Document):
	pass
SEGPY

touch $APP_PATH/doctype/trip_segment/__init__.py
echo "  Trip Segment DONE"

echo "=== PHASE 4: WRITE TRIP CHARGE DOCTYPE (NEW) ==="
mkdir -p $APP_PATH/doctype/trip_charge
cat > $APP_PATH/doctype/trip_charge/trip_charge.json << 'CHRGJSON'
{"actions":[],"allow_rename":1,"creation":"2026-04-14 03:45:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["charge_type","description","amount","currency","related_traveler"],"fields":[{"fieldname":"charge_type","fieldtype":"Select","in_list_view":1,"label":"Charge Type","options":"\nSeat\nCIP\nBundle\nBaggage\nTransfer\nOther","reqd":1},{"fieldname":"description","fieldtype":"Data","in_list_view":1,"label":"Description"},{"fieldname":"amount","fieldtype":"Currency","in_list_view":1,"label":"Amount","options":"currency","reqd":1},{"fieldname":"currency","fieldtype":"Link","label":"Currency","options":"Currency","default":"TRY"},{"fieldname":"related_traveler","fieldtype":"Link","in_list_view":1,"label":"Related Traveler","options":"Traveler"}],"index_web_pages_for_search":1,"istable":1,"links":[],"modified":"2026-04-14 03:45:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip Charge","naming_rule":"Random","owner":"Administrator","permissions":[],"sort_field":"modified","sort_order":"DESC","states":[]}
CHRGJSON

cat > $APP_PATH/doctype/trip_charge/trip_charge.py << 'CHRGPY'
import frappe
from frappe.model.document import Document


class TripCharge(Document):
	pass
CHRGPY

touch $APP_PATH/doctype/trip_charge/__init__.py
echo "  Trip Charge DONE"

echo "=== PHASE 5: COPY TO APP-LEVEL (izge_travel/izge_travel/doctype/) ==="
# Frappe looks at both levels; ensure app-level has the latest
mkdir -p $APP_PKG/doctype
touch $APP_PKG/doctype/__init__.py
for dt in traveler traveler_emergency_contact trip trip_segment trip_charge; do
    if [ -d "$APP_PATH/doctype/$dt" ]; then
        rm -rf "$APP_PKG/doctype/$dt"
        cp -r "$APP_PATH/doctype/$dt" "$APP_PKG/doctype/"
        echo "  Copied $dt to app-level"
    fi
done

echo "=== PHASE 6: ENSURE modules.txt + patches.txt AT APP LEVEL ==="
echo "Izge Travel" > $APP_PKG/modules.txt
touch $APP_PKG/patches.txt
echo "  modules.txt + patches.txt at app level OK"

echo "=== PHASE 7: FIX PERMISSIONS ==="
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel

echo "=== PHASE 8: MIGRATE ==="
cd /home/frappe/bench
su frappe -c "bench --site $SITE migrate" 2>&1 | tail -30
echo "  Migrate DONE"

echo "=== PHASE 9: CLEAR CACHE ==="
su frappe -c "bench --site $SITE clear-cache"
su frappe -c "bench --site $SITE clear-website-cache"
echo "  Cache cleared"

echo "=== PHASE 10: FINAL VERIFICATION ==="
su frappe -c "bench --site $SITE console" << 'PYEOF'
import frappe
print("=== VERIFICATION ===")
print("1. Module Def:", frappe.db.get_value("Module Def", "Izge Travel", ["name", "app_name"], as_dict=1))
doctypes = frappe.db.sql("SELECT name, module FROM `tabDocType` WHERE module='Izge Travel'", as_dict=1)
print("2. DocTypes:", [d['name'] for d in doctypes])
print("3. Trip Charge exists:", frappe.db.exists("DocType", "Trip Charge"))
# Check Trip fields
trip_fields = [f.fieldname for f in frappe.get_meta("Trip").fields]
print("4. Trip has booking_reference:", "booking_reference" in trip_fields)
print("5. Trip has profit:", "profit" in trip_fields)
print("6. Trip has trip_charges:", "trip_charges" in trip_fields)
print("7. Trip has sales_owner:", "sales_owner" in trip_fields)
print("8. Trip has office:", "office" in trip_fields)
# Check Trip Segment fields
seg_fields = [f.fieldname for f in frappe.get_meta("Trip Segment").fields]
print("9. Segment has direction:", "direction" in seg_fields)
print("10. Segment has origin:", "origin" in seg_fields)
# Check Traveler fields
trav_fields = [f.fieldname for f in frappe.get_meta("Traveler").fields]
print("11. Traveler has title_prefix:", "title_prefix" in trav_fields)
print("=== ALL CHECKS COMPLETE ===")
PYEOF

echo ""
echo "=== DEPLOY COMPLETE ==="
