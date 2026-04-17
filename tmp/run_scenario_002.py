import frappe
from frappe.utils import today, add_days

def run_scenario_002():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-002 Execution Started ---")
    
    # 1. Load the original Trip
    original_id = "TRIP-2026-00131"
    if not frappe.db.exists("Trip", original_id):
        print(f"Error: Original Trip {original_id} not found.")
        return
    
    doc = frappe.get_doc("Trip", original_id)
    
    # 2. Cancel the original (This will also cancel/delete the invoices via trip.py:on_cancel)
    if doc.docstatus == 1:
        print(f"Cancelling original Trip {original_id}...")
        doc.cancel()
        frappe.db.commit()
    
    # 3. Create Amendment
    print(f"Creating Amendment for {original_id}...")
    new_doc = frappe.copy_doc(doc)
    new_doc.amended_from = doc.name
    new_doc.docstatus = 0
    new_doc.booking_reference = f"{doc.booking_reference}-REV"
    new_doc.customer_invoice_no = ""
    new_doc.supplier_invoice_no = ""
    
    # Clear current segments to rebuild precisely for the scenario
    # Actually, we have 4 segments (3 adults + 1 child) from previous scenario.
    segments = new_doc.get("trip_flight_segments")
    
    # We'll treat:
    # Segment 0: Ahmet (Adult 1) -> Cancelled
    # Segment 1: Ayşe (Adult 2) -> Modified
    # Segment 2: Mehmet (Adult 3) -> Original
    # Segment 3: Can (Child 1) -> Original
    
    # Update Segment 0 (Ahmet) - Total Cancellation Handling
    # User: 4000 refund from op, 1000 penalty. -> Cost = 1000.
    # User: 2000 refund to customer. -> Sale = 6500 - 2000 = 4500.
    segments[0].cost_amount = 1000
    segments[0].sale_amount = 4500
    segments[0].service_amount = 1500 # We keep the service fee (Original 1500)
    segments[0].flight_no = "THY-101 (CANCELLED)"
    
    # Update Segment 1 (Ayşe) - Modification Handling
    # User: Op fee 1100, Customer fee 1900. -> Added to original.
    segments[1].cost_amount = 5000 + 1100
    segments[1].sale_amount = 6500 + 1900
    segments[1].flight_no = "THY-202 (REVERSED)"
    segments[1].origin, segments[1].destination = segments[1].destination, segments[1].origin
    
    # Segments 2 and 3 remain same as original
    
    # 4. Save and Submit
    new_doc.save(ignore_permissions=True)
    new_doc.submit()
    frappe.db.commit()
    
    print(f"Trip {new_doc.name} (Amendment) Submitted Successfully!")
    print(f"New Totals -> Sale: {new_doc.total_sale_amount}, Cost: {new_doc.cost_amount}, Profit: {new_doc.profit}")
    print(f"Sales Invoice: {new_doc.customer_invoice_no}")
    print(f"Purchase Invoices: {new_doc.supplier_invoice_no}")
    
    print("--- Scenario SCEN-BEE-002 Completed ---")

if __name__ == "__main__":
    run_scenario_002()
