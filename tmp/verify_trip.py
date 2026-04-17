import frappe

def verify_trip():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    trip_id = "TRIP-2026-00131"
    exists = frappe.db.exists("Trip", trip_id)
    print(f"Trip {trip_id} exists: {exists}")
    
    if exists:
        doc = frappe.get_doc("Trip", trip_id)
        print(f"Status: {doc.status}, DocStatus: {doc.docstatus}")
        print(f"Customer: {doc.customer}")
        print(f"Total Sale: {doc.total_sale_amount}")
    else:
        print("Last 5 Trips:")
        last_trips = frappe.get_all("Trip", order_by="creation desc", limit=5)
        for t in last_trips:
            print(f"- {t.name}")

if __name__ == "__main__":
    verify_trip()
