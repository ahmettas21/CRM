import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def after_migrate():
	"""
	Run after bench migrate to setup default CRM Naming Series and Master Settings
	for Customers and Suppliers.
	"""
	frappe.logger("izge_travel").info("Configuring Custom Naming Series and Fields for Izge Travel...")

	# 1. Update Customer Naming Series Options
	setup_naming_series_field("Customer", "M-.YYYY.-.####")

	# 2. Update Supplier Naming Series Options
	setup_naming_series_field("Supplier", "T-.YYYY.-.####")

	# Ensure Supplier Link field exists in Trip child tables
	setup_supplier_field("Trip Flight Segment")
	setup_supplier_field("Trip Hotel Stay")
	setup_supplier_field("Trip Service Item")
	setup_supplier_field("Trip Charge")

	# 3. Update Selling Settings (Customer Naming By)
	if frappe.db.exists("DocType", "Selling Settings"):
		selling_settings = frappe.get_single("Selling Settings")
		if selling_settings.cust_master_name != "Naming Series":
			selling_settings.cust_master_name = "Naming Series"
			selling_settings.save(ignore_permissions=True)

	# 4. Update Buying Settings (Supplier Naming By)
	if frappe.db.exists("DocType", "Buying Settings"):
		buying_settings = frappe.get_single("Buying Settings")
		if buying_settings.supp_master_name != "Naming Series":
			buying_settings.supp_master_name = "Naming Series"
			buying_settings.save(ignore_permissions=True)

	frappe.db.commit()

	from izge_travel.izge_travel.setup_items_taxes import setup_all
	setup_all()

	setup_suppliers()
	setup_payment_terms()

	frappe.logger("izge_travel").info("Custom configuration completed successfully.")

def setup_suppliers():
	"""Create essential suppliers for Izge Travel."""
	suppliers = [
		"Oteller", "BOOKINGAGORA", "VİZECİ", 
		"SERENA AŞ", "KOLAY BİLET", "BİLET BANK", "SERENA THY İÇHAT"
	]
	# Get a default supplier group
	sup_group = frappe.db.get_value("Supplier Group", {"name": ["like", "%Distrib%"]}, "name") or \
				frappe.db.get_value("Supplier Group", {}, "name") or "All Supplier Groups"
	
	for s in suppliers:
		if not frappe.db.exists("Supplier", {"supplier_name": s}):
			sup = frappe.get_doc({
				"doctype": "Supplier",
				"supplier_name": s,
				"supplier_group": sup_group,
				"supplier_type": "Company"
			})
			sup.insert(ignore_permissions=True)

def setup_payment_terms():
	"""
	Create Payment Terms Templates for Izge Travel:
	- Peşin (Anında)
	- 7 Gün Vade
	- 15 Gün Vade
	- 30 Gün Vade
	- 45 Gün Vade
	- Devre Vade (1-15 → diğer ayın 1'i, 15-30 → diğer ayın 15'i)
	"""
	templates = [
		{
			"name": "Peşin",
			"terms": [{"payment_term": "Peşin Ödeme", "invoice_portion": 100, "credit_days": 0}]
		},
		{
			"name": "7 Gün Vade",
			"terms": [{"payment_term": "7 Gün", "invoice_portion": 100, "credit_days": 7}]
		},
		{
			"name": "15 Gün Vade",
			"terms": [{"payment_term": "15 Gün", "invoice_portion": 100, "credit_days": 15}]
		},
		{
			"name": "30 Gün Vade",
			"terms": [{"payment_term": "30 Gün", "invoice_portion": 100, "credit_days": 30}]
		},
		{
			"name": "45 Gün Vade",
			"terms": [{"payment_term": "45 Gün", "invoice_portion": 100, "credit_days": 45}]
		},
		{
			"name": "Devre Vade (1-15 Ayın 1i)",
			"terms": [{"payment_term": "Devre 1-15", "invoice_portion": 100, "credit_days_based_on": "Day(s) after invoice date", "credit_days": 30}]
		},
		{
			"name": "Devre Vade (15-30 Ayın 15i)",
			"terms": [{"payment_term": "Devre 15-30", "invoice_portion": 100, "credit_days_based_on": "Day(s) after invoice date", "credit_days": 30}]
		}
	]
	
	for tmpl in templates:
		if not frappe.db.exists("Payment Terms Template", tmpl["name"]):
			pt = frappe.new_doc("Payment Terms Template")
			pt.template_name = tmpl["name"]
			
			for term in tmpl["terms"]:
				# First ensure Payment Term exists
				term_name = term.pop("payment_term")
				if not frappe.db.exists("Payment Term", term_name):
					pt_term = frappe.new_doc("Payment Term")
					pt_term.payment_term_name = term_name
					pt_term.invoice_portion = term.get("invoice_portion", 100)
					pt_term.credit_days = term.get("credit_days", 0)
					pt_term.insert(ignore_permissions=True)
				
				pt.append("terms", {
					"payment_term": term_name,
					"invoice_portion": term.get("invoice_portion", 100),
					"credit_days": term.get("credit_days", 0)
				})
			
			pt.insert(ignore_permissions=True)
			frappe.logger("izge_travel").info(f"Payment Terms Template '{tmpl['name']}' created.")
	
	frappe.db.commit()

def setup_naming_series_field(doctype, default_series):
	"""Manually add naming_series field if missing and set options."""
	if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "naming_series"}):
		from frappe.custom.doctype.custom_field.custom_field import create_custom_field
		create_custom_field(doctype, {
			"fieldname": "naming_series",
			"label": "Naming Series",
			"fieldtype": "Select",
			"options": default_series,
			"insert_after": "naming_series_insertion_point", # Will be handled by Frappe order
			"reqd": 1,
			"default": default_series
		})
	else:
		# Update existing custom field options
		make_property_setter(doctype, "naming_series", "options", default_series, "Text")
		make_property_setter(doctype, "naming_series", "default", default_series, "Text")

def setup_supplier_field(doctype):
	"""Manually add supplier link field to child tables if missing."""
	if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": "supplier"}):
		from frappe.custom.doctype.custom_field.custom_field import create_custom_field
		create_custom_field(doctype, {
			"fieldname": "supplier",
			"label": "Supplier",
			"fieldtype": "Link",
			"options": "Supplier",
			"insert_after": "traveler", # Usually after traveler or first fields
			"in_list_view": 1
		})
