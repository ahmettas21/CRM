// Copyright (c) 2026, Izge Turizm and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip', {
	refresh(frm) {
		calculate_parent_totals(frm);

		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__('Satış Faturaları'), () => {
				frappe.set_route("List", "Sales Invoice", {
					"remarks": ["like", "%" + (frm.doc.booking_reference || frm.doc.name) + "%"]
				});
			}, __('Muhasebe'));

			frm.add_custom_button(__('Alış Faturaları'), () => {
				frappe.set_route("List", "Purchase Invoice", {
					"remarks": ["like", "%" + (frm.doc.booking_reference || frm.doc.name) + "%"]
				});
			}, __('Muhasebe'));
		}
	},

	validate(frm) {
		calculate_parent_totals(frm);
	}
});

// --- Child Table Calculation Logic ---
const tables = ['Trip Flight Segment', 'Trip Hotel Stay', 'Trip Service Item', 'Trip Charge'];

tables.forEach(table => {
	frappe.ui.form.on(table, {
		cost_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn, 'cost_amount'); },
		service_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn, 'service_amount'); },
		extra_amount(frm, cdt, cdn) { calculate_row_sale(frm, cdt, cdn, 'extra_amount'); },
		sale_amount(frm, cdt, cdn) { calculate_parent_totals(frm); },
		tax_amount(frm, cdt, cdn) { calculate_parent_totals(frm); }
	});

	// Handle row removal
	let table_field = table.toLowerCase().replace(/ /g, '_') + 's';
	if (table === 'Trip Charge') table_field = 'trip_charges';
	
	let removal_handler = {};
	removal_handler[table_field + '_remove'] = function(frm) {
		calculate_parent_totals(frm);
	};
	frappe.ui.form.on('Trip', removal_handler);
});

function calculate_row_sale(frm, cdt, cdn, triggered_field) {
	let row = frappe.get_doc(cdt, cdn);
	let cost = flt(row.cost_amount);
	let service = flt(row.service_amount);
	let extra = flt(row.extra_amount);
	
	// 1. Calculate main sale amount (Sale = Cost + Service + Extra)
	let sale = flt(cost + service + extra);
	frappe.model.set_value(cdt, cdn, 'sale_amount', sale);

	// 2. Auto-calc Tax from Service Fee (20% VAT)
	if (triggered_field === 'service_amount' && service > 0) {
		let tax = flt(Math.round((service / 1.20) * 0.20 * 100) / 100);
		frappe.model.set_value(cdt, cdn, 'tax_amount', tax);
	}

	calculate_parent_totals(frm);
}

function calculate_parent_totals(frm) {
	let total_cost = 0;
	let total_service = 0;
	let total_extra = 0;
	let total_sale = 0;
	let total_tax = 0;

	let child_table_fields = ['trip_flight_segments', 'trip_hotel_stays', 'trip_service_items', 'trip_charges'];

	child_table_fields.forEach(t => {
		(frm.doc[t] || []).forEach(row => {
			total_cost += flt(row.cost_amount);
			total_service += flt(row.service_amount);
			total_extra += flt(row.extra_amount);
			total_sale += flt(row.sale_amount);
			total_tax += flt(row.tax_amount);
		});
	});

	frm.set_value({
		cost_amount: total_cost,
		base_service_amount: total_service,
		extra_amount: total_extra,
		total_sale_amount: total_sale,
		total_tax_amount: total_tax,
		profit: flt(total_sale - total_cost)
	});
}

