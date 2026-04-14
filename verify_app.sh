echo '--- FIND APP STRUCTURE ---'
cd /home/frappe/bench/apps/izge_travel && find . -maxdepth 4 -not -path '*/.*' | sort
echo '--- BENCH LIST-APPS ---'
cd /home/frappe/bench && su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app list-apps'
echo '--- PYTHON IMPORT CHECK ---'
cd /home/frappe/bench && su frappe -c "python3 -c 'import izge_travel; print(izge_travel.__file__)'"
echo '--- IMPORTLIB SPEC CHECK ---'
cd /home/frappe/bench && su frappe -c "python3 -c 'import importlib.util; print(importlib.util.find_spec(\"izge_travel\"))'"
