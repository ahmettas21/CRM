# SCEN-TRIP-HOTEL-001: Yurtiçi Otel Konaklaması

## Senaryo Tanımı (BDD Formats)

**Given:**
- Ürün tipi `Hotel` olan bir Trip (1 oda, 3 gece, yurtiçi şehir, TRY).
- Otel maliyeti `KONAKLAMA-MALIYETI` item’ı ile temsil ediliyor (is_purchase_item=1).
- Müşteriye satılan `OTEL-KONAKLAMA` (KDV %10) + `HIZMET-BEDELI` (KDV %20) item’ları mevcut.

**When:**
- Trip kaydedilip submit ediliyor,
- Muhasebe ekibi Sales Invoice’ı kontrol edip (TAX-DOMESTIC-PACKAGE şablonuyla) submit ediyor,
- Payment Entry ile nakit/KK tahsilat yapılıyor.

**Then:**
- Trip’te cost / sale / kâr (profit) child tablolardan doğru şekilde aggregate edilerek hesaplanmış olmalı.
- Orijinal otel tedarikçisine doğru maliyetle bir Purchase Invoice (PI) bağlanmalı veya Draft olarak yaratılmalı.
- Sales Invoice’da konaklama satırı KDV %10, hizmet bedeli satırı KDV %20 olmalı (KDV blueprint kuralları).
- Vergi hesaplaması sonrası SI + İlgili tahsilat PE sonrası müşteri bakiyesi (outstanding) `0` olmalı.
- P&L (Gelir Tablosu)'nda: "Otel Konaklama Geliri" hesabı, "Hizmet Bedeli Geliri" hesabı ve "Otel Konaklama Gideri" hesapları doğru tutarları (KDV hariç net tutarlar) yansıtmalı.

## 🌟 Demo Case: 2025 Kapadokya Lüks Kaçamak Paketi (Boutique Cave Hotel)

**Paket Özeti:** 2026 trendlerine uygun, 2 yetişkin için butik mağara otelde 3 gece konaklama.
- **Pax:** 2 Yetişkin, 1 Oda
- **Tarihler:** Hafta sonu (3 Gece)
- **Maliyet (Gece Başı):** 8.000 TL 
- **Toplam Otel Maliyeti:** 24.000 TL
- **Acente Hizmet Bedeli (Kâr):** 6.000 TL
- **Trip Toplam Satış (KDV Hariç):** 30.000 TL

**KDV & Fatura Kırılımı (Item Segmentation):**
1. `OTEL-KONAKLAMA-YANSITMA`: 24.000 TL (Tabi olduğu KDV: **%10** = 2.400 TL)
2. `HIZMET-BEDELI`: 6.000 TL (Tabi olduğu KDV: **%20** = 1.200 TL)
- **Sales Invoice Grand Total:** 33.600 TL (Müşteriden tahsil edilecek)

## Muhasebe Hedef (GL Expected)

| Kayıt | Belge | Account | Debit | Credit |
|:---|:---|:---|:---|:---|
| Maliyet | PI | `740 - Otel Giderleri` | X | - |
| Tedarikçi Borç | PI | `320.02 - Satıcılar` | - | X + % KDV |
| Alacak | SI | `120.01 - Alıcılar` | Toplam Satış | - |
| Gelir (Otel) | SI | `600.0x - Otel Konaklama` | - | Otel Net |
| KDV (%10) | SI | `391.01 - Hesaplanan KDV (%10)`| - | Otel %10 |
| Gelir (Hizmet) | SI | `600.0y - Hizmet Bedeli` | - | Hizmet Net |
| KDV (%20) | SI | `391.02 - Hesaplanan KDV (%20)`| - | Hizmet %20 |
| Tahsilat | PE | `102.xx - Kasa/Banka` | Toplam Satış | - |
| Borç Kapatma | PE | `120.01 - Alıcılar` | - | Toplam Satış |

## Riskler & Guardrail Önerileri
- **Risk:** Trip üzerinden faturaya geçilirken Otel konaklama ve Hizmet bedelinin ayrı satırlara basılmaması.
- **Guardrail:** `trip.py` içerisindeki `_add_hotel_items_to_invoice()` fonksiyonu kesin olarak item segmentation yapmalı. Otel net satışı ve hizmet bedelini farklı item_code'lar ile geçmeli.
