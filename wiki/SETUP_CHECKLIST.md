# ⚙️ İzge Travel — ERPNext Zorunlu Ayarlar Kontrol Listesi (Setup Checklist)

> **Versiyon:** 1.0 | **Tarih:** 2026-04-17
> **Amaç:** Bu listedeki ayarlardan herhangi biri eksik veya hatalıysa, Trip otomasyonu, faturalama veya raporlama çökebilir.
> **Referans:** [MASTER_OVERVIEW.md](MASTER_OVERVIEW.md) · [UX_FLOWS.md](UX_FLOWS.md)

---

## 1. 🏢 Şirket Ayarları (Company)

| # | Ayar | Konum | Değer | Kritiklik |
|:---|:---|:---|:---|:---|
| 1.1 | Şirket Adı | Setup → Company | `İzge Turizm` | 🔴 Kritik |
| 1.2 | Varsayılan Para Birimi | Company → Default Currency | `TRY` | 🔴 Kritik |
| 1.3 | Hesap Planı (Chart of Accounts) | Company → Chart of Accounts | TDHP tabanlı | 🔴 Kritik |
| 1.4 | **Kur Farkı Hesabı** | Company → Exchange Gain/Loss Account | Tanımlı olmalı (örn: `680 Çalışmayan Kısım Giderleri`) | 🔴 Kritik |
| 1.5 | Varsayılan Maliyet Merkezi | Company → Cost Center | `İzge Turizm - İT` veya benzer | 🟡 Önemli |
| 1.6 | **Yuvarlama Hesabı** | Company → Round Off Account | Tanımlı olmalı | 🟡 Önemli |

> 🛡️ **Guardrail (SCEN-010):** `exchange_gain_loss_account` tanımlı değilse, EUR/USD faturalı ödeme (Payment Entry) hata verir ve kaydedilemez.

---

## 2. 📊 Hesap Planı (Chart of Accounts)

### 2.1 Zorunlu Hesaplar

| # | Hesap Adı | Hesap Tipi | Kullanım Yeri | Kritiklik |
|:---|:---|:---|:---|:---|
| 2.1 | **Müşteri Alacak (Debtors)** | Receivable | Sales Invoice → AR | 🔴 Kritik |
| 2.2 | **Tedarikçi Borç (Creditors)** | Payable | Purchase Invoice → AP | 🔴 Kritik |
| 2.3 | **Nakit Kasa** | Cash | Nakit tahsilat | 🔴 Kritik |
| 2.4 | **POS Banka Hesabı** | Bank | Kredi kartı tahsilatı | 🔴 Kritik |
| 2.5 | **Ana Banka Hesabı** | Bank | Havale/EFT tahsilatı | 🔴 Kritik |
| 2.6 | **Havayolu POS Clearing** | Bank veya Asset | SCEN-007B: Payment on Behalf akışı | 🟡 Senaryo Bağımlı |
| 2.7 | **Uçak Bileti Gelir** | Income | SI item gelir hesabı | 🔴 Kritik |
| 2.8 | **Hizmet Bedeli Gelir** | Income | Service Fee geliri | 🟡 Önemli |
| 2.9 | **Bilet Maliyet Gider** | Expense | PI item gider hesabı | 🔴 Kritik |
| 2.10 | **Banka Masraf Gideri** | Expense | SCEN-016: Chargeback cezası | 🟡 Senaryo Bağımlı |
| 2.11 | **KK Komisyon Gideri** | Expense | trip.py → CC Commission JE | 🟡 Önemli |
| 2.12 | **Kur Farkı (Exchange G/L)** | Expense/Income | Otomatik FX farkı | 🔴 Kritik |

### 2.2 Çok Para Birimli Hesaplar (Multi-Currency)

| # | Hesap | Para Birimi | Kullanım |
|:---|:---|:---|:---|
| 2.13 | Satıcılar EUR (Creditors EUR) | EUR | EUR havayolu faturaları |
| 2.14 | Satıcılar USD (Creditors USD) | USD | USD otel faturaları |

