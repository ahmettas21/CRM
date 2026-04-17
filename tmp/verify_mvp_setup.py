import frappe

def verify_mvp_setup():
    """
    MVP Setup Doğrulama: 13 zorunlu ayarın canlı sistemdeki durumunu kontrol eder.
    Her madde için PASS/FAIL + detay döndürür.
    """
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    print("=" * 60)
    print("🚀 MVP SETUP DOĞRULAMA — Pilot-001 Hazırlık Kontrolü")
    print("=" * 60)

    results = []

    # MVP #1: Company
    company = frappe.db.get_value("Company", {"name": ["like", "%zge%"]}, ["name", "default_currency"], as_dict=True)
    if not company:
        company = frappe.db.get_value("Company", {}, ["name", "default_currency"], as_dict=True)
    
    if company:
        results.append(("MVP #1", "Company", "PASS", f"{company.name}"))
        # MVP #2: Currency
        if company.default_currency == "TRY":
            results.append(("MVP #2", "Default Currency = TRY", "PASS", company.default_currency))
        else:
            results.append(("MVP #2", "Default Currency = TRY", "FAIL", f"Mevcut: {company.default_currency}"))
        
        company_name = company.name
    else:
        results.append(("MVP #1", "Company", "FAIL", "Hiç Company kaydı yok!"))
        results.append(("MVP #2", "Default Currency = TRY", "FAIL", "Company yok"))
        company_name = None

    # MVP #3: Debtors (Receivable)
    debtors = frappe.db.get_value("Account", {
        "account_type": "Receivable",
        "company": company_name
    }, "name") if company_name else None
    results.append(("MVP #3", "Debtors (Receivable) hesabı", 
                    "PASS" if debtors else "FAIL",
                    debtors or "Receivable tipinde hesap yok"))

    # MVP #4: Creditors (Payable)
    creditors = frappe.db.get_value("Account", {
        "account_type": "Payable",
        "company": company_name
    }, "name") if company_name else None
    results.append(("MVP #4", "Creditors (Payable) hesabı",
                    "PASS" if creditors else "FAIL",
                    creditors or "Payable tipinde hesap yok"))

    # MVP #5: Income account
    income = frappe.db.get_value("Account", {
        "root_type": "Income",
        "is_group": 0,
        "company": company_name
    }, "name") if company_name else None
    results.append(("MVP #5", "Gelir hesabı (Income)",
                    "PASS" if income else "FAIL",
                    income or "Income tipinde hesap yok"))

    # MVP #6: Expense account
    expense = frappe.db.get_value("Account", {
        "root_type": "Expense",
        "is_group": 0,
        "company": company_name
    }, "name") if company_name else None
    results.append(("MVP #6", "Gider hesabı (Expense)",
                    "PASS" if expense else "FAIL",
                    expense or "Expense tipinde hesap yok"))

    # MVP #7: Cash or Bank account
    cash_or_bank = frappe.db.get_value("Account", {
        "account_type": ["in", ["Cash", "Bank"]],
        "is_group": 0,
        "company": company_name
    }, "name") if company_name else None
    results.append(("MVP #7", "Nakit Kasa veya Banka hesabı",
                    "PASS" if cash_or_bank else "FAIL",
                    cash_or_bank or "Cash/Bank tipinde hesap yok"))

    # MVP #8: Item Groups (Hizmetler + Maliyetler)
    ig_hizmetler = frappe.db.exists("Item Group", "Hizmetler")
    ig_maliyetler = frappe.db.exists("Item Group", "Maliyetler")
    if ig_hizmetler and ig_maliyetler:
        results.append(("MVP #8", "Item Groups (Hizmetler + Maliyetler)", "PASS", "Her ikisi de mevcut"))
    else:
        missing = []
        if not ig_hizmetler: missing.append("Hizmetler")
        if not ig_maliyetler: missing.append("Maliyetler")
        results.append(("MVP #8", "Item Groups", "FAIL", f"Eksik: {', '.join(missing)}"))

    # MVP #9: Customer Group (Bireysel)
    cg = frappe.db.exists("Customer Group", "Bireysel")
    if not cg:
        cg = frappe.db.exists("Customer Group", "Individual")
    results.append(("MVP #9", "Customer Group (Bireysel/Individual)",
                    "PASS" if cg else "FAIL",
                    cg or "Bireysel/Individual grubu yok"))

    # MVP #10: At least 1 Supplier
    supplier_count = frappe.db.count("Supplier")
    results.append(("MVP #10", "En az 1 Supplier",
                    "PASS" if supplier_count > 0 else "FAIL",
                    f"{supplier_count} adet Supplier mevcut"))

    # MVP #11: At least 1 Airport
    airport_count = frappe.db.count("Airport")
    results.append(("MVP #11", "En az 1 Airport",
                    "PASS" if airport_count > 0 else "FAIL",
                    f"{airport_count} adet Airport mevcut"))

    # MVP #12: At least 1 Airline
    airline_count = frappe.db.count("Airline")
    results.append(("MVP #12", "En az 1 Airline",
                    "PASS" if airline_count > 0 else "FAIL",
                    f"{airline_count} adet Airline mevcut"))

    # MVP #13: izge_travel app
    installed_apps = frappe.get_installed_apps()
    results.append(("MVP #13", "izge_travel app kurulu",
                    "PASS" if "izge_travel" in installed_apps else "FAIL",
                    f"Apps: {', '.join(installed_apps)}"))

    # PRINT RESULTS
    print()
    passed = 0
    failed = 0
    for mvp_id, label, status, detail in results:
        icon = "✅" if status == "PASS" else "❌"
        print(f"  {icon} {mvp_id}: {label}")
        print(f"        → {detail}")
        if status == "PASS":
            passed += 1
        else:
            failed += 1

    print()
    print("=" * 60)
    print(f"📊 SONUÇ: {passed}/13 PASS, {failed}/13 FAIL")
    if failed == 0:
        print("🎉 TÜM MVP AYARLARI HAZIR! Pilot-001 başlatılabilir.")
    else:
        print(f"⚠️  {failed} ayar eksik. Pilot öncesi düzeltilmeli.")
    print("=" * 60)

if __name__ == "__main__":
    verify_mvp_setup()
