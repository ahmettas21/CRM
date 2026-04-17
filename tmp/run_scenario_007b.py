import frappe
from frappe.utils import today

def run_scenario_007b():
    """
    SCEN-BEE-007B Regression: Payment on Behalf (Model C: Clearing Account)
    Tests B2B Settlement via 2 Receive + 1 Pay Payment Entries.
    """
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    company = "İzge Turizm"
    customer = "Payment On Behalf Client"
    supplier = "B2B Clearing Tedarikçisi"
    clearing_acc_name = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    
    total_sales = 10000.0             # Müşteriye satılan (Sales Invoice)
    supplier_cost = 8000.0            # Tedarikçinin bizden alacağı bilet maliyeti (Purchase Invoice)
    cash_to_izge = 2000.0             # Acentemize nakit giren kâr (Service/Kasa)

    print("--- Running Test: SCEN-BEE-007B (Model C - Clearing Account) ---")

    # 1. Setup: Müşteri, Tedarikçi ve Kasa Hazırlıkları
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
    if not frappe.db.exists("Supplier", supplier):
        frappe.get_doc({"doctype": "Supplier", "supplier_name": supplier, "supplier_group": "Hizmet"}).insert(ignore_permissions=True)
    
    cash_acc = frappe.db.sql("select name from tabAccount where is_group=0 and account_type='Cash' and company=%s limit 1", (company,))
    if cash_acc:
        cash_acc = cash_acc[0][0]
    else: 
        raise Exception("Cash account not defined!")

    # 3. YARAT: Müşteriye Satış Faturası (10.000 TL)
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = today()
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": total_sales})
    si.insert(ignore_permissions=True)
    si.submit()

    # 4. YARAT: Tedarikçi Bilet Maliyeti Faturası (8.000 TL)
    # Tedarikçi Müşteriden 8000 TL çekti, bizim bu tedarikçiye bu biletin borcunu ERPNext'te (PI) var etmemiz lazım.
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.posting_date = today()
    pi.bill_no = f"CLR-COST-{frappe.generate_hash()[:6]}"
    pi.bill_date = today()
    pi.append("items", {"item_code": "BILET-MALIYETI", "qty": 1, "rate": supplier_cost})
    pi.insert(ignore_permissions=True)
    pi.submit()

    # 5. PE-1 (Receive): Gerçek Kasamıza giren 2.000 TL Müşteri Tahsilatı
    pe1 = frappe.new_doc("Payment Entry")
    pe1.payment_type = "Receive"
    pe1.party_type = "Customer"
    pe1.party = customer
    pe1.posting_date = today()
    pe1.paid_to = cash_acc
    pe1.paid_amount = cash_to_izge
    pe1.received_amount = cash_to_izge
    pe1.append("references", {"reference_doctype": "Sales Invoice", "reference_name": si.name, "allocated_amount": cash_to_izge})
    pe1.insert(ignore_permissions=True)
    pe1.submit()

    # 6. PE-2 (Receive): Clearing (Sanal POS) Hesabına Müşterinin Ödediği 8.000 TL
    pe2 = frappe.new_doc("Payment Entry")
    pe2.payment_type = "Receive"
    pe2.party_type = "Customer"
    pe2.party = customer
    pe2.posting_date = today()
    pe2.paid_to = clearing_acc_name
    pe2.paid_amount = supplier_cost
    pe2.received_amount = supplier_cost
    pe2.reference_no = "POS-B2B-100"
    pe2.reference_date = today()
    pe2.append("references", {"reference_doctype": "Sales Invoice", "reference_name": si.name, "allocated_amount": supplier_cost})
    pe2.insert(ignore_permissions=True)
    pe2.submit()

    # 7. PE-3 (Pay): Clearing Hesabındaki 8.000 TL'nin Tedarikçiye (Havayoluna) Aktarılması / Kapanması
    pe3 = frappe.new_doc("Payment Entry")
    pe3.payment_type = "Pay"
    pe3.party_type = "Supplier"
    pe3.party = supplier
    pe3.posting_date = today()
    pe3.paid_from = clearing_acc_name
    pe3.paid_amount = supplier_cost
    pe3.received_amount = supplier_cost
    pe3.reference_no = "POS-B2B-CLR"
    pe3.reference_date = today()
    pe3.append("references", {"reference_doctype": "Purchase Invoice", "reference_name": pi.name, "allocated_amount": supplier_cost})
    pe3.insert(ignore_permissions=True)
    pe3.submit()

    frappe.db.commit()

    # --------------------------------------------------------------------------
    # 8. Mükemmellik Testi (Assertions)
    # --------------------------------------------------------------------------
    print("\n--- Running Assertions (Clearing Model) ---")
    
    # A1: Sales Invoice Outstanding 0 olacak (Müşterinin Borcu Bitti mi?)
    si_out = frappe.db.get_value("Sales Invoice", si.name, "outstanding_amount")
    assert si_out == 0.0, f"FAIL: Sales Invoice outstanding is {si_out}"
    print("✅ P1: Müşteri Satış Faturası Açık Bakiyesi (AR) tam olarak 0.0 TL.")

    # A2: Purchase Invoice Outstanding 0 olacak (Tedarikçiye Olan Borcumuz Bitti mi?)
    pi_out = frappe.db.get_value("Purchase Invoice", pi.name, "outstanding_amount")
    assert pi_out == 0.0, f"FAIL: Purchase Invoice outstanding is {pi_out}"
    print("✅ P2: Tedarikçi Alış Faturası Açık Bakiyesi (AP) tam olarak 0.0 TL.")

    # A3: Kasa Hesabına SADECE 2000 TL girdi mi?
    cash_diff = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no=%s AND account=%s", (pe1.name, cash_acc))[0][0] or 0
    assert cash_diff == 2000.0, f"FAIL: Expected Cash 2000, got {cash_diff}"
    print("✅ P3: Merkez Kasamıza sadece kârımız/hizmet bedelimiz (+2.000 TL) yansıdı.")

    # A4: Havayolu POS Clearing hesabı günü 0.0 bakiye ile kapatıyor olmalı! (Müthiş AR/AP uyumu)
    clr_diff = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE account=%s", (clearing_acc_name,))[0][0] or 0
    assert clr_diff == 0.0, f"FAIL: Clearing Account balance mismatch! Got {clr_diff}"
    print("✅ P4: Clearing (Sanal Mahsup) Hesabının şu anki Genel Bakiyesi (Balance) 0.00 TL! (Sistem Tertemiz).")

    print("\n🎉 ALL ASSERTS PASSED. Model C (Clearing Account) B2B Payment Regression is incredibly stable.")

if __name__ == "__main__":
    run_scenario_007b()
