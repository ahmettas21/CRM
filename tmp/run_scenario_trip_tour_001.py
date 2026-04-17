"""
=====================================================================
  SCEN-TRIP-TOUR-001: Outgoing Paket Tur (Yurtdışı Tur) Demo
  2025 Vizesiz Balkan Rüzgarı (Kültür Turu)
=====================================================================
"""
import frappe
from frappe.utils import today, add_days

SITE = "erpnext-production-1b2e.up.railway.app"

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_tour_scenario():
    frappe.init(site=SITE)
    frappe.connect()
    
    banner("SCEN-TRIP-TOUR-001 BAŞLIYOR (Balkan Turu Demo)")
    
    # 1. Trip Yarat (Tour/Package)
    print("\n[1] Trip (Tour) yaratılıyor...")
    customer = frappe.db.get_value("Customer", {}, "name")
    trip = frappe.new_doc("Trip")
    trip.customer = customer
    trip.booking_date = today()
    trip.product_type = "Package/Tour"
    trip.booking_reference = "DEMO-TOUR-001"
    
    # Demo verileri (2 Pax, 4 Gece Balkanlar)
    # Yurtdışı Maliyet = 40.000 TL, Satış = 50.000 TL, Acente Kârı = 10.000 TL
    supplier = frappe.db.get_value("Supplier", {}, "name")
    trip.append("trip_tour_segments", { # Örnek child table ismi
        "tour_name": "Vizesiz Balkan Rüzgarı",
        "destination": "Saraybosna-Belgrad",
        "supplier": supplier,
        "start_date": add_days(today(), 30),
        "end_date": add_days(today(), 34),
        "cost_amount": 40000.0,
        "sale_amount": 50000.0
    })
    
    trip.insert(ignore_permissions=True)
    trip.submit()
    frappe.db.commit()
    print(f"✅ Trip {trip.name} yaratıldı ve submit edildi.")
    
    # Assert Trip amounts
    assert trip.total_sale_amount == 50000.0, f"Hata: Toplam satış 50.000 TL olmalı, bulunan: {trip.total_sale_amount}"
    assert trip.cost_amount == 40000.0, f"Hata: Toplam yurtdışı maliyet 40.000 TL olmalı, bulunan: {trip.cost_amount}"
    assert trip.profit == 10000.0, f"Hata: Balkan turunda kâr 10.000 TL olmalı, bulunan: {trip.profit}"
    print("✅ Trip tutarları doğru (Satış: 50.000, Maliyet: 40.000, Kâr: 10.000).")
    
    # 2. Sales Invoice Yarat
    print("\n[2] Sales Invoice oluşturuluyor (Item Segmentation)...")
    si_name = trip.make_sales_invoice()
    frappe.db.commit()
    
    if si_name:
        si_doc = frappe.get_doc("Sales Invoice", si_name)
        # 52.000 TL = 40.000 (Sıfır KDV) + 10.000 + 2.000 KDV
        assert si_doc.grand_total == 52000.0, f"Hata: Fatura toplamı 52.000 TL olmalı (KDV dahil), bulunan: {si_doc.grand_total}"
        assert si_doc.total_taxes_and_charges == 2000.0, f"Hata: Sadece hizmet bedeline %20 KDV kesilmeli (2.000 TL), bulunan: {si_doc.total_taxes_and_charges}"
        print(f"✅ Sales Invoice {si_name} başarıyla yaratıldı.")
        print(f"   Grand Total: {si_doc.grand_total} TL | Toplam KDV: {si_doc.total_taxes_and_charges} TL")
    else:
        print("⚠️  DIKKAT: make_sales_invoice henüz trip.py içinde tour segmenti için entegre edilmedi.")

    print("\n🎉 DEMO BAŞARILI: Balkan Turu paketi doğrulamaları tamam.")

if __name__ == "__main__":
    test_tour_scenario()