> 🛡️ **Guardrail (SCEN-010):** Supplier'ın Party Account Currency'si ile PI'daki Payable Account Currency'si eşleşmelidir. TRY hesabına EUR fatura kesilemez.

---

## 3. 📦 Ürün Kalemleri (Items & Item Groups)

### 3.1 Item Groups (Zorunlu)

| # | Grup Adı | Parent Group | Kritiklik |
|:---|:---|:---|:---|
| 3.1 | `Hizmetler` | All Item Groups | 🔴 Kritik |
| 3.2 | `Maliyetler` | All Item Groups | 🔴 Kritik |
| 3.3 | `Servis` | All Item Groups | 🟡 Önemli |

> 🛡️ **Guardrail (SCEN-008):** `parent_item_group` boş bırakılan grup, root seviyesinde olmadığı sürece `LinkValidationError` fırlatır. Dinamik SQL ile root grubu çekilmelidir.

### 3.2 Items (Otomatik Yaratılır, Ama Doğrulanmalı)

| # | Item Code | Item Name | Group | `is_sales_item` | `is_purchase_item` | Kritiklik |
|:---|:---|:---|:---|:---|:---|:---|
| 3.4 | `UCAK-BILETI` | Uçak Bileti | Hizmetler | ✅ | ✅ | 🔴 Kritik |
| 3.5 | `OTEL-KONAKLAMA` | Otel Konaklama | Hizmetler | ✅ | ✅ | 🟡 Önemli |
| 3.6 | `HIZMET-BEDELI` | Hizmet Bedeli | Servis | ✅ | ❌ | 🟡 Önemli |
| 3.7 | `EK-MASRAF-SATIS` | Ek Masraf | Hizmetler | ✅ | ❌ | 🟢 Opsiyonel |
| 3.8 | `BILET-MALIYETI` | Bilet/Hizmet Maliyeti | Maliyetler | ❌ | ✅ | 🔴 Kritik |
| 3.9 | `KONAKLAMA-MALIYETI` | Konaklama Maliyeti | Maliyetler | ❌ | ✅ | 🟡 Önemli |
| 3.10 | `AIRPORT-TAX` | Havalimanı Vergisi | Hizmetler | ✅ | ❌ | 🟡 SCEN-008 |

> 🛡️ **Guardrail (SCEN-015):** Turizm acenteliğinde bilet ürünleri hem `is_sales_item = 1` hem `is_purchase_item = 1` olmalıdır. Aksi takdirde PI aşamasında `Item not allowed for Purchase` hatası alınır.

> ⚙️ **Not:** `trip.py → _ensure_item()` metodu eksik item'ları otomatik yaratır. Ancak mevcut item'ların flag'lerinin doğruluğu elle kontrol edilmelidir.

---

## 4. 👥 Müşteri & Tedarikçi Yapılandırması

### 4.1 Customer Groups (Müşteri Grupları)

| # | Grup | Kullanım | Kritiklik |
|:---|:---|:---|:---|
| 4.1 | `Bireysel` | Bireysel yolcular | 🔴 Kritik |
| 4.2 | `Commercial` | Kurumsal müşteriler | 🟡 Önemli |

### 4.2 Supplier Groups (Tedarikçi Grupları)

| # | Grup | Kullanım | Kritiklik |
|:---|:---|:---|:---|
| 4.3 | `Havayolları` | THY, Pegasus, Lufthansa vb. | 🔴 Kritik |
| 4.4 | `Oteller` | Otel zincirleri ve bağımsız oteller | 🟡 Önemli |
| 4.5 | `Operatörler` | Tur operatörleri, transfer firmaları | 🟢 Opsiyonel |

> 🛡️ **Guardrail (SCEN-015):** Supplier Group root hiyerarşisi (`parent_supplier_group`) eksikse `LinkValidationError` alınır. `All Supplier Groups` root'u mutlaka mevcut olmalıdır.

### 4.3 Naming Series

| DocType | Series | Örnek |
|:---|:---|:---|
| Customer | `M-.YYYY.-.####` | M-2026-0001 |
| Supplier | `T-.YYYY.-.####` | T-2026-0001 |

---

## 5. 💳 Ödeme Yöntemi (Mode of Payment)

