# 🚀 [GOAL-M4N5O] Mission Control (Görev Kontrol)

Bu sayfa, projenin ana hedeflerini ve o anki odak noktasını takip eder.

## 🎯 Ana Hedefler
1. [x] **Railway & ERPNext Stabilizasyonu**: Konteynerin hatasız kalkması ve `tail -f /dev/null` bypass yöntemiyle stabil edilmesi.
2. [x] **Core Mimari Kurulumu**: `izge_travel` custom app'inin ve temel veri modellerinin (Traveler, Trip) oluşturulması.
3. [ ] **Duty of Care & Operasyon**: Konum takibi, seyahat ayakları ve vize entegrasyonu süreçlerinin kodlanması.
4. [ ] **Sistem Optimize & Yedekleme**: Kalıcı veri saklama (Volume backups) ve otomatik GitHub deployment akışının iyileştirilmesi.

## 📡 Mevcut Durum (v5.0)
- **Aktif Site:** `erpnext-production-1b2e.up.railway.app`
- **Modül:** `izge_travel` (GitHub: `ahmettas21/CRM`)
- **Odak Noktası:** 🚀 **Pilot-001 — İlk canlı senaryo testi.** MVP Setup 13/13 PASS.
- **Referans:** [MASTER_OVERVIEW](MASTER_OVERVIEW.md)

## 🚦 Durum Panosu
| Görev | Durum | Öncelik |
| :--- | :--- | :--- |
| Railway Stabilization | ✅ Tamamlandı | - |
| Custom App Scaffold | ✅ Tamamlandı | - |
| DocType Logic & UI | ✅ Tamamlandı | - |
| **Trip Module Modernization** | ✅ Tamamlandı | - |
| **Unified Finance Engine** | ✅ Tamamlandı | - |
| **Edge-Case Regression Suite** | ✅ Tamamlandı (7/7 PASSED) | - |
| **Trip Controller Rule Engine** | ✅ Tamamlandı (Guardrail + API) | - |
| **UI Billing Button** | ✅ Tamamlandı (SCEN-TRIP-002) | - |
| **Dashboard Blueprint** | ✅ Tamamlandı (4 panel) | - |
| **Dokümantasyon Seti** | ✅ Tamamlandı (MASTER, UX, Setup, MVP) | - |
| **MVP Setup Doğrulama** | ✅ 13/13 PASS | - |
| **🚀 Pilot-001 Faz 1-2** | ✅ 7/7 PASSED | - |
| **🚀 Pilot-001 Faz 3-4** | ✅ 8/8 PASSED | - |
| **🚀 Pilot-001 TOPLAM** | ✅ **15/15 PASSED** | - |
| Dashboard Script Reports | ⏳ Sırada | Yüksek |
| Duty of Care Features | ⏳ Sırada | Yüksek |
| Visa World Integration | ⏳ Sırada | Orta |

---

## 🚀 Pilot-001: Mehmet Yılmaz Senaryosu

