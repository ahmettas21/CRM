import frappe
from frappe.utils import today

def run_scenario_006():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    print("--- Scenario SCEN-BEE-006 (Operator Commission / Direct Pay) ---")
    
    company = "İzge Turizm"
    customer = "Doğrudan Müşteri"
    supplier = "MNG TURİZM"  # Example operator
    date = today()
    
    # 0. Setup Customer & Supplier if not exist
    if not frappe.db.exists("Customer", customer):
        c = frappe.new_doc("Customer")
        c.customer_name = customer
        c.customer_group = "Bireysel"
        c.territory = "Turkey"
        c.insert(ignore_permissions=True)
        
    if not frappe.db.exists("Supplier", supplier):
        s = frappe.new_doc("Supplier")
        s.supplier_name = supplier
        s.supplier_group = "Yerel"
        s.insert(ignore_permissions=True)
    
    frappe.db.commit()
    
    sale_amount = 10000
    cost_amount = 9000
    
    print(f"Creating Operator Ticket -> Sale: {sale_amount}, Cost(Net): {cost_amount}")
    
    # 1. Sales Invoice (Customer Debt)
    si = frappe.new_doc("Sales Invoice")
    si.customer = customer
    si.posting_date = date
    si.append("items", {"item_code": "UCAK-BILETI", "qty": 1, "rate": sale_amount})
    si.insert(ignore_permissions=True)
    si.submit()
    print(f"Sales Invoice {si.name} Submitted (Cust Debt = {sale_amount})")
    
    # 2. Purchase Invoice (Our Debt to Supplier)
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.posting_date = date
    pi.append("items", {"item_code": "BILET-MALIYETI", "qty": 1, "rate": cost_amount})
    pi.insert(ignore_permissions=True)
    pi.submit()
    print(f"Purchase Invoice {pi.name} Submitted (Sup Credit = {cost_amount})")
    
    # 3. THE MAGIC: Journal Entry (Virman) -> Customer directly paid the supplier
    # This means we debit the supplier (they got money) and credit the customer (they paid the money)
    # Total transferred from Customer's CC straight to Supplier's POS: 10000 TL
    
    cust_account = si.debit_to
    sup_account = pi.credit_to
    
    je = frappe.new_doc("Journal Entry")
    je.voucher_type = "Journal Entry"
    je.company = company
    je.posting_date = date
    je.user_remark = "Operatör Komisyonlu: Müşteri Kartıyla Direkt Tedarikçiye Ödeme"
    
    # Credit the Customer (Reduces custom debt, links to SI)
    je.append("accounts", {
        "account": cust_account,
        "party_type": "Customer",
        "party": customer,
        "credit_in_account_currency": sale_amount,
        "reference_type": "Sales Invoice",
        "reference_name": si.name
    })
    
    # Debit the Supplier: 9000 to cover Invoice, 1000 as Commission Claim (Unallocated/Advance)
    je.append("accounts", {
        "account": sup_account,
        "party_type": "Supplier",
        "party": supplier,
        "debit_in_account_currency": cost_amount, # 9000 pays the invoice
        "reference_type": "Purchase Invoice",
        "reference_name": pi.name
    })
    
    je.append("accounts", {
        "account": sup_account,
        "party_type": "Supplier",
        "party": supplier,
        "debit_in_account_currency": sale_amount - cost_amount, # 1000 sits as credit/commission claim
    })
    
    je.insert(ignore_permissions=True)
    je.submit()
    print(f"Journal Entry (Mahsup) {je.name} Submitted: Transferred {sale_amount} from Cust->Sup")
    
    frappe.db.commit()
    
    # 4. Final Verification
    print("\n--- Accounting Integration Proof (Operator Commission) ---")
    cust_bal = frappe.db.sql("SELECT SUM(debit)-SUM(credit) FROM `tabGL Entry` WHERE account=%s AND party=%s AND is_cancelled=0", (cust_account, customer))[0][0] or 0
    sup_bal = frappe.db.sql("SELECT SUM(credit)-SUM(debit) FROM `tabGL Entry` WHERE account=%s AND party=%s AND is_cancelled=0", (sup_account, supplier))[0][0] or 0
    # Note for sup_bal: positive means we owe them. Negative means they owe us!
    
    print(f"Customer ('{customer}') Final Balance: {cust_bal} TL (Expected: 0)")
    print(f"Supplier ('{supplier}') Balance: {sup_bal} TL (Expected: -1000 -> They owe us our commission!)")
    
    if cust_bal == 0 and sup_bal == (cost_amount - sale_amount):
        print("✅ COMMISSION SYNC SUCCESS: Customer closed, Supplier owes us commission.")
    else:
        print("❌ SYNC FAILED")

if __name__ == "__main__":
    run_scenario_006()
