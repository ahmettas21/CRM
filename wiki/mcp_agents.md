# 🤖 [NAV-A3G2T] MCP ve Ajan Rehberi (Konsept Katmanı)

## Amaç
Bu çalışma alanı içinde ajanın (AI) **3 ana MCP sunucusu** kullanması yapılandırılmıştır. Tüm yapay zeka ajanları aşağıdaki prensipler ve görev ayrımı algoritmasına göre hareket etmek ZORUNDADIR.

## 3 Ana MCP Sunucusu
1. **GitHub MCP** = Repo ve kod işleri
2. **ERPNext Runtime MCP** = Canlı ERP veri ve belge işleri
3. **Frappe Development MCP** = DocType, workspace, script, app, bench geliştirme işlemleri

---

## 🏛️ GENEL PRENSİPLER (Ajan Anayasası)
- Her zaman önce en az riskli MCP’yi kullan.
- **Önce oku, sonra doğrula, en son değiştir.** Kör `create`/`update` yapma.
- Doğrudan production üzerinde write işlemi yapmadan önce her zaman read-only doğrulama yap ve **kullanıcı onayı iste**.
- Bir işlem yapılabiliyorsa önce metadata ve mevcut durum okunmalı.
- **Secret, token, API key, API secret, cookie veya auth bilgilerini ASLA çıktıda açık yazma.**
- Mümkün olan her durumda değişiklikleri küçük ve geri alınabilir adımlarla yap. Gereksiz veya tekrar eden değişiklik yapma.
- Emin değilsen önce sor veya read-only analiz yap.

---

## ⚖️ MCP GÖREV AYRIMI & SEÇİM KURALI

Aşağıdaki karar ağacını uygula:

### 1) GitHub MCP (Kalıcı Kod Değişikliklerini Yönetir)
**Ne Zaman Kullanılmalı?** Konu repo, dosya, branch, commit, PR ise.
**Kurallar:**
- Önce ilgili repo ve dosyaları bul ve mevcut dosyayı oku.
- Büyük değişikliklerde doğrudan `main/master`’a yazma; branch aç, commit et, sonra PR öner.
- Workflow / deployment dosyalarında ekstra dikkatli ol.
- Değişiklik yaptıysan hangi dosyaları neden değiştirdiğini özetle.
- Kod üretimi gerekiyorsa önce *Frappe Development MCP*’den sistem mantığını öğren, sonra *GitHub MCP* ile repo seviyesinde uygula.

### 2) ERPNext Runtime MCP (Canlı Sistemi Yönetir)
**Ne Zaman Kullanılmalı?** Konu ERP içindeki kayıtlar, belge verisi, field metadata, rapor ise.
**Kurallar:**
- İlk adımda `get_doctypes` veya `get_doctype_fields` ile metadata keşfi yap. Kör `create_document` çağrısı YAPMA.
- Sonra `get_documents` ile mevcut kayıtları incele. Yeni belge oluşturmadan önce zorunlu alanları öğren.
- Aynı belgeyi birden fazla kez üretme riskine dikkat et. Canlı finansal belgeler (fatura, ödeme vb.) üzerinde yıkıcı işlemlere karşı çok hassas ol.
- Eğer yalnızca listeleme/analiz yeterliyse `write` yapma.

### 3) Frappe Development MCP (Geliştirme Sistemini Yönetir)
**Ne Zaman Kullanılmalı?** Konu DocType, workspace, custom script, app, bench, development işlemleri ise.
**Kurallar:**
- Önce bench/app yapısını keşfet. Geliştirme sürecini planla.
- Yeni DocType veya workspace üretmeden önce benzer bir yapı zaten var mı kontrol et.
- Bench komutlarını (migration, reload, patch, vb.) çalıştırırken yıkıcı etkileri açısından dikkatli değerlendir. Etkiyi raporla.
- Runtime veri işlemlerini BUNUNLA YAPMA. Bu MCP geliştirme ortamı içindir.

### 🎯 Kombo İşlemler (Multi-MCP)
- **İş hem development hem repo değişikliği içeriyorsa:** Önce *Frappe Dev MCP* ile analiz/üretim planı yap, sonra *GitHub MCP* ile dosya değişikliklerini işle.
- **İş hem canlı veri hem geliştirme içeriyorsa:** Önce *ERPNext Runtime MCP* ile canlı şemayı ve veriyi doğrula, sonra *Frappe Dev MCP* ile geliştirmeyi planla, en son *GitHub MCP* ile repoya uygula.

---

## 🛠️ ÇALIŞMA TARZI & ÇIKTI FORMATI
Her görevde şu döngüyü izlemelisin:
1. Hangi MCP’nin uygun olduğunu seç.
2. Mevcut durumu, metadata'yı, yapı ve izin kontrolünü yap (Oku).
3. Değişiklik planını kısa yaz.
4. Küçük, kontrollü adım uygula & sonucu doğrula.
5. Yapılan değişiklikleri özetle (Kısa ve operasyonel yaz).
6. **Hata Yakalama:** Başarısız olursa hatayı şu şekilde sınıflandır: `auth` / `permission` / `validation` / `config` / `network` / `repository state` / `bench state`. 

> 🔗 **Deep Dive Teknik Kurulum & Config:** [raw/mcp_setup.md](../raw/mcp_setup.md)
