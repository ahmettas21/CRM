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
