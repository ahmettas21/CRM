import frappe

def add_cc_custom_fields():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    
    fields = [
        {
            "fieldname": "cc_section_break",
            "fieldtype": "Section Break",
            "label": "Kredi Kartı Detayları",
            "insert_after": "account_type"
        },
        {
            "fieldname": "is_credit_card",
            "fieldtype": "Check",
            "label": "Kredi Kartı mı?",
            "insert_after": "cc_section_break"
        },
        {
            "fieldname": "cc_billing_day",
            "fieldtype": "Int",
            "label": "Hesap Kesim Günü (1-31)",
            "insert_after": "is_credit_card",
            "depends_on": "eval:doc.is_credit_card==1"
        },
        {
            "fieldname": "cc_grace_period",
            "fieldtype": "Int",
            "label": "Son Ödeme Gün Farkı",
            "insert_after": "cc_billing_day",
            "depends_on": "eval:doc.is_credit_card==1"
        },
        {
            "fieldname": "cc_min_payment_percent",
            "fieldtype": "Percent",
            "label": "Asgari Ödeme Oranı (%)",
            "insert_after": "cc_grace_period",
            "depends_on": "eval:doc.is_credit_card==1"
        },
        {
            "fieldname": "cc_monthly_interest_rate",
            "fieldtype": "Percent",
            "label": "Aylık Akdi Faiz Oranı (%)",
            "insert_after": "cc_min_payment_percent",
            "depends_on": "eval:doc.is_credit_card==1"
        },
        {
            "fieldname": "cc_limit",
            "fieldtype": "Currency",
            "label": "Kart Limiti",
            "insert_after": "cc_monthly_interest_rate",
            "depends_on": "eval:doc.is_credit_card==1"
        }
    ]
    
    for f in fields:
        if not frappe.db.exists("Custom Field", {"dt": "Account", "fieldname": f["fieldname"]}):
            df = frappe.new_doc("Custom Field")
            df.dt = "Account"
            df.update(f)
            df.insert(ignore_permissions=True)
            print(f"Custom Field Created: {f['label']}")
        else:
            print(f"Custom Field already exists: {f['label']}")
            
    frappe.db.commit()
    print("\n--- Account Custom Fields Update Completed ---")

if __name__ == "__main__":
    add_cc_custom_fields()
