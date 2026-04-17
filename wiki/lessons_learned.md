# 🧠 Ders Çıkarılan Hatalar (Lessons Learned)

## 🪆 [MEM-K3L4M] Matruşka Klasör Tuzağı (Ağustos 2026 Vak'ası)

### Sorun
Uygulama sunucuya gönderildiğinde `hooks.py` dosyasının bulunamaması (`ModuleNotFoundError`) ve sol panelin (sidebar) boş görünmesi.

### Kök Neden
Kodların yereldeki dizin yapısı (`CRM/izge_travel/izge_travel/izge_travel...`) ile Git repsounun birleşmesi sonucunda, sunucuda 4-5 kat derinliğe sahip bir yapı oluşması. Frappe, Python import mantığı gereği modülü (izge_travel) yüklerken en fazla 2 kat derinlikte `hooks.py` arar. Daha derindeyse sistemi kilitler.

### Çözüm (Forum & Saha Onaylı)
- Dizin yapısını **Frappe Standartlarına** indirge. (Bkz: [raw/frappe_structure.md](../raw/frappe_structure.md))
- Uygulamayı sunucuda daima `pip install -e .` (Editable Mode) ile yükle.
- `__init__.py` içinde `__version__` bilgisini ASLA unutma.

### Altın Öğreti
> "Eğer sol panel yüklenmiyorsa veya 'No module named hooks' hatası geliyorsa, koda değil dizin derinliğine bak!"

---
🔗 **Derin Teknik Kök Neden (Deep Dive):** [raw/frappe_structure.md](../raw/frappe_structure.md)

## 📋 Senaryo İndeksi (Test & Regresyon)

| Senaryo ID | Başlık | Dokümantasyon | Durum |
| :--- | :--- | :--- | :--- |
| SCEN-BEE-008 | Item Group & Credit Note Ledger Test | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-012 | Kısmi İptal ve P&L Optimizasyonu | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-016 | Chargeback ve Hesap Planı Maskesi | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-015 | Supplier Group & Purchase Item Validation | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-TRIP-001 | Trip Controller & Otomatik Faturalandırma | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-TRIP-002 | UI 'Make Invoice' Buton & API Tetikleyici | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-DASH-001 | Dashboard SQL & Number Card Validasyonu | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| **PILOT-001** | **Mehmet Yılmaz E2E: Trip→SI→PE→GL (Faz 1-2)** | [Detay](../../raw/pilot/PILOT-001_phase1_2_success_log.txt) | ✅ **7/7 PASSED** |

> 🔗 **Detaylı Sonuçlar:** [raw/scenarios/results.md](../../raw/scenarios/results.md)

## 🔄 [MEM-P7Q8R] on_submit Sync Uyumsuzluğu (PILOT-001 Gözlemi)

### Sorun
Pilot-001'de Trip submit edildiğinde `create_purchase_invoices()` ve `create_cc_commission_entry()` çalışmadı — otomatik PI ve CC JE yaratılmadı.

### Kök Neden
`trip.py`'nin en son sürümü (on_submit hook'ları dahil) production sunucusuna tam olarak sync edilmemiş. Yerel depo bu metodları içeriyor ancak sunucudaki Python dosyası eski versiyonda.

### Çözüm
- `trip.py`'yi base64 yöntemiyle production'a sync et
- Ardından `bench clear-cache` çalıştır
- Doğrulama: `bench console` ile `from izge_travel.izge_travel.doctype.trip.trip import Trip; print(dir(Trip))` → `create_purchase_invoices` mevcut mu kontrol et

### Altın Öğreti
> "Sunucuya `git push` yapıldıysa bile, Python bytecode cache (.pyc) eski kalabilir. Her deploy sonrası `bench clear-cache` zorunludur."


## 💶 [MEM-F2X3Z] Multi-Currency ve Finansal Test Püf Noktaları

### Sorun
Kur farkı veya Split Payment senaryolarının testlerinde karşılaşılan ERPNext'in sert finansal kuralları. Bu kurallar göz ardı edildiğinde "Validation Error" döner.

