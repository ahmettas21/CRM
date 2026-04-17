import frappe
from frappe.utils import today

def run_scenario_003():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-003 (Full Void) Started ---")
    
    company = "İzge Turizm"
    customer_name = "Bee Akademi KOLAY BİLET"
    supplier_name = "Pegasus Hava Yolları"
    
    # 1. Ensure Supplier exists
    if not frappe.db.exists("Supplier", supplier_name):
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = supplier_name
        supp.supplier_group = "Hizmetler"
        supp.insert(ignore_permissions=True)
        print(f"Supplier created: {supplier_name}")
    else:
        supp = frappe.get_doc("Supplier", supplier_name)

    # 2. Ensure Traveler exists
    traveler_name = "Ahmet Bee Pegasus"
    trav_id = frappe.db.get_value("Traveler", {"full_name": traveler_name}, "name")
    if not trav_id:
        trav = frappe.new_doc("Traveler")
        trav.first_name = "Ahmet Bee"
        trav.last_name = "Pegasus"
        trav.full_name = traveler_name
        trav.customer = customer_name
        trav.insert(ignore_permissions=True)
        trav_id = trav.name
        print(f"Traveler created: {trav_id}")

    # 3. Create Trip (Initial State: Flight to HAM)
    trip = frappe.new_doc("Trip")
    trip.naming_series = "TRIP-.YYYY.-.#####"
    trip.customer = customer_name
    trip.supplier = supplier_name
    trip.booking_reference = "PEG-HAM-VOID-001"
    trip.product_type = "Flight"
    trip.trip_scope = "International"
    trip.booking_date = today()
    trip.status = "Normal"
    
    # Add Segment
    trip.append("trip_flight_segments", {
        "traveler": trav_id,
        "direction": "Outbound",
        "flight_no": "PC-1022",
        "airline": "PC", # Correct ID
        "origin": "IST",
        "destination": "HAM",
        "departure_date": today(),
        "supplier": supplier_name,
        "cost_amount": 3500,
        "sale_amount": 4200,
        "service_amount": 700
    })
    
    # 3. Submit Trip (Triggers Invoices)
    trip.insert(ignore_permissions=True)
    trip.submit()
    frappe.db.commit()
    print(f"Trip {trip.name} Created and Submitted (Initial Booking).")
    print(f"Initial SI: {trip.customer_invoice_no}, Initial PI: {trip.supplier_invoice_no}")
    
    # 4. Perform VOID (Cancel Trip)
    print(f"Performing VOID on {trip.name}...")
    trip.cancel()
    frappe.db.commit()
    
    # 5. Verify Accounting and Deletion
    # Check if invoices still exist or are cancelled
    si_exists = frappe.db.exists("Sales Invoice", trip.customer_invoice_no)
    pi_exists = frappe.db.exists("Purchase Invoice", trip.supplier_invoice_no)
    
    si_status = frappe.db.get_value("Sales Invoice", trip.customer_invoice_no, "docstatus") if si_exists else "DELETED"
    pi_status = frappe.db.get_value("Purchase Invoice", trip.supplier_invoice_no, "docstatus") if pi_exists else "DELETED"
    
    print(f"\n--- Post-Void Accounting Status ---")
    print(f"Sales Invoice ({trip.customer_invoice_no}) Status: {si_status}")
    print(f"Purchase Invoice ({trip.supplier_invoice_no}) Status: {pi_status}")
    
    if si_status in ["DELETED", 2] and pi_status in ["DELETED", 2]:
        print("✅ VOID SUCCESS: Accounting impact is zeroed out/removed.")
    else:
        print("❌ VOID ISSUE: Invoices are still active.")

    print("--- Scenario SCEN-BEE-003 Completed ---")

if __name__ == "__main__":
    run_scenario_003()
