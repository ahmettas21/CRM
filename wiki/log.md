# 📝 [LOG-S9T0U] Değişim Günlüğü (Log)

Tüm teknik değişimler burada kronolojik olarak kaydedilir.

## [2026-04-13]
### 🚀 Railway MCP Entegrasyonu
- Railway CLI yüklendi (`v4.36.1`).
- `mcp_config.json` dosyasına `Railway` sunucusu eklendi.
- API Token (`293763ac...`) ile yetkilendirme sağlandı.
- `considerate-magic` projesi yerel dizine linklendi.

### 🏛️ LLM Wiki Kurulumu
- `.agents/rules/llm-wiki.md` oluşturuldu.
- `wiki/` klasörü başlatıldı (`index.md`, `log.md`, `mission_control.md`).

### 🔍 ERPNext Hata Analizi
- Loglar incelendi. `Container failed to start: The executable cd could not be found.` hatası tespit edildi.
- Çözüm önerisi: Start Command kabuk üzerinden çalıştırılmalı (`sh /usr/local/bin/railway-cmd.sh`).

## [2026-04-14]
### ✈️ Izge Travel Core Mimari Kurulumu
- `izge_travel` custom app'i bench içinde oluşturuldu.
- Sitenin geliştirici modu (`developer_mode: 1`) aktif edildi.
- 4 adet çekirdek DocType kod seviyesinde ayağa kaldırıldı:
    - `Traveler` (Gezgin kartı, Naming: TRAV-)
    - `Trip` (Seyahat operasyonu, Naming: TRIP-)
    - `Trip Segment` (Çoklu seyahat ayakları - Child Table)
    - `Traveler Emergency Contact` (Acil durum kişileri - Child Table)
- Python validasyonları (`passport_expiry`, `return_date` kontrolü vb.) yazıldı.
- GitHub (`ahmettas21/CRM`) üzerinden üretim ortamına senkronizasyon ve `bench migrate` başarılı.

### 💰 Muhasebe ve Finansal Altyapı
- İzge Turizm için "Ana Satıcı (Principal - Model B)" muhasebe kurgusu kararlaştırıldı.
- `muhasebekonusması.md` içerisindeki tüm detaylar (TDHP kodları, KDV şablonları, POS akışları, iade senaryoları) kümülatif ve kesintisiz şekilde `muhasebe_uygulama_plani.md` (v2.0) Master Planına aktarıldı.
- Hafıza kaybını önlemek için `.agents/rules/llm-wiki.md` dosyasına "Hafıza Kaybı Yasağı" (No Memory Loss) kuralı eklendi.

### 💻 Trip UI Geliştirmeleri (Client Script)
- `Trip` DocType'ı ve 4 adet Child Table (`Trip Flight Segment`, `Trip Hotel Stay`, `Trip Service Item`, `Trip Charge`) için finansal hesaplama scripti (`trip.js`) yazıldı.
- `Frappe Client Script Skill` referans alınarak; `frm.doc` yerine `frappe.model.set_value()` kullanıldı ve anlık `Sale Amount` ile `Profit` hesaplamaları eklendi.
- Kod çevrimiçi ortama (Railway) `git push` üzerinden başarıyla entegre edildi.

### 🏭 Cari Kart Yapılandırması (Customer & Supplier)
- Müşteri (Customer) ve Tedarikçi (Supplier) DocType'ları için Standart Frappe Core ayarları kod tabanlı (Patch/Setup Script) olarak yapılandırıldı.
- Standart `Selling Settings` ve `Buying Settings` üzerinden adlandırma kuralı `Naming Series`'e çekildi.
- `Property Setter` kurgusu ile Customer serisine `M-.YYYY.-.####`, Supplier serisine `T-.YYYY.-.####` şablonu atandı.
- Tüm bu güncellemelerin sisteme `bench migrate` sonrasında (after_migrate) otomatik entegre olması için `hooks.py` kancası `/setup.py` dosyasına bağlandı.

### 📦 Hizmet ve Satış Kalemleri (Items & Item Groups) Yapılandırması
- İzge Travel biletleme ve operasyonlarında kullanılacak ana Item ürünleri oluşturuldu.
- **Gruplar:** `Uçak Bileti`, `Otel`, `Vize`, `Hizmet Bedeli`, `Vergi ve Harçlar`
- **Kalemler (Items):** Yurt İçi Uçak, Yurt Dışı Uçak, Havalimanı Vergisi, Acente Komisyonu (Gelir/Gider).
- *Teknik Not:* Vergi şablonları (Tax Templates) doğrudan Hesap Planı'ndaki (Chart of Accounts) KDV hesaplarına (191/391) "Account" bağımlılığı içerdiği için Python tarafında kodlanması ertelendi. Bu kurgu şirket kurulumundan sonra arayüzden veya ayrı bir aktarım ile yapılacaktır.
- Betik `setup_items_taxes.py` olarak yazıldı ve ana setup kancasına eklendi.

