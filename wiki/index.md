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
- **Bağlantı**: Sunucuya IP/Port ile değil, daima `railway ssh` ile bağlanılmalıdır.
- **Dizin Yapısı**: Uygulama asla matruşka (iç içe 3+) klasöre gömülemez.
- **Komut Gönderimi**: Karmaşık komutlar için daima PowerShell `Base64` sarmalama kullanılır.
- **Konfigürasyon**: Veritabanı ve Redis adresleri asla manuel silinemez.

## 🛠️ Mevcut Durum (Özeti)
İzge Turizm Accounting otomasyonu (Tam Cari Kontrol) %100 tamamlanmış ve Railway sunucusuna yukarıdaki protokol ile aktarılmıştır.
