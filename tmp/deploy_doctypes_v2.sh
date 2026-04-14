#!/bin/sh
set -e

APP_PATH="/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel"
APP_PKG="/home/frappe/bench/apps/izge_travel/izge_travel"
SITE="erpnext-production-1b2e.up.railway.app"

echo "=== PHASE 1: WRITE TRIP DOCTYPE ==="
mkdir -p $APP_PATH/doctype/trip
cat > $APP_PATH/doctype/trip/trip.json << 'TRIPJSON'
{"actions":[],"allow_rename":1,"autoname":"naming_series:","creation":"2026-04-14 00:20:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["naming_series","booking_reference","supplier_pnr","booking_date","column_break_basic","customer","primary_traveler","pax_count","section_classification","product_type","trip_scope","column_break_class","status","sales_owner","office","section_financial","cost_amount","base_service_amount","column_break_fin","extra_amount","total_sale_amount","column_break_fin2","profit","currency","section_invoicing","customer_invoice_no","column_break_inv","supplier_invoice_no","section_segments","trip_flight_segments","section_hotels","trip_hotel_stays","section_charges","trip_charges"],"fields":[{"fieldname":"naming_series","fieldtype":"Select","label":"Naming Series","options":"TRIP-.YYYY.-.#####","reqd":1},{"fieldname":"booking_reference","fieldtype":"Data","in_list_view":1,"in_standard_filter":1,"label":"Booking Reference (PNR)","reqd":1,"unique":1},{"fieldname":"supplier_pnr","fieldtype":"Data","label":"Supplier PNR"},{"fieldname":"booking_date","fieldtype":"Date","in_list_view":1,"label":"Booking Date","reqd":1},{"fieldname":"column_break_basic","fieldtype":"Column Break"},{"fieldname":"customer","fieldtype":"Link","in_list_view":1,"in_standard_filter":1,"label":"Customer","options":"Customer","reqd":1},{"fieldname":"primary_traveler","fieldtype":"Link","in_list_view":1,"in_standard_filter":1,"label":"Primary Traveler","options":"Traveler"},{"fieldname":"pax_count","fieldtype":"Int","label":"Pax Count","default":"1"},{"fieldname":"section_classification","fieldtype":"Section Break","label":"Classification"},{"fieldname":"product_type","fieldtype":"Select","in_standard_filter":1,"label":"Product Type","options":"\nFlight\nHotel\nTransfer\nTrain\nOther"},{"fieldname":"trip_scope","fieldtype":"Select","in_standard_filter":1,"label":"Trip Scope","options":"\nDomestic\nInternational"},{"fieldname":"column_break_class","fieldtype":"Column Break"},{"default":"Draft","fieldname":"status","fieldtype":"Select","in_list_view":1,"in_standard_filter":1,"label":"Status","options":"Draft\nNormal\nConfirmed\nCompleted\nCancelled\nRefunded","reqd":1},{"fieldname":"sales_owner","fieldtype":"Link","in_standard_filter":1,"label":"Sales Owner","options":"User"},{"fieldname":"office","fieldtype":"Select","in_standard_filter":1,"label":"Office","options":"\nİZGE TURİZM 2018\nSANCAKTEPE 2018"},{"fieldname":"section_financial","fieldtype":"Section Break","label":"Financial Details"},{"fieldname":"cost_amount","fieldtype":"Currency","label":"Cost Amount (Paid to Supplier)","options":"currency"},{"fieldname":"base_service_amount","fieldtype":"Currency","label":"Service Fee","options":"currency"},{"fieldname":"column_break_fin","fieldtype":"Column Break"},{"fieldname":"extra_amount","fieldtype":"Currency","label":"Extra Amount","options":"currency"},{"fieldname":"total_sale_amount","fieldtype":"Currency","label":"Total Sale","options":"currency","in_list_view":1},{"fieldname":"column_break_fin2","fieldtype":"Column Break"},{"fieldname":"profit","fieldtype":"Currency","label":"Profit","options":"currency","read_only":1,"in_list_view":1},{"fieldname":"currency","fieldtype":"Link","label":"Currency","options":"Currency","default":"TRY"},{"fieldname":"section_invoicing","fieldtype":"Section Break","label":"Invoice References","collapsible":1},{"fieldname":"customer_invoice_no","fieldtype":"Data","label":"Customer Invoice No"},{"fieldname":"column_break_inv","fieldtype":"Column Break"},{"fieldname":"supplier_invoice_no","fieldtype":"Data","label":"Supplier Invoice No"},{"fieldname":"section_segments","fieldtype":"Section Break","label":"Flight Segments"},{"fieldname":"trip_flight_segments","fieldtype":"Table","label":"Flight Segments","options":"Trip Flight Segment"},{"fieldname":"section_hotels","fieldtype":"Section Break","label":"Hotel Stays","collapsible":1},{"fieldname":"trip_hotel_stays","fieldtype":"Table","label":"Hotel Stays","options":"Trip Hotel Stay"},{"fieldname":"section_charges","fieldtype":"Section Break","label":"Additional Charges","collapsible":1},{"fieldname":"trip_charges","fieldtype":"Table","label":"Trip Charges","options":"Trip Charge"}],"index_web_pages_for_search":1,"links":[],"modified":"2026-04-14 03:45:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip","naming_rule":"By \"Naming Series\" field","owner":"Administrator","permissions":[{"create":1,"delete":1,"email":1,"export":1,"print":1,"read":1,"report":1,"role":"System Manager","share":1,"write":1}],"sort_field":"modified","sort_order":"DESC","states":[],"title_field":"booking_reference","search_fields":"booking_reference,customer,primary_traveler"}
TRIPJSON

echo "=== PHASE 2: WRITE TRIP FLIGHT SEGMENT DOCTYPE ==="
mkdir -p $APP_PATH/doctype/trip_flight_segment
cat > $APP_PATH/doctype/trip_flight_segment/trip_flight_segment.json << 'FLIGHTJSON'
{"actions":[],"allow_rename":1,"creation":"2026-04-14 00:20:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["direction","flight_no","departure_date","departure_time","arrival_time","origin","destination","airline","operator","supplier_locator","ticket_no","traveler"],"fields":[{"fieldname":"direction","fieldtype":"Select","in_list_view":1,"label":"Direction","options":"\nOutbound\nReturn","reqd":1},{"fieldname":"flight_no","fieldtype":"Data","in_list_view":1,"label":"Flight No"},{"fieldname":"departure_date","fieldtype":"Date","in_list_view":1,"label":"Departure Date","reqd":1},{"fieldname":"departure_time","fieldtype":"Time","label":"Departure Time"},{"fieldname":"arrival_time","fieldtype":"Time","label":"Arrival Time"},{"fieldname":"origin","fieldtype":"Data","in_list_view":1,"label":"Origin (IATA)","reqd":1},{"fieldname":"destination","fieldtype":"Data","in_list_view":1,"label":"Destination (IATA)","reqd":1},{"fieldname":"airline","fieldtype":"Data","in_list_view":1,"label":"Airline"},{"fieldname":"operator","fieldtype":"Data","label":"Operator"},{"fieldname":"supplier_locator","fieldtype":"Data","label":"Supplier Locator"},{"fieldname":"ticket_no","fieldtype":"Data","label":"Ticket No"},{"fieldname":"traveler","fieldtype":"Link","label":"Traveler","options":"Traveler"}],"index_web_pages_for_search":1,"istable":1,"links":[],"modified":"2026-04-14 03:55:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip Flight Segment","naming_rule":"Random","owner":"Administrator","permissions":[],"sort_field":"modified","sort_order":"DESC","states":[]}
FLIGHTJSON

cat > $APP_PATH/doctype/trip_flight_segment/trip_flight_segment.py << 'FLIGHTPY'
import frappe
from frappe.model.document import Document
class TripFlightSegment(Document):
	pass
FLIGHTPY
touch $APP_PATH/doctype/trip_flight_segment/__init__.py

echo "=== PHASE 3: WRITE TRIP HOTEL STAY DOCTYPE ==="
mkdir -p $APP_PATH/doctype/trip_hotel_stay
cat > $APP_PATH/doctype/trip_hotel_stay/trip_hotel_stay.json << 'HOTELJSON'
{"actions":[],"allow_rename":1,"creation":"2026-04-14 03:55:00.000000","doctype":"DocType","engine":"InnoDB","field_order":["hotel_name","supplier","supplier_locator","check_in_date","check_in_time","check_out_date","check_out_time","voucher_no","traveler"],"fields":[{"fieldname":"hotel_name","fieldtype":"Data","in_list_view":1,"label":"Hotel Name","reqd":1},{"fieldname":"supplier","fieldtype":"Data","in_list_view":1,"label":"Supplier"},{"fieldname":"supplier_locator","fieldtype":"Data","label":"Supplier Locator"},{"fieldname":"check_in_date","fieldtype":"Date","in_list_view":1,"label":"Check In Date","reqd":1},{"fieldname":"check_in_time","fieldtype":"Time","label":"Check In Time"},{"fieldname":"check_out_date","fieldtype":"Date","in_list_view":1,"label":"Check Out Date","reqd":1},{"fieldname":"check_out_time","fieldtype":"Time","label":"Check Out Time"},{"fieldname":"voucher_no","fieldtype":"Data","label":"Voucher No"},{"fieldname":"traveler","fieldtype":"Link","label":"Traveler","options":"Traveler"}],"index_web_pages_for_search":1,"istable":1,"links":[],"modified":"2026-04-14 03:55:00.000000","modified_by":"Administrator","module":"Izge Travel","name":"Trip Hotel Stay","naming_rule":"Random","owner":"Administrator","permissions":[],"sort_field":"modified","sort_order":"DESC","states":[]}
HOTELJSON

cat > $APP_PATH/doctype/trip_hotel_stay/trip_hotel_stay.py << 'HOTELPY'
import frappe
from frappe.model.document import Document
class TripHotelStay(Document):
	pass
HOTELPY
touch $APP_PATH/doctype/trip_hotel_stay/__init__.py

echo "=== PHASE 4: REMOVE OLD TRIP SEGMENT & COPY ==="
rm -rf $APP_PATH/doctype/trip_segment
rm -rf $APP_PKG/doctype/trip_segment

for dt in trip trip_flight_segment trip_hotel_stay; do
    if [ -d "$APP_PATH/doctype/$dt" ]; then
        rm -rf "$APP_PKG/doctype/$dt"
        cp -r "$APP_PATH/doctype/$dt" "$APP_PKG/doctype/"
        echo "  Copied $dt to app-level"
    fi
done

echo "=== PHASE 5: FIX PERMISSIONS AND MIGRATE ==="
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel

# Delete the old Trip Segment DocType from Database if exists
su frappe -c "bench --site $SITE console << 'PYEOF'
import frappe
try:
    if frappe.db.exists('DocType', 'Trip Segment'):
        frappe.delete_doc('DocType', 'Trip Segment')
        frappe.db.commit()
        print('Deleted Trip Segment from DB')
except Exception as e:
    print('Failed to delete Trip Segment from DB:', e)
PYEOF
"

cd /home/frappe/bench
su frappe -c "bench --site $SITE migrate" 2>&1 | tail -30
echo "  Migrate DONE"

echo "=== PHASE 6: VERIFICATION ==="
su frappe -c "bench --site $SITE console" << 'PYEOF'
import frappe
print("1. Trip Flight Segment exists:", frappe.db.exists("DocType", "Trip Flight Segment"))
print("2. Trip Hotel Stay exists:", frappe.db.exists("DocType", "Trip Hotel Stay"))
trip_fields = [f.fieldname for f in frappe.get_meta("Trip").fields]
print("3. Trip has trip_flight_segments:", "trip_flight_segments" in trip_fields)
print("4. Trip has trip_hotel_stays:", "trip_hotel_stays" in trip_fields)
PYEOF

echo "=== DEPLOY COMPLETE ==="
