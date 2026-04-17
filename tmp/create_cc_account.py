import frappe

def create_cc_account():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    company = "İzge Turizm"
    cc_account = "102.01 - ŞİRKET KREDİ KARTI - IZGET"
    
    if not frappe.db.exists("Account", cc_account):
        acc = frappe.new_doc("Account")
        acc.account_name = "ŞİRKET KREDİ KARTI"
        acc.account_number = "102.01"
        acc.parent_account = "102 - BANKALAR - IZGET"
        acc.company = company
        acc.account_type = "Bank"
        acc.insert(ignore_permissions=True)
        print(f"Account Created: {cc_account}")
    else:
        print(f"Account already exists: {cc_account}")
    
    frappe.db.commit()

if __name__ == "__main__":
    create_cc_account()
