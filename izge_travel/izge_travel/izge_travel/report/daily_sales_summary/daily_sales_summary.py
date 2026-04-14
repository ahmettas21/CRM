import frappe
from frappe import _
from frappe.utils import flt


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	chart = get_chart(data)
	report_summary = get_summary(data)
	return columns, data, None, chart, report_summary


def get_columns(filters):
	group_by = filters.get("group_by", "Date")
	first_col = {
		"Date": {"fieldname": "period", "label": _("Tarih"), "fieldtype": "Date", "width": 120},
		"Sales Owner": {"fieldname": "period", "label": _("Satışçı"), "fieldtype": "Data", "width": 150},
		"Office": {"fieldname": "period", "label": _("Ofis"), "fieldtype": "Data", "width": 160},
		"Product Type": {"fieldname": "period", "label": _("Ürün Tipi"), "fieldtype": "Data", "width": 120},
	}

	return [
		first_col.get(group_by, first_col["Date"]),
		{"fieldname": "trip_count", "label": _("Rezervasyon Sayısı"), "fieldtype": "Int", "width": 130},
		{"fieldname": "pax_count", "label": _("Yolcu Sayısı"), "fieldtype": "Int", "width": 110},
		{"fieldname": "total_cost", "label": _("Toplam Maliyet"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_sale", "label": _("Toplam Satış"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "total_profit", "label": _("Toplam Kâr"), "fieldtype": "Currency", "width": 130},
		{"fieldname": "avg_margin", "label": _("Ort. Marj %"), "fieldtype": "Percent", "width": 100},
		{"fieldname": "total_service", "label": _("Hizmet Bedeli"), "fieldtype": "Currency", "width": 120},
	]


def get_data(filters):
	conditions = []
	values = {}

	if filters.get("from_date"):
		conditions.append("booking_date >= %(from_date)s")
		values["from_date"] = filters["from_date"]
	if filters.get("to_date"):
		conditions.append("booking_date <= %(to_date)s")
		values["to_date"] = filters["to_date"]
	if filters.get("office"):
		conditions.append("office = %(office)s")
		values["office"] = filters["office"]
	if filters.get("sales_owner"):
		conditions.append("sales_owner = %(sales_owner)s")
		values["sales_owner"] = filters["sales_owner"]

	where_clause = " AND ".join(conditions) if conditions else "1=1"

	group_by = filters.get("group_by", "Date")
	group_field = {
		"Date": "booking_date",
		"Sales Owner": "COALESCE(sales_owner, 'Bilinmiyor')",
		"Office": "COALESCE(office, 'Bilinmiyor')",
		"Product Type": "COALESCE(product_type, 'Bilinmiyor')"
	}.get(group_by, "booking_date")

	data = frappe.db.sql(f"""
		SELECT 
			{group_field} as period,
			COUNT(*) as trip_count,
			SUM(pax_count) as pax_count,
			SUM(cost_amount) as total_cost,
			SUM(total_sale_amount) as total_sale,
			SUM(profit) as total_profit,
			SUM(base_service_amount) as total_service
		FROM `tabTrip`
		WHERE {where_clause}
		GROUP BY {group_field}
		ORDER BY {group_field} DESC
	""", values, as_dict=True)

	for row in data:
		if flt(row.total_sale) > 0:
			row["avg_margin"] = flt(row.total_profit) / flt(row.total_sale) * 100
		else:
			row["avg_margin"] = 0

	return data


def get_chart(data):
	if not data:
		return None

	labels = [str(row.period) for row in data[:30]]
	labels.reverse()

	sales = [flt(row.total_sale) for row in data[:30]]
	sales.reverse()
	profits = [flt(row.total_profit) for row in data[:30]]
	profits.reverse()

	return {
		"data": {
			"labels": labels,
			"datasets": [
				{"name": _("Satış"), "values": sales},
				{"name": _("Kâr"), "values": profits}
			]
		},
		"type": "bar",
		"colors": ["#5e64ff", "#49c97a"]
	}


def get_summary(data):
	total_trips = sum(r.get("trip_count", 0) for r in data)
	total_sale = sum(flt(r.get("total_sale", 0)) for r in data)
	total_profit = sum(flt(r.get("total_profit", 0)) for r in data)
	avg_margin = (total_profit / total_sale * 100) if total_sale > 0 else 0

	return [
		{"value": total_trips, "indicator": "Blue", "label": _("Toplam Rezervasyon"), "datatype": "Int"},
		{"value": total_sale, "indicator": "Blue", "label": _("Toplam Satış"), "datatype": "Currency", "currency": "TRY"},
		{"value": total_profit, "indicator": "Green" if total_profit > 0 else "Red", "label": _("Toplam Kâr"), "datatype": "Currency", "currency": "TRY"},
		{"value": round(avg_margin, 1), "indicator": "Green" if avg_margin > 5 else "Orange", "label": _("Ort. Marj"), "datatype": "Percent"},
	]
