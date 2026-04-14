#!/bin/sh
set -e
echo '=== UPDATING TRAVELER DOCTYPE ==='
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
  "title_prefix",
  "full_name",
  "customer",
  "section_contact",
  "email",
  "mobile_phone",
  "section_identity",
  "nationality",
  "passport_number",
  "passport_expiry_date",
  "date_of_birth",
  "section_emergency",
  "emergency_contacts",
  "section_notes",
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
   "fieldname": "title_prefix",
   "fieldtype": "Select",
   "label": "Title",
   "options": "\nMR\nMRS\nCHD\nINF"
  },
  {
   "fieldname": "full_name",
   "fieldtype": "Data",
   "in_list_view": 1,
   "in_standard_filter": 1,
   "label": "Full Name",
   "reqd": 1
  },
  {
   "fieldname": "customer",
   "fieldtype": "Link",
   "in_list_view": 1,
   "in_standard_filter": 1,
   "label": "Customer",
   "options": "Customer",
   "reqd": 1
  },
  {
   "fieldname": "section_contact",
   "fieldtype": "Section Break",
   "label": "Contact Information"
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
   "fieldname": "section_identity",
   "fieldtype": "Section Break",
   "label": "Identity & Travel Documents"
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
   "fieldname": "section_emergency",
   "fieldtype": "Section Break",
   "label": "Emergency Contacts"
  },
  {
   "fieldname": "emergency_contacts",
   "fieldtype": "Table",
   "label": "Emergency Contacts",
   "options": "Traveler Emergency Contact"
  },
  {
   "fieldname": "section_notes",
   "fieldtype": "Section Break",
   "label": "Notes"
  },
  {
   "fieldname": "notes",
   "fieldtype": "Small Text",
   "label": "Notes"
  }
 ],
 "index_web_pages_for_search": 1,
 "links": [],
 "modified": "2026-04-14 03:45:00.000000",
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
 "show_title_field_in_link": 1,
 "sort_field": "modified",
 "sort_order": "DESC",
 "states": [],
 "title_field": "full_name",
 "search_fields": "full_name,customer"
}

EOF
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel
cd /home/frappe/bench
su frappe -c "bench --site erpnext-production-1b2e.up.railway.app migrate"
echo '=== DONE ==='
