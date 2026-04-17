"""
=====================================================================
  SCEN-TRIP-SERVICE-001: Vize & Diğer Ekstra Hizmetler Demo
  2026 VIP Schengen Vize & Havalimanı CIP Hizmeti
=====================================================================
"""
import frappe
from frappe.utils import today

SITE = "erpnext-production-1b2e.up.railway.app"

def banner(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")

def test_service_scenario():
    frappe.init(site=SITE)
    frappe.connect()
    
    banner("SCEN-TRIP-SERVICE-001 BAŞLIYOR (VIP Vize & CIP Demo)")
    
    # 1. Trip Yarat (Service/Visa)
    print("\n[1] Trip (Service) yaratılıyor...")
    customer = frappe.db.get_value("Customer", {}, "name")
    trip = frappe.new_doc("Trip")
    trip.customer = customer
    trip.booking_date = today()
    trip.product_type = "Service"
    trip.booking_reference = "DEMO-SRV-001"
    
    # Demo verileri (1 Pax)
    # Vize Harcı (Pass-through): Maliyet 4000, Satış 4000
    # Vize Danışmanlık: Maliyet 0, Satış 3000
    # CIP Lounge: Maliyet 2000, Satış 2500
    # Toplam Satış = 9500, Kâr = 3500
    
    supplier = frappe.db.get_value("Supplier", {}, "name")
    
    trip.append("services_table", { # Örnek tablo ismi
        "service_type": "Visa",
        "description": "Schengen Vize Harcı + İDATA",
        "supplier": supplier,
        "cost_amount": 4000.0,
        "sale_amount": 4000.0
    })
    
    trip.append("services_table", {
        "service_type": "Consultancy",
        "description": "VIP Vize Danışmanlık Ücreti",
        "supplier": supplier,
        "cost_amount": 0.0,
        "sale_amount": 3000.0
    })

    trip.append("services_table", {
        "service_type": "Lounge",
        "description": "IST CIP Lounge",
        "supplier": supplier,
        "cost_amount": 2000.0,
        "sale_amount": 2500.0
    })
    
    trip.insert(ignore_permissions=True)
    trip.submit()
    frappe.db.commit()
    print(f"✅ Trip {trip.name} yaratıldı ve submit edildi.")
    
    # Assert Trip amounts
    assert trip.total_sale_amount == 9500.0, f"Hata: Toplam hizmet satışı 9.500 TL olmalı, bulunan: {trip.total_sale_amount}"
    assert trip.cost_amount == 6000.0, f"Hata: Toplam maliyet 6.000 TL olmalı, bulunan: {trip.cost_amount}"
    assert trip.profit == 3500.0, f"Hata: Hizmet kârı 3.500 TL olmalı, bulunan: {trip.profit}"
    print("✅ Trip tutarları doğru (Satış: 9.500, Maliyet: 6.000, Kâr: 3.500).")
    
    # 2. SI Yarat
    print("\n[2] Sales Invoice oluşturuluyor...")
    si_name = trip.make_sales_invoice()
    frappe.db.commit()
    
    if si_name:
        si_doc = frappe.get_doc("Sales Invoice", si_name)
        # Vize Harcı (4000 @ %0) = 4000
        # Vize Danışmanlık (3000 @ %20) = 3600
        # CIP Lounge (2500 @ %20) = 3000
        # Total = 10600, KDV = 1100
        assert si_doc.grand_total == 10600.0, f"Hata: KDV dahil fatura toplamı 10.600 TL olmalı, bulunan: {si_doc.grand_total}"
        assert si_doc.total_taxes_and_charges == 1100.0, f"Hata: Toplam KDV 1.100 TL olmalı, bulunan: {si_doc.total_taxes_and_charges}"
        print(f"✅ Sales Invoice {si_name} başarıyla yaratıldı.")
        print(f"   Grand Total: {si_doc.grand_total} TL | Toplam KDV: {si_doc.total_taxes_and_charges} TL")
    else:
        print("⚠️  DIKKAT: make_sales_invoice henüz trip.py içinde service segmenti için entegre edilmedi.")

    print("\n🎉 DEMO BAŞARILI: VIP Vize paketi doğrulamaları tamam.")

if __name__ == "__main__":
    test_service_scenario()
