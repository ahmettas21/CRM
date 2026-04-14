import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data


def get_columns():
	return [
		{"fieldname": "supplier", "label": _("Tedarikçi"), "fieldtype": "Link", "options": "Supplier", "width": 200},
		{"fieldname": "trip_count", "label": _("Trip Sayısı"), "fieldtype": "Int", "width": 100},
		{"fieldname": "total_cost", "label": _("Toplam Maliyet"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "invoiced_amount", "label": _("Fatura Kesilen"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "paid_amount", "label": _("Ödenen"), "fieldtype": "Currency", "width": 140},
		{"fieldname": "outstanding", "label": _("Kalan Borç"), "fieldtype": "Currency", "width": 140},
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
	if filters.get("supplier"):
		conditions.append("fs.supplier = %(supplier)s")
		values["supplier"] = filters["supplier"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	# Gather all cost data from child tables with supplier
	cost_data = []
	child_tables = [
		("Trip Flight Segment", "trip_flight_segments"),
		("Trip Hotel Stay", "trip_hotel_stays"),
		("Trip Service Item", "trip_service_items"),
		("Trip Charge", "trip_charges"),
	]

	for child_dt, child_field in child_tables:
		rows = frappe.db.sql(f"""
			SELECT fs.supplier, fs.cost_amount, t.name as trip_name
			FROM `tab{child_dt}` fs
			JOIN `tabTrip` t ON fs.parent = t.name
			WHERE fs.supplier IS NOT NULL AND fs.supplier != '' AND fs.cost_amount > 0
			AND {where_clause}
		""", values, as_dict=True)
		cost_data.extend(rows)

	# Aggregate by supplier
	suppliers = {}
	for row in cost_data:
		s = row.supplier
		if s not in suppliers:
			suppliers[s] = {"supplier": s, "total_cost": 0, "trips": set()}
		suppliers[s]["total_cost"] += flt(row.cost_amount)
		suppliers[s]["trips"].add(row.trip_name)

	# Get invoiced and paid amounts from Purchase Invoice
	result = []
	for s, info in suppliers.items():
		invoiced = frappe.db.sql("""
			SELECT COALESCE(SUM(grand_total), 0) as total
			FROM `tabPurchase Invoice`
			WHERE supplier = %s AND docstatus = 1
		""", s)[0][0]

		paid = frappe.db.sql("""
			SELECT COALESCE(SUM(paid_amount), 0) as total
			FROM `tabPayment Entry`
			WHERE party_type = 'Supplier' AND party = %s AND docstatus = 1
		""", s)[0][0]

		result.append({
			"supplier": s,
			"trip_count": len(info["trips"]),
			"total_cost": info["total_cost"],
			"invoiced_amount": flt(invoiced),
			"paid_amount": flt(paid),
			"outstanding": flt(invoiced) - flt(paid)
		})

	result.sort(key=lambda x: x["outstanding"], reverse=True)
	return result