### 🧾 Trip & Satış Faturası (Sales Invoice) Entegrasyonu
- Operasyonlardan gelen müşteri bakiyesi istekleri doğrultusunda **Otomatik Taslak Fatura** kurgusu uygulandı.
- `trip.py` içerisinde `on_submit` ve `on_cancel` kancaları aktifleştirildi.
- Biletçi (Acente çalışanı) bir formu `Submit` ettiği an arka planda **Draft (Taslak)** statüsünde Sales Invoice oluşur.
- Olası iptallerde, faturanın statusüne bağlı olarak taslak ise silinir, onaylı ise `cancel` işlemine alınır.
- `_ensure_item` kontrolcüsüyle, item bulunamazsa kullanıcıya hata vermek yerine arka planda dinamik olarak Item yaratılması (Fall-back) sağlandı.
- Müşterinin (Müşterinin Carisine) bakiyesinin akması, oluşan bu faturanın muhasebe personeli tarafından kontrol edilip onaylanmasına (Submit edilmesine) bağlandı.
- ### 🛡️ Tam Cari Kontrol & Railway SSH Protokolü (Final)
- **Accounting Otomasyonu (v2.0):** `Trip` formu onaylandığında hem Müşteri (Satış Faturası) hem de tüm Tedarikçiler (Alış Faturası) için otomatik fatura oluşturma mantığı tamamlandı.
- **Teknik Standartlaşma:** `hooks.py`, `trip.py`, `trip.js` ve `setup.py` dosyaları Frappe Skill protokollerine (%100 flt(), super() çağrıları, no manual commit) uygun hale getirildi.
- **Kritik Hata Onarımı:** Railway üzerinde kopan veritabanı (`db_host`) ve Redis bağlantıları `site_config.json` ve `common_site_config.json` üzerinden dinamik olarak fixlendi.
- **Sert Protokol Kurulumu:** `llm-wiki.md` ve `wiki/INDEX.md` dosyalarına, sunucuya sadece `railway ssh` ve `Base64` yöntemiyle müdahale edilebileceğine dair "Sert Kurallar" eklendi.
- **Deployment Başarısı:** Tüm sistem `monorail.proxy.rlwy.net` üzerinden Railway üretim ortamına saniyeler içinde, hatasız bir şekilde akıtıldı ve `bench migrate` ile devreye alındı.

