import frappe
from frappe.utils import today

def run_scenario_010():
    """
    SCEN-BEE-010 Regression Test: Realized Exchange Difference
    Preconditions: setup_company_for_fx_tests.py must be run first.
    """
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    company = "İzge Turizm"
    supplier = "Lufthansa Otoyol"
    eur_acc_name = "320.02 - SATICILAR EUR - IZGET"
    past_date = "2026-01-15"
    inv_eur = 1000
    kur_old = 35.0
    kur_new = 40.0
    paid_bank = "102.01.001 - İŞ BANKASI 4846 - IZGET"

    print("--- Running Test: SCEN-BEE-010 (Realized FX Difference) ---")

    # 1. Ensure Supplier Exists
    if not frappe.db.exists("Supplier", supplier):
        s = frappe.new_doc("Supplier")
        s.supplier_name = supplier
        s.supplier_group = "Hizmet"
        s.default_currency = "EUR"
        s.insert(ignore_permissions=True)

    # 2. Simulate Past Invoice (35.000 TL Base)
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.credit_to = eur_acc_name
    pi.posting_date = past_date
    pi.bill_no = f"INV-{frappe.generate_hash()[:6]}"
    pi.bill_date = past_date
    pi.currency = "EUR"
    pi.conversion_rate = kur_old
    pi.append("items", {"item_code": "BILET-MALIYETI", "qty": 1, "rate": inv_eur})
    pi.insert(ignore_permissions=True)
    pi.submit()
    
    # 3. Process Payment Today (40.000 TL Payment)
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Pay"
    pe.party_type = "Supplier"
    pe.party = supplier
    pe.posting_date = today()
    pe.paid_from = paid_bank
    pe.paid_from_account_currency = "TRY"
    pe.paid_amount = inv_eur * kur_new
    pe.source_exchange_rate = 1.0
    pe.paid_to = eur_acc_name
    pe.paid_to_account_currency = "EUR"
    pe.received_amount = inv_eur
    pe.target_exchange_rate = kur_new
    pe.reference_no = f"PE-{frappe.generate_hash()[:6]}"
    pe.reference_date = today()
    pe.append("references", {"reference_doctype": "Purchase Invoice", "reference_name": pi.name, "allocated_amount": inv_eur})
    pe.insert(ignore_permissions=True)
    pe.submit()

    frappe.db.commit()

    # 4. Assertions (Regressions)
    print("\n--- Running Assertions ---")
    
    # Assert 1: Supplier EUR Balance is 0
    sup_eur_bal = frappe.db.sql("SELECT SUM(credit_in_account_currency)-SUM(debit_in_account_currency) FROM `tabGL Entry` WHERE account=%s AND party=%s AND is_cancelled=0", (eur_acc_name, supplier))[0][0] or 0
    assert sup_eur_bal == 0, f"ASSERT FAIL: Supplier EUR Balance should be 0, but is {sup_eur_bal}"
    print("✅ P1: Supplier EUR Balance is exactly 0.0")

    # Assert 2: Cost Account remains untouched by Kur Farkı (35.000)
    cost_base = frappe.db.sql("SELECT base_net_total FROM `tabPurchase Invoice` WHERE name=%s", (pi.name,))[0][0]
    assert cost_base == 35000.0, f"ASSERT FAIL: Base cost should be 35000, but is {cost_base}"
    print("✅ P2: Cost account (PI) is safely locked at 35.000 TRY.")

    # Assert 3: 5.000 TL generated in Exchange Gain/Loss
    exchange_diff = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no=%s AND account LIKE '%%Exchange%%'", (pe.name,))[0][0] or 0
    assert exchange_diff == 5000.0, f"ASSERT FAIL: Exchange difference should be 5000, but is {exchange_diff}"
    print("✅ P3: Exactly 5.000 TRY routed to Exchange Gain/Loss account.")

    print("🎉 ALL ASSERTS PASSED. Regression SCEN-BEE-010 is stable.")

if __name__ == "__main__":
    run_scenario_010()
