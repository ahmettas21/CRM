import frappe
from frappe.utils import today

def run_scenario_007():
    """
    SCEN-BEE-007 & 014 Regression: Split Payment + İkiz POS
    Tests assigning multiple payment types (Nakit + Bank) to a single Sales Invoice.
    """
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    company = "İzge Turizm"
    customer = "Split Ödeme Müşterisi"
    
    # Dinamik Kasa Hesabı Bulma
    cash_account_list = frappe.db.sql("select name from tabAccount where is_group=0 and account_type='Cash' and company=%s limit 1", (company,))
    if cash_account_list:
        cash_account = cash_account_list[0][0]
    else:
        parent = frappe.db.sql("select name from tabAccount where account_name like '100%%' and is_group=1 and company=%s limit 1", (company,))[0][0]
        acc = frappe.new_doc("Account")
        acc.account_name = "100.01 - Merkez Kasa"
        acc.company = company
        acc.parent_account = parent
        acc.account_type = "Cash"
        acc.insert(ignore_permissions=True)
        cash_account = acc.name

    pos_account = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    
    total_sales = 10000.0
    cash_amount = 2000.0
    pos_amount = 8000.0

    print("--- Running Test: SCEN-BEE-007 & 014 (Split Payment) ---")

    if not frappe.db.exists("Customer", customer):
        c = frappe.new_doc("Customer")
        c.customer_name = customer
        c.customer_group = "Bireysel"
        c.territory = "Turkey"
        c.insert(ignore_permissions=True)

    # 1. Müşteriye Fatura Kes (10.000 TL)
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = today()
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": total_sales})
    si.insert(ignore_permissions=True)
    si.submit()

    # 2. Çoklu Tahsilat (Split Payment Entry using multi-line logic in Accounts/References if possible)
    # Native ERPNext usually suggests two PE documents for two payment modes/accounts, but let's test ERPNext's multi Payment Entry.
    
    # PE-1: Nakit (2.000 TL)
    pe1 = frappe.new_doc("Payment Entry")
    pe1.payment_type = "Receive"
    pe1.party_type = "Customer"
    pe1.party = customer
    pe1.posting_date = today()
    pe1.paid_to = cash_account
    pe1.paid_amount = cash_amount
    pe1.received_amount = cash_amount
    pe1.append("references", {
        "reference_doctype": "Sales Invoice", 
        "reference_name": si.name, 
        "allocated_amount": cash_amount
    })
    pe1.insert(ignore_permissions=True)
    pe1.submit()
    
    # PE-2: POS/Kredi Kartı (8.000 TL)
    pe2 = frappe.new_doc("Payment Entry")
    pe2.payment_type = "Receive"
    pe2.party_type = "Customer"
    pe2.party = customer
    pe2.posting_date = today()
    pe2.paid_to = pos_account
    pe2.paid_amount = pos_amount
    pe2.received_amount = pos_amount
    pe2.reference_no = "SPLIT-POS-9923"
    pe2.reference_date = today()
    pe2.append("references", {
        "reference_doctype": "Sales Invoice", 
        "reference_name": si.name, 
        "allocated_amount": pos_amount
    })
    pe2.insert(ignore_permissions=True)
    pe2.submit()
    
    frappe.db.commit()

    # 3. Assertions (Regressions)
    print("\n--- Running Assertions ---")
    
    # Assert 1: Outstanding Amount on Invoice must be exactly 0
    outstanding = frappe.db.get_value("Sales Invoice", si.name, "outstanding_amount")
    assert outstanding == 0.0, f"ASSERT FAIL: Invoice outstanding should be 0, but is {outstanding}"
    print("✅ P1: Tek Faturanın Bakiyesi (Outstanding) 0.0 olarak başarıyla kapandı.")

    # Assert 2: Nakit Kasa Bakiyesi (Cash Account) kontrolü
    cash_gl_diff = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no=%s AND account=%s", (pe1.name, cash_account))[0][0] or 0
    assert cash_gl_diff == cash_amount, f"ASSERT FAIL: Cash mismatch. Expected {cash_amount}, Got {cash_gl_diff}"
    print("✅ P2: Nakit (Kasa) hesabına tam olarak 2.000 TL giriş atandı.")

    # Assert 3: Banka POS Bakiyesi kontrolü
    pos_gl_diff = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no=%s AND account=%s", (pe2.name, pos_account))[0][0] or 0
    assert pos_gl_diff == pos_amount, f"ASSERT FAIL: POS mismatch. Expected {pos_amount}, Got {pos_gl_diff}"
    print("✅ P3: Banka (POS) hesabına tam olarak 8.000 TL giriş atandı.")

    print("🎉 ALL ASSERTS PASSED. Regression SCEN-BEE-007 (Split Payment) is stable.")

if __name__ == "__main__":
    run_scenario_007()
