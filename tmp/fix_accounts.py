import frappe

def fix_accounts():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    # Fix Payable Account
    payable_acc = "320.01 - SATICILAR TRY - IZGET"
    if frappe.db.exists("Account", payable_acc):
        acc = frappe.get_doc("Account", payable_acc)
        if acc.account_type != "Payable":
            acc.account_type = "Payable"
            acc.save(ignore_permissions=True)
            print(f"Fixed {payable_acc} account type to Payable.")
            
    # Fix Receivable Account
    receivable_acc = "120.01 - ALICILAR - IZGET"
    if frappe.db.exists("Account", receivable_acc):
        acc = frappe.get_doc("Account", receivable_acc)
        if acc.account_type != "Receivable":
            acc.account_type = "Receivable"
            acc.save(ignore_permissions=True)
            print(f"Fixed {receivable_acc} account type to Receivable.")
            
    frappe.db.commit()

if __name__ == "__main__":
    fix_accounts()
