import frappe
from frappe.utils import today

def run_scenario_008():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-BEE-008: No-Show & Partial (Tax-Only) Refund ---")
    
    company = "İzge Turizm"
    customer = "No-Show Passenger"
    
    base_fare = 9200.0
    airport_tax = 800.0
    total_invoice = base_fare + airport_tax
    
    # Setup Customer
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
    
    # Setup Items
    # Guardrail: Never use hardcoded item groups, fetch from DB.
    itg_list = frappe.db.sql("select name from `tabItem Group` limit 1")
    group_name = itg_list[0][0] if itg_list else "All Item Groups"
    
    for i_code in ["UCAK-BILETI", "AIRPORT-TAX"]:
        if not frappe.db.exists("Item", i_code):
            frappe.get_doc({"doctype": "Item", "item_code": i_code, "item_group": group_name, "is_stock_item": 0}).insert(ignore_permissions=True)
            
    income_account = frappe.db.get_value("Company", company, "default_income_account") or "600.01 - Yurt Içi Satışlar - IZGET"
    
    # 1. Original SI (Base + Tax)
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = today()
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": base_fare})
    si.append("items", {"item_code": "AIRPORT-TAX", "qty": 1, "rate": airport_tax})
    
    try:
        si.insert(ignore_permissions=True)
        si.submit()
        print(f"✅ Original Sales Invoice Created: {si.name} | Total: {si.grand_total}")
    except Exception as e:
        print("HATA: Original Invoice Creation:", str(e))
        return

    # 2. Credit Note (Return ONLY Airport Tax = 800 TL)
    cn = frappe.new_doc("Sales Invoice")
    cn.is_return = 1
    cn.return_against = si.name
    cn.customer = customer
    cn.posting_date = today()
    
    # IMPORTANT: Credit note uses negative quantities for returned items.
    cn.append("items", {
        "item_code": "AIRPORT-TAX", 
        "qty": -1, 
        "rate": airport_tax
    })
    
    try:
        cn.insert(ignore_permissions=True)
        cn.submit()
        print(f"✅ Credit Note Created: {cn.name} (Sadece Vergi İadesi={airport_tax} TL)")
    except Exception as e:
        print("HATA: Credit Note Creation Failed:", str(e))
        return
        
    frappe.db.commit()
    
    # 3. Assertions (Regressions)
    print("\n--- Running Assertions (No-Show Ledger Immutability) ---")
    
    # Guardrail: Doküman Outstanding'ine Tükürme, Ledger'ı Oku!
    cus_acc = frappe.db.sql("select name from tabAccount where account_type='Receivable' and company=%s limit 1", (company,))[0][0]
    
    # Müşterinin bu 2 belge sonrası Net Borcu:
    si_out = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no IN (%s, %s) AND account=%s", (si.name, cn.name, cus_acc))[0][0] or 0
    
    assert float(si_out) == base_fare, f"FAIL: Customer GL Balance changed unexpectedly to {si_out}. Expected {base_fare}"
    print(f"✅ P1: Customer Ledger Net Balance perfectly matched to the unflown Base Fare ({base_fare} TL). Tax liability removed securely.")
    
    print("🎉 ALL ASSERTS PASSED. No-Show & Tax-Only Refund works perfectly under ERPNext Rules.")

if __name__ == "__main__":
    run_scenario_008()