| # | Mod | Varsayılan Hesap | Kritiklik |
|:---|:---|:---|:---|
| 5.1 | `Cash` | Nakit Kasa | 🔴 Kritik |
| 5.2 | `Credit Card` | POS Banka Hesabı | 🔴 Kritik |
| 5.3 | `Bank Transfer` | Ana Banka Hesabı | 🔴 Kritik |
| 5.4 | `Wire Transfer` | Ana Banka Hesabı | 🟢 Opsiyonel |

> ⚠️ Her Mode of Payment'ın `Default Account` alanı doldurulmalıdır. Aksi takdirde Payment Entry sırasında hesap seçimi zorunlu olur (ve hata riski artar).

---

## 6. 📋 Ödeme Koşulları (Payment Terms)

| # | Şablon Adı | Koşul | Kullanım |
|:---|:---|:---|:---|
| 6.1 | `Peşin` | %100, 0 gün | Nakit/KK satışlar |
| 6.2 | `30 Gün Vadeli` | %100, 30 gün | Kurumsal vadeli satışlar |
| 6.3 | `50/50 Split` | %50 peşin + %50 30 gün | Büyük grup satışlar |

---

## 7. ✈️ Operasyonel Master Data

### 7.1 Airport (Havalimanı)

| # | Kontrol | Kritiklik |
|:---|:---|:---|
| 7.1 | Airport DocType'ında en az 1 kayıt mevcut mu? | 🔴 Kritik |
| 7.2 | Sık kullanılan havalimanları (IST, SAW, ESB, ADB, AYT) tanımlı mı? | 🟡 Önemli |
| 7.3 | `iata_code` alanı (Naming Series field) dolu mu? | 🔴 Kritik |

### 7.2 Airline (Havayolu)

| # | Kontrol | Kritiklik |
|:---|:---|:---|
| 7.4 | Airline DocType'ında en az 1 kayıt mevcut mu? | 🔴 Kritik |
| 7.5 | Sık kullanılan havayolları (TK, PC, XQ, LH) tanımlı mı? | 🟡 Önemli |

> 🛡️ **Guardrail:** Trip Flight Segment'te `origin` ve `destination` alanları Airport'a, `airline` alanı Airline'a Link'tir. Bu DocType'larda kayıt yoksa segment eklenemez.

---

## 8. 🔧 Genel ERPNext Ayarları

### 8.1 Accounts Settings

| # | Ayar | Konum | Değer | Kritiklik |
|:---|:---|:---|:---|:---|
| 8.1 | Allow Multi Currency | Accounts Settings | ✅ Aktif | 🔴 Kritik |
| 8.2 | Automatically Fetch Payment Terms | Accounts Settings | ✅ Önerilir | 🟢 Opsiyonel |
| 8.3 | Unlink Payment on Cancel | Accounts Settings | ❌ Kapalı önerilir | 🟡 Önemli |

### 8.2 Selling Settings

| # | Ayar | Değer | Kritiklik |
|:---|:---|:---|:---|
| 8.4 | Customer Naming By | Naming Series | 🟡 Önemli |
| 8.5 | Default Selling Price List | Standard Selling | 🟢 Opsiyonel |

### 8.3 Buying Settings

| # | Ayar | Değer | Kritiklik |
|:---|:---|:---|:---|
| 8.6 | Supplier Naming By | Naming Series | 🟡 Önemli |
| 8.7 | Default Buying Price List | Standard Buying | 🟢 Opsiyonel |

---

## 9. 🔒 İzge Travel Custom App (izge_travel)

| # | Kontrol | Komut / Yol | Kritiklik |
|:---|:---|:---|:---|
| 9.1 | App kurulu mu? | `bench --site SITE list-apps` → `izge_travel` görünmeli | 🔴 Kritik |
| 9.2 | Python import çalışıyor mu? | `python -c "import izge_travel; print(izge_travel.__file__)"` | 🔴 Kritik |
| 9.3 | `__version__` tanımlı mı? | `izge_travel/__init__.py` içinde `__version__ = "x.y.z"` | 🔴 Kritik |
| 9.4 | `modules.txt` doğru mu? | `Izge Travel` satırı (boşluksuz, tek satır) | 🔴 Kritik |
| 9.5 | DocType'lar migrate edildi mi? | `bench migrate` hatasız tamamlanmalı | 🔴 Kritik |
| 9.6 | trip.py production'a sync mi? | Son controller kodunun sunucuda olduğunu doğrula | 🔴 Kritik |
| 9.7 | trip.js production'a sync mi? | UI butonlarının görünürlüğünü doğrula | 🟡 Önemli |

