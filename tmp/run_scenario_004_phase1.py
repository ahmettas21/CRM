import frappe
from frappe.utils import today, flt

def execute_phase_1():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-004 (Phase 1: Professional Booking) Resume ---")
    
    booking_ref = "PEG-CRITICAL-VOID"
    trip_id = frappe.db.get_value("Trip", {"booking_reference": booking_ref}, "name")
    
    if not trip_id:
        print("Error: Trip not found. Something is wrong.")
        return
    
    trip = frappe.get_doc("Trip", trip_id)
    print(f"Resuming for Trip: {trip.name}")
    
    # 1. Ensure Invoices are Submitted
    si_name = trip.customer_invoice_no
    pi_name = trip.supplier_invoice_no
    
    if si_name:
        si = frappe.get_doc("Sales Invoice", si_name)
        if si.docstatus == 0:
            si.submit()
            print(f"Sales Invoice {si_name} Submitted.")
        else:
            print(f"Sales Invoice {si_name} already in state {si.docstatus}")
            
    if pi_name:
        pi = frappe.get_doc("Purchase Invoice", pi_name)
        if pi.docstatus == 0:
            pi.submit()
            print(f"Purchase Invoice {pi_name} Submitted.")
        else:
            print(f"Purchase Invoice {pi_name} already in state {pi.docstatus}")

    # 2. Create Payment Entry for Pegasus (Credit Card Payment)
    company = "İzge Turizm"
    supplier_name = "Pegasus Hava Yolları"
    cc_account = "102.01 - ŞİRKET KREDİ KARTI - IZGET"
    
    # Check if payment already exists
    already_paid = frappe.db.exists("Payment Entry", {"reference_no": "CC-AUTH-9999", "docstatus": ["<", 2]})
    if not already_paid:
        pi = frappe.get_doc("Purchase Invoice", pi_name)
        
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.party_type = "Supplier"
        pe.party = supplier_name
        pe.paid_from = cc_account
        pe.paid_from_account_currency = "TRY"
        pe.paid_to = pi.credit_to
        pe.paid_to_account_currency = "TRY"
        pe.paid_amount = 4000
        pe.received_amount = 4000
        pe.source_exchange_rate = 1.0
        pe.target_exchange_rate = 1.0
        pe.reference_no = "CC-AUTH-9999"
        pe.reference_date = today()
        
        pe.append("references", {
            "reference_doctype": "Purchase Invoice",
            "reference_name": pi_name,
            "total_amount": 4000,
            "outstanding_amount": 4000,
            "allocated_amount": 4000
        })
        
        pe.insert(ignore_permissions=True)
        pe.submit()
        print(f"Payment Entry {pe.name} Created (CC Paid to Pegasus).")
    else:
        print("Payment already exists.")
    
    frappe.db.commit()
    print("\n--- Phase 1 Resume Completed ---")
    print(f"Everything is now LIVE on the Ledger for {trip.name}.")

if __name__ == "__main__":
    execute_phase_1()
