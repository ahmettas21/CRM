import frappe
from frappe.utils import today

def run_scenario_016():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-BEE-016: Chargeback (Ters İbraz) ---")
    company = "İzge Turizm"
    customer = "Chargeback Passenger"
    
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
        
    itg_list = frappe.db.sql("select name from `tabItem Group` limit 1")
    group_name = itg_list[0][0] if itg_list else "All Item Groups"
    if not frappe.db.exists("Item", "CHARGEBACK-TICKET"):
        frappe.get_doc({"doctype": "Item", "item_code": "CHARGEBACK-TICKET", "item_group": group_name, "is_stock_item": 0}).insert(ignore_permissions=True)
        
    base_fare = 10000.0
    chargeback_fee = 250.0  # Banka bize para çaldırdığımız için ceza kesti
    total_bank_deduction = base_fare + chargeback_fee
    
    # Hesapları Topla
    cus_acc = frappe.db.sql("select name from tabAccount where account_type='Receivable' and company=%s limit 1", (company,))[0][0]
    bank_acc = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    
    # Guardrail: Account name maskesi ('7%%') yerine evrensel tiplere güven.
    exp_acc_list = frappe.db.sql("select name from tabAccount where account_type='Expense Account' and is_group=0 and company=%s limit 1", (company,))
    if exp_acc_list:
        expense_acc = exp_acc_list[0][0]
    else:
        exp_acc_list2 = frappe.db.sql("select name from tabAccount where root_type='Expense' and is_group=0 and company=%s limit 1", (company,))
        if exp_acc_list2:
           expense_acc = exp_acc_list2[0][0]
        else:
           raise Exception("HATA: Sistemde hiçbir Gider (Expense) hesabı bulunamadı!")

    # -------------------------------------------------------------
    # Step 1: Normal Sales Invoice (Döneminde kesildi)
    # -------------------------------------------------------------
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = today()
    si.append("items", {"item_code": "CHARGEBACK-TICKET", "qty": 1, "rate": base_fare})
    si.insert(ignore_permissions=True)
    si.submit()
    print(f"✅ Original Invoice Created: {si.name} | Total: {base_fare}")
    
    # -------------------------------------------------------------
    # Step 2: Normal Payment Entry (Müşteri ödedi, SI kapandı sandık)
    # -------------------------------------------------------------
    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = customer
    pe.posting_date = today()
    pe.paid_to = bank_acc
    pe.paid_amount = base_fare
    pe.received_amount = base_fare
    pe.reference_no = "POS-INITIAL"
    pe.reference_date = today()
    pe.append("references", {"reference_doctype": "Sales Invoice", "reference_name": si.name, "allocated_amount": base_fare})
    pe.insert(ignore_permissions=True)
    pe.submit()
    print(f"✅ Payment Received: {pe.name} | Outstanding became 0 TL")
    
    # -------------------------------------------------------------
    # Step 3: THE CHARGEBACK (Banka 2 ay sonra parayı zorla geri çekti)
    # Orijinal Faturayı asla bozmuyoruz, müşteri borcunu Journal ile yeniden hortlatıyoruz
    # -------------------------------------------------------------
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.posting_date = today()
    je.company = company
    
    # Satır 1: Müşteriyi borçlandır (+10000) - Müşteri Dispute/Mahkemelik oldu
    je.append("accounts", {
        "account": cus_acc,
        "party_type": "Customer",
        "party": customer,
        "debit_in_account_currency": base_fare
    })
    
    # Satır 2: Banka Ceza Giderini P&L'e yükle (+250)
    je.append("accounts", {
        "account": expense_acc,
        "debit_in_account_currency": chargeback_fee
    })
    
    # Satır 3: Bankadan Para Çıktı (-10250)
    je.append("accounts", {
        "account": bank_acc,
        "credit_in_account_currency": total_bank_deduction,
        "user_remark": "Chargeback Deduction from ISSUER Bank"
    })
    
    je.user_remark = "Chargeback Rekreasyonu & Banka Cezası"
    je.insert(ignore_permissions=True)
    je.submit()
    
    print(f"✅ Chargeback Journal Entry Confirmed: {je.name} (-10250 TL Bankadan zorla düşüldü)")
    frappe.db.commit()
    
    # -------------------------------------------------------------
    # ASSERTIONS (Denetçinin gözünden Mizan)
    # -------------------------------------------------------------
    print("\n--- Running Chargeback GL Assertions ---")
    
    si_out = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE account=%s AND party=%s AND is_cancelled=0", (cus_acc, customer))[0][0] or 0
    assert float(si_out) == base_fare, f"FAIL: Customer owes {si_out}, Expected {base_fare}"
    print(f"✅ P1: Customer successfully re-debited! AR report reflects new debt of {base_fare} TL perfectly.")
    
    exp_out = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no=%s AND account=%s", (je.name, expense_acc))[0][0] or 0
    assert float(exp_out) == chargeback_fee, f"FAIL: Expense account {exp_out}, Expected {chargeback_fee}"
    print(f"✅ P2: Bank Charge penalty ({chargeback_fee} TL) correctly written off directly to P&L Expense account.")
    
    print("🎉 ALL ASSERTS PASSED. Chargeback Architecture is Immutable and Stable!")

if __name__ == "__main__":
    run_scenario_016()
