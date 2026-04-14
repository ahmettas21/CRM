#!/bin/sh
set -e

APP_PATH="/home/frappe/bench/apps/izge_travel/izge_travel/izge_travel"
SITE="erpnext-production-1b2e.up.railway.app"

echo "=== DEPLOYING trip.js ==="

cat > $APP_PATH/doctype/trip/trip.js << 'EOF_TRIPJS'
// Copyright (c) 2026, Izge Turizm and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip', {
	refresh(frm) {
		if (!frm.is_new() && frm.doc.status !== 'Cancelled' && frm.doc.status !== 'Draft') {
			frm.add_custom_button(__('Create Sales Invoice'), () => {
				frappe.msgprint(__('Sales Invoice oluşturma henüz aktif değil.'));
			}, __('Create'));
		}
	},
	validate(frm) {
		calculate_parent_totals(frm);
	}
});

frappe.ui.form.on('Trip Flight Segment', {
	cost_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	service_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	extra_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	trip_flight_segments_remove(frm) { calculate_parent_totals(frm); }
});

frappe.ui.form.on('Trip Hotel Stay', {
	cost_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	service_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	extra_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	trip_hotel_stays_remove(frm) { calculate_parent_totals(frm); }
});

frappe.ui.form.on('Trip Service Item', {
	cost_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	service_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	extra_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	trip_service_items_remove(frm) { calculate_parent_totals(frm); }
});

frappe.ui.form.on('Trip Charge', {
	cost_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	service_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	extra_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn); },
	trip_charges_remove(frm) { calculate_parent_totals(frm); }
});

function calculate_row_sale(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	let sale = flt(row.cost_amount) + flt(row.service_amount) + flt(row.extra_amount);
	frappe.model.set_value(cdt, cdn, 'sale_amount', sale);
	calculate_parent_totals(frm);
}

function calculate_parent_totals(frm) {
	let total_cost = 0, total_service = 0, total_extra = 0, total_sale = 0;
	['trip_flight_segments','trip_hotel_stays','trip_service_items','trip_charges'].forEach(t => {
		(frm.doc[t] || []).forEach(row => {
			total_cost += flt(row.cost_amount);
			total_service += flt(row.service_amount);
			total_extra += flt(row.extra_amount);
			total_sale += flt(row.sale_amount);
		});
	});
	frm.set_value('cost_amount', total_cost);
	frm.set_value('base_service_amount', total_service);
	frm.set_value('extra_amount', total_extra);
	frm.set_value('total_sale_amount', total_sale);
	frm.set_value('profit', total_sale - total_cost);
}
EOF_TRIPJS

echo "  trip.js written OK"

echo "=== FIX OWNERSHIP ==="
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel
echo "  ownership fixed"

echo "=== BUILD ASSETS ==="
cd /home/frappe/bench
su frappe -c "bench build --app izge_travel" 2>&1 | tail -10
echo "  build DONE"

echo "=== DEPLOY COMPLETE ==="
