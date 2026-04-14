import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def after_migrate():
	"""
	Run after bench migrate to setup default CRM Naming Series and Master Settings
	for Customers and Suppliers.
	"""
	frappe.logger("izge_travel").info("Configuring Custom Naming Series for Izge Travel...")

	# 1. Update Customer Naming Series Options
	if frappe.db.exists("DocType", "Customer"):
		make_property_setter("Customer", "naming_series", "options", "M-.YYYY.-.####", "Text")
		make_property_setter("Customer", "naming_series", "default", "M-.YYYY.-.####", "Text")

	# 2. Update Supplier Naming Series Options
	if frappe.db.exists("DocType", "Supplier"):
		make_property_setter("Supplier", "naming_series", "options", "T-.YYYY.-.####", "Text")
		make_property_setter("Supplier", "naming_series", "default", "T-.YYYY.-.####", "Text")

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
	frappe.logger("izge_travel").info("Custom Naming Series configured successfully.")
