import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	chart = get_chart(data)
	return columns, data, None, chart


def get_columns():
	return [
		{"fieldname": "name", "label": _("Trip ID"), "fieldtype": "Link", "options": "Trip", "width": 140},
		{"fieldname": "booking_reference", "label": _("PNR"), "fieldtype": "Data", "width": 120},
		{"fieldname": "booking_date", "label": _("Tarih"), "fieldtype": "Date", "width": 100},
		{"fieldname": "customer", "label": _("Müşteri"), "fieldtype": "Link", "options": "Customer", "width": 180},
		{"fieldname": "primary_traveler", "label": _("Yolcu"), "fieldtype": "Link", "options": "Traveler", "width": 150},
		{"fieldname": "product_type", "label": _("Ürün"), "fieldtype": "Data", "width": 80},
		{"fieldname": "trip_scope", "label": _("Kapsam"), "fieldtype": "Data", "width": 100},
		{"fieldname": "sales_owner", "label": _("Satışçı"), "fieldtype": "Link", "options": "User", "width": 120},
		{"fieldname": "office", "label": _("Ofis"), "fieldtype": "Data", "width": 140},
		{"fieldname": "cost_amount", "label": _("Maliyet"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "total_sale_amount", "label": _("Satış"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "profit", "label": _("Kâr"), "fieldtype": "Currency", "width": 120},
		{"fieldname": "margin", "label": _("Marj %"), "fieldtype": "Percent", "width": 80},
		{"fieldname": "payment_method", "label": _("Ödeme"), "fieldtype": "Data", "width": 100},
		{"fieldname": "payment_status", "label": _("Ödeme Durumu"), "fieldtype": "Data", "width": 110},
		{"fieldname": "status", "label": _("Durum"), "fieldtype": "Data", "width": 100},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("t.booking_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("t.booking_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("customer"):
		conditions.append("t.customer = %(customer)s")
		values["customer"] = filters["customer"]
	if filters.get("sales_owner"):
		conditions.append("t.sales_owner = %(sales_owner)s")
		values["sales_owner"] = filters["sales_owner"]
	if filters.get("product_type"):
		conditions.append("t.product_type = %(product_type)s")
		values["product_type"] = filters["product_type"]
	if filters.get("office"):
		conditions.append("t.office = %(office)s")
		values["office"] = filters["office"]
	if filters.get("trip_scope"):
		conditions.append("t.trip_scope = %(trip_scope)s")
		values["trip_scope"] = filters["trip_scope"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	data = frappe.db.sql(f"""
		SELECT 
			t.name, t.booking_reference, t.booking_date,
			t.customer, t.primary_traveler, t.product_type,
			t.trip_scope, t.sales_owner, t.office,
			t.cost_amount, t.total_sale_amount, t.profit,
			t.payment_method, t.payment_status, t.status
		FROM `tabTrip` t
		WHERE {where_clause}
		ORDER BY t.booking_date DESC
	""", values, as_dict=True)

	for row in data:
		if flt(row.total_sale_amount) > 0:
			row["margin"] = flt(row.profit) / flt(row.total_sale_amount) * 100
		else:
			row["margin"] = 0

	return data


def get_chart(data):
	if not data:
		return None

	# Daily profit chart
	daily = {}
	for row in data:
		d = str(row.get("booking_date", ""))
		if d not in daily:
			daily[d] = {"sale": 0, "cost": 0, "profit": 0}
		daily[d]["sale"] += flt(row.total_sale_amount)
		daily[d]["cost"] += flt(row.cost_amount)
		daily[d]["profit"] += flt(row.profit)

	labels = sorted(daily.keys())[-30:]  # last 30 days
	
	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Satış"), "values": [daily[d]["sale"] for d in labels]},
				{"name": _("Kâr"), "values": [daily[d]["profit"] for d in labels]}
			]
		},
		"type": "bar",
		"colors": ["#5e64ff", "#49c97a"]
	}
