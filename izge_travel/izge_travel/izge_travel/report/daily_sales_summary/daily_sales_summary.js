frappe.query_reports["Daily Sales Summary"] = {
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
			fieldname: "group_by",
			label: __("Grupla"),
			fieldtype: "Select",
			options: "Date\nSales Owner\nOffice\nProduct Type",
			default: "Date"
		},
		{
			fieldname: "office",
			label: __("Ofis"),
			fieldtype: "Select",
			options: "\nİZGE TURİZM 2018\nSANCAKTEPE 2018"
		},
		{
			fieldname: "sales_owner",
			label: __("Satışçı"),
			fieldtype: "Link",
			options: "User"
		}
	]
};
