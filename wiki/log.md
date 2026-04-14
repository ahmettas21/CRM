# 📝 Değişim Günlüğü (Log)

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
### 🛡️ Tam Cari Kontrol & Railway SSH Protokolü (Final)
- **Accounting Otomasyonu (v2.0):** `Trip` formu onaylandığında hem Müşteri (Satış Faturası) hem de tüm Tedarikçiler (Alış Faturası) için otomatik fatura oluşturma mantığı tamamlandı.
- **Teknik Standartlaşma:** `hooks.py`, `trip.py`, `trip.js` ve `setup.py` dosyaları Frappe Skill protokollerine (%100 flt(), super() çağrıları, no manual commit) uygun hale getirildi.
- **Kritik Hata Onarımı:** Railway üzerinde kopan veritabanı (`db_host`) ve Redis bağlantıları `site_config.json` ve `common_site_config.json` üzerinden dinamik olarak fixlendi.
- **Sert Protokol Kurulumu:** `llm-wiki.md` ve `wiki/INDEX.md` dosyalarına, sunucuya sadece `railway ssh` ve `Base64` yöntemiyle müdahale edilebileceğine dair "Sert Kurallar" eklendi.
- **Deployment Başarısı:** Tüm sistem `monorail.proxy.rlwy.net` üzerinden Railway üretim ortamına saniyeler içinde, hatasız bir şekilde akıtıldı ve `bench migrate` ile devreye alındı.