### Ders (1): Party Account Currency ≠ Document Currency Olmaz
Supplier (party) eğer EUR fatura veya ödeme yaratacaksa, faturadaki Payable Account hesabının da kesinlikle EUR olması gerekir. TRY ana cari hesabına doğrudan dövizli evrak işlenemez. *Çözüm: `320.xx SATICILAR EUR` veya çok paralı hesap kullanın.*

### Ders (2): exchange_gain_loss_account Tanımsızsa FX GL Atılamaz
Company ayarlarında bu hesap zorunlu olarak tanıtılmazsa, kur farkı oluştuğunda ödeme makbuzu (Payment Entry) hata verir ve kaydedilmez. Önlem olarak; `setup_company` scriptlerinde bu hesabı validate ettirin.

### Ders (3): PyMySQL'de Tuple ile Parametre Geçme (String Format Hatası)
Python betiklerinde `frappe.db.sql` fonksiyonlarında format (%s) parametresi geçerken, sadece `company` değil mutlaka `(company, )` tuple olarak verilmelidir. Aksi taktirde ERPNext veritabanı "not enough arguments for format string" hatasıyla sistemi patlatır.

## 🚨 Failure Analysis: Item Group LinkValidationError (SCEN-BEE-008 Testi)

### Sebep
Test altyapısı için gerekli olan eksik ürünleri (Item: AIRPORT-TAX vb.) manuel kodla yaratırken `item_group="Services"` atandı. Ancak ERPNext kurulumunda (Örn: Türkiye yerelleştirmesi veya Vanilla) bu Item Group bulunamadığı için `LinkValidationError: Could not find Item Group: Services` alındı.

### Etkilediği Modüller
- `Item` (Master Data Creation)
- `Sales Invoice` (Item bulunamayınca fatura oluşturulamıyor).

### Çözüm Denemesi ve Sonraki Aksiyon
Sabitlenmiş (Hardcoded) "Services" veya "Hizmet" gibi İngilizce/Türkçe grup isimleri vermek yerine, sistemde ilk karşılaşılan geçerli grup ismi SQL ile aranarak (`frappe.db.sql("select name from tabItem Group limit 1")`) item'a atanacaktır. 

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Python test betiklerindeki Setup aşamalarında `Item`, `Supplier Group` gibi master-data alanlarına asla Hardcoded (Elle yazılmış) isimler atamayın. Veritabanının dil veya konfigürasyondan etkilenmemesi için `[0][0]` limitli SQL lookup yapın.*

## 🚨 Failure Analysis: İade (Credit Note) Sonrası Doküman vs Mizan Farkı (SCEN-BEE-008)

### Sebep
Müşteriye 10.000 TL fatura kesilmiş ve arkasından 800 TL Credit Note (is_return=1) oluşturulmuştur. Ancak test esnasında `si.outstanding_amount` çağrıldığında rakamın 9.200 TL'ye düşmediği, hala 10.000 TL olduğu görülüp AssertionError alınmıştır.

### Etkilediği Modüller
- `Sales Invoice`, `Credit Note`, `Accounts Receivable (AR)`

### Çözüm Denemesi ve Sonraki Aksiyon
ERPNext 13+ versiyonlarında Credit Note yaratımı **sadece GL Ledger (Muhasebe Defteri)** bakiyesini anında değiştirir. Ancak ilgili ana faturanın (DocType üstündeki) `outstanding_amount` alanını düşürmek için `Payment Reconciliation` (Mahsup) aracıyla eşleştirilmeleri zorunludur.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Testlerde "Müşteri Borcu" ölçülecekse, ASLA Sales Invoice `outstanding_amount` alanına güvenmeyin. Orijinal olan tek defter Ledger'dır (Mizan). Değerleri daima `tabGL Entry` tablosundan `SUM(debit)-SUM(credit)` atarak doğrulayın.*

## 💡 Success Analysis: Kısmi İptalde P&L Optimizasyonu (SCEN-BEE-012)

