#!/bin/sh
set -e

echo "=== STEP 1: DIAGNOSTICS ==="

# Check modules.txt location
echo "--- MODULES.TXT ---"
cat /home/frappe/bench/apps/izge_travel/izge_travel/modules.txt 2>/dev/null && echo "(app level OK)" || echo "NOT FOUND at app level"
cat /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/modules.txt 2>/dev/null && echo "(module level found)" || echo "NOT FOUND at module level"

# Check hooks.py
echo "--- HOOKS.PY ---"
ls -la /home/frappe/bench/apps/izge_travel/izge_travel/hooks.py 2>/dev/null || echo "NOT FOUND"

echo "=== STEP 2: FIX modules.txt AT CORRECT LEVEL ==="
# Frappe expects modules.txt at izge_travel/izge_travel/modules.txt (app package level)
cp /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/modules.txt /home/frappe/bench/apps/izge_travel/izge_travel/modules.txt 2>/dev/null || echo "Izge Travel" > /home/frappe/bench/apps/izge_travel/izge_travel/modules.txt
echo "modules.txt at app level:"
cat /home/frappe/bench/apps/izge_travel/izge_travel/modules.txt

echo "=== STEP 3: FIX patches.txt AT CORRECT LEVEL ==="
# Same issue with patches.txt
cp /home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/patches.txt /home/frappe/bench/apps/izge_travel/izge_travel/patches.txt 2>/dev/null || touch /home/frappe/bench/apps/izge_travel/izge_travel/patches.txt

echo "=== STEP 4: CREATE DOCTYPE SYMLINKS OR COPY ==="
# The key issue: Frappe looks for doctypes at izge_travel/izge_travel/doctype/
# But they are at izge_travel/izge_travel/izge_travel/doctype/
# We need to ensure doctype directory exists at app package level

# Check if app-level doctype exists
if [ -d "/home/frappe/bench/apps/izge_travel/izge_travel/doctype" ]; then
    echo "doctype dir exists at app level"
    ls /home/frappe/bench/apps/izge_travel/izge_travel/doctype/
else
    echo "Creating doctype dir at app level..."
    mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/doctype
    touch /home/frappe/bench/apps/izge_travel/izge_travel/doctype/__init__.py
fi

# Copy doctypes from triple-nested to correct location
echo "--- Copying doctypes to correct location ---"
for dt in traveler traveler_emergency_contact trip trip_segment; do
    if [ -d "/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/$dt" ]; then
        cp -r "/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel/doctype/$dt" "/home/frappe/bench/apps/izge_travel/izge_travel/doctype/" 2>/dev/null || true
        echo "  Copied $dt"
    fi
done

# Verify
echo "--- App-level doctype contents ---"
ls -la /home/frappe/bench/apps/izge_travel/izge_travel/doctype/

echo "=== STEP 5: ENSURE config directory ==="
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/config
touch /home/frappe/bench/apps/izge_travel/izge_travel/config/__init__.py

echo "=== STEP 6: ENSURE templates/public/www ==="
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/templates/includes
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/templates/pages
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/public/css
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/public/js
mkdir -p /home/frappe/bench/apps/izge_travel/izge_travel/www

echo "=== STEP 7: CREATE Module Def in DB ==="
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app execute frappe.client.insert --args "{\"doc\": {\"doctype\": \"Module Def\", \"module_name\": \"Izge Travel\", \"app_name\": \"izge_travel\"}}"' 2>/dev/null || echo "Module Def may already exist, trying update..."

# Force create via console
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app console' <<'PYEOF'
import frappe

# Create Module Def if not exists
if not frappe.db.exists("Module Def", "Izge Travel"):
    doc = frappe.get_doc({
        "doctype": "Module Def",
        "module_name": "Izge Travel",
        "app_name": "izge_travel",
        "custom": 0
    })
    doc.flags.ignore_permissions = True
    doc.insert(ignore_permissions=True, ignore_if_duplicate=True)
    frappe.db.commit()
    print("Module Def CREATED!")
else:
    # Ensure app_name is set correctly
    frappe.db.set_value("Module Def", "Izge Travel", "app_name", "izge_travel")
    frappe.db.commit()
    print("Module Def already exists, app_name verified")

print("Module Def check:", frappe.db.get_value("Module Def", "Izge Travel", ["name", "app_name"], as_dict=1))
PYEOF

echo "=== STEP 8: FIX PERMISSIONS ==="
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel

echo "=== STEP 9: REINSTALL APP + MIGRATE ==="
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app install-app izge_travel --force' || echo "install failed, trying migrate..."
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app migrate'
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app clear-cache'
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app clear-website-cache'

echo "=== STEP 10: FINAL VERIFICATION ==="
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app console' <<'PYEOF'
import frappe

print("=== FINAL CHECKS ===")
print("1. Module Def:", frappe.db.get_value("Module Def", "Izge Travel", ["name", "app_name"], as_dict=1))
print("2. DocTypes:", frappe.db.sql("SELECT name, module FROM `tabDocType` WHERE module='Izge Travel'", as_dict=1))
print("3. Installed Apps:", frappe.get_installed_apps())

# Check file system
import os
app_path = "/home/frappe/bench/apps/izge_travel/izge_travel"
print("4. modules.txt at app level:", os.path.exists(os.path.join(app_path, "modules.txt")))
print("5. hooks.py:", os.path.exists(os.path.join(app_path, "hooks.py")))
print("6. doctype dir:", os.path.exists(os.path.join(app_path, "doctype")))
if os.path.exists(os.path.join(app_path, "doctype")):
    print("   doctypes:", os.listdir(os.path.join(app_path, "doctype")))
PYEOF

echo ""
echo "=== ALL DONE ==="