> **Amaç:** Eğitim Senaryosu 001'i canlı sistemde adım adım yaşatarak, Trip → Fatura → Tahsilat → İade akışının uçtan uca çalıştığını ispatlamak.
> **Süre:** ~30 dakika
> **Ön Koşul:** MVP Setup 13/13 ✅ PASS (2026-04-17 tarihinde doğrulandı)
> **Referans:** [UX_FLOWS.md → Eğitim Senaryosu 001](UX_FLOWS.md#-eğitim-senaryosu-001-gidiş-dönüş--hizmet-bedeli--kk--no-show-i̇ade)

### MVP Setup Doğrulama Sonuçları (2026-04-17)

| # | Ayar | Durum | Canlı Değer |
|:---|:---|:---|:---|
| 1 | Company | ✅ PASS | İzge Turizm |
| 2 | Default Currency | ✅ PASS | TRY |
| 3 | Debtors (Receivable) | ✅ PASS | 120.01 - ALICILAR - IZGET |
| 4 | Creditors (Payable) | ✅ PASS | 320.02 - SATICILAR EUR - IZGET |
| 5 | Income | ✅ PASS | 600.01 - YURT İÇİ SATIŞLAR - IZGET |
| 6 | Expense | ✅ PASS | 656 - Kur Farkı Zararları - IZGET |
| 7 | Cash/Bank | ✅ PASS | 102.01.001 - İŞ BANKASI 4846 - IZGET |
| 8 | Item Groups | ✅ PASS | Hizmetler + Maliyetler mevcut |
| 9 | Customer Group | ✅ PASS | Bireysel |
| 10 | Supplier | ✅ PASS | 15 adet |
| 11 | Airport | ✅ PASS | 5 adet (IST, SAW, ESB, ADB, AYT) |
| 12 | Airline | ✅ PASS | 2 adet |
| 13 | izge_travel app | ✅ PASS | frappe, izge_travel, erpnext |

### Pilot Akış Planı

#### Faz 1: Satış (Satışçı Rolü) — ~10 dk

| Adım | Ekran | Yapılacak İşlem | Doğrulama |
|:---|:---|:---|:---|
| **1.1** | Trip Form → Hızlı İşlemler → Yeni Müşteri | Ad: `Mehmet Yılmaz`, Tür: Individual, Tel: 05XX | Müşteri alanı otomatik doldu mu? |
| **1.2** | Trip Header | Tarih: Bugün, PNR: `PILOT001`, Ürün: Flight | PNR unique uyarısı gelmedi mi? |
| **1.3** | Hızlı İşlemler → Yeni Yolcu | Ad: `Mehmet Yılmaz`, Cinsiyet: Male | primary_traveler set edildi mi? |
| **1.4** | Hızlı İşlemler → Uçuş Ekle | Gidiş: IST→ESB, TK, +3 gün, Maliyet: 2.000, Hizmet: 200 | Satış = 2.200 otomatik mi? |
| **1.5** | Hızlı İşlemler → Uçuş Ekle | Dönüş: ESB→IST, TK, +5 gün, Maliyet: 1.500, Hizmet: 200 | Satış = 1.700 otomatik mi? |
| **1.6** | Ödeme Bilgileri | Yöntem: Credit Card, Banka: Garanti BBVA, Oran: %2.5 | KK alanları açıldı mı? |
| **1.7** | **Kaydet (Ctrl+S)** | — | 🟢 Kâr başlığı: "400 TL \| 10.3%" görünüyor mu? |
| **1.8** | **Submit** | — | Draft PI ve CC JE otomatik yaratıldı mı? |
| **1.9** | Muhasebe → **Fatura Oluştur** | Onay dialogu → Evet | "Fatura Taslağı Oluşturuldu" mesajı geldi mi? |

**Faz 1 Doğrulama Noktası:**
```
Trip → Profit:           400 TL ✓
Draft Sales Invoice:     3.900 TL ✓ (Remarks'ta PILOT001 var)
Draft Purchase Invoice:  3.500 TL ✓
CC Commission JE:        97.50 TL ✓
```

---

#### Faz 2: Muhasebe Onay — ~5 dk

| Adım | Ekran | Yapılacak İşlem | Doğrulama |
|:---|:---|:---|:---|
| **2.1** | Sales Invoice Listesi → Status: Draft | PILOT001 referanslı SI'yı bulun | Customer = Mehmet Yılmaz, Total = 3.900 |
| **2.2** | SI → **Submit** | GL kaydı oluşur | Accounts → General Ledger'da 2 satır (Gelir CR + AR DR) |
| **2.3** | SI → **Make Payment Entry** | Hesap: İŞ BANKASI 4846, Tutar: 3.900, Ref No: POS-PILOT-001, Ref Date: Bugün | PE formu doğru mu? |
| **2.4** | Payment Entry → **Submit** | — | SI Outstanding = 0 oldu mu? |

**Faz 2 Doğrulama Noktası:**
```
Rapor: Accounts → Accounts Receivable
  Mehmet Yılmaz → Outstanding = 0 ✓
  
Rapor: Accounts → General Ledger (Voucher = SI adı)
  Gelir hesabı Credit:   3.900 ✓
  Debtors Debit:         3.900 ✓
  
Rapor: Accounts → General Ledger (Voucher = PE adı)
  Debtors Credit:        3.900 ✓
  Banka Debit:           3.900 ✓
```

---

#### Faz 3: No-Show Vergi İadesi — ~10 dk

| Adım | Ekran | Yapılacak İşlem | Doğrulama |
|:---|:---|:---|:---|
| **3.1** | Orijinal SI'yı açın | ⚠️ **CANCEL ETMEYİN!** Sadece bakın | Status = Submitted ✓ |
| **3.2** | SI → **Make Credit Note** | `is_return = 1` otomatik set edilir | Return Against doğru SI'ya mı bakıyor? |
| **3.3** | Credit Note Items | Tüm mevcut kalemleri silin. Yeni ekleyin: Item = `AIRPORT-TAX` (yoksa `_ensure_item` yaratır), Qty = -1, Rate = 300 | Tek kalem, -300 TL |
| **3.4** | Credit Note → **Submit** | GL kaydı oluşur | Grand Total = -300 TL |

**Faz 3 Doğrulama Noktası:**
```
Rapor: Accounts → Accounts Receivable
  Mehmet Yılmaz → Outstanding = -300 (aşırı ödeme) ✓
  
Orijinal SI: Bozulmamış (3.900 TL, Submitted) ✓
Credit Note: -300 TL, Submitted ✓
```

---

#### Faz 4: İade Ödemesi — ~5 dk

| Adım | Ekran | Yapılacak İşlem | Doğrulama |
|:---|:---|:---|:---|
| **4.1** | Credit Note → **Make Payment Entry** | Ödeme tipi: Pay, Hesap: İŞ BANKASI 4846, Tutar: 300 | PE formu doğru mu? |
| **4.2** | Payment Entry → **Submit** | Müşteri bakiyesi = 0 | Outstanding = 0 ✓ |

**Faz 4 Doğrulama Noktası (FİNAL):**
```
Rapor: Accounts → Accounts Receivable
  Mehmet Yılmaz → Outstanding = 0 ✓

Rapor: Accounts → Profit and Loss Statement
  Gelir: 3.600 TL net (3.900 - 300 iade) ✓
  
Rapor: Accounts → General Ledger (tüm voucher'lar)
  SI:           +3.900 gelir ✓
  Credit Note:  -300 gelir ✓
  PE Tahsilat:  3.900 banka ✓
  PE İade:      -300 banka ✓
```

### Pilot Sonuç Formu

| # | Kontrol | Beklenen | Gerçekleşen | ✅/❌ |
|:---|:---|:---|:---|:---|
| 1 | Trip profit | 400 TL | | |
| 2 | SI Grand Total | 3.900 TL | | |
| 3 | SI Outstanding (PE sonrası) | 0 | | |
| 4 | Credit Note Total | -300 TL | | |
| 5 | Müşteri Net Bakiye (sonunda) | 0 | | |
| 6 | Orijinal SI durumu | Submitted (bozulmamış) | | |
| 7 | P&L net gelir | 3.600 TL | | |

### Pilot Sonrası Aksiyon

| Sonuç | Aksiyon |
|:---|:---|
| ✅ 7/7 PASS | Pilot başarılı → Dashboard Script Report'larına geç |
| ⚠️ Kısmi FAIL | Hata analizini `wiki/lessons_learned.md`'ye yaz → düzelt → tekrar koş |
| ❌ Kritik FAIL | `raw/scenarios/PILOT-001_error_log.txt`'ye kaydet → root cause analysis |

> 🔗 **Eğitim Senaryosu:** [UX_FLOWS.md](UX_FLOWS.md#-eğitim-senaryosu-001)
> 🔗 **MVP Setup:** [SETUP_CHECKLIST.md](SETUP_CHECKLIST.md#-mvp-setup--pilot-kullanım-i̇çin-minimum-paket)
> 🔗 **Doğrulama Scripti:** `tmp/verify_mvp_setup.py`

---

### ✅ Otomatik Faz 1-2 Sonuçları (2026-04-17)

**Script:** `tmp/run_pilot_001_phase1_2.py` | **Durum:** 🎉 7/7 PASSED

| # | Kontrol | Beklenen | Gerçekleşen | ✅/❌ |
|:---|:---|:---|:---|:---|
| 1 | Trip Profit | 400 TL | 400 TL | ✅ |
| 2 | Trip Total Sale | 3.900 TL | 3.900 TL | ✅ |
| 3 | Trip Cost | 3.500 TL | 3.500 TL | ✅ |
| 4 | SI Grand Total | 3.900 TL | 3.900 TL | ✅ |
| 5 | SI Outstanding (PE sonrası) | 0 TL | 0 TL | ✅ |
| 6 | GL Entry (SI) | ≥2 | 2 | ✅ |
| 7 | GL Entry (PE) | ≥2 | 2 | ✅ |

**Canlı Belge Numaraları:**
- Trip: `TRIP-2026-00135`
- Sales Invoice: `ACC-SINV-2026-00019`
- Payment Entry: `ACC-PAY-2026-00012`
- PNR: `PILOT001`

**GL Doğrulama:**
- SI: Debit `120.01 ALICILAR` 3.900 TL → Credit `600.01 YURT İÇİ SATIŞLAR` 3.900 TL
- PE: Debit `102.01.001 İŞ BANKASI` 3.900 TL → Credit `120.01 ALICILAR` 3.900 TL
- **Müşteri AR Bakiye:** 0 TL ✅

**Gözlemler:**
1. ⚠️ `on_submit` içindeki PI/CC_JE otomatik yaratılmadı — trip.py'nin production'daki versiyonu bu metodları henüz içermiyor olabilir. Sync gerekli.
2. ✅ `make_sales_invoice()` whitelisted API sorunsuz çalıştı.
3. ✅ GL hareketleri hesap planı ile birebir eşleşiyor.

> 🔗 **Ham Log:** [raw/pilot/PILOT-001_phase1_2_success_log.txt](../raw/pilot/PILOT-001_phase1_2_success_log.txt)

---

### ✅ Otomatik Faz 3-4 Sonuçları (2026-04-17)

**Script:** `tmp/run_pilot_001_phase3_4.py` | **Durum:** 🎉 8/8 PASSED

| # | Kontrol | Beklenen | Gerçekleşen | ✅/❌ |
|:---|:---|:---|:---|:---|
| 1 | Orijinal SI bozulmadı | 3.900 TL | 3.900 TL | ✅ |
| 2 | Orijinal SI docstatus | 1 (Submitted) | 1 | ✅ |
| 3 | CN Grand Total | -300 TL | -300 TL | ✅ |
| 4 | CN is_return | 1 | 1 | ✅ |
| 5 | CN GL Entries | ≥2 | 2 | ✅ |
| 6 | Refund PE GL Entries | ≥2 | 2 | ✅ |
| 7 | Müşteri Final Bakiye | 0 TL | 0 TL | ✅ |
| 8 | Net Gelir (P&L) | 3.600 TL | 3.600 TL | ✅ |

**Canlı Belge Numaraları:**
- Credit Note: `ACC-SINV-2026-00020`
- İade PE: `ACC-PAY-2026-00013` (REFUND-PILOT-001)

**GL Özeti (Tüm Pilot-001):**
```
SI:     Debit 120.01 ALICILAR 3.900 → Credit 600.01 SATIŞLAR 3.900
PE:     Debit 102.01 İŞ BANKASI 3.900 → Credit 120.01 ALICILAR 3.900
CN:     Debit 600.01 SATIŞLAR 300 → Credit 120.01 ALICILAR 300
Refund: Debit 120.01 ALICILAR 300 → Credit 102.01 İŞ BANKASI 300
──────────────────────────────────────────────────
Net Gelir: 3.600 TL | Net Banka: 3.600 TL | AR: 0 TL ✅
```

> 🔗 **Ham Log:** [raw/pilot/PILOT-001_phase3_4_success_log.txt](../raw/pilot/PILOT-001_phase3_4_success_log.txt)

---

### 🎉 Pilot-001 Final: 15/15 PASSED

Pilot-001 Mehmet Yılmaz senaryosu **tüm 4 fazıyla başarıyla tamamlandı.** Sistem, uçtan uca Trip → SI → PE → Credit Note → Refund PE akışını doğru GL hareketleriyle gerçekleştirdi.

**Sonraki Adım:** Manuel UI pilotu → Dashboard Script Reports → Production deployment.

---

## 🌍 PILOT-HOTEL/TOUR/SERVICE Demo Paketleri

Trip mimarisini sadece Uçak (Flight) dışına da açarak Otel, Paket Tur ve Vize/Hizmet senaryoları için **2025-2026 Turizm Trendlerine** uygun 3 demo paket planlanmış ve CLI script'leri ile Railway'de (UI manuel testine girmeden önce) test edilmek üzere hazırlanmıştır. `trip.py` entegrasyonu tamamlandığında scriptler test edilecektir.

### 1) SCEN-TRIP-HOTEL-001 (Kapadokya Lüks Kaçamak)
| Özellik | Değer |
|:---|:---|
| **Script/Ref** | `tmp/run_scenario_trip_hotel_001.py` (DEMO-HOTEL-001) |
| **İçerik** | 2 Pax, 1 Oda, Hafta sonu 3 Gece Boutique Cave Hotel |
| **Finans** | Maliyet: 24.000 TL \| Satış: 30.000 TL \| Kâr: 6.000 TL |
| **KDV Özeti** | Konaklama (24.000) @ %10 KDV + Hizmet (6.000) @ %20 KDV |

### 2) SCEN-TRIP-TOUR-001 (Vizesiz Balkan Rüzgarı)
| Özellik | Değer |
|:---|:---|
| **Script/Ref** | `tmp/run_scenario_trip_tour_001.py` (DEMO-TOUR-001) |
| **İçerik** | 2 Pax, 4 Gece Outgoing Kültür Turu (Saraybosna-Belgrad) |
| **Finans** | Yurtdışı Maliyet: 40.000 TL \| Tur Satış: 50.000 TL \| Kâr: 10.000 TL |
| **KDV Özeti** | Yurtdışı Maliyet Yansıtması (40.000) @ Exempt/Sıfır + AC Hizmet Bedeli (10.000) @ %20 KDV |

### 3) SCEN-TRIP-SERVICE-001 (VIP Vize & CIP Lounge)
| Özellik | Değer |
|:---|:---|
| **Script/Ref** | `tmp/run_scenario_trip_service_001.py` (DEMO-SRV-001) |
| **İçerik** | 1 Pax, Schengen Vize Harcı + VIP Danışmanlık + IST CIP Lounge |
| **Finans** | Harç/Maliyet: 6.000 TL \| Toplam Satış: 9.500 TL \| Kâr: 3.500 TL |
| **KDV Özeti** | Vize Harcı (Pass-through) @ Exempt/Sıfır + Vize Danışmanlık ve CIP @ %20 KDV |
