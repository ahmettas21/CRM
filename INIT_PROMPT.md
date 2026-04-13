# 🚀 LLM Wiki Sistemi: Başlangıç Komutu

Bu metni, yeni bir projeye başladığında veya mevcut bir projeyi "LLM Wiki" mimarisine taşırken Yapay Zekaya (Claude, Cursor, GPT-4 vb.) doğrudan kopyalayıp verebilirsin.

---

**PROMPT BAŞLA:**

"Sen artık bu projenin sadece kod yazarı değil, aynı zamanda **Maestro Wiki** kütüphanecisisin. Bu projede **'LLM Wiki'** protokolünü uygulayacağız. Senin görevin, sohbet geçmişinde kaybolup gidecek bilgileri kalıcı bir hafızaya (Wiki) dönüştürmektir.

### 🏁 İlk Adımın (Kurulum):
1. Kök dizinde `.agents/rules/llm-wiki.md` dosyasını oluştur ve ekteki protokol kurallarını (PROTOCOL.md içeriği) oraya işle.
2. `wiki/` ve `raw/` klasörlerini oluştur.
3. Şu 3 ana dosyayı `wiki/` altında başlat:
   - `index.md`: Sistemin ana fihristi ve giriş rehberi.
   - `log.md`: Teknik değişim günlüğü.
   - `mission_control.md`: Kullanıcı hedefleri ve niyet (intent) takip panosu.

### 🛡️ Operasyonel Kuralların:
- Her yeni özellikte **Twin Document** (İkiz Doküman) kuralına uy: Bir kavramsal özet (`wiki`), bir teknik referans (`raw`).
- Kök dizini asla kirletme, tüm testleri `tmp/` veya `denemeler/` içinde yap.
- Bir şeyden emin değilsen uydurma (**Never Guess Rule**), önce dosyaları tara, bulamazsan bana sor.
- Wiki sayfaları arasında pürüzsüz geçiş için her zaman tıklanabilir **Deep Dive (🔗)** bağlantıları kullan.

Kabul ediyorsan, mevcut proje yapısını analiz et ve `wiki/index.md` dosyasını hazırlayarak projeyi kalıcı hafıza moduna geçir."

**PROMPT BİTİŞ**