## [2026-04-17]
### 🛡️ Trip Controller — Kural Motoru (SCEN-TRIP-001)
- `trip.py` → `check_margin_guardrail()` metodu eklendi: `Total Sale < Cost` olanlar `validate` aşamasında bloklanır.
- `make_sales_invoice` whitelisted API metodu eklendi: Trip'ten tek tuşla Draft Sales Invoice oluşturulur.
- `on_submit` otomatik fatura mantığı kaldırıldı; artık fatura sadece kullanıcı tetiklemesiyle yaratılır.
- `create_sales_invoice` metoduna eksik `si = frappe.new_doc("Sales Invoice")` satırı eklenerek kritik bug giderildi.
- SOP-5 döngüsü ile 7 kademeli hata analizi yapıldı (Traveler Link, Full Name, Customer Mandatory, Document ID, Fieldname, Mandatory Fields, Airport Link).
- **Sonuç:** SCEN-TRIP-001 → PASSED (Guardrail aktif, Production'da doğrulandı).

### 🎨 Trip UI — Fatura Oluştur Butonu (SCEN-TRIP-002)
- `trip.js` → `refresh()` metoduna "Fatura Oluştur" custom butonu eklendi.
- **Koşullar:** `docstatus == 1` (Submitted), `profit > 0` (Kârlı), `!customer_invoice_no` (Faturasız).
- Buton, `frappe.confirm` ile onay ister, ardından `frm.call('make_sales_invoice')` ile API'yi tetikler.
- Mükerrer fatura koruması: `customer_invoice_no` doluysa buton görünmez ve API `ValidationError` fırlatır.
- `trip.py` Railway sunucusuna SOP-2 protokolü ile (base64 senkronizasyon) gönderildi.
- **Sonuç:** SCEN-TRIP-002 → PASSED (UI tetikleyici, Draft SI oluşturma ve mükerrer engelleme doğrulandı).

### 📊 Dashboard Blueprint & İlk Regresyon (SCEN-DASH-001)
- `wiki/dashboard_blueprint.md` oluşturuldu: 4 panelli yönetim dashboard tasarımı.
  - Panel 1: Sales & Profitability Monitor (Trip bazlı satış/kâr)
  - Panel 2: ADM Alert Panel (Havayolu borç dekontları)
  - Panel 3: Chargeback Risk Tracker (KK yaşlandırma)
  - Panel 4: Operational Health (Zararlı/faturasız Trip tespiti)
- Her panel için veri kaynağı (SQL), filtreler, widget tipleri (Number Card, Chart, Table) detaylandırıldı.
- `run_scenario_dash_001.py` yazıldı: 6 aşamalı BDD regresyonu (syntax, margin, aggregate, filtre, widget, health).
- **Sonuç:** SCEN-DASH-001 → PASSED (2 Trip, 26.800 TL Satış, 9.700 TL Kâr, %36.2 Marj).

### 📚 Dokümantasyon Güncellemeleri
- `wiki/lessons_learned.md`: 6 yeni Failure Analysis + Guardrail eklendi (Traveler Link, Full Name, Customer, Document ID, Mandatory Fields, Remote Sync/AttributeError).
- `wiki/scenarios/index.md`: SCEN-TRIP-001, SCEN-TRIP-002, SCEN-DASH-001 eklendi.
- `raw/scenarios/`: 8 adet log/error dosyası arşivlendi.

### 🏛️ Konsolide Mimari Doküman (MASTER_OVERVIEW)
- `wiki/MASTER_OVERVIEW.md` oluşturuldu: Projenin "tek kaynak gerçeği" (Single Source of Truth).
- 4 bölüm: Finans Edge-Case Mimarisi, Trip Controller & Faturalama, Dashboard Blueprint, Açık Kalan Adımlar.
- 7 kalıcı Guardrail, 4 teknik borç, 14 gelecek görev kataloglandı.
- `wiki/index.md` navigasyonuna MASTER_OVERVIEW ve Dashboard Blueprint linkleri eklendi.

### 🖥️ Kullanıcı Ekran Akışları (UX Flows)
- `wiki/UX_FLOWS.md` oluşturuldu: Satışçı (10 adımlık Trip lifecycle) ve Muhasebe (5 iş akışı) ekran akışları.
- İptal/İade, ADM ve Chargeback kriz yönetimi akışları adım adım tanımlandı.
- Mermaid akış diyagramı ile roller arası geçişler görselleştirildi.

### ⚙️ Setup Checklist
- `wiki/SETUP_CHECKLIST.md` oluşturuldu: ~38 zorunlu ERPNext ayarı.
- 10 kategori: Company, Chart of Accounts, Items, Customer/Supplier, Mode of Payment, Payment Terms, Airport/Airline, Accounts/Selling/Buying Settings, Custom App.
- Kritiklik seviyeleri: 🔴 ~20 kritik, 🟡 ~12 önemli, 🟢 ~6 opsiyonel.
- `wiki/index.md` navigasyonuna UX Flows ve Setup Checklist linkleri eklendi.

### 🚀 MVP Setup (Pilot Minimum Paket)
- `SETUP_CHECKLIST.md` sonuna MVP tablosu eklendi: 13 olmazsa olmaz ayar + 21 Phase 2 ayarı.
- Pilot akış: Company → CoA (5 hesap) → Item Groups → Customer Group → 1 Supplier → 1 Airport → 1 Airline → App = Trip → Submit → Fatura → Tahsilat.
- `MASTER_OVERVIEW.md` Bölüm 4'e MVP Setup referansı eklendi.

### 🖥️ UX Flows v2.0 — Kullanılabilirlik Denetimi
- `wiki/UX_FLOWS.md` v1.0 → v2.0 güncellendi.
- Her adıma kullanılabilirlik etiketi eklendi: ✅ OK (7), ⚠️ Dikkat (5), 🔍 Gözden Geçir (4).
- En yüksek riskli noktalar: Uçuş segmenti girişi (13 alan), Amend (fatura zinciri), Credit Note (pro-rata hesap), Chargeback JE (3 bacak).
- Kullanılabilirlik Özet Tablosu eklendi (16 satırlık tam matris).

### 🎓 Eğitim Senaryosu 001
- Uçtan uca pilot eğitim senaryosu UX_FLOWS.md'ye eklendi.
- Hikaye: Gidiş-Dönüş + Hizmet Bedeli + Kredi Kartı + Kısmi No-Show Vergi İadesi.
- 4 fazlı akış: Satış (10 adım) → Muhasebe Onay (4 adım) → No-Show İade (4 adım) → İade Ödemesi (2 adım).
- 7 maddelik doğrulama kontrol listesi + 13 MVP ayar bağımlılık matrisi eklendi.

### 🚀 Pilot-001 Hazırlık
- `tmp/verify_mvp_setup.py` oluşturuldu ve Railway production'da koşturuldu.
- **Sonuç: 13/13 PASS** — Tüm MVP ayarları hazır.
- Canlı değerler: Company=İzge Turizm, Debtors=120.01, Creditors=320.02, Banka=İŞ BANKASI 4846, 15 Supplier, 5 Airport, 2 Airline.
- `wiki/mission_control.md` v4.0 → v5.0 güncellendi: Pilot-001 planı eklendi (4 faz, 20 adım, 7 doğrulama noktası).
- Durum panosuna: Dokümantasyon Seti ✅, MVP Setup ✅, Pilot-001 ⏳ AKTİF eklendi.

### 🎉 Pilot-001 Faz 1-2: Otomatik Regresyon (PASSED)
- `tmp/run_pilot_001_phase1_2.py` yazıldı ve Railway production'da koşturuldu.
- **Sonuç: 7/7 PASSED** — Trip → SI → PE → GL akışı uçtan uca doğrulandı.
- Canlı belgeler: TRIP-2026-00135, ACC-SINV-2026-00019, ACC-PAY-2026-00012.
- GL doğrulama: AR=120.01 ALICILAR, Gelir=600.01 YURT İÇİ SATIŞLAR, Banka=102.01.001 İŞ BANKASI.
- Müşteri final AR bakiye: 0 TL ✅
- **Gözlem:** on_submit PI/CC_JE otomatik yaratılmadı — trip.py tam sync gerekli (teknik borç T4).
- `raw/pilot/PILOT-001_phase1_2_success_log.txt` arşivlendi.
- `wiki/mission_control.md` güncellendi: Pilot-001 Faz 1-2 ✅ PASSED, Faz 3-4 ⏳ Sırada.

### 🎉 Pilot-001 Faz 3-4: Otomatik Regresyon (PASSED)
- `tmp/run_pilot_001_phase3_4.py` yazıldı ve Railway production'da koşturuldu.
- **Sonuç: 8/8 PASSED** — Credit Note + Refund PE + GL + P&L doğrulandı.
- Canlı belgeler: CN=ACC-SINV-2026-00020, Refund PE=ACC-PAY-2026-00013.
- Orijinal SI (ACC-SINV-2026-00019): Bozulmadı ✅ (Immutable Ledger prensibi doğrulandı).
- GL net: Gelir=3.600 TL, Banka=3.600 TL, AR=0 TL.
- `raw/pilot/PILOT-001_phase3_4_success_log.txt` arşivlendi.

### 🏆 Pilot-001 Final: 15/15 PASSED
- Tüm 4 faz (Satış → Muhasebe → No-Show → İade) otomatik regresyonla doğrulandı.
- Faz 1-2: 7/7, Faz 3-4: 8/8 = Toplam 15/15 PASSED.
- `wiki/mission_control.md` güncellendi: Pilot-001 TOPLAM ✅ 15/15 PASSED.
- Sonraki adım: Manuel UI pilotu → Dashboard Script Reports.

### 🌍 HOTEL, TOUR ve SERVICE Demo Paketleri Hazırlandı
- 2025-2026 turizm trendlerine (Lüks Kapadokya, Vizesiz Balkan Turu, VIP Schengen) uygun BDD senaryoları tasarlanarak indexlendi.
- `SCEN-TRIP-HOTEL-001`, `SCEN-TRIP-TOUR-001` ve `SCEN-TRIP-SERVICE-001` test betikleri (**tmp/** altında) gerçek satış fiyatları, KDV oranları ve finansal margin (kâr) formülleri ile dolduruldu.
- `wiki/mission_control.md` güncellendi ve Demo Paket detayları eklendi.
- `wiki/UX_FLOWS.md` dosyasına satışçıların veri girerken kullanacağı KDV/Gider/Satış kuralları (Adım 5) demo değerlerle dahil edildi.
- **Sonraki Adım:** `trip.py` entegrasyonu tamamlandığında Railway üzerinden bu 3 regresyon script'i otomatik olarak test edilecek.
