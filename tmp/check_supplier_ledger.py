import frappe

def check_supplier_movements():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    suppliers = ["Pegasus Hava Yolları", "THY - Türk Hava Yolları"]
    
    print("--- Supplier General Ledger Check ---")
    for supplier_name in suppliers:
        # Get GL Entries for the supplier
        entries = frappe.get_all("GL Entry", filters={
            "party_type": "Supplier",
            "party": supplier_name
        }, fields=["name", "voucher_no", "debit", "credit", "remarks"])
        
        print(f"\nSupplier: {supplier_name}")
        if not entries:
            print("  -> Hareket Yok (Cari Tertemiz)")
        else:
            for e in entries:
                print(f"  - Belge: {e.voucher_no} | Borç: {e.debit} | Alacak: {e.credit} | Not: {e.remarks}")

if __name__ == "__main__":
    check_supplier_movements()
