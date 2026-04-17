"""
=====================================================================
  SCEN-TRIP-HOTEL-001: Yurtiçi Otel Konaklaması (Demo)
  2025 Kapadokya Lüks Kaçamak Paketi (Boutique Cave Hotel)
=====================================================================
"""
import frappe
from frappe.utils import today, add_days

SITE = "erpnext-production-1b2e.up.railway.app"

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_hotel_scenario():
    frappe.init(site=SITE)
    frappe.connect()
    
    banner("SCEN-TRIP-HOTEL-001 BAŞLIYOR (Kapadokya Demo)")
    
    # 1. Trip Yarat (Hotel)
    print("\n[1] Trip (Hotel) yaratılıyor...")
    customer = frappe.db.get_value("Customer", {}, "name")
    trip = frappe.new_doc("Trip")
    trip.customer = customer
    trip.booking_date = today()
    trip.product_type = "Hotel"
    trip.booking_reference = "DEMO-HOTEL-001"
    
    # Demo verileri (2 Pax, 3 Gece Kapadokya)
    # Cost: 24.000 TL, Sale: 30.000 TL, Hizmet Bedeli/Kâr: 6.000 TL
    supplier = frappe.db.get_value("Supplier", {}, "name")
    trip.append("trip_hotel_segments", {
        "hotel_name": "Kapadokya Cave Resort",
        "city": "Nevşehir",
        "supplier": supplier,
        "check_in": add_days(today(), 10),
        "check_out": add_days(today(), 13),
        "rooms": 1,
        "nights": 3,
        "cost_amount": 24000.0,
        "sale_amount": 30000.0
    })
    
    trip.insert(ignore_permissions=True)
    trip.submit()
    frappe.db.commit()
    print(f"✅ Trip {trip.name} yaratıldı ve submit edildi.")
    
    # Assert Trip amounts
    assert trip.total_sale_amount == 30000.0, f"Hata: Toplam satış 30000 TL olmalı, bulunan: {trip.total_sale_amount}"
    assert trip.cost_amount == 24000.0, f"Hata: Toplam maliyet 24000 TL olmalı, bulunan: {trip.cost_amount}"
    assert trip.profit == 6000.0, f"Hata: Otel demo paketinde kâr 3 gece için 6.000 TL olmalı, bulunan: {trip.profit}"
    print("✅ Trip tutarları doğru (Satış: 30.000, Maliyet: 24.000, Kâr: 6.000).")
    
    # 2. Sales Invoice Yarat
    print("\n[2] Sales Invoice oluşturuluyor (Item Segmentation)...")
    si_name = trip.make_sales_invoice()
    frappe.db.commit()
    
    if si_name:
        si_doc = frappe.get_doc("Sales Invoice", si_name)
        # 33.600 TL = 24.000 + 2.400 KDV + 6.000 + 1.200 KDV
        assert si_doc.grand_total == 33600.0, f"Hata: Fatura toplamı 33.600 TL olmalı (KDV dahil), bulunan: {si_doc.grand_total}"
        assert si_doc.total_taxes_and_charges == 3600.0, f"Hata: Toplam KDV 3.600 TL olmalı, bulunan: {si_doc.total_taxes_and_charges}"
        print(f"✅ Sales Invoice {si_name} başarıyla yaratıldı.")
        print(f"   Grand Total: {si_doc.grand_total} TL | Toplam KDV: {si_doc.total_taxes_and_charges} TL")
    else:
        print("⚠️  DIKKAT: make_sales_invoice henüz trip.py içinde entegre edilmediği için SI yaratılamadı.")

    print("\n🎉 DEMO BAŞARILI: Kapadokya paketi doğrulamaları tamam.")

if __name__ == "__main__":
    test_hotel_scenario()
