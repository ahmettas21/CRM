#!/bin/sh
# Fix __init__.py
cat > /home/frappe/bench/apps/izge_travel/izge_travel/__init__.py << 'PYEOF'
__version__ = "0.0.1"
PYEOF

chown frappe:frappe /home/frappe/bench/apps/izge_travel/izge_travel/__init__.py

# Verify
echo "--- INIT CONTENT ---"
cat /home/frappe/bench/apps/izge_travel/izge_travel/__init__.py

# pip install
echo "--- PIP INSTALL ---"
cd /home/frappe/bench/apps/izge_travel
su frappe -c '/home/frappe/bench/env/bin/pip install -e .'

# Python import test
echo "--- PYTHON IMPORT TEST ---"
su frappe -c '/home/frappe/bench/env/bin/python -c "import izge_travel; print(izge_travel.__file__)"'

# Migrate and restart
echo "--- MIGRATE ---"
cd /home/frappe/bench
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app migrate'
su frappe -c 'bench --site erpnext-production-1b2e.up.railway.app clear-cache'
pkill -f gunicorn || true

echo "--- DONE ---"
