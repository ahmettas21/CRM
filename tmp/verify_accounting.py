import frappe
from frappe.utils import flt

def verify_accounting_balance():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Accounting Integrity Verification Start ---")
    
    trip_id = "TRIP-2026-00131-1"
    trip = frappe.get_doc("Trip", trip_id)
    
    print(f"Verify Trip: {trip.name}")
    print(f"Target Customer: {trip.customer}")
    print(f"Target Supplier: THY - Türk Hava Yolları")
    
    # 1. Check Sales Invoice Balance
    si_name = trip.customer_invoice_no
    si = frappe.get_doc("Sales Invoice", si_name)
    print(f"\n[Sales Invoice: {si.name}]")
    print(f"Grand Total: {si.grand_total} TL")
    print(f"Customer: {si.customer}")
    
    # 2. Check Purchase Invoice Balance
    pi_name = trip.supplier_invoice_no # It might be a comma separated list
    pis = pi_name.split(", ")
    for p in pis:
        p_doc = frappe.get_doc("Purchase Invoice", p)
        print(f"\n[Purchase Invoice: {p_doc.name}]")
        print(f"Grand Total: {p_doc.grand_total} TL")
        print(f"Supplier: {p_doc.supplier}")
    
    # 3. Calculate Accounting Profit
    accounting_profit = flt(si.grand_total) - sum([flt(frappe.get_doc("Purchase Invoice", p).grand_total) for p in pis])
    print(f"\n--- Final Verdict ---")
    print(f"Trip Profit: {trip.profit} TL")
    print(f"Accounting Profit (SI - PI): {accounting_profit} TL")
    
    if abs(flt(trip.profit) - accounting_profit) < 0.01:
        print("✅ INTEGRITY CHECK PASSED: Trip and Accounting are in sync.")
    else:
        print("❌ INTEGRITY CHECK FAILED: Mismatch between Trip and Invoices.")

if __name__ == "__main__":
    verify_accounting_balance()
