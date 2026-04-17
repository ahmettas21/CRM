# ⚙️ [TECH-M4C1P] MCP Kurulum ve Konfigürasyon (Teknik Deep Dive)

## Genel Mimari
Model Context Protocol, Antigravity altında JSON listesi (`mcp_config.json`) şeklinde yapılandırılmıştır. Bir MCP'nin sisteme sağlıklı bind edilebilmesi için şu şema kullanılır:
1. `command` genellikle Node/npx paketleri veya executable'lardır.
2. `args` ilgili argümanlardır.
3. `env` token/dizin bağlamı taşır.  
**ÖNEMLİ KURAL:** Hiçbir secret (token vb.) hardcoded olarak JSON içinde barındırılamaz. JSON içinde ortam değişkeninden (`$env:GITHUB_PERSONAL_ACCESS_TOKEN` vb.) kalıtım alınması için User Environment objeleri tanımlanır.

## Kayıtlı Sunucular (Standart Şema)

### 1) GitHub MCP
- **Modül Formatı:** NPM -> `@modelcontextprotocol/server-github`
- **Kullanılan Env:** `GITHUB_PERSONAL_ACCESS_TOKEN` (Sistemden otomatik kalıtılır)
- **Token Türü:** Fine-grained tercih edilmelidir. Ancak limitlerine takılırsa Klasik (Personal Access Token) kullanılabilir.

### 2) ERPNext API MCP (`@casys/mcp-erpnext`)
- **Modül Formatı:** NPM -> `@casys/mcp-erpnext`
- **Görev:** CANLI sistem (Production) belgelerini okuma/yazma, listeleme ve canlı metadata analizi. Dev işlemleri BURADA YAPILMAZ.
- **Kullanılan Env:**
  - `ERPNEXT_URL`: Hedef Railway üretim bandı URL'si.
  - `ERPNEXT_API_KEY`: Ayrıcalıklı kullanıcı anahtarı.
  - `ERPNEXT_API_SECRET`: Ayrıcalıklı kullanıcı şifresi.
- **Kabiliyet Sınırı:** Canlı instance'ı (production) modifiye etme potansiyeline sahiptir, bu yüzden write komutlarında (`update_document`, `create_document`) LLM her halükârda önce read-only keşif yapmalı, ardından kullanıcıdan insiyatif/onay istemelidir.

### 3) Frappe Dev MCP (`frappe-dev-mcp-server`)
- **Modül Formatı:** NPM -> `frappe-dev-mcp-server`
- **Görev:** GELİŞTİRME sistemi. App yapısı, DocType üretme, Bench komutları. Canlı veri işlemleri BURADA YAPILMAZ.
- **Kullanılan Env:** 
  - `FRAPPE_PATH`: Hedef projenin kök yolu, örneğin `C:\Users\asus\Desktop\crm`.  
- **Kabiliyet Sınırı:** Bench root erişimi sağlar. Yıkıcı etki potansiyeli yüksektir (migration, patch). Mutlaka durum değerlendirmesi yapılarak çalıştırılmalıdır.

## 🛡️ Hata ve Teknik Sınıflandırma
Sistem herhangi bir MCP aracından reject/hata dönerse, LLM körü körüne denemeye devam etmek yerine arızanın tipini terminal loglarına bakarak raporlamalıdır:
- *Auth / Permission* (Kapsam veya kullanıcı yetersiz)
- *Validation / Mismatch* (Eksik alan veya tutarsız schema)
- *Config / Network* (Port erişimi, URL yanlışlığı)
- *Repository / Bench State* (Dosya format hatası, git kilidi)

> 🔗 **Kavramsal Kullanım:** [wiki/mcp_agents.md](../wiki/mcp_agents.md)
> 🔗 **Tüm İlgili Kurallar:** [.agents/rules/llm-wiki.md](../.agents/rules/llm-wiki.md)
