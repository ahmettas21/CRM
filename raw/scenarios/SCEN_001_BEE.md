# 🧪 [SCEN-BEE-001] Bee Akademi KOLAY BİLET Test Senaryosu

Bu doküman, Bee Akademi KOLAY BİLET müşterisi için yapılan uçak bileti satışının teknik detaylarını ve beklenen sonuçlarını içerir.

## 📋 Senaryo Detayları

- **Test ID:** SCEN-BEE-001
- **Tarih:** 2026-04-17
- **Aşama:** Planlama
- **Hedef:** Çoklu yolcu maliyeti, kâr hesaplama ve 30 günlük vade otomasyonu doğrulaması.

## 📥 Girdi Verileri (Payload)

### Trip Header
- `customer`: "Bee Akademi KOLAY BİLET"
- `payment_method`: "Credit (Vadeli)"
- `payment_terms_template`: "30 Günlük Vade"
- `product_type`: "Flight"

### Flight Segments (Child Table)
| Yolcu | Tip | Maliyet (Supplier) | Satış (Customer) | Tedarikçi |
| :--- | :--- | :--- | :--- | :--- |
| Yolcu 1 | Yetki | 5.000 TL | 6.800 TL | THY |
| Yolcu 2 | Yetki | 5.000 TL | 6.800 TL | THY |
| Yolcu 3 | Yetki | 5.000 TL | 6.800 TL | THY |
| Yolcu 4 | Çocuk | 4.000 TL | 5.600 TL | THY |

## 🏁 Beklenen Sonuçlar (Expected Results)

1. **Trip Totals:**
   - `total_cost`: 19.000 TL
   - `total_sale_amount`: 26.000 TL
   - `profit`: 7.000 TL
2. **Accounting Automation:**
   - **Sales Invoice:** 26.000 TL tutarında, 30 gün vadeli taslak fatura.
   - **Purchase Invoice:** "THY" adına 19.000 TL tutarında taslak alış faturası.
3. **Cari Durum:**
   - Bee Akademi bakiyesi 26.000 TL borçlanmalı.
   - THY bakiyesi 19.000 TL alacaklanmalı.

## 📊 Test Çıktıları (Actual Results)
*Henüz test icra edilmedi.*

> 🔗 **Kavramsal Özet:** [wiki/scenarios/index.md](../../wiki/scenarios/index.md)
