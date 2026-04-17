// Copyright (c) 2026, Izge Turizm and contributors
// For license information, please see license.txt

frappe.ui.form.on('Trip', {
	setup(frm) {
		// Quick filters for linked fields
		frm.set_query("primary_traveler", function() {
			return { filters: { customer: frm.doc.customer } };
		});
	},

	refresh(frm) {
		calculate_parent_totals(frm);

		// ═══════════════════════════════════════════
		// PRATİK EKRAN: Custom Buttons & Quick Actions
		// ═══════════════════════════════════════════

		// Quick Customer Creation Button (before submit)
		if (frm.doc.docstatus === 0) {
			frm.add_custom_button(__('Yeni Müşteri'), () => {
				let d = new frappe.ui.Dialog({
					title: 'Hızlı Müşteri Oluştur',
					fields: [
						{ fieldname: 'customer_name', fieldtype: 'Data', label: 'Müşteri Adı', reqd: 1 },
						{ fieldname: 'customer_type', fieldtype: 'Select', label: 'Tür',
						  options: 'Company\nIndividual', default: 'Individual' },
						{ fieldname: 'mobile_no', fieldtype: 'Data', label: 'Telefon' },
						{ fieldname: 'email_id', fieldtype: 'Data', label: 'E-posta', options: 'Email' }
					],
					primary_action_label: 'Oluştur',
					primary_action(values) {
						frappe.call({
							method: 'frappe.client.insert',
							args: {
								doc: {
									doctype: 'Customer',
									customer_name: values.customer_name,
									customer_type: values.customer_type,
									customer_group: 'Commercial',
									territory: 'All Territories',
									mobile_no: values.mobile_no,
									email_id: values.email_id
								}
							},
							callback(r) {
								if (r.message) {
									frm.set_value('customer', r.message.name);
									frappe.show_alert({message: __('Müşteri oluşturuldu: ') + r.message.name, indicator: 'green'});
									d.hide();
								}
							}
						});
					}
				});
				d.show();
			}, __('Hızlı İşlemler'));

			// Quick Traveler Creation
			frm.add_custom_button(__('Yeni Yolcu'), () => {
				if (!frm.doc.customer) {
					frappe.msgprint(__('Önce müşteri seçiniz.'));
					return;
				}
				let d = new frappe.ui.Dialog({
					title: 'Hızlı Yolcu Oluştur',
					fields: [
						{ fieldname: 'title_prefix', fieldtype: 'Select', label: 'Ünvan',
						  options: '\nMR\nMRS\nCHD\nINF', default: 'MR' },
						{ fieldname: 'full_name', fieldtype: 'Data', label: 'Ad Soyad', reqd: 1 },
						{ fieldname: 'mobile_phone', fieldtype: 'Data', label: 'Telefon' },
						{ fieldname: 'email', fieldtype: 'Data', label: 'E-posta', options: 'Email' },
						{ fieldname: 'passport_number', fieldtype: 'Data', label: 'Pasaport No' },
						{ fieldname: 'passport_expiry_date', fieldtype: 'Date', label: 'Pasaport Bitiş' },
						{ fieldname: 'date_of_birth', fieldtype: 'Date', label: 'Doğum Tarihi' },
						{ fieldname: 'nationality', fieldtype: 'Link', label: 'Uyruk', options: 'Country', default: 'Turkey' }
					],
					primary_action_label: 'Oluştur',
					primary_action(values) {
						frappe.call({
							method: 'frappe.client.insert',
							args: {
								doc: {
									doctype: 'Traveler',
									customer: frm.doc.customer,
									...values
								}
							},
							callback(r) {
								if (r.message) {
									if (!frm.doc.primary_traveler) {
										frm.set_value('primary_traveler', r.message.name);
									}
									frappe.show_alert({message: __('Yolcu oluşturuldu: ') + r.message.full_name, indicator: 'green'});
									d.hide();
								}
							}
						});
					}
				});
				d.show();
			}, __('Hızlı İşlemler'));

			// Quick Flight Segment Add
			frm.add_custom_button(__('Uçuş Ekle'), () => {
				let d = new frappe.ui.Dialog({
					title: 'Hızlı Uçuş Segmenti',
					fields: [
						{ fieldname: 'traveler', fieldtype: 'Link', label: 'Yolcu', options: 'Traveler',
						  get_query: () => ({ filters: { customer: frm.doc.customer } }) },
						{ fieldname: 'direction', fieldtype: 'Select', label: 'Yön',
						  options: 'Outbound\nReturn', default: 'Outbound', reqd: 1 },
						{ fieldname: 'cb1', fieldtype: 'Column Break' },
						{ fieldname: 'origin', fieldtype: 'Data', label: 'Nereden (IATA)', reqd: 1 },
						{ fieldname: 'destination', fieldtype: 'Data', label: 'Nereye (IATA)', reqd: 1 },
						{ fieldname: 'sb1', fieldtype: 'Section Break', label: 'Uçuş Detayları' },
						{ fieldname: 'airline', fieldtype: 'Data', label: 'Havayolu' },
						{ fieldname: 'flight_no', fieldtype: 'Data', label: 'Uçuş No' },
						{ fieldname: 'departure_date', fieldtype: 'Date', label: 'Uçuş Tarihi', reqd: 1 },
						{ fieldname: 'cb2', fieldtype: 'Column Break' },
						{ fieldname: 'departure_time', fieldtype: 'Time', label: 'Kalkış' },
						{ fieldname: 'arrival_time', fieldtype: 'Time', label: 'İniş' },
						{ fieldname: 'ticket_no', fieldtype: 'Data', label: 'Bilet No' },
						{ fieldname: 'sb2', fieldtype: 'Section Break', label: 'Finansal' },
						{ fieldname: 'supplier', fieldtype: 'Link', label: 'Tedarikçi', options: 'Supplier' },
						{ fieldname: 'cost_amount', fieldtype: 'Currency', label: 'Maliyet', default: 0 },
						{ fieldname: 'cb3', fieldtype: 'Column Break' },
						{ fieldname: 'service_amount', fieldtype: 'Currency', label: 'Hizmet Bedeli', default: 0 },
						{ fieldname: 'extra_amount', fieldtype: 'Currency', label: 'Ekstra', default: 0 }
					],
					size: 'large',
					primary_action_label: 'Ekle',
					primary_action(values) {
						let sale = flt(values.cost_amount) + flt(values.service_amount) + flt(values.extra_amount);
						let tax = flt(values.service_amount) > 0 ? flt(Math.round((flt(values.service_amount) / 1.20) * 0.20 * 100) / 100) : 0;
						let row = frm.add_child('trip_flight_segments', {
							...values,
							sale_amount: sale,
							tax_amount: tax
						});
						frm.refresh_field('trip_flight_segments');
						calculate_parent_totals(frm);
						frappe.show_alert({message: __('Uçuş segmenti eklendi'), indicator: 'green'});
						d.hide();
					}
				});
				d.show();
			}, __('Hızlı İşlemler'));
		}

		// ═══════════════════════════════════════════
		// SUBMITTED STATE: Accounting Buttons
		// ═══════════════════════════════════════════
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

			frm.add_custom_button(__('Payment Entry'), () => {
				frappe.model.open_mapped_doc({
					method: "erpnext.accounts.doctype.payment_entry.payment_entry.get_payment_entry",
					frm: frm,
					source_doctype: "Sales Invoice",
					args: {
						"dt": "Sales Invoice",
						"dn": frm.doc.customer_invoice_no
					}
				});
			}, __('Muhasebe'));
		}

		// ═══════════════════════════════════════════
		// VISUAL INDICATORS
		// ═══════════════════════════════════════════
		if (frm.doc.profit < 0 && frm.doc.total_sale_amount > 0) {
			frm.dashboard.set_headline(
				__('<span style="color:red; font-weight:bold;">⚠️ DİKKAT: Bu trip zararda! Kâr: {0}</span>', [format_currency(frm.doc.profit, frm.doc.currency)])
			);
		} else if (frm.doc.profit > 0) {
			frm.dashboard.set_headline(
				__('<span style="color:green;">✅ Kâr: {0} | Marj: {1}%</span>', [
					format_currency(frm.doc.profit, frm.doc.currency),
					(frm.doc.total_sale_amount > 0 ? ((frm.doc.profit / frm.doc.total_sale_amount) * 100).toFixed(1) : 0)
				])
			);
		}
	},

	// Auto-set booking date to today
	customer(frm) {
		if (frm.doc.customer && !frm.doc.booking_date) {
			frm.set_value('booking_date', frappe.datetime.get_today());
		}
	},

	// Auto-set product type based on child tables
	validate(frm) {
		calculate_parent_totals(frm);
		
		// Auto-detect product type
		if (!frm.doc.product_type) {
			let has_flight = (frm.doc.trip_flight_segments || []).length > 0;
			let has_hotel = (frm.doc.trip_hotel_stays || []).length > 0;
			if (has_flight && has_hotel) frm.set_value('product_type', 'Package');
			else if (has_flight) frm.set_value('product_type', 'Flight');
			else if (has_hotel) frm.set_value('product_type', 'Hotel');
		}
	},

	// CC Commission auto-calculate
	payment_method(frm) {
		calculate_cc_commission(frm);
	},
	cc_commission_rate(frm) {
		calculate_cc_commission(frm);
	}
});

