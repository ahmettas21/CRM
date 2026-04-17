import frappe

def check_groups():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Groups ---")
    cg = frappe.get_all("Customer Group", limit=5)
    print("Customer Groups:", [g.name for g in cg])
    
    tr = frappe.get_all("Territory", limit=5)
    print("Territories:", [t.name for t in tr])
    
    sg = frappe.get_all("Supplier Group", limit=5)
    print("Supplier Groups:", [s.name for s in sg])
    
    ig = frappe.get_all("Item Group", filters={"is_group": 1})
    print("Item Groups (Groups):", [i.name for i in ig])

    travelers = frappe.get_all("Traveler", fields=["name", "full_name"])
    for t in travelers:
        print(f"Traveler: {t.name} | {t.full_name}")

if __name__ == "__main__":
    check_groups()
