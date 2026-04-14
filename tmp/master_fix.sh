#!/bin/sh
# 1. DocType Dosyalarını Yaz
echo "--- WRITING DOCTYPE FILES ---"

# Traveler (Güncelleme)
cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler/traveler.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "naming_series:",
 "creation": "2026-04-14 00:20:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "naming_series",
  "customer",
  "full_name",
  "email",
  "mobile_phone",
  "nationality",
  "passport_number",
  "passport_expiry_date",
  "date_of_birth",
  "emergency_contacts",
  "notes"
 ],
 "fields": [
  {
   "fieldname": "naming_series",
   "fieldtype": "Select",
   "label": "Naming Series",
   "options": "TRAV-.YYYY.-.#####",
   "reqd": 1
  },
  {
   "fieldname": "customer",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Customer",
   "options": "Customer",
   "reqd": 1
  },
  {
   "fieldname": "full_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "label": "Full Name",
   "reqd": 1
  },
  {
   "fieldname": "email",
   "fieldtype": "Data",
   "label": "Email",
   "options": "Email"
  },
  {
   "fieldname": "mobile_phone",
   "fieldtype": "Phone",
   "in_list_view": 1,
   "label": "Mobile Phone"
  },
  {
   "fieldname": "nationality",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Nationality",
   "options": "Country"
  },
  {
   "fieldname": "passport_number",
   "fieldtype": "Data",
   "label": "Passport Number"
  },
  {
   "fieldname": "passport_expiry_date",
   "fieldtype": "Date",
   "label": "Passport Expiry Date"
  },
  {
   "fieldname": "date_of_birth",
   "fieldtype": "Date",
   "label": "Date of Birth"
  },
  {
   "fieldname": "emergency_contacts",
   "fieldtype": "Table",
   "label": "Emergency Contacts",
   "options": "Traveler Emergency Contact"
  },
  {
   "fieldname": "notes",
   "fieldtype": "Small Text",
   "label": "Notes"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-04-14 00:20:00.000000",
 "modified_by": "Administrator",
 "module": "Izge Travel",
 "name": "Traveler",
 "naming_rule": "By \"Naming Series\" field",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": []
}
EOF

cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler/traveler.py << 'EOF'
import frappe
from frappe import _, utils
from frappe.model.document import Document

class Traveler(Document):
	def validate(self):
		if not self.full_name:
			frappe.throw(_("Full Name cannot be empty."))
		
		if self.passport_expiry_date:
			if utils.get_datetime(self.passport_expiry_date) < utils.get_datetime(utils.today()):
				frappe.throw(_("Passport already expired"))
		
		if self.date_of_birth:
			if utils.get_datetime(self.date_of_birth) > utils.get_datetime(utils.today()):
				frappe.throw(_("Date of Birth cannot be in the future."))
EOF

# Traveler Emergency Contact
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler_emergency_contact
cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler_emergency_contact/traveler_emergency_contact.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "creation": "2026-04-14 00:20:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "contact_name",
  "relationship",
  "phone",
  "email"
 ],
 "fields": [
  {
   "fieldname": "contact_name",
   "fieldtype": "Data",
   "label": "Contact Name",
   "reqd": 1
  },
  {
   "fieldname": "relationship",
   "fieldtype": "Data",
   "label": "Relationship",
   "reqd": 1
  },
  {
   "fieldname": "phone",
   "fieldtype": "Phone",
   "label": "Phone",
   "reqd": 1
  },
  {
   "fieldname": "email",
   "fieldtype": "Data",
   "label": "Email",
   "options": "Email"
  }
 ],
 "index_web_pages_for_search": 1,
 "istable": 1,
 "links": [],
 "modified": "2026-04-14 00:20:00.000000",
 "modified_by": "Administrator",
 "module": "Izge Travel",
 "name": "Traveler Emergency Contact",
 "naming_rule": "Random",
 "owner": "Administrator",
 "permissions": [],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": []
}
EOF

cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler_emergency_contact/traveler_emergency_contact.py << 'EOF'
import frappe
from frappe.model.document import Document

class TravelerEmergencyContact(Document):
	pass
EOF

