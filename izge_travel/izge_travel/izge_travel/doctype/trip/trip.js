// Copyright (c) 2026, Izge Turizm and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip', {
	refresh(frm) {
		// Finansal toplamlar read-only ve otomatik hesaplanır
		// Yeni kayıt değilse ve onaylanmışsa fatura oluşturma butonu ekle
		if (!frm.is_new() && frm.doc.status !== 'Cancelled' && frm.doc.status !== 'Draft') {
			frm.add_custom_button(__('Create Sales Invoice'), () => {
				frappe.msgprint(__('Sales Invoice oluşturma henüz aktif değil.'));
			}, __('Create'));
		}
	},

	validate(frm) {
		// Server-side calculate_totals() zaten çalışacak,
		// ama client-side de toplamları göster
		calculate_parent_totals(frm);
	}
});

// =====================================================
// CHILD TABLE EVENT HANDLERS
// Her child table için aynı finansal hesaplama mantığı:
// sale_amount = cost_amount + service_amount + extra_amount
// =====================================================

// --- Trip Flight Segment ---
frappe.ui.form.on('Trip Flight Segment', {
	cost_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	service_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	extra_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	trip_flight_segments_remove(frm) {
		calculate_parent_totals(frm);
	}
});

// --- Trip Hotel Stay ---
frappe.ui.form.on('Trip Hotel Stay', {
	cost_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	service_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	extra_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	trip_hotel_stays_remove(frm) {
		calculate_parent_totals(frm);
	}
});

// --- Trip Service Item ---
frappe.ui.form.on('Trip Service Item', {
	cost_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	service_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	extra_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	trip_service_items_remove(frm) {
		calculate_parent_totals(frm);
	}
});

// --- Trip Charge ---
frappe.ui.form.on('Trip Charge', {
	cost_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	service_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	extra_amount(frm, cdt, cdn) {
		calculate_row_sale(frm, cdt, cdn);
	},
	trip_charges_remove(frm) {
		calculate_parent_totals(frm);
	}
});

// =====================================================
// HESAPLAMA FONKSİYONLARI
// =====================================================

/**
 * Satır bazında: sale_amount = cost_amount + service_amount + extra_amount
 * Ardından parent toplamlarını günceller.
 */
function calculate_row_sale(frm, cdt, cdn) {
	let row = frappe.get_doc(cdt, cdn);
	let cost = flt(row.cost_amount);
	let service = flt(row.service_amount);
	let extra = flt(row.extra_amount);
	let sale = cost + service + extra;

	frappe.model.set_value(cdt, cdn, 'sale_amount', sale);
	calculate_parent_totals(frm);
}

/**
 * Tüm child table satırlarını toplayarak parent finansal alanları günceller.
 * trip.py validate()'deki calculate_totals() ile aynı mantık (client-side mirror).
 */
function calculate_parent_totals(frm) {
	let total_cost = 0;
	let total_service = 0;
	let total_extra = 0;
	let total_sale = 0;

	let tables = [
		'trip_flight_segments',
		'trip_hotel_stays',
		'trip_service_items',
		'trip_charges'
	];

	tables.forEach(table_name => {
		let rows = frm.doc[table_name] || [];
		rows.forEach(row => {
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
