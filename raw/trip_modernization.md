# ✈️ Seyahat Modülü Modernizasyonu: Teknik Mimari (v1.0)

**[RULE-Z1X2Y]** - Bu döküman, Izge Travel ERPNext sistemindeki `Trip` modülünün grup rezervasyonları ve karmaşık finansal işlemler için nasıl modernize edildiğini belgeler.

## 1. Mimari Değişiklikler

### 1.1. DocType Güncellemeleri
- **Trip (Ana):** Finansal özet alanları (`total_cost`, `total_service`, `total_sale`) eklendi.
- **Trip Ticket (Çocuk):** 
    - `commission_rate` (Percent): Yüzdesel komisyon girişi.
    - `payment_mode`: Cari, Müşteri Kredi Kartı, Şirket Kredi Kartı seçenekleri.
    - `extra_amount`: Bilet bazlı ek maliyetler/gelirler.
- **Master Data:** Havalimanı (Airport) ve Havayolu (Airline) DocType'ları üzerinden IATA uyumlu Link alanlarına geçildi.

## 2. Akıllı Motorlar (Smart Engines)

### 2.1. Akıllı Klonlama (Smart Duplicate) [RULE-P1A2M]
- Yolcu eklendiğinde bir önceki satırdaki; **Tedarikçi, Maliyet, Hizmet Bedeli, Komisyon Oranı ve Ödeme Tipi** otomatik miras alınır. 
- **Bilet No Tetikleyicisi:** Bilet numarası rakamla bitiyorsa, yeni satırda otomatik `+1` artırılarak önerilir.

### 2.2. Birleşik Finans Motoru (Unified Financial Engine) [RULE-F5S9L]
Sistem, aşağıdaki tüm kaynaklardan gelen verileri anlık olarak "Seyahat Finansal Özeti" kutularına toplar:
- `trip_tickets` (Biletler)
- `trip_charges` (Ekstra Ücretler / Seat, Bagaj vb.)
- `trip_hotel_stays` (Oteller)
- `trip_service_items` (Genel Hizmetler)

**Hesaplama Mantığı:**
`Maliyet + (Maliyet * Komisyon%) + Ekstra = Toplam Satış`
*Not: Komisyon kutusuna rakam girildiğinde Hizmet Bedeli otomatik hesaplanır.*

## 3. UI/UX Standartları
- **Collapsible Sectionlar:** Vergi detayları ve Pasaport bilgileri gibi "kalabalık" alanlar varsayılan olarak kapalı (açılır-kapanır) gelir.
- **IATA Strict Formatting [RULE-D4B7C]:** Airport ve Airline kodları her zaman büyük harf ve İngilizce karakter (Ç->C, İ->I vb.) olarak kaydedilir.
- **Read-Only Entegrite:** Genel toplam alanları manuel müdahaleye kapatılmıştır; veri doğruluğu sistem tarafından garanti edilir.

## 4. Kullanılan Script Dosyaları
- **Client Script:** `Trip Ticket Advanced Duplicate` (Tüm toplama ve klonlama mantığını barındırır).

---
> 🔗 **İlgili Kurallar:** [[RULE-P1A2M]](../../raw/ui_ux_standards.md) | [[RULE-D4B7C]](../../raw/ui_ux_standards.md)
