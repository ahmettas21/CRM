import frappe
from frappe.utils import today

def run_scenario_trip_001():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-TRIP-001: Trip Controller Rule Engine & Billing ---")
    company = "İzge Turizm"
    customer = "Logic Test Passenger"
    
    # Setup
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
    
    # Guardrail: Dynamic Master Data Fetch (SOP-5)
    airport_id = frappe.db.get_value("Airport", {}, "name") or "IST"
    airline_id = frappe.db.get_value("Airline", {}, "name") or "LH"
    sup_name = frappe.db.get_value("Supplier", {"is_group": 0}, "name")
    if not sup_name:
        raise Exception("Sistemde hiç Supplier tanımlı değil! Test için önce bir Supplier yaratılmalı.")
    
    # RE-FIX: Traveler ID
    traveler_id = frappe.db.get_value("Traveler", {"full_name": "Test User Full Name"}, "name")
    if not traveler_id:
        t_doc = frappe.get_doc({"doctype": "Traveler", "full_name": "Test User Full Name", "customer": customer, "gender": "Other"}).insert(ignore_permissions=True)
        traveler_id = t_doc.name

    # 1. TEST: Margin Guardrail
    print("\n[Step 1] Testing Margin Guardrail (Negative Profit)...")
    trip_fail = frappe.new_doc("Trip")
    trip_fail.customer = customer
    trip_fail.booking_date = today()
    trip_fail.booking_reference = "FAIL-MAR-001"
    trip_fail.status = "Draft"
    trip_fail.product_type = "Flight"
    
    trip_fail.append("trip_flight_segments", {
        "traveler": traveler_id,
        "airline": airline_id,
        "supplier": sup_name,
        "origin": airport_id,
        "destination": airport_id,
        "direction": "Outbound",
        "departure_date": today(),
        "cost_amount": 1000.0,
        "sale_amount": 800.0
    })
    
    try:
        trip_fail.save()
        print("❌ FAIL: System allowed saving a Trip with negative margin!")
        raise Exception("SOP-GUARDRAIL bypassed!")
    except frappe.exceptions.ValidationError as e:
        print(f"✅ SUCCESS: Guardrail blocked negative margin. Error: {str(e)}")

    # 2. TEST: Auto Calculation & Whitelisted Invoicing
    print("\n[Step 2] Testing Auto-Calculation & Manual Invoicing...")
    trip_ok = frappe.new_doc("Trip")
    trip_ok.customer = customer
    trip_ok.booking_date = today()
    trip_ok.booking_reference = "PASSED-TRIP-777"
    trip_ok.status = "Draft"
    trip_ok.product_type = "Flight"
    
    # 5000 Cost, 7000 Sale + Mandatory Fields
    trip_ok.append("trip_flight_segments", {
        "traveler": traveler_id,
        "airline": airline_id,
        "supplier": sup_name,
        "origin": airport_id,
        "destination": airport_id,
        "direction": "Outbound",
        "departure_date": today(),
        "cost_amount": 5000.0,
        "sale_amount": 7000.0,
        "service_amount": 500.0
    })
    
    trip_ok.save()
    print(f"✅ Trip Saved. Profit: {trip_ok.profit} TL | Sale: {trip_ok.total_sale_amount} TL")
    
    assert trip_ok.profit == 2000.0, f"Profit calculation mismatch! Expected 2000, got {trip_ok.profit}"
    assert trip_ok.total_sale_amount == 7000.0, "Total sale mismatch!"
    
    # Submit Trip to enable invoicing
    trip_ok.submit()
    print(f"✅ Trip Submitted: {trip_ok.name}")
    
    # Trigger Whitelisted Function
    print("[Step 3] Triggering make_sales_invoice API...")
    si_name = trip_ok.make_sales_invoice()
    
    if si_name:
        si = frappe.get_doc("Sales Invoice", si_name)
        print(f"✅ Draft Sales Invoice Created: {si_name} | DocStatus: {si.docstatus}")
        assert si.docstatus == 0, "Invoice should be Draft!"
        assert si.grand_total == 7000.0, f"Invoice amount mismatch! Expected 7000, got {si.grand_total}"
        assert si.customer == customer, "Customer mismatch on Invoice!"
    else:
        raise Exception("Whitelisted make_sales_invoice failed to return invoice name!")

    frappe.db.commit()
    print("\n🎉 ALL TRIP LOGIC ASSERTS PASSED. Rule Engine is now enforced.")

if __name__ == "__main__":
    run_scenario_trip_001()
