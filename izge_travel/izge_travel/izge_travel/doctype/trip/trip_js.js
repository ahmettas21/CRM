frappe.ui.form.on('Trip', {
	setup: function(frm) {
		// Set default values if new
		if (frm.is_new()) {
			frm.set_value('booking_date', frappe.datetime.get_today());
		}
	},
	refresh: function(frm) {
		// Add a custom button to trigger calculator manually if needed
		frm.add_custom_button(__('Calculate Totals'), function() {
			frm.trigger('calculate_totals');
		});
	},
	calculate_totals: function(frm) {
		let cost = 0, service = 0, extra = 0, sale = 0, tax = 0;

		(frm.doc.trip_flight_segments || []).forEach(d => {
			cost += d.cost_amount || 0;
			service += d.service_amount || 0;
			extra += d.extra_amount || 0;
			sale += d.sale_amount || 0;
			tax += d.tax_amount || 0;
		});

		(frm.doc.trip_hotel_stays || []).forEach(d => {
			cost += d.cost_amount || 0;
			service += d.service_amount || 0;
			extra += d.extra_amount || 0;
			sale += d.sale_amount || 0;
			tax += d.tax_amount || 0;
		});

		(frm.doc.trip_service_items || []).forEach(d => {
			cost += d.cost_amount || 0;
			service += d.service_amount || 0;
			extra += d.extra_amount || 0;
			sale += d.sale_amount || 0;
			tax += d.tax_amount || 0;
		});

		(frm.doc.trip_charges || []).forEach(d => {
			cost += d.cost_amount || 0;
			service += d.service_amount || 0;
			extra += d.extra_amount || 0;
			sale += d.sale_amount || 0;
			tax += d.tax_amount || 0;
		});

		frm.set_value('cost_amount', cost);
		frm.set_value('base_service_amount', service);
		frm.set_value('extra_amount', extra);
		frm.set_value('total_sale_amount', sale);
		frm.set_value('total_tax_amount', tax);
		frm.set_value('profit', sale - cost);
	}
});

// Trigger calculations on table rows change
const tables = ['trip_flight_segments', 'trip_hotel_stays', 'trip_service_items', 'trip_charges'];
tables.forEach(table => {
	frappe.ui.form.on(table + '_add', function(frm) {
		frm.trigger('calculate_totals');
	});
	frappe.ui.form.on(table + '_remove', function(frm) {
		frm.trigger('calculate_totals');
	});
	
	// Fields to watch in each table
	const watch_fields = ['cost_amount', 'service_amount', 'extra_amount', 'sale_amount', 'tax_amount'];
	watch_fields.forEach(f => {
		frappe.ui.form.on(table, f, function(frm, cdt, cdn) {
			// Auto calculate tax if service_amount is entered
			if (f === 'service_amount') {
				let row = locals[cdt][cdn];
				if (row.service_amount > 0) {
					let tax = Math.round((row.service_amount / 1.20) * 0.20 * 100) / 100;
					frappe.model.set_value(cdt, cdn, 'tax_amount', tax);
				}
			}
			frm.trigger('calculate_totals');
		});
	});
});
