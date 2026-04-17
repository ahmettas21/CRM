import frappe

def setup_fx_alt_yapi():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    company = "İzge Turizm"
    print("--- Setup: Company FX Configuration ---")

    # 1. Company Exchange Gain/Loss Account Setup
    comp_doc = frappe.get_doc("Company", company)
    if not comp_doc.exchange_gain_loss_account:
        egl_acc_list = frappe.db.sql("select name from tabAccount where account_name like '%%Exchange%%' and company=%s limit 1", (company,))
        if egl_acc_list:
            egl_acc = egl_acc_list[0][0]
        else:
            parent_exp = frappe.db.sql("select name from tabAccount where is_group=1 and root_type='Expense' and company=%s limit 1", (company,))[0][0]
            new_egl = frappe.new_doc("Account")
            new_egl.account_name = "656 - Kur Farkı Zararları"
            new_egl.company = company
            new_egl.parent_account = parent_exp
            new_egl.insert(ignore_permissions=True)
            egl_acc = new_egl.name
        
        comp_doc.exchange_gain_loss_account = egl_acc
        comp_doc.save(ignore_permissions=True)
        print(f"Company FX Account Linked: {egl_acc}")

    # 2. Multi-Currency Supplier Account Setup (320.02 EUR)
    eur_acc_name = "320.02 - SATICILAR EUR - IZGET"
    if not frappe.db.exists("Account", eur_acc_name):
        try:
            parent_list = frappe.db.sql("select name from tabAccount where is_group=1 and account_type='Payable' and company=%s limit 1", (company,))
            if not parent_list:
                parent_list = frappe.db.sql("select name from tabAccount where is_group=1 and root_type='Liability' and company=%s limit 1", (company,))
            
            acc = frappe.new_doc("Account")
            acc.account_name = "320.02 - SATICILAR EUR"
            acc.company = company
            acc.parent_account = parent_list[0][0]
            acc.account_type = "Payable"
            acc.account_currency = "EUR"
            acc.insert(ignore_permissions=True)
            print(f"EUR Payable Account Created: {acc.name}")
        except Exception as e:
            print("Account Creation Error:", e)

    frappe.db.commit()
    print("Setup Complete.")

if __name__ == "__main__":
    setup_fx_alt_yapi()
