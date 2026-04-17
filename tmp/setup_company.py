import frappe

def setup_company():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    company = "İzge Turizm"
    # Essential accounts
    defaults = {
        "default_income_account": "600.01 - YURT İÇİ SATIŞLAR - IZGET",
        "default_expense_account": "623.01 - DİĞR. SATŞ. MALYT. - IZGET",
        "default_payable_account": "320.01 - SATICILAR TRY - IZGET",
        "default_receivable_account": "120.01 - ALICILAR - IZGET",
        "default_inventory_account": "157.01 - DİĞR. STOK. - IZGET",
        "stock_received_but_not_billed": "320.01 - SATICILAR TRY - IZGET",
        "stock_adjustment_account": "940.01 - STOK SAYIM AYARLAMA - IZGET",
        "expenses_included_in_valuation": "623.01 - DİĞR. SATŞ. MALYT. - IZGET"
    }
    
    comp_doc = frappe.get_doc("Company", company)
    for field, acc in defaults.items():
        if frappe.db.exists("Account", acc):
            setattr(comp_doc, field, acc)
            print(f"Set {field} to {acc}")
        else:
            print(f"Warning: Account {acc} does not exist. Skipping {field}.")
            
    comp_doc.save(ignore_permissions=True)
    frappe.db.commit()
    print("Company defaults full update completed.")

if __name__ == "__main__":
    setup_company()
