# 🏛️ LLM Wiki: Evrensel Hafıza Protokolü (v2.0)

Bu doküman, herhangi bir yazılım projesini "kendi kendini belgeleyen ve hatalardan ders çıkaran" ölümsüz bir yapıya dönüştürmek için tasarlanmıştır.

## 1. Mimari Katmanlar (Architecture Layers)
- **`raw/` (Kaynak Katmanı):** Projenin teknik referans kitapları. Kodun derin matematiği, SQL şemaları ve değişmez dokümanlar.
- **`wiki/` (Kavramsal Katman):** AI tarafından yazılan, insanların (ve diğer AI'ların) sistemi anlamasını sağlayan canlı hafıza.
- **`.agents/rules/llm-wiki.md` (Anayasa):** AI'ın nasıl davranacağını belirleyen kural seti.

## 2. Temel Kuralları (Core Rules)

### ♊ İkiz Doküman (Twin Document Rule)
Her yeni özellik veya kod bloğu hem `wiki/` (kavramsal özet) hem de `raw/` (teknik derinlik) katmanında eş zamanlı belgelenmelidir. **Öksüz kod (belgelenmemiş kod) yasaktır.**

### 🛑 "Asla Tahmin Etme" Zırhı (Self-Verification)
- Yapay zeka, sistemde olmayan bir şeyi biliyormuş gibi yapamaz. 
- Bir iddiayı doğrulamak için önce `wiki/` dizinini, sonra fiziksel dosya sistemini (`grep`/`ls`) taramalıdır. 
- Bilgi yoksa uydurmak yerine kullanıcıya sormalıdır.

### 🛡️ Sandbox & Arşivleme (Anti-Clutter)
- Kök dizin (Root) sadece ana operasyonel dosyaları barındırabilir.
- Tüm denemeler, testler ve geçici dosyalar `tmp/` veya `denemeler/` içinde yapılmalıdır.
- Başarılı olan testler arşivlenmeli, başarısızlar silinmelidir.

### 🔗 Derin Bağlantı Standardı (Deep Dive)
Wiki ile Raw arasındaki köprü her zaman şu formatta tıklanabilir linklerle kurulmalıdır:
`> 🔗 **Derin Teknik Kök Neden (Deep Dive):** [raw/referans.md](../../raw/referans.md)`

### 🚀 Mission Control (Niyet Takibi)
`wiki/mission_control.md` üzerinden kullanıcının yüksek seviyeli hedefleri (Neden yapıyoruz?) ve tamamlanma durumları takip edilmelidir.

## 3. Geliştirme Yaşam Döngüsü (Lifecycle)
**Planla -> Test Et (Sandbox) -> Onay Al -> Entegre Et & Dokümante Et.**
