#!/bin/sh
# 1. ERPNext'i siteye kur (Customer hatasını çözmek için)
echo "--- INSTALLING ERPNEXT ---"
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app install-app erpnext'

# 2. Eksik DocType klasörlerini oluştur (Trip, Segment vs.)
echo "--- CREATING MISSING DOCTYPE DIRS ---"
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/trip_segment
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/traveler_emergency_contact

# 3. Ownership düzelt
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel

echo "--- READY FOR SYNC ---"
