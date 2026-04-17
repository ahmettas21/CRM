import frappe
from frappe.utils import today, add_months

def run_scenario_015():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- SCEN-BEE-015: ADM (Agency Debit Memo) Management ---")
    company = "İzge Turizm"
    supplier = "Lufthansa Airlines"
    customer = "ADM Affected Passenger"
    trip_id = "TRIP-ADM-999"
    
    # 1. Setup Master Data
    # Guardrail: Fetch dynamic groups
    sup_group = frappe.db.sql("select name from `tabSupplier Group` limit 1")[0][0]
    cust_group = frappe.db.sql("select name from `tabCustomer Group` limit 1")[0][0]
    itg_list = frappe.db.sql("select name from `tabItem Group` limit 1")
    group_name = itg_list[0][0] if itg_list else "All Item Groups"

    if not frappe.db.exists("Supplier", supplier):
        frappe.get_doc({"doctype": "Supplier", "supplier_name": supplier, "supplier_group": sup_group}).insert(ignore_permissions=True)
    if not frappe.db.exists("Customer", customer):
        frappe.get_doc({"doctype": "Customer", "customer_name": customer, "customer_group": cust_group}).insert(ignore_permissions=True)
    
    # Item Fix: Must be both Purchase and Sales
    if not frappe.db.exists("Item", "UCAK-BILETI"):
        frappe.get_doc({
            "doctype": "Item", 
            "item_code": "UCAK-BILETI", 
            "item_group": group_name, 
            "is_stock_item": 0,
            "is_purchase_item": 1,
            "is_sales_item": 1
        }).insert(ignore_permissions=True)
    else:
        # Mevcutsa bayrağı güncelle
        frappe.db.set_value("Item", "UCAK-BILETI", {"is_purchase_item": 1, "is_sales_item": 1})
    
    # Cost Center setup for Trip Profitability Tracking
    cost_center = f"{trip_id} - IZGET"
    if not frappe.db.exists("Cost Center", cost_center):
        parent_cc = frappe.db.get_value("Cost Center", {"is_group": 1, "company": company}, "name")
        frappe.get_doc({
            "doctype": "Cost Center", 
            "cost_center_name": trip_id, 
            "parent_cost_center": parent_cc, 
            "company": company
        }).insert(ignore_permissions=True)

    # 2. Original Transaction (Dönem Başı)
    # Sales Invoice: 10.000 TL
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = add_months(today(), -1) # Geçen ay kesildi
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": 10000.0, "cost_center": cost_center})
    si.insert(ignore_permissions=True)
    si.submit()
    print(f"✅ Original Sales Invoice (Closed Month): {si.name} | Revenue: 10,000 TL")

    # Original Purchase Invoice (Maliyet): 9.000 TL
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.posting_date = add_months(today(), -1)
    pi.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": 9000.0, "cost_center": cost_center})
    pi.insert(ignore_permissions=True)
    pi.submit()
    print(f"✅ Original Cost (Purchase Invoice): {pi.name} | Base Cost: 9,000 TL")

    # Initial Profit: 1,000 TL
    
    # 3. THE ADM (Yeni Dönemde Gelen Borç Dekontu)
    adm_amount = 500.0
    adm_pi = frappe.new_doc("Purchase Invoice")
    adm_pi.supplier = supplier
    adm_pi.posting_date = today() # Bu ay geldi
    adm_pi.remarks = f"ADM for {si.name} - Under-collected fare"
    # ADM kalemini 'UCAK-BILETI' üzerinden ama sadece fiyat farkı olarak giriyoruz
    adm_pi.append("items", {
        "item_code": "UCAK-BILETI", 
        "qty": 1, 
        "rate": adm_amount, 
        "cost_center": cost_center
    })
    
    try:
        adm_pi.insert(ignore_permissions=True)
        adm_pi.submit()
        print(f"✅ ADM (Purchase Invoice) Created in Current Month: {adm_pi.name} | Extra Cost: {adm_amount} TL")
    except Exception as e:
        print("HATA: ADM Purchase Invoice Failure:", str(e))
        return

    frappe.db.commit()

    # 4. ASSERTIONS
    print("\n--- Running ADM Profitability Assertions ---")
    
    # Check Original SI remains untouched
    si_total = frappe.db.get_value("Sales Invoice", si.name, "grand_total")
    assert si_total == 10000.0, f"FAIL: Original Sales Invoice modified! Total is {si_total}"
    print("✅ P1: Original Sales Invoice remains Immutable (Audit Safe).")

    # Check Total Cost in GL for the Cost Center
    # Expense accounts usually start with 6 or 7. Let's find the specific GL entries for this CC.
    total_cost = frappe.db.sql("""
        SELECT SUM(debit) - SUM(credit) 
        FROM `tabGL Entry` 
        WHERE cost_center = %s 
        AND voucher_type = 'Purchase Invoice'
    """, (cost_center,))[0][0] or 0
    
    expected_total_cost = 9000.0 + 500.0
    assert float(total_cost) == expected_total_cost, f"FAIL: Total Cost mismatch! Expected {expected_total_cost}, Got {total_cost}"
    print(f"✅ P2: Cost Center '{trip_id}' accurately reflects cumulative cost ({total_cost} TL).")

    # Verify P&L Impact (Net Profit for this CC)
    total_rev = frappe.db.sql("SELECT SUM(credit) - SUM(debit) FROM `tabGL Entry` WHERE cost_center = %s AND voucher_type = 'Sales Invoice'", (cost_center,))[0][0] or 0
    net_profit = float(total_rev) - float(total_cost)
    assert net_profit == 500.0, f"FAIL: Net Profit mismatch! Expected 500.0, Got {net_profit}"
    print(f"✅ P3: Net Profit for Trip successfully adjusted to {net_profit} TL without altering history.")

    print("🎉 ALL ASSERTS PASSED. ADM Scenario is valid.")

if __name__ == "__main__":
    run_scenario_015()