---

## 10. ✅ Hızlı Doğrulama Scripti

Aşağıdaki 4 komut, sistemin sağlığını doğrular. **Tümü başarılı olmalıdır:**

```bash
# 1. Dosya yapısı
find /home/frappe/bench/apps/izge_travel -maxdepth 4 -not -path '*/.*' | sort

# 2. App listede mi?
bench --site SITE_NAME list-apps

# 3. Python import çalışıyor mu?
/home/frappe/bench/env/bin/python -c "import izge_travel; print(izge_travel.__file__)"

# 4. HTTP 200 dönüyor mu?
curl -I https://erpnext-production-1b2e.up.railway.app
```

---

## 11. 🧾 Turizm KDV & Tax Template Yapılandırması

Türkiye'nin turizm sektörüne yönelik KDV iade ve istisna kurallarını yönetmek için uygulanması gereken vergi grupları ve şablonlar aşağıdadır. (❗ *Uygulama öncesinde mutlaka güncel vergi mevzuatına istinaden mali müşavir tarafından onaylanmalıdır.*)

### 11.1 Item & Tax Category Yapısı (Ana Sınıflar)

Ürünlerin doğru orandan vergilendirilmesi için önce `Tax Category` oluşturulur ve `Item` bu kategoriye bağlanır.

| Turizm Ürünü (Item) | Tax Category (Yeni) | Örnek KDV Oranı | Uygulanacak Gelir Hesabı | Özel Notlar |
|:---|:---|:---|:---|:---|
| `Domestic Flight Ticket` | `DOM_FLIGHT` | %20 (Genel Oran) | 600.X (Yurtiçi Bilet S.) | Bilet geliri KDV'lidir. |
| `International Flight Ticket` | `INTL_FLIGHT_EXEMPT` | %0 (İstisna) | 601.X (Yurtdışı Bilet S.) | İstisna kapsamındadır. |
| `Domestic Hotel Night` | `DOM_HOTEL_10` | %10 (İndirimli Oran)| 600.X (Konaklama S.) | Sadece geceleme hizmeti (Ekstra servis hariç). |
| `Outgoing Tour Package` | `OUTGOING_TOUR` | KDV İstisna / %0 | 601.X (Yurtdışı Tur S.) | Bedelin içindeki yurtdışı maliyet kısmı için satır. |
| `Service Fee` | `SERVICE_FEE_20` | %20 (Genel Oran) | 600.X (Hizmet Bedeli) | Outgoing turda Acente Hizmet Bedeli / Kâr Matrahı olarak. |

### 11.2 Sales/Purchase Taxes and Charges Templates

Ürün ve hizmet kombinasyonlarına göre (örn. yurtdışı tur satışı), otomatik seçilecek KDV şablonları:

| Şablon Adı | Detay & Mantık | Formül / Rate (%) | Satır Notu |
|:---|:---|:---|:---|
| `TAX-DOMESTIC-PACKAGE` | Geceleme %10, diğer hizmetler %20 karışık | Satır 1: %10 KDV (Account: 391.01) | Sadece `DOM_HOTEL_10` kategorili ürünlere uygulanır. |
| | | Satır 2: %20 KDV (Account: 391.02) | Diğer standart kalemler (`SERVICE_FEE_20` vb.) içindir. |
| `TAX-INTL-FLIGHT` | Uluslararası bilet ve komisyon | Satır 1: %0 KDV (İstisna beyanı) | KDV tahakkuk etmez (Account seçilmeyebilir). |
| `TAX-OUTGOING-PACKAGE` | Yurtdışı maliyet (0%) + Hizmet bedeli (%20) | Satır 1: %0 KDV (Maliyet parçası) | Tour Cost satırı KDV'ye tabi değildir. |
| | | Satır 2: %20 KDV (Hizmet bedeli) | Sadece `Service Fee` öğesine uygulanır. KDV Matrah indirme formülü donanımsal olarak uygulanmış olur. |

