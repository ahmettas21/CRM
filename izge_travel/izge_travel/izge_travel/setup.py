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

	frappe.logger("izge_travel").info("Custom configuration completed successfully.")

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
