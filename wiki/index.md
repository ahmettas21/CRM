# 📖 Maestro Wiki
Hoş geldiniz. Bu proje **LLM Wiki** protokolü ile yönetilmektedir.

## 🧭 Navigasyon
- [**Mission Control**](mission_control.md): Mevcut hedefler ve proje durumu.
- [**Change Log**](log.md): Teknik değişim günlüğü.
- [🧠 **Lessons Learned**](lessons_learned.md): Acı tecrübeler ve altın çözümler.
- [**AI Oath**](oath.md): Sadakat ve dürüstlük yemini.
- [**Infrastructure**](../raw/infrastructure.md): Altyapı ve sistem mimarisi.

## 🛑 Sert Protokoller (Strict Protocols)
- [**☁️ Cloud Operasyon Merkezi**](cloud.md): Sunucu yönetimi ve Deployment protokolleri.
- **Bağlantı**: Sunucuya IP/Port ile değil, daima `railway ssh -s erpnext --environment production` komutuyla bağlanılmalıdır.
- **Dizin Yapısı**: Uygulama dosyaları asla matruşka (iç içe 3+) klasöre gömülemez. İdeal yapı: `apps/APP_NAME/APP_NAME/` şeklindedir.
- **Komut Gönderimi**: Karmaşık komutlar asla doğrudan gönderilmez. Daima PowerShell üzerinde `[Convert]::ToBase64String` ile sarmalama yapılmalıdır.
- **Konfigürasyon**: `site_config.json` veya `common_site_config.json` dosyalarındaki `db_host` ve `redis` adresleri asla manuel silinemez, değiştirilemez.

## 🛠️ Mevcut Durum (Özeti)
İzge Turizm Accounting otomasyonu (Tam Cari Kontrol) %100 tamamlanmış ve Railway sunucusuna yukarıdaki protokol ile aktarılmıştır.
