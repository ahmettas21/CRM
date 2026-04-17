import frappe
from frappe.utils import today

def run_scenario_trip_002():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-TRIP-002: UI-Triggered Billing (Client-Side Simulation) ---")
    company = "İzge Turizm"
    customer = "UI Test Passenger"
    
    # 1. Setup Data
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
    
    traveler_id = frappe.db.get_value("Traveler", {"full_name": "UI Test Traveler"}, "name")
    if not traveler_id:
        t_doc = frappe.get_doc({
            "doctype": "Traveler", 
            "full_name": "UI Test Traveler", 
            "gender": "Other",
            "customer": customer
        }).insert(ignore_permissions=True)
        traveler_id = t_doc.name

    airport = frappe.db.get_value("Airport", {}, "name") or "IST"
    airline = frappe.db.get_value("Airline", {}, "name") or "LH"
    # Unified Supplier Lookup (V15 compatible)
    supplier = frappe.db.get_value("Supplier", {}, "name")

    # 2. Create and Submit Trip
    print("[Step 1] Creating a Profit-Positive Trip...")
    trip = frappe.new_doc("Trip")
    trip.customer = customer
    trip.supplier = supplier
    trip.booking_date = today()
    trip.booking_reference = f"UI-TEST-{frappe.utils.random_string(4).upper()}"
    trip.product_type = "Flight"
    
    trip.append("trip_flight_segments", {
        "traveler": traveler_id,
        "airline": airline,
        "supplier": supplier,
        "origin": airport,
        "destination": airport,
        "direction": "Outbound",
        "departure_date": today(),
        "cost_amount": 1000.0,
        "sale_amount": 1500.0
    })
    
    trip.insert(ignore_permissions=True)
    trip.submit()
    print(f"✅ Trip Submitted: {trip.name} (Profit: {trip.profit} TL)")

    # 3. Simulate UI Button Click (Whitelisted Call)
    print("\n[Step 2] Triggering make_sales_invoice (Simulating UI Click)...")
    
    # Reload to ensure we have the submitted object
    trip_doc = frappe.get_doc("Trip", trip.name)
    si_name = trip_doc.make_sales_invoice()
    
    if si_name:
        print(f"✅ Whitelisted API Success: Sales Invoice {si_name} created.")
        # Assert relation
        updated_trip = frappe.get_doc("Trip", trip.name)
        assert updated_trip.customer_invoice_no == si_name, f"Trip focus fail: expected field update to {si_name}"
        print(f"✅ P1: Trip correctly linked to Invoice ID {si_name}.")
    else:
        raise Exception("API failed to generate invoice!")

    # 4. Test Duplicate Prevention (Should fail)
    print("\n[Step 3] Testing Duplicate Prevention (Anti-Nesting Rule)...")
    try:
        trip_doc.make_sales_invoice()
        raise Exception("FAIL: System allowed duplicate invoices for one trip!")
    except frappe.exceptions.ValidationError as e:
        print(f"✅ SUCCESS: Guardrail blocked duplicate invoice. Error: {str(e)}")

    frappe.db.commit()
    print("\n🎉 ALL UI LOGIC ASSERTS PASSED. Billing Button is Stable and Secure!")

if __name__ == "__main__":
    run_scenario_trip_002()
