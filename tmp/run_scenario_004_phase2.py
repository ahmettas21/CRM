import frappe

def execute_phase_2_void():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-004 (Phase 2: THE VOID) Started ---")
    
    trip_id = "TRIP-2026-00133"
    trip = frappe.get_doc("Trip", trip_id)
    
    # 1. Handle Payments First (ERPNext requires unlinking payments before cancelling invoices)
    # We find payments linked to the Purchase Invoice
    pi_name = trip.supplier_invoice_no
    payments = frappe.get_all("Payment Entry Reference", filters={
        "reference_doctype": "Purchase Invoice",
        "reference_name": pi_name,
        "docstatus": 1
    }, fields=["parent"])
    
    for p in payments:
        pe = frappe.get_doc("Payment Entry", p.parent)
        print(f"Cancelling Payment Entry {pe.name} (Refund from Pegasus to CC)...")
        pe.cancel()
    
    # 2. Cancel the Trip (This will call on_cancel in trip.py which cancels Invoices)
    print(f"Cancelling Trip {trip.name}...")
    trip.cancel()
    
    frappe.db.commit()
    
    # 3. Final Verification
    print("\n--- Final Accounting Audit After VOID ---")
    
    # Check Customer Balance (Bee Akademi)
    customer = "Bee Akademi KOLAY BİLET"
    # We check if there are any active (docstatus=1) GL entries for this trip.SI
    si_name = trip.customer_invoice_no
    gl_entries = frappe.db.exists("GL Entry", {"voucher_no": si_name, "is_cancelled": 0})
    print(f"Customer Invoice ({si_name}) has active GL Entries: {'YES' if gl_entries else 'NO'}")
    
    # Check Bank Balance (İş Bankası 4846)
    bank_acc = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    # When cancelled, GL entries for that voucher should be marked as is_cancelled=1 or reversed
    # In ERPNext v14+, it usually creates reverse entries.
    
    # Let's check the total balance of the Bank account
    # In ERPNext, we calculate from GL
    balance = frappe.db.sql("""
        SELECT SUM(debit) - SUM(credit) 
        FROM `tabGL Entry` 
        WHERE account = %s AND is_cancelled = 0
    """, bank_acc)[0][0] or 0
    
    print(f"İş Bankası 4846 Final Balance: {balance} TL")
    if balance == 0:
        print("✅ BANK SYNC: The 4000 TL was spent then reversed. Net is ZERO.")
    
    print("--- Scenario SCEN-BEE-004 Completed ---")

if __name__ == "__main__":
    execute_phase_2_void()
