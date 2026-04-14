#!/bin/sh
# 1. modules.txt içeriğini kontrol et ve düzelt
echo "Izge Travel" > /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/modules.txt

# 2. Module Def'i veritabanında zorla oluştur (Python ile)
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app execute frappe.get_doc --args "{\"doctype\": \"Module Def\", \"module_name\": \"Izge Travel\", \"app_name\": \"izge_travel\"}"' || echo "Module already exists or error"
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app execute frappe.db.commit'

# 3. Migrate ve cache temizle
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app migrate'
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app clear-cache'

echo "--- MODULE REPAIR DONE ---"
