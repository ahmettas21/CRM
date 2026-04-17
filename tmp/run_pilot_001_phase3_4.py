"""
=====================================================================
  PILOT-001 FAZ 3-4: No-Show Vergi İadesi + İade Ödemesi
=====================================================================
  Faz 3 — Credit Note: Orijinal SI'ya dokunmadan sadece vergi iadesi
  Faz 4 — Refund PE: İade ödemesi → Müşteri bakiye = 0
=====================================================================
  Ön Koşul: Faz 1-2 PASSED (TRIP-2026-00135, ACC-SINV-2026-00019)
  Mimari: SCEN-008 (Immutable SI + Credit Note)
=====================================================================
"""
import frappe
from frappe.utils import today

SITE = "erpnext-production-1b2e.up.railway.app"
COMPANY = "İzge Turizm"
PNR = "PILOT001"
TAX_REFUND_AMOUNT = 300.0

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def step(num, desc):
    print(f"\n  [{num}] {desc}")

def ok(msg):
    print(f"      ✅ {msg}")

def run_pilot_phase3_4():
    frappe.init(site=SITE)
    frappe.connect()

    banner("🚀 PILOT-001 FAZ 3-4: No-Show Vergi İadesi + İade Ödemesi")
    print(f"  Site: {SITE}")
    print(f"  Tarih: {today()}")

    # ═══════════════════════════════════════════════════════
    # PRE-CHECK: Faz 1-2 belgelerini bul
    # ═══════════════════════════════════════════════════════
    step("PRE", "Faz 1-2 belgelerini doğruluyorum...")

    trip_name = frappe.db.get_value("Trip", {"booking_reference": PNR}, "name")
    assert trip_name, f"PNR={PNR} ile Trip bulunamadı! Faz 1-2 koşturulmuş olmalı."
    trip = frappe.get_doc("Trip", trip_name)
    ok(f"Trip: {trip_name} (docstatus={trip.docstatus}, profit={trip.profit})")

    # Find the submitted SI linked to this trip
    si_name = trip.customer_invoice_no
    assert si_name, "Trip'te customer_invoice_no boş! Faz 1-2'de SI yaratılmış olmalı."
    si_doc = frappe.get_doc("Sales Invoice", si_name)
    assert si_doc.docstatus == 1, f"SI submitted olmalı, docstatus={si_doc.docstatus}"
    ok(f"Original SI: {si_name} (docstatus=1, grand_total={si_doc.grand_total})")

    customer_id = si_doc.customer
    ok(f"Customer: {customer_id}")

    # Check current outstanding
    current_outstanding = si_doc.outstanding_amount
    ok(f"SI Outstanding (başlangıç): {current_outstanding} TL")

    # ═══════════════════════════════════════════════════════
    # FAZ 3: NO-SHOW VERGİ İADESİ (CREDIT NOTE)
    # ═══════════════════════════════════════════════════════
    banner("FAZ 3: No-Show Vergi İadesi (Credit Note)")

    # --- Adım 3.1: Orijinal SI kontrolü ---
    step("3.1", "Orijinal SI kontrolü — CANCEL ETMİYORUZ!")
    original_si_total = si_doc.grand_total
    original_si_status = si_doc.docstatus
    ok(f"Orijinal SI Grand Total: {original_si_total} TL")
    ok(f"Orijinal SI Durumu: {'Submitted' if original_si_status == 1 else 'HATA!'}")
    assert original_si_status == 1, "Orijinal SI submitted olmalı!"

    # --- Adım 3.2: AIRPORT-TAX item kontrolü/yaratma ---
    step("3.2", "AIRPORT-TAX item kontrolü...")
    tax_item = "AIRPORT-TAX"
    if not frappe.db.exists("Item", tax_item):
        # Find item group
        ig = frappe.db.get_value("Item Group", {"name": "Hizmetler"}, "name")
        if not ig:
            ig = frappe.db.get_value("Item Group", {"is_group": 0}, "name")
        
        frappe.get_doc({
            "doctype": "Item",
            "item_code": tax_item,
            "item_name": "Havalimanı Vergisi",
            "item_group": ig,
            "is_sales_item": 1,
            "is_purchase_item": 0
        }).insert(ignore_permissions=True)
        ok(f"AIRPORT-TAX item yaratıldı (grup: {ig})")
    else:
        ok(f"AIRPORT-TAX item zaten mevcut")

    # --- Adım 3.3: Credit Note oluştur ---
    step("3.3", "Credit Note oluşturuluyor (is_return=1)...")

    # Get income account from original SI items
    income_account = None
    if si_doc.items:
        income_account = si_doc.items[0].income_account
    if not income_account:
        income_account = frappe.db.get_value("Account", {
            "root_type": "Income",
            "is_group": 0,
            "company": COMPANY
        }, "name")
    ok(f"Gelir hesabı: {income_account}")

    # Get debtors account
    debtors_account = frappe.db.get_value("Account", {
        "account_type": "Receivable",
        "company": COMPANY
    }, "name")
    ok(f"AR hesabı: {debtors_account}")

    cn = frappe.new_doc("Sales Invoice")
    cn.customer = customer_id
    cn.company = COMPANY
    cn.is_return = 1
    cn.return_against = si_name
    cn.set_posting_time = 1
    cn.posting_date = today()
    cn.due_date = today()
    cn.remarks = f"No-Show Vergi İadesi — PNR: {PNR} | Trip: {trip_name}"

    cn.append("items", {
        "item_code": tax_item,
        "item_name": "Havalimanı Vergisi İadesi",
        "qty": -1,
        "rate": TAX_REFUND_AMOUNT,
        "income_account": income_account
    })

    cn.set_missing_values()
    cn.insert(ignore_permissions=True)
    ok(f"Credit Note Draft yaratıldı: {cn.name}")

    # Assert CN details
    assert cn.is_return == 1, "is_return = 1 olmalı"
    ok(f"is_return: {cn.is_return} ✓")
    assert cn.return_against == si_name, f"return_against yanlış: {cn.return_against}"
    ok(f"return_against: {cn.return_against} ✓")
    
    # Grand total should be negative
    cn_total = cn.grand_total
    ok(f"CN Grand Total: {cn_total} TL (negatif olmalı)")

    # --- Adım 3.4: Credit Note Submit ---
    step("3.4", "Credit Note Submit ediliyor (GL kaydı oluşur)...")
    cn.submit()
    frappe.db.commit()
    ok(f"Credit Note submitted: {cn.name} (docstatus={cn.docstatus})")

    # Assert GL entries for CN
    cn_gl = frappe.get_all("GL Entry", filters={
        "voucher_no": cn.name,
        "is_cancelled": 0
    }, fields=["account", "debit", "credit"])
    
    assert len(cn_gl) >= 2, f"CN GL Entry sayısı en az 2 olmalı, gerçek: {len(cn_gl)}"
    ok(f"CN GL Entry sayısı: {len(cn_gl)} ✓")

    for gl in cn_gl:
        if gl.debit > 0:
            ok(f"CN GL Debit: {gl.account} = {gl.debit} TL (Gelir iade)")
        if gl.credit > 0:
            ok(f"CN GL Credit: {gl.account} = {gl.credit} TL (AR düşürme)")

    # Assert: Orijinal SI bozulmamış
    step("CHECK", "Orijinal SI bozulmamışlık kontrolü...")
    si_after_cn = frappe.get_doc("Sales Invoice", si_name)
    assert si_after_cn.docstatus == 1, "Orijinal SI hâlâ submitted olmalı!"
    assert si_after_cn.grand_total == original_si_total, f"Orijinal SI total değişmemeli! {si_after_cn.grand_total} vs {original_si_total}"
    ok(f"Orijinal SI: {si_name} — Grand Total={si_after_cn.grand_total} TL, Status=Submitted ✓ (BOZULMADI)")

    # Check customer AR after CN
    ar_after_cn = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as total
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, (customer_id,), as_dict=True)
    ar_balance_after_cn = ar_after_cn[0].total if ar_after_cn and ar_after_cn[0].total else 0
    ok(f"Müşteri AR bakiye (CN sonrası): {ar_balance_after_cn} TL")

    banner("FAZ 3 TAMAMLANDI ✅")
    print(f"""
    Orijinal SI:    {si_name} (Bozulmadı: {original_si_total} TL, Submitted)
    Credit Note:    {cn.name} (Grand Total: {cn_total} TL)
    CN GL Entries:  {len(cn_gl)} satır
    AR Bakiye:      {ar_balance_after_cn} TL
    """)

    # ═══════════════════════════════════════════════════════
    # FAZ 4: İADE ÖDEMESİ
    # ═══════════════════════════════════════════════════════
    banner("FAZ 4: İade Ödemesi (Refund Payment Entry)")

    # --- Adım 4.1: İade PE oluştur ---
    step("4.1", "İade Payment Entry oluşturuluyor...")

    bank_account = frappe.db.get_value("Account", {
        "account_type": ["in", ["Bank", "Cash"]],
        "is_group": 0,
        "company": COMPANY
    }, "name")
    assert bank_account, "Bank/Cash hesabı bulunamadı!"
    ok(f"Banka hesabı: {bank_account}")

    refund_pe = frappe.new_doc("Payment Entry")
    refund_pe.payment_type = "Pay"
    refund_pe.party_type = "Customer"
    refund_pe.party = customer_id
    refund_pe.company = COMPANY
    refund_pe.paid_from = bank_account
    refund_pe.paid_to = debtors_account
    refund_pe.paid_amount = TAX_REFUND_AMOUNT
    refund_pe.received_amount = TAX_REFUND_AMOUNT
    refund_pe.reference_no = "REFUND-PILOT-001"
    refund_pe.reference_date = today()
    refund_pe.remarks = f"No-Show Vergi İadesi — PNR: {PNR}"

    refund_pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": cn.name,
        "allocated_amount": -TAX_REFUND_AMOUNT
    })

    refund_pe.insert(ignore_permissions=True)
    ok(f"İade PE Draft yaratıldı: {refund_pe.name}")

    # --- Adım 4.2: İade PE Submit ---
    step("4.2", "İade PE Submit ediliyor...")
    refund_pe.submit()
    frappe.db.commit()
    ok(f"İade PE submitted: {refund_pe.name}")

    # Assert: PE GL entries
    refund_gl = frappe.get_all("GL Entry", filters={
        "voucher_no": refund_pe.name,
        "is_cancelled": 0
    }, fields=["account", "debit", "credit"])
    
    assert len(refund_gl) >= 2, f"Refund PE GL Entry sayısı en az 2 olmalı"
    ok(f"Refund PE GL Entry sayısı: {len(refund_gl)} ✓")

    for gl in refund_gl:
        if gl.debit > 0:
            ok(f"Refund GL Debit: {gl.account} = {gl.debit} TL")
        if gl.credit > 0:
            ok(f"Refund GL Credit: {gl.account} = {gl.credit} TL")

    # --- Final AR Check ---
    step("FINAL", "Müşteri final bakiye kontrolü...")

    final_ar = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as total
        FROM `tabSales Invoice`
        WHERE customer = %s AND docstatus = 1
    """, (customer_id,), as_dict=True)
    final_balance = final_ar[0].total if final_ar and final_ar[0].total else 0
    ok(f"Müşteri final AR bakiye: {final_balance} TL")

    # P&L check: net gelir = 3900 - 300 = 3600
    step("P&L", "Gelir hesabı net kontrol...")
    gl_income = frappe.db.sql("""
        SELECT SUM(credit) - SUM(debit) as net_income
        FROM `tabGL Entry`
        WHERE account = %s
        AND voucher_no IN (%s, %s)
        AND is_cancelled = 0
    """, (income_account, si_name, cn.name), as_dict=True)
    
    net_income = gl_income[0].net_income if gl_income and gl_income[0].net_income else 0
    ok(f"Net Gelir (SI + CN): {net_income} TL (Beklenen: {original_si_total - TAX_REFUND_AMOUNT})")

    banner("FAZ 4 TAMAMLANDI ✅")
    print(f"""
    Credit Note:        {cn.name}
    İade PE:            {refund_pe.name} (REFUND-PILOT-001)
    Refund GL Entries:  {len(refund_gl)} satır
    Final AR Bakiye:    {final_balance} TL
    Net Gelir (P&L):    {net_income} TL
    """)

    # ═══════════════════════════════════════════════════════
    # FİNAL RAPOR
    # ═══════════════════════════════════════════════════════
    banner("🎉 PILOT-001 FAZ 3-4: SONUÇ RAPORU")

    expected_net = original_si_total - TAX_REFUND_AMOUNT

    checks = [
        ("Orijinal SI bozulmadı", original_si_total, si_after_cn.grand_total),
        ("Orijinal SI docstatus", 1, si_after_cn.docstatus),
        ("CN Grand Total", -TAX_REFUND_AMOUNT, cn_total),
        ("CN is_return", 1, cn.is_return),
        ("CN GL Entries", "≥2", len(cn_gl)),
        ("Refund PE GL Entries", "≥2", len(refund_gl)),
        ("Müşteri Final Bakiye", 0.0, float(final_balance)),
        ("Net Gelir (P&L)", expected_net, float(net_income)),
    ]

    all_pass = True
    for label, expected, actual in checks:
        if isinstance(expected, str):
            status = "✅" if actual >= 2 else "❌"
        else:
            status = "✅" if actual == expected else "❌"
            if actual != expected:
                all_pass = False
        print(f"  {status} {label}: Beklenen={expected}, Gerçek={actual}")

    print()
    if all_pass:
        print("  🎉 TÜM KONTROLLER PASSED! Pilot-001 Faz 3-4 başarılı.")
        print("  → Pilot-001 Faz 1-4 tamamlandı. Manuel UI pilotu başlatılabilir.")
    else:
        print("  ⚠️  BAZI KONTROLLER BAŞARISIZ. İnceleme gerekli.")

    print(f"\n  Orijinal SI:   {si_name}")
    print(f"  Credit Note:   {cn.name}")
    print(f"  İade PE:       {refund_pe.name}")
    print(f"  PNR:           {PNR}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_pilot_phase3_4()
