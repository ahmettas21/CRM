frappe.query_reports["Trip Profitability"] = {
	"filters": [
		{
			fieldname: "from_date",
			label: __("Başlangıç Tarihi"),
			fieldtype: "Date",
			default: frappe.datetime.add_months(frappe.datetime.get_today(), -1),
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: __("Bitiş Tarihi"),
			fieldtype: "Date",
			default: frappe.datetime.get_today(),
			reqd: 1
		},
		{
			fieldname: "customer",
			label: __("Müşteri"),
			fieldtype: "Link",
			options: "Customer"
		},
		{
			fieldname: "sales_owner",
			label: __("Satışçı"),
			fieldtype: "Link",
			options: "User"
		},
		{
			fieldname: "product_type",
			label: __("Ürün Tipi"),
			fieldtype: "Select",
			options: "\nFlight\nHotel\nTransfer\nTrain\nVisa\nTour\nPackage\nOther"
		},
		{
			fieldname: "office",
			label: __("Ofis"),
			fieldtype: "Select",
			options: "\nİZGE TURİZM 2018\nSANCAKTEPE 2018"
		},
		{
			fieldname: "trip_scope",
			label: __("Kapsam"),
			fieldtype: "Select",
			options: "\nDomestic\nInternational"
		}
	]
};
