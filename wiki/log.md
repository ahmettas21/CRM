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
