import frappe

def check_company_fields():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    meta = frappe.get_meta("Company")
    print("--- Fields containing 'billed' or 'stock' ---")
    for field in meta.fields:
        if "billed" in field.fieldname or "stock" in field.fieldname or "inventory" in field.fieldname:
            print(f"- {field.fieldname} ({field.fieldtype}): {field.label}")

if __name__ == "__main__":
    check_company_fields()
