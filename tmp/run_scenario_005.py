import frappe
from frappe.utils import today, flt

def run_scenario_005():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-005 (Historical Refund) ---")
    
    company = "İzge Turizm"
    customer = "Bee Akademi KOLAY BİLET"
    supplier = "Pegasus Hava Yolları"
    cc_account = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    past_date = "2026-01-15"
    current_date = today()
    
    # 1. Past
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = past_date
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": 12000})
    si.insert(ignore_permissions=True)
    si.submit()
    
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.posting_date = past_date
    pi.append("items", {"item_code": "BILET-MALIYETI", "qty": 1, "rate": 10000})
    pi.insert(ignore_permissions=True)
    pi.submit()
    
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.party = supplier
    pe.posting_date = past_date
    pe.paid_from = cc_account
    pe.paid_to = pi.credit_to
    pe.paid_amount = 10000
    pe.received_amount = 10000
    pe.source_exchange_rate = 1.0
    pe.target_exchange_rate = 1.0
    pe.reference_no = "OLD-PAID-JAN"
    pe.reference_date = past_date
    pe.insert(ignore_permissions=True)
    pe.submit()
    
    # 2. Refund Today
    cn = frappe.get_doc({
        "doctype": "Sales Invoice", "is_return": 1, "return_against": si.name,
        "customer": customer, "posting_date": current_date,
        "items": [{"item_code": "UCAK-BILETI", "qty": -1, "rate": 12000}]
    })
    cn.insert(ignore_permissions=True)
    cn.submit()
    
    dn = frappe.get_doc({
        "doctype": "Purchase Invoice", "is_return": 1, "return_against": pi.name,
        "supplier": supplier, "posting_date": current_date,
        "items": [{"item_code": "BILET-MALIYETI", "qty": -1, "rate": 10000}]
    })
    dn.insert(ignore_permissions=True)
    dn.submit()
    
    ref_pe = frappe.new_doc("Payment Entry")
    ref_pe.payment_type = "Receive"
    ref_pe.party_type = "Supplier"
    ref_pe.party = supplier
    ref_pe.posting_date = current_date
    ref_pe.paid_from = pi.credit_to
    ref_pe.paid_to = cc_account
    ref_pe.paid_amount = 10000
    ref_pe.received_amount = 10000
    ref_pe.source_exchange_rate = 1.0
    ref_pe.target_exchange_rate = 1.0
    ref_pe.reference_no = "REF-APR"
    ref_pe.reference_date = current_date
    ref_pe.insert(ignore_permissions=True)
    ref_pe.submit()
    
    frappe.db.commit()
    
    # 3. Verify
    past_bal = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE account=%s AND posting_date < '2026-04-01' AND is_cancelled=0", cc_account)[0][0] or 0
    now_bal = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE account=%s AND is_cancelled=0", cc_account)[0][0] or 0
    print(f"March Balance: {past_bal} TL")
    print(f"Today Balance: {now_bal} TL")
    
if __name__ == "__main__":
    run_scenario_005()
