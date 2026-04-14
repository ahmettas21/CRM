#!/bin/bash
set -e

APP_PATH="/home/frappe/bench/apps/izge_travel"
INNER_PATH="$APP_PATH/izge_travel"
MODULE_PATH="$INNER_PATH/izge_travel"
SITE_NAME="erpnext-production-1b2e.up.railway.app"

echo "Checking directory structure..."
if [ -d "$INNER_PATH/doctype" ]; then
    echo "Fixing nested folder structure..."
    mkdir -p "$MODULE_PATH/doctype"
    mv "$INNER_PATH/doctype/"* "$MODULE_PATH/doctype/"
    rm -rf "$INNER_PATH/doctype"
fi

echo "Fixing permissions..."
chown -R frappe:frappe "$APP_PATH"

echo "Installing app in editable mode..."
cd /home/frappe/bench
su frappe -c "./env/bin/pip install -e $APP_PATH"

echo "Running migrate..."
su frappe -c "bench --site $SITE_NAME migrate"

echo "Verifying installation..."
/home/frappe/bench/env/bin/python -c "import izge_travel; print('Import successful:', izge_travel.__file__)"

echo "Done!"
