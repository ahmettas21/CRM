import frappe

def create_item_groups():
	groups = ["Uçak Bileti", "Otel", "Vize", "Tur", "Transfer", "Vergi ve Harçlar", "Hizmet Bedeli"]
	parent_group = "Services" # ERPNext default for non-stock items

	if not frappe.db.exists("Item Group", parent_group):
		parent_group = "All Item Groups"

	for group in groups:
		if not frappe.db.exists("Item Group", group):
			doc = frappe.new_doc("Item Group")
			doc.item_group_name = group
			doc.parent_item_group = parent_group
			doc.is_group = 0
			doc.insert(ignore_permissions=True)

def create_items():
	items = [
		{"item_code": "YURTICI-UCAK", "item_name": "Yurt İçi Uçak Bileti", "item_group": "Uçak Bileti"},
		{"item_code": "YURTDISI-UCAK", "item_name": "Yurt Dışı Uçak Bileti", "item_group": "Uçak Bileti"},
		{"item_code": "HAVALIMANI-VERGISI", "item_name": "Havalimanı Vergisi", "item_group": "Vergi ve Harçlar"},
		{"item_code": "ACENTE-KOMISYONU-GELIR", "item_name": "Acente Komisyonu (Gelir)", "item_group": "Hizmet Bedeli"},
		{"item_code": "ACENTE-KOMISYONU-GIDER", "item_name": "Alt Acente Komisyonu (Gider)", "item_group": "Hizmet Bedeli"}
	]

	for item in items:
		if not frappe.db.exists("Item", item["item_code"]):
			doc = frappe.new_doc("Item")
			doc.item_code = item["item_code"]
			doc.item_name = item["item_name"]
			doc.item_group = item["item_group"]
			doc.is_stock_item = 0
			doc.is_sales_item = 1
			doc.is_purchase_item = 1 if "GIDER" in item["item_code"] or "UCAK" in item["item_code"] else 0
			doc.insert(ignore_permissions=True)

def setup_all():
	frappe.logger("izge_travel").info("Setting up Izge Travel Items and Item Groups...")
	create_item_groups()
	create_items()
	frappe.db.commit()
	frappe.logger("izge_travel").info("Izge Travel Items setup completed successfully.")