# Trip
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip
cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip/trip.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "autoname": "naming_series:",
 "creation": "2026-04-14 00:20:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "naming_series",
  "customer",
  "primary_traveler",
  "departure_date",
  "return_date",
  "trip_status",
  "risk_level",
  "budget",
  "visa_required",
  "expected_location",
  "last_confirmed_location",
  "last_location_update_at",
  "last_location_source",
  "trip_segments"
 ],
 "fields": [
  {
   "fieldname": "naming_series",
   "fieldtype": "Select",
   "label": "Naming Series",
   "options": "TRIP-.YYYY.-.#####",
   "reqd": 1
  },
  {
   "fieldname": "customer",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Customer",
   "options": "Customer",
   "reqd": 1
  },
  {
   "fieldname": "primary_traveler",
   "fieldtype": "Link",
   "in_list_view": 1,
   "label": "Primary Traveler",
   "options": "Traveler",
   "reqd": 1
  },
  {
   "fieldname": "departure_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "label": "Departure Date",
   "reqd": 1
  },
  {
   "fieldname": "return_date",
   "fieldtype": "Date",
   "in_list_view": 1,
   "label": "Return Date",
   "reqd": 1
  },
  {
   "default": "Draft",
   "fieldname": "trip_status",
   "fieldtype": "Select",
   "in_list_view": 1,
   "label": "Trip Status",
   "options": "Draft\nPlanned\nConfirmed\nCompleted\nCancelled",
   "reqd": 1
  },
  {
   "default": "Low",
   "fieldname": "risk_level",
   "fieldtype": "Select",
   "in_list_view": 1,
   "label": "Risk Level",
   "options": "Low\nMedium\nHigh\nExtreme",
   "reqd": 1
  },
  {
   "fieldname": "budget",
   "fieldtype": "Currency",
   "label": "Budget"
  },
  {
   "default": "0",
   "fieldname": "visa_required",
   "fieldtype": "Check",
   "label": "Visa Required"
  },
  {
   "fieldname": "expected_location",
   "fieldtype": "Data",
   "label": "Expected Location"
  },
  {
   "fieldname": "last_confirmed_location",
   "fieldtype": "Data",
   "label": "Last Confirmed Location"
  },
  {
   "fieldname": "last_location_update_at",
   "fieldtype": "Datetime",
   "label": "Last Location Update At"
  },
  {
   "fieldname": "last_location_source",
   "fieldtype": "Select",
   "label": "Last Location Source",
   "options": "Manual\nMobile Check-in\nItinerary Prediction\nSupplier Feed"
  },
  {
   "fieldname": "trip_segments",
   "fieldtype": "Table",
   "label": "Trip Segments",
   "options": "Trip Segment"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-04-14 00:20:00.000000",
 "modified_by": "Administrator",
 "module": "Izge Travel",
 "name": "Trip",
 "naming_rule": "By \"Naming Series\" field",
 "owner": "Administrator",
 "permissions": [
  {
   "create": 1,
   "delete": 1,
   "email": 1,
   "export": 1,
   "print": 1,
   "read": 1,
   "report": 1,
   "role": "System Manager",
   "share": 1,
   "write": 1
  }
 ],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": []
}
EOF

cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip/trip.py << 'EOF'
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
EOF

# Trip Segment
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip_segment
cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip_segment/trip_segment.json << 'EOF'
{
 "actions": [],
 "allow_rename": 1,
 "creation": "2026-04-14 00:20:00.000000",
 "doctype": "DocType",
 "engine": "InnoDB",
 "field_order": [
  "segment_type",
  "from_city",
  "from_country",
  "to_city",
  "to_country",
  "start_datetime",
  "end_datetime",
  "supplier_name",
  "reference_no"
 ],
 "fields": [
  {
   "fieldname": "segment_type",
   "fieldtype": "Select",
   "label": "Segment Type",
   "options": "Flight\nHotel\nTransfer\nTrain",
   "reqd": 1
  },
  {
   "fieldname": "from_city",
   "fieldtype": "Data",
   "label": "From City",
   "reqd": 1
  },
  {
   "fieldname": "from_country",
   "fieldtype": "Link",
   "label": "From Country",
   "options": "Country",
   "reqd": 1
  },
  {
   "fieldname": "to_city",
   "fieldtype": "Data",
   "label": "To City",
   "reqd": 1
  },
  {
   "fieldname": "to_country",
   "fieldtype": "Link",
   "label": "To Country",
   "options": "Country",
   "reqd": 1
  },
  {
   "fieldname": "start_datetime",
   "fieldtype": "Datetime",
   "label": "Start Datetime",
   "reqd": 1
  },
  {
   "fieldname": "end_datetime",
   "fieldtype": "Datetime",
   "label": "End Datetime",
   "reqd": 1
  },
  {
   "fieldname": "supplier_name",
   "fieldtype": "Data",
   "label": "Supplier Name"
  },
  {
   "fieldname": "reference_no",
   "fieldtype": "Data",
   "label": "Reference No"
  }
 ],
 "index_web_pages_for_search": 1,
 "istable": 1,
 "links": [],
 "modified": "2026-04-14 00:20:00.000000",
 "modified_by": "Administrator",
 "module": "Izge Travel",
 "name": "Trip Segment",
 "naming_rule": "Random",
 "owner": "Administrator",
 "permissions": [],
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": []
}
EOF

cat > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip_segment/trip_segment.py << 'EOF'
import frappe
from frappe import _
from frappe.model.document import Document

class TripSegment(Document):
	def validate(self):
		if self.start_datetime and self.end_datetime:
			if self.end_datetime < self.start_datetime:
				frappe.throw(_("End Datetime cannot be before Start Datetime."))
EOF

# Ensure __init__.py files
find /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/ -type d -exec touch {}/__init__.py \;

# 2. ERPNext'i Force ile Kur
echo "--- INSTALLING ERPNEXT (FORCE) ---"
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app install-app erpnext --force'

# 3. İzinleri ve Migration'ı Çalıştır
echo "--- FINALIZING ---"
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app migrate'
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app clear-cache'

echo "--- ALL ERRORS SHOULD BE RESOLVED NOW ---"