---

## Kritiklik Özeti

| Seviye | Anlam | Adet |
|:---|:---|:---|
| 🔴 Kritik | Eksikse sistem çöker veya fatura/ödeme oluşturulamaz | ~20 |
| 🟡 Önemli | Eksikse bazı senaryolar çalışmaz veya veri bütünlüğü risk altında | ~12 |
| 🟢 Opsiyonel | İş akışını kolaylaştırır ama yoksa sistem çalışmaya devam eder | ~6 |

---

> 📌 **Bu checklist, her yeni ortam kurulumunda (staging, production, test) baştan sona işletilmelidir.**
> 🔗 **Referans:** [MASTER_OVERVIEW.md](MASTER_OVERVIEW.md) · [UX_FLOWS.md](UX_FLOWS.md) · [lessons_learned.md](lessons_learned.md)

---

## 🚀 MVP Setup — Pilot Kullanım İçin Minimum Paket

> **Amaç:** Aşağıdaki 13 ayar tamamlandığında, satışçı bir Trip oluşturup Submit edebilir, Fatura Oluştur butonuyla Draft Sales Invoice yaratabilir ve muhasebe ekibi bu faturayı onaylayıp nakit/KK tahsilatını kaydedebilir. Geri kalan ayarlar **Phase 2** olarak işaretlenmiştir ve pilot sonrası tamamlanabilir.

### MVP Tablosu (13 Zorunlu Ayar)

| Sıra | Kategori | Ayar | Neden Zorunlu | Doğrulama |
|:---|:---|:---|:---|:---|
| **1** | Company | `İzge Turizm` şirketi mevcut | Tüm fatura/ödeme bu şirkete bağlanır | Setup → Company → İzge Turizm var mı? |
| **2** | Company | Varsayılan Para Birimi = `TRY` | Yanlışsa tüm tutarlar bozulur | Company → Default Currency = TRY |
| **3** | CoA | Müşteri Alacak (Debtors) hesabı | SI Submit edildiğinde AR kaydı bulamaz | Receivable tipinde en az 1 hesap var mı? |
| **4** | CoA | Tedarikçi Borç (Creditors) hesabı | PI Submit edildiğinde AP kaydı bulamaz | Payable tipinde en az 1 hesap var mı? |
| **5** | CoA | Gelir hesabı (Uçak Bileti vb.) | SI item'ına gelir hesabı atanır | Income tipinde en az 1 hesap var mı? |
| **6** | CoA | Gider hesabı (Bilet Maliyeti vb.) | PI item'ına gider hesabı atanır | Expense tipinde en az 1 hesap var mı? |
| **7** | CoA | Nakit Kasa VEYA Banka hesabı | Tahsilat kaydedilemez; Payment Entry hesap bulamaz | Cash veya Bank tipinde en az 1 hesap var mı? |
| **8** | Items | `Hizmetler` + `Maliyetler` Item Group | `_ensure_item()` yeni ürün yaratırken parent grubu bulmak zorunda | Item Group listesinde bu 2 grup mevcut mu? |
| **9** | Customer | `Bireysel` Customer Group | İlk müşteri yaratılırken grup seçilmeli | Customer Group listesinde mevcut mu? |
| **10** | Supplier | En az 1 Supplier kaydı | Trip Flight Segment supplier alanı zorunlu | Supplier listesinde en az 1 kayıt var mı? |
| **11** | Airport | En az 1 Airport kaydı (örn: IST) | Trip segment `origin`/`destination` Link'i boş kalamaz | Airport listesinde en az 1 kayıt var mı? |
| **12** | Airline | En az 1 Airline kaydı (örn: TK) | Trip segment `airline` Link'i boş kalamaz | Airline listesinde en az 1 kayıt var mı? |
| **13** | Custom App | `izge_travel` kurulu + `bench migrate` başarılı | Trip DocType mevcut değilse hiçbir şey çalışmaz | `bench --site SITE list-apps` → izge_travel |

