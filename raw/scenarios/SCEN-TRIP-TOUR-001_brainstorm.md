# SCEN-TRIP-TOUR-001: Outgoing Paket Tur (Yurtdışı Tur) - KDV Matrah İndirimi

## Senaryo Tanımı (BDD Formats)

**Given:**
- Ürün tipi `Package/Tour` olan, yurtdışı destinasyonlu bir Trip.
- Yurtdışı otel/ulaşım/operatör maliyetleri (Exempt/KDV 0) `KONAKLAMA-MALIYETI` ve/veya `BILET-MALIYETI` item’ları ile temsil ediliyor.
- Müşteriye satılan paket bedeli, item içinde "Yurtdışı Maliyet Yansıtması" + "Acente Hizmet Bedeli/Kâr Marjı" içeriyor.

**When:**
- Trip kaydedilip submit ediliyor,
- Trip üzerinden Sales Invoice (TAX-OUTGOING-PACKAGE şablonuyla) oluşturuluyor,
- Outgoing KDV politikasına göre Item Segmentation ile vergilendiriliyor (Maliyet = %0, Hizmet = %20),
- Payment Entry ile tahsilat yapılıyor.

**Then:**
- KDV matrahı “Toplam Tutar – Yurtdışı Maliyetler” formülüne eşdeğer şekilde, yalnızca `Service Fee` (Hizmet Bedeli) satırına %20 KDV uygulanarak hesaplanmış olmalı.
- P&L’de yurtdışı maliyetler "KDV’siz Yurtdışı Gider", müşteriye yansıtılan kısmı "KDV'siz Yurtdışı Gelir (Geçiş)" veya doğrudan maliyet sıfırlaması şeklinde, asıl kâr ise "Hizmet Bedeli Geliri" olarak KDV'li görülmeli.
- Faturada (SI) Grand Total beklenen brüt satış rakamıyla birebir eşleşmeli, tüm GL ve Outstanding kontrolleri PASS olmalı.

## 🌟 Demo Case: 2025 Vizesiz Balkan Rüzgarı (Outgoing Kültür Turu)

**Paket Özeti:** Artan Schengen vize krizine karşı 2025-2026'nın en popüler çözümü; 2 kişi için uçak+otel dahil paket tur.
- **Pax:** 2 Yetişkin
- **Rota:** IST -> SJJ (Saraybosna) / 4 Gece 5 Gün
- **Yurtdışı Uçak Maliyeti:** 15.000 TL (Exempt / %0 KDV)
- **Yurtdışı Operatör (Otel+Transfer) Maliyeti:** 25.000 TL (Exempt / %0 KDV)
- **Toplam Tur Maliyeti:** 40.000 TL
- **Acente Kârı / Hizmet Bedeli:** 10.000 TL
- **Trip Toplam Satış (KDV Hariç):** 50.000 TL

**KDV & Fatura Kırılımı (Item Segmentation ile Matrah İndirimi):**
1. `YURTDISI-MALIYET-YANSITMA`: 40.000 TL (Tabi olduğu KDV: **%0 / İstisna**)
2. `HIZMET-BEDELI`: 10.000 TL (Tabi olduğu KDV: **%20** = 2.000 TL)
- **Sales Invoice Grand Total:** 52.000 TL (Normalde tümüne %20 kesilse 60.000 TL olacaktı; doğru kurguyla 52.000 TL fatura kesildi).

## Muhasebe Hedef (GL Expected)

| Kayıt | Belge | Account | Debit | Credit | Açıklama |
|:---|:---|:---|:---|:---|:---|
| Yurtdışı Gider | PI | `740.xx - Yurtdışı Tur Gid.` | 1000 | - | KDV'siz |
| Tedarikçi Borç | PI | `320.xx - Yurtdışı Satıcı` | - | 1000 | KDV'siz |
| Müşteri Alacak | SI | `120.01 - Alıcılar` | 1240 | - | Toplam = 1000 + 200 + 40 KDV |
| Yurtdışı Yansıtma| SI | `601.xx - Yurtdışı Tur Geliri`| - | 1000 | Exempt / %0 KDV |
| Hizmet Bedeli | SI | `600.xx - Paket Tur Hizmet Gelirli`| - | 200 | Vergiye tabi matrah |
| KDV (%20) | SI | `391.02 - Hesaplanan KDV (%20)`| - | 40 | KDV (Sadece hizmete) |

## Riskler & Guardrail Önerileri
- **Risk:** Kullanıcının (veya sistemin) yanlış KDV şablonunu seçmesi ve yurtdışı maliyete de KDV hesaplanması.
- **Guardrail:** `trip.py` controller'ı "Package/Tour" ve "International" rotasında **zorunlu** olarak exempt or mixed template seçecek mantık barındırmalı.
- **Risk:** Kullanıcının toplam paket bedelini tek satıra girmesi, böylece KDV indirim matrahının kaybolması.
- **UI Guardrail:** Trip formunda, "Tour Total Sale" alanı yerine "Tour Cost" ve "Agency Fee" alanları ayrı tutulmalı, SI oluşurken bu ikisi farklı Item satırlarına bölünmelidir.
