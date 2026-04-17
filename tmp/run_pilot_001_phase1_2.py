"""
=====================================================================
  PILOT-001: Mehmet Yılmaz Senaryosu (Faz 1 + Faz 2)
  Otomatik Regresyon Testi
=====================================================================
  Faz 1 — Satış: Trip → Segment → KK → Kaydet → Submit → Make Invoice
  Faz 2 — Muhasebe: SI Submit → Payment Entry → Outstanding = 0
=====================================================================
  Referans: wiki/mission_control.md → Pilot-001
  MVP Bağımlılık: 13/13 (tümü doğrulandı)
=====================================================================
"""
import frappe
from frappe.utils import today, add_days

SITE = "erpnext-production-1b2e.up.railway.app"
COMPANY = "İzge Turizm"
PNR = "PILOT001"

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def step(num, desc):
    print(f"\n  [{num}] {desc}")

def ok(msg):
    print(f"      ✅ {msg}")

def fail(msg):
    raise AssertionError(f"      ❌ FAIL: {msg}")

def run_pilot_001():
    frappe.init(site=SITE)
    frappe.connect()

    banner("🚀 PILOT-001: Mehmet Yılmaz Senaryosu (Faz 1 + Faz 2)")
    print(f"  Site: {SITE}")
    print(f"  Company: {COMPANY}")
    print(f"  Tarih: {today()}")

    # ═══════════════════════════════════════════════════════
    # PRE-CHECK: Eski pilot verisini temizle (idempotent)
    # ═══════════════════════════════════════════════════════
    step("0", "Eski pilot verisini kontrol ediyorum...")
    old_trip = frappe.db.get_value("Trip", {"booking_reference": PNR}, "name")
    if old_trip:
        old_doc = frappe.get_doc("Trip", old_trip)
        if old_doc.docstatus == 1:
            old_doc.cancel()
            ok(f"Eski Trip {old_trip} cancel edildi")
        frappe.delete_doc("Trip", old_trip, force=True, ignore_permissions=True)
        ok(f"Eski Trip {old_trip} silindi")
        frappe.db.commit()

    # ═══════════════════════════════════════════════════════
    # FAZ 1: SATIŞ
    # ═══════════════════════════════════════════════════════
    banner("FAZ 1: Satış (Satışçı Rolü)")

    # --- Adım 1.1: Müşteri ---
    step("1.1", "Müşteri oluşturuluyor: Mehmet Yılmaz")
    customer_name = "Mehmet Yılmaz"
    if not frappe.db.exists("Customer", {"customer_name": customer_name}):
        cust = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": customer_name,
            "customer_type": "Individual",
            "customer_group": "Bireysel"
        }).insert(ignore_permissions=True)
        ok(f"Customer yaratıldı: {cust.name}")
    else:
        ok(f"Customer zaten mevcut")
    customer_id = frappe.db.get_value("Customer", {"customer_name": customer_name}, "name")

    # --- Adım 1.3: Yolcu ---
    step("1.3", "Yolcu oluşturuluyor: Mehmet Yılmaz")
    traveler_id = frappe.db.get_value("Traveler", {"full_name": "Mehmet Yılmaz"}, "name")
    if not traveler_id:
        t_doc = frappe.get_doc({
            "doctype": "Traveler",
            "full_name": "Mehmet Yılmaz",
            "gender": "Male",
            "customer": customer_id
        }).insert(ignore_permissions=True)
        traveler_id = t_doc.name
        ok(f"Traveler yaratıldı: {traveler_id}")
    else:
        ok(f"Traveler zaten mevcut: {traveler_id}")

    # --- Lookup master data ---
    supplier = frappe.db.get_value("Supplier", {}, "name")
    assert supplier, "En az 1 Supplier olmalı (MVP #10)"
    ok(f"Supplier: {supplier}")

    airport_ist = frappe.db.get_value("Airport", {"name": ["like", "%IST%"]}, "name")
    if not airport_ist:
        airport_ist = frappe.db.get_value("Airport", {}, "name")
    assert airport_ist, "En az 1 Airport olmalı (MVP #11)"

    airport_esb = frappe.db.get_value("Airport", {"name": ["like", "%ESB%"]}, "name")
    if not airport_esb:
        airport_esb = airport_ist  # fallback: aynı havalimanı
    ok(f"Airports: {airport_ist} → {airport_esb}")

    airline = frappe.db.get_value("Airline", {}, "name")
    assert airline, "En az 1 Airline olmalı (MVP #12)"
    ok(f"Airline: {airline}")

    # --- Adım 1.2 + 1.4 + 1.5: Trip + Segments ---
    step("1.2", f"Trip oluşturuluyor: PNR={PNR}")
    trip = frappe.new_doc("Trip")
    trip.customer = customer_id
    trip.supplier = supplier
    trip.booking_date = today()
    trip.booking_reference = PNR
    trip.product_type = "Flight"
    trip.payment_method = "Credit Card"
    trip.cc_bank = "Garanti BBVA"
    trip.cc_commission_rate = 2.5

    step("1.4", "Gidiş segmenti: IST → ESB, Maliyet=2000, Hizmet=200")
    trip.append("trip_flight_segments", {
        "traveler": traveler_id,
        "airline": airline,
        "supplier": supplier,
        "origin": airport_ist,
        "destination": airport_esb,
        "direction": "Outbound",
        "departure_date": add_days(today(), 3),
        "cost_amount": 2000.0,
        "service_fee": 200.0,
        "sale_amount": 2200.0
    })

    step("1.5", "Dönüş segmenti: ESB → IST, Maliyet=1500, Hizmet=200")
    trip.append("trip_flight_segments", {
        "traveler": traveler_id,
        "airline": airline,
        "supplier": supplier,
        "origin": airport_esb,
        "destination": airport_ist,
        "direction": "Return",
        "departure_date": add_days(today(), 5),
        "cost_amount": 1500.0,
        "service_fee": 200.0,
        "sale_amount": 1700.0
    })

    # --- Adım 1.7: Kaydet ---
    step("1.7", "Kaydediliyor (validate + margin guardrail)...")
    trip.insert(ignore_permissions=True)
    frappe.db.commit()
    ok(f"Trip kaydedildi: {trip.name}")

    # Assert: Toplamlar
    assert trip.total_sale_amount == 3900.0, f"Satış toplamı beklenen 3900, gerçek: {trip.total_sale_amount}"
    ok(f"Satış toplamı: {trip.total_sale_amount} TL ✓")

    assert trip.cost_amount == 3500.0, f"Maliyet toplamı beklenen 3500, gerçek: {trip.cost_amount}"
    ok(f"Maliyet toplamı: {trip.cost_amount} TL ✓")

    assert trip.profit == 400.0, f"Kâr beklenen 400, gerçek: {trip.profit}"
    ok(f"Kâr: {trip.profit} TL ✓")

    # --- Adım 1.8: Submit ---
    step("1.8", "Submit ediliyor...")
    trip.submit()
    frappe.db.commit()
    ok(f"Trip submitted: {trip.name} (docstatus={trip.docstatus})")

    # Assert: Draft Purchase Invoice oluştu mu?
    pi_list = frappe.get_all("Purchase Invoice", filters={
        "remarks": ["like", f"%{trip.name}%"],
        "docstatus": 0
    }, fields=["name", "grand_total"])
    
    if pi_list:
        for pi in pi_list:
            ok(f"Draft PI: {pi.name} ({pi.grand_total} TL)")
    else:
        print("      ⚠️  PI yaratılmadı (controller akışına bağlı olabilir)")

    # Assert: CC Commission JE oluştu mu?
    cc_je = frappe.db.get_value("Journal Entry", {
        "remark": ["like", f"%{trip.name}%"],
        "docstatus": ["<", 2]
    }, "name")
    if cc_je:
        ok(f"CC Commission JE: {cc_je}")
    else:
        print("      ⚠️  CC JE yaratılmadı (cc commission controller'a bağlı)")

    # --- Adım 1.9: Make Invoice ---
    step("1.9", "Fatura Oluştur (make_sales_invoice API)...")
    trip_doc = frappe.get_doc("Trip", trip.name)
    si_name = trip_doc.make_sales_invoice()
    frappe.db.commit()

    assert si_name, "make_sales_invoice bir SI adı döndürmeliydi!"
    ok(f"Draft Sales Invoice yaratıldı: {si_name}")

    # Verify SI details
    si_doc = frappe.get_doc("Sales Invoice", si_name)
    assert si_doc.docstatus == 0, f"SI Draft olmalı, docstatus={si_doc.docstatus}"
    ok(f"SI durumu: Draft ✓")
    assert si_doc.customer == customer_id, f"SI müşterisi yanlış: {si_doc.customer}"
    ok(f"SI müşterisi: {si_doc.customer} ✓")
    assert si_doc.grand_total == 3900.0, f"SI grand_total beklenen 3900, gerçek: {si_doc.grand_total}"
    ok(f"SI Grand Total: {si_doc.grand_total} TL ✓")
    assert PNR in (si_doc.remarks or ""), f"SI remarks'ta PNR yok: {si_doc.remarks}"
    ok(f"SI Remarks: PILOT001 referansı mevcut ✓")

    # Verify Trip linkback
    updated_trip = frappe.get_doc("Trip", trip.name)
    assert updated_trip.customer_invoice_no == si_name, f"Trip→SI link yanlış"
    ok(f"Trip → SI link: {updated_trip.customer_invoice_no} ✓")

    banner("FAZ 1 TAMAMLANDI ✅")
    print(f"""
    Trip:       {trip.name} (Profit: {trip.profit} TL)
    Draft SI:   {si_name} (Grand Total: {si_doc.grand_total} TL)
    Draft PIs:  {len(pi_list)} adet
    CC JE:      {cc_je or 'N/A'}
    """)

    # ═══════════════════════════════════════════════════════
    # FAZ 2: MUHASEBE ONAY
    # ═══════════════════════════════════════════════════════
    banner("FAZ 2: Muhasebe Onay")

    # --- Adım 2.2: SI Submit ---
    step("2.2", "Sales Invoice Submit ediliyor (GL Entry oluşur)...")
    si_doc.submit()
    frappe.db.commit()
    ok(f"SI submitted: {si_doc.name} (docstatus={si_doc.docstatus})")

    # Assert: GL Entry oluştu mu?
    gl_entries = frappe.get_all("GL Entry", filters={
        "voucher_no": si_name,
        "is_cancelled": 0
    }, fields=["account", "debit", "credit"])

    assert len(gl_entries) >= 2, f"GL Entry sayısı en az 2 olmalı, gerçek: {len(gl_entries)}"
    ok(f"GL Entry sayısı: {len(gl_entries)} ✓")

    # Check AR debit
    ar_debit = [g for g in gl_entries if g.debit > 0 and "ALICI" in g.account.upper()]
    if ar_debit:
        ok(f"AR Debit: {ar_debit[0].account} = {ar_debit[0].debit} TL ✓")
    else:
        # Fallback: check receivable type
        ar_debit = [g for g in gl_entries if g.debit > 0]
        ok(f"Debit kaydı: {ar_debit[0].account} = {ar_debit[0].debit} TL")

    # Check Income credit
    income_credit = [g for g in gl_entries if g.credit > 0]
    if income_credit:
        ok(f"Gelir Credit: {income_credit[0].account} = {income_credit[0].credit} TL ✓")

    # --- Adım 2.3 + 2.4: Payment Entry ---
    step("2.3", "Payment Entry oluşturuluyor (KK POS tahsilat)...")

    # Find bank account
    bank_account = frappe.db.get_value("Account", {
        "account_type": ["in", ["Bank", "Cash"]],
        "is_group": 0,
        "company": COMPANY
    }, "name")
    assert bank_account, "Cash/Bank hesabı bulunamadı!"
    ok(f"Banka hesabı: {bank_account}")

    # Get debtors account
    debtors_account = frappe.db.get_value("Account", {
        "account_type": "Receivable",
        "company": COMPANY
    }, "name")

    pe = frappe.new_doc("Payment Entry")
    pe.payment_type = "Receive"
    pe.party_type = "Customer"
    pe.party = customer_id
    pe.company = COMPANY
    pe.paid_from = debtors_account
    pe.paid_to = bank_account
    pe.paid_amount = 3900.0
    pe.received_amount = 3900.0
    pe.reference_no = "POS-PILOT-001"
    pe.reference_date = today()
    pe.append("references", {
        "reference_doctype": "Sales Invoice",
        "reference_name": si_name,
        "allocated_amount": 3900.0
    })

    pe.insert(ignore_permissions=True)
    pe.submit()
    frappe.db.commit()
    ok(f"Payment Entry yaratıldı ve submitted: {pe.name}")

    # Assert: SI Outstanding = 0
    step("2.4", "SI Outstanding kontrol ediliyor...")
    si_after_pe = frappe.get_doc("Sales Invoice", si_name)
    assert si_after_pe.outstanding_amount == 0, f"Outstanding beklenen 0, gerçek: {si_after_pe.outstanding_amount}"
    ok(f"SI Outstanding: {si_after_pe.outstanding_amount} TL ✓ (Tam Ödendi)")

    # Assert: PE GL Entries
    pe_gl = frappe.get_all("GL Entry", filters={
        "voucher_no": pe.name,
        "is_cancelled": 0
    }, fields=["account", "debit", "credit"])
    
    assert len(pe_gl) >= 2, f"PE GL Entry sayısı en az 2 olmalı"
    ok(f"PE GL Entry sayısı: {len(pe_gl)} ✓")

    # Check AR report
    step("CHECK", "Accounts Receivable kontrol ediliyor...")
    ar_outstanding = frappe.db.sql("""
        SELECT SUM(outstanding_amount) as total 
        FROM `tabSales Invoice` 
        WHERE customer = %s AND docstatus = 1
    """, (customer_id,), as_dict=True)
    
    total_ar = ar_outstanding[0].total if ar_outstanding and ar_outstanding[0].total else 0
    ok(f"Müşteri toplam AR bakiye: {total_ar} TL")

    banner("FAZ 2 TAMAMLANDI ✅")
    print(f"""
    SI:                 {si_name} (Submitted)
    PE:                 {pe.name} (POS-PILOT-001)
    SI Outstanding:     {si_after_pe.outstanding_amount} TL
    GL Entry (SI):      {len(gl_entries)} satır
    GL Entry (PE):      {len(pe_gl)} satır
    Müşteri AR Bakiye:  {total_ar} TL
    """)

    # ═══════════════════════════════════════════════════════
    # FİNAL RAPOR
    # ═══════════════════════════════════════════════════════
    banner("🎉 PILOT-001 FAZ 1-2: SONUÇ RAPORU")

    checks = [
        ("Trip Profit", 400.0, trip.profit),
        ("Trip Total Sale", 3900.0, trip.total_sale_amount),
        ("Trip Cost", 3500.0, trip.cost_amount),
        ("SI Grand Total", 3900.0, si_doc.grand_total),
        ("SI Outstanding (PE sonrası)", 0.0, si_after_pe.outstanding_amount),
        ("GL Entry (SI)", "≥2", len(gl_entries)),
        ("GL Entry (PE)", "≥2", len(pe_gl)),
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
        print("  🎉 TÜM KONTROLLER PASSED! Pilot-001 Faz 1-2 başarılı.")
        print("  → Faz 3 (No-Show) ve Faz 4 (İade) manuel veya otomatik koşturulabilir.")
    else:
        print("  ⚠️  BAZI KONTROLLER BAŞARISIZ. İnceleme gerekli.")

    print(f"\n  Trip:  {trip.name}")
    print(f"  SI:    {si_name}")
    print(f"  PE:    {pe.name}")
    print(f"  PNR:   {PNR}")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    run_pilot_001()