### Konsept ve Başarı
SCEN-012 testi ile; bir biletin (Gidiş-Dönüş) sadece belli bir bölümü iptal edildiğinde (Kısmi Kullanım/Partial Usage), faturada bulunan Komisyon (Service Fee) kaleminin de tamamen iade edilmesi engellenmiş, "Pro-Rata (Yüzdesel)" iade mantığı ERPNext'te kanıtlanmıştır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Kısmı iadelerde komisyon/hizmet bedelleri her zaman '(İptal Edilen Segment) / (Toplam Bilet Bedeli)' oranıyla eksiye (Credit Note Item Qty: -1 Rate: ServiceFee * Oran) düşürülmelidir. Bu sayede şirket, yolcunun %100 iptallerindeki gibi tüm komisyon kârını kaybetmez, uçulan bacakların kârı ERPNext Mizanında korunur.*

## 🚨 Failure Analysis: Hesap Planı Maskesi Hatası (SCEN-BEE-016)

### Sebep
Chargeback testindeki ceza kesintisini (Expense) kaydetmek için `account_name like '7%%'` üzerinden Türkçe standartlara (770 vb.) güvenilerek SQL sorgusu yapıldı. Sistem bu maskeye uyan hesabı bulamayınca test patladı. 

### Etkilediği Modüller
- `Account` (Chart of Accounts Lookup)
- `Journal Entry` (Banka gider fişi)

### Çözüm Denemesi ve Sonraki Aksiyon
İsim maskesi yerine ERPNext'in evrensel root özelliklerine güvenilerek `account_type='Expense Account'` veya `root_type='Expense'` WHERE parametreleri kullanılarak sorgu genelleştirildi.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Muhasebe hesaplarını SQL ile ararken asla isim (`account_name`) kalıplarına güvenmeyin. Frappe'nin her kurulumda sabit tuttuğu `is_group`, `root_type` veya `account_type` meta alanları üzerinden sorgu atarak evrenselliği koruyun.*

## 💡 Success Analysis: Chargeback ve Kapanmış Faturayı Bozmama (SCEN-BEE-016)

### Konsept ve Başarı
Bir otel veya uçuş rezervasyonu Müşteri tarafından bankaya sahtecilik (Chargeback) olarak bildirildiğinde, tahsil edilmiş para aylar sonra banka tarafından zorla çekilir. SCEN-016 testi ile, faturanın veya ödeme makbuzunun (PE) iptal edilmeden (Ledger Immutable kuralı ile), `Journal Entry` kullanılarak Müşterinin AR listesinde yeniden borçlandırılması (Dispute) ve kesilen komisyon cezasının P&L'de direkt Gidere (Expense) yazılması ispatlanmıştır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Chargeback veya Fraud (Sahtecilik) vakalarında ASLA eski `Sales Invoice` veya `Payment Entry` belgelerini iptal etmeyin (Cancel/Amend). Bu durum KDV/Vergi beyannamelerini bozar. Bunun yerine daima 3 Bacaklı bir `Journal Entry` kullanın: 1) Müşteriye (+) Borç Ver, 2) Gider/Ceza Hesabına (+) Borç Ver, 3) Kasa/Bankadan (-) Para Düş.*

## 🚨 Failure Analysis: Supplier Group LinkValidationError (SCEN-BEE-015)

### Sebep
`Supplier` (Lufthansa) yaratılırken `supplier_group="Airlines"` atandı. Sistemde bu isimle bir grup tanımlı olmadığı için `LinkValidationError` alındı.

### Etkilediği Modüller
- `Supplier`
- `Purchase Invoice` (Supplier bulunamayınca maliyet faturası oluşturulamıyor).

### Çözüm Denemesi ve Sonraki Aksiyon
`Item Group` hatasında olduğu gibi, `Supplier Group` için de dinamik SQL lookup (`select name from tabSupplier Group limit 1`) kullanılarak testlerin master-data bağımsızlığı sağlanacaktır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Master-data yaratırken (`Supplier`, `Item`, `Customer` vb.) zorunlu grup alanlarına asla hardcoded isim yazmayın. Sistemdeki mevcut ilk grubu SQL ile çekip (`limit 1`) ona atayın.*

