import frappe

def fix_payment_with_specific_cc():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    company = "İzge Turizm"
    specific_cc_account = "102.01.001 - İŞ BANKASI 4846 - IZGET"
    
    print(f"--- Updating Payment to Specific Card: {specific_cc_account} ---")
    
    # 1. Create the specific account
    if not frappe.db.exists("Account", specific_cc_account):
        acc = frappe.new_doc("Account")
        acc.account_name = "İŞ BANKASI 4846"
        acc.account_number = "102.01.001"
        acc.parent_account = "102 - BANKALAR - IZGET"
        acc.company = company
        acc.account_type = "Bank"
        acc.insert(ignore_permissions=True)
        print(f"Account Created: {specific_cc_account}")
    else:
        print(f"Account already exists: {specific_cc_account}")
    
    # 2. Cancel the old Payment Entry
    old_pe_name = "ACC-PAY-2026-00001"
    if frappe.db.exists("Payment Entry", old_pe_name):
        pe = frappe.get_doc("Payment Entry", old_pe_name)
        if pe.docstatus == 1:
            pe.cancel()
            print(f"Old Payment Entry {old_pe_name} Cancelled.")
    
    # 3. Create NEW Payment Entry with specific CC
    pi_name = "ACC-PINV-2026-00002"
    pi = frappe.get_doc("Purchase Invoice", pi_name)
    
    new_pe = frappe.new_doc("Payment Entry")
    new_pe.payment_type = "Pay"
    new_pe.party_type = "Supplier"
    new_pe.party = "Pegasus Hava Yolları"
    new_pe.paid_from = specific_cc_account
    new_pe.paid_from_account_currency = "TRY"
    new_pe.paid_to = pi.credit_to
    new_pe.paid_to_account_currency = "TRY"
    new_pe.paid_amount = 4000
    new_pe.received_amount = 4000
    new_pe.source_exchange_rate = 1.0
    new_pe.target_exchange_rate = 1.0
    new_pe.reference_no = "CC-AUTH-4846-9999"
    new_pe.reference_date = frappe.utils.today()
    
    new_pe.append("references", {
        "reference_doctype": "Purchase Invoice",
        "reference_name": pi_name,
        "total_amount": 4000,
        "outstanding_amount": 4000,
        "allocated_amount": 4000
    })
    
    new_pe.insert(ignore_permissions=True)
    new_pe.submit()
    print(f"New Payment Entry {new_pe.name} Created via İş Bankası 4846.")
    
    frappe.db.commit()
    print("\n--- Card Update Completed. Ready for Void test. ---")

if __name__ == "__main__":
    fix_payment_with_specific_cc()
