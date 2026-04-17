import frappe

def check_trip_fields():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    meta = frappe.get_meta("Trip")
    print("--- Mandatory Fields (Trip) ---")
    for field in meta.fields:
        if field.reqd:
            print(f"- {field.fieldname} ({field.fieldtype})")
    
    # Check if 'supplier' field exists at all
    sup_field = meta.get_field("supplier")
    if sup_field:
        print(f"Supplier field exists: {sup_field.label} - reqd: {sup_field.reqd}")
    else:
        print("Supplier field does NOT exist in Trip header.")

if __name__ == "__main__":
    check_trip_fields()