## 🚨 Failure Analysis: Purchase Item Validation Error (SCEN-BEE-015)

### Sebep
`Sales Invoice` üzerinde sorunsuz çalışan `UCAK-BILETI` ürünü, `Purchase Invoice` (ADM) üzerinde kullanılırken `is_purchase_item=0` olduğu için ERPNext tarafından reddedildi.

### Etkilediği Modüller
- `Item Master`
- `Purchase Invoice` / `Purchase Order`

### Çözüm Denemesi ve Sonraki Aksiyon
Ürün yaratma aşamasında `is_purchase_item=1` ve `is_sales_item=1` bayraklarının her ikisi de set edilmelidir. Mevcut ürünler için `frappe.db.set_value` veya `doc.save()` ile bayrak güncellenmelidir.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Turizm acenteliği bir 'Reseller' (aracı) iş kolu olduğu için, tüm bilet/otel/tur ürünleri ERPNext üzerinde hem **Purchase** hem de **Sales** ürünü olarak işaretlenmelidir. Aksi takdirde maliyetlendirme (Purchase Invoice) aşamaları patlayacaktır.*

## 🚨 Failure Analysis: Traveler LinkValidationError (SCEN-TRIP-001)

### Sebep
`Trip` segmentlerine manuel veri girilirken `traveler` alanı (Link) dolduruldu ancak sistemde bu isme sahip bir `Traveler` dokümanı mevcut değildi. Frappe link validasyonu kaydı reddetti.

### Etkilediği Modüller
- `Trip` (Header & Child Tables)
- `Traveler` (Identity Master)

### Çözüm Denemesi ve Sonraki Aksiyon
Testlerde `Customer` yaratıldığı gibi, segmentlerde kullanılacak her bir benzersiz isim için bir `Traveler` dokümanı da önceden insert edilmelidir.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Child tablo bazlı Link alanlarını (örn: Traveler) test ederken, fiktif veri basmadan önce bağımlı (Parent) dokümanın varlığını kontrol edin veya yaratın. ERPNext UI'daki 'Create on the fly' özelliği Python API seviyesinde otomatik çalışmaz.*

## 🚨 Failure Analysis: Traveler Full Name Validation (SCEN-TRIP-001)

### Sebep
`Traveler` kaydı oluşturulurken `full_name` alanı boş bırakıldı. Traveler Controller (`validate` metodu) bu alanın doluluğunu kontrol ettiği için kayıt başarısız oldu.

### Etkilediği Modüller
- `Traveler` (Identity Master)

### Çözüm Denemesi ve Sonraki Aksiyon
Traveler yaratırken `traveler_name` (Name ID) ile birlikte `full_name` alanı da anlamlı bir veriyle doldurulmalıdır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Master data yaratırken sadece teknik alanlara odaklanmayın. İlgili DocType'ın Python controller'ını (`validate` metodu) hızlıca kontrol ederek zorunlu tutulan iş mantığı alanlarını (örn: Full Name, Gender, Birth Date vb.) doldurduğunuzdan emin olun.*

## 🚨 Failure Analysis: Traveler Customer Mandatory Check (SCEN-TRIP-001)

### Sebep
`Traveler` kaydı oluşturulurken `customer` alanı boş bırakıldı. Sistem tasarımı gereği her Traveler dokümanı bir Customer'a bağlı olmak zorundadır.

### Etkilediği Modüller
- `Traveler` (Identity Master)

### Çözüm Denemesi ve Sonraki Aksiyon
Traveler yaratırken `customer` alanı, Trip üzerinde kullanılan ana Customer ile aynı olacak şekilde doldurulmalıdır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Turizm CRM yapısında Yolcu (Traveler) ve Müşteri (Customer/Cari) arasındaki hiyerarşiyi asla unutmayın. Bir Yolcu dokümanı yaratırken mutlaka geçerli bir `customer` linkini parametre olarak geçin.*

