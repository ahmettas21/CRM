import frappe
from frappe.utils import today

def run_scenario_012():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-BEE-012: Kısmi Kullanım (Pro-Rata İade) ---")
    
    company = "İzge Turizm"
    customer = "Pro-Rata Passenger"
    
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": "Bireysel"}).insert(ignore_permissions=True)
        
    itg_list = frappe.db.sql("select name from `tabItem Group` limit 1")
    group_name = itg_list[0][0] if itg_list else "All Item Groups"
    for i_code in ["FLIGHT-OUTBOUND", "FLIGHT-INBOUND", "SERVICE-FEE"]:
        if not frappe.db.exists("Item", i_code):
            frappe.get_doc({"doctype": "Item", "item_code": i_code, "item_group": group_name, "is_stock_item": 0}).insert(ignore_permissions=True)
            
    # Gidiş: 6000, Dönüş: 4000. Service Fee: 1000.
    base_outbound = 6000.0
    base_inbound = 4000.0
    total_ticket = base_outbound + base_inbound
    service_fee = 1000.0
    # Original Total = 11.000 TL.
    
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = today()
    # Segmentleri şeffaflık için tek tek Invoice Item yapıyoruz.
    si.append("items", {"item_code": "FLIGHT-OUTBOUND", "qty": 1, "rate": base_outbound})
    si.append("items", {"item_code": "FLIGHT-INBOUND", "qty": 1, "rate": base_inbound})
    si.append("items", {"item_code": "SERVICE-FEE", "qty": 1, "rate": service_fee})
    
    si.insert(ignore_permissions=True)
    si.submit()
    print(f"✅ Original Invoice: {si.name} | Total: {si.grand_total} TL")
    
    # ----------------------------------------------------
    # Pro-Rata İade Matematiği (Sadece Dönüş iptal oluyor)
    # ----------------------------------------------------
    # İade Oranı (Refund Ratio) = 4000 / (6000+4000) = %40
    refund_ratio = base_inbound / total_ticket
    
    cn = frappe.new_doc("Sales Invoice")
    cn.is_return = 1
    cn.return_against = si.name
    cn.customer = customer
    cn.posting_date = today()
    # 1. 4000 TL Dönüş segmentinin iadesi
    cn.append("items", {"item_code": "FLIGHT-INBOUND", "qty": -1, "rate": base_inbound})
    # 2. Service Fee komisyonunun orantılı (%40) iadesi, kalan %60 kâr bizimdir.
    cn.append("items", {"item_code": "SERVICE-FEE", "qty": -1, "rate": service_fee * refund_ratio})
    cn.insert(ignore_permissions=True)
    cn.submit()
    
    print(f"✅ Credit Note (Pro-Rata): {cn.name} | Oran: %{refund_ratio*100} | Total: {cn.grand_total} (Beklenen: -4400.0 TL)")
    
    frappe.db.commit()
    
    # ----------------------------------------------------
    # ASSERTIONS (SOP-5 ile doğrulanan GL Mizan Sorgusu)
    # ----------------------------------------------------
    print("\n--- Running Pro-Rata GL Assertions ---")
    cus_acc = frappe.db.sql("select name from tabAccount where account_type='Receivable' and company=%s limit 1", (company,))[0][0]
    si_out = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE voucher_no IN (%s, %s) AND account=%s", (si.name, cn.name, cus_acc))[0][0] or 0
    
    expected_balance = 11000.0 - 4400.0
    
    assert float(si_out) == expected_balance, f"FAIL: Expected Balance {expected_balance}, Got {si_out}"
    print(f"✅ P1: Customer Ledger Net Balance exactly {expected_balance} TL. Pro-rata calculation flawlessly matched.")
    print("🎉 ALL ASSERTS PASSED.")

if __name__ == "__main__":
    run_scenario_012()