// ═══════════════════════════════════════════
// CHILD TABLE EVENT HANDLERS
// ═══════════════════════════════════════════
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

// ═══════════════════════════════════════════
// CALCULATION FUNCTIONS
// ═══════════════════════════════════════════
function calculate_row_sale(frm, cdt, cdn, triggered_field) {
	let row = frappe.get_doc(cdt, cdn);
	let cost = flt(row.cost_amount);
	let service = flt(row.service_amount);
	let extra = flt(row.extra_amount);
	
	// Sale = Cost + Service + Extra
	let sale = flt(cost + service + extra);
	frappe.model.set_value(cdt, cdn, 'sale_amount', sale);

	// Auto-calc Tax from Service Fee (20% VAT included)
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

	calculate_cc_commission(frm);
}

function calculate_cc_commission(frm) {
	if (frm.doc.payment_method === 'Credit Card' && flt(frm.doc.cc_commission_rate) > 0) {
		let comm = flt(frm.doc.total_sale_amount * flt(frm.doc.cc_commission_rate) / 100, 2);
		frm.set_value('cc_commission_amount', comm);
	} else {
		frm.set_value('cc_commission_amount', 0);
	}
}
frappe.ui.form.on('Trip', {
    booking_reference: function(frm) {
        if (frm.doc.booking_reference) {
            frm.set_value('booking_reference', frm.doc.booking_reference.toUpperCase());
        }
    },
    supplier_pnr: function(frm) {
        if (frm.doc.supplier_pnr) {
            frm.set_value('supplier_pnr', frm.doc.supplier_pnr.toUpperCase());
        }
    },
    sales_owner: function(frm) {
        if (frm.doc.sales_owner) {
            frm.set_value('sales_owner', frm.doc.sales_owner.toLowerCase());
        }
    }
});

frappe.ui.form.on('Trip Flight Segment', {
    flight_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.flight_no) frappe.model.set_value(cdt, cdn, 'flight_no', row.flight_no.toUpperCase());
    },
    origin: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.origin) frappe.model.set_value(cdt, cdn, 'origin', row.origin.toUpperCase());
    },
    destination: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.destination) frappe.model.set_value(cdt, cdn, 'destination', row.destination.toUpperCase());
    },
    supplier_locator: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.supplier_locator) frappe.model.set_value(cdt, cdn, 'supplier_locator', row.supplier_locator.toUpperCase());
    },
     ticket_no: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.ticket_no) frappe.model.set_value(cdt, cdn, 'ticket_no', row.ticket_no.toUpperCase());
    }
});

frappe.ui.form.on('Trip Hotel Stay', {
	hotel_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		// Ilk harfleri buyut (Title Case)
		if(row.hotel_name) {
			let newVal = row.hotel_name.replace(/\\w\\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
			frappe.model.set_value(cdt, cdn, 'hotel_name', newVal);
		}
	},
    supplier_locator: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        if(row.supplier_locator) frappe.model.set_value(cdt, cdn, 'supplier_locator', row.supplier_locator.toUpperCase());
    }
});