### Phase 2 Tablosu (Pilot Sonrası Tamamlanacak)

| Kategori | Ayar | Ne Zaman Gerekli |
|:---|:---|:---|
| Company | Kur Farkı Hesabı (Exchange G/L) | İlk EUR/USD fatura kesildiğinde |
| Company | Varsayılan Maliyet Merkezi | Cost Center bazlı raporlama istendiğinde |
| Company | Yuvarlama Hesabı | Kuruş farkı JE'si otomatik yaratılsın istendiğinde |
| CoA | POS Banka Hesabı (ayrı) | KK tahsilatı ayrı bankaya yönlendirildiğinde |
| CoA | Havayolu POS Clearing | SCEN-007B (Payment on Behalf) akışı kullanıldığında |
| CoA | Hizmet Bedeli Gelir (ayrı) | Service Fee ayrı gelir hesabında izlensin istendiğinde |
| CoA | KK Komisyon Gideri | KK komisyon JE'si otomatik yansıtılsın istendiğinde |
| CoA | Banka Masraf Gideri | Chargeback senaryosu yaşandığında |
| CoA | Satıcılar EUR / USD | İlk dövizli tedarikçi faturası kesildiğinde |
| Items | `OTEL-KONAKLAMA`, `HIZMET-BEDELI`, `AIRPORT-TAX` vb. | İlgili ürün tipi kullanıldığında (otomatik yaratılır) |
| Customer | `Commercial` Customer Group | İlk kurumsal müşteri eklendiğinde |
| Supplier | `Havayolları` / `Oteller` Supplier Group | Tedarikçi raporlaması yapıldığında |
| Supplier | Naming Series (`T-.YYYY.-.####`) | Standart adlandırma istendiğinde |
| Mode of Payment | Cash / Credit Card / Bank Transfer | İlk Payment Entry yapılmadan önce |
| Payment Terms | Peşin / 30 Gün Vadeli / Split | Vadeli satış yapılmaya başlandığında |
| Accounts Settings | Allow Multi Currency | İlk dövizli işlem öncesinde |
| Accounts Settings | Unlink Payment on Cancel = Kapalı | Fatura iptali güvenliği istendiğinde |
| Selling/Buying | Naming Series ayarları | Standart müşteri/tedarikçi kodlaması istendiğinde |
| Custom App | trip.js production sync | UI butonlarının çalışması için |
| Operasyonel | Yaygın Airport listesi (IST, SAW, ESB, ADB, AYT) | Operatörlerin hızlı veri girişi için |
| Operasyonel | Yaygın Airline listesi (TK, PC, XQ, LH) | Operatörlerin hızlı veri girişi için |

### MVP → Pilot Geçiş Akışı

```
┌─────────────────────────────────────────────────┐
│  MVP (13 ayar)                                  │
│  ═══════════════                                │
│  Company ✓ → CoA (5 hesap) ✓ → Item Groups ✓   │
│  → Customer Group ✓ → 1 Supplier ✓             │
│  → 1 Airport ✓ → 1 Airline ✓ → App ✓           │
│                                                 │
│  ✅ Pilot başlayabilir!                         │
│     Trip → Submit → Fatura → Tahsilat           │
└─────────────┬───────────────────────────────────┘
              │ Pilot başarılı olursa
              ▼
┌─────────────────────────────────────────────────┐
│  Phase 2 (21 ayar)                              │
│  ══════════════                                 │
│  Döviz Hesapları → KK Komisyon → Clearing       │
│  → Payment Terms → Mode of Payment              │
│  → Seed Data (Airport/Airline listeleri)         │
│  → Naming Series → trip.js sync                 │
│                                                 │
│  🚀 Tam operasyonel!                            │
└─────────────────────────────────────────────────┘
```

> 🔗 **Referans:** [MASTER_OVERVIEW.md](MASTER_OVERVIEW.md) · [UX_FLOWS.md](UX_FLOWS.md)