## 🚨 Failure Analysis: Document ID vs Field Name Link (SCEN-TRIP-001)

### Sebep
Frappe Link alanları, dokümanın "ID" (İsim) alanını bekler. `Traveler` DocType'ı Naming Series kullandığı için, `traveler_name` alanına yazılan veri ile dokümanın gerçek kimliği (`TRAV-xxx`) farklıdır. Link alanına fiktif isim yazıldığı için validasyon patlamıştır.

### Etkilediği Modüller
- `Trip` (Child Tables)
- Tüm Link içeren DocType'lar.

### Çözüm Denemesi ve Sonraki Aksiyon
Doküman yaratıldıktan sonra dönen `doc.name` değeri bir değişkene alınmalı ve Link alanına bu ID değeri set edilmelidir.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Test senaryolarında Link alanlarını doldururken asla elle isim (String) girmeyin. Bağımlı dokümanı `get_doc` veya `insert` ile oluşturup, dönen `.name` (ID) değerini kullanın. Bu, Naming Series kullanılan dokümanlarda (Traveler, SI, PI vb.) hayati önem taşır.*

## 🚨 Failure Analysis: Trip Segment Mandatory Validation (SCEN-TRIP-001)

### Sebep
Finansal mantığı test ederken, `Trip Flight Segment` tablosundaki operasyonel alanlar (`origin`, `destination`, `departure_date`, `supplier`) boş bırakıldı. Sistem bu alanları veritabanı seviyesinde zorunlu kıldığı için kayıt reddedildi.

### Etkilediği Modüller
- `Trip` (Operational Integrity)

### Çözüm Denemesi ve Sonraki Aksiyon
Finansal regresyon testlerinde bile, segment satırlarına fiktif ama geçerli operasyonel veri (Örn: IST-LHR, Today) basılmalıdır.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Operasyonel DocType'larda (Uçuş, Otel vb.) 'Mandatory' (Zorunlu) kutucukları sadece arayüz için değil, veri bütünlüğü içindir. Test hazırlarken bu alanların bir listesini çıkarın ve mutlaka doldurun.*

## 💡 Success Analysis: Trip Controller "Karar Makamı" (SCEN-TRIP-001)

### Konsept ve Başarı
`Trip` DocType'ı artık sadece veri tutan bir form değil; kârlılığı denetleyen bir kural motorudur. SCEN-TRIP-001 regresyonu ile şu özellikler mühürlenmiştir:
- **Zarar Engelleme:** Satış fiyatı maliyetin altında olan kayıtların `frappe.throw()` ile bloklanması.
- **Whitelisted Invoicing:** `Sales Invoice` yaratma işleminin otomatik değil, `make_sales_invoice` butonuyla (API) kontrollü ve draf olarak başlatılması.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Muhasebe belgeleri (Fatura/Ödeme) her zaman 'Draft' olarak yaratılmalı ve son kontrol kullanıcıya bırakılmalıdır. Karar makamı (Trip) veriyi hazırlar, icra makamı (Sales Invoice) resmileştirir.*

## 🚨 Failure Analysis: Remote Controller Sync (AttributeError)

### Sebep
Lokalde yapılan `trip.py` güncellemeleri (whitelisted metodlar vb.) Railway sunucusuna aktarılmadığı veya Python cache'i temizlenmediği için `AttributeError: 'Trip' object has no attribute 'make_sales_invoice'` hatası alındı.

### Etkilediği Modüller
- `Trip` Python Controller
- Remote API Calls

### Çözüm Denemesi ve Sonraki Aksiyon
SOP-2 (Remote Sync) protokolü işletildi; dosya `base64` ile gönderildi ve `bench restart` (veya modül reload) ile yeni kod aktif edildi.

### 🛡️ Guardrail (Kalıcı Bellek Notu)
*Büyük controller değişikliklerinden sonra sadece 'save file' yeterli değildir. Üretim ortamında (Production) metodun varlığını `bench console` veya regresyon testi ile doğrulamadan UI katmanına geçmeyin.*

