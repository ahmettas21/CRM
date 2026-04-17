# 🎨 Gelişmiş UI / UX Standartları

Bu kütük, projenin ekranlarında karmaşıklığı engellemek, formları okunabilir kılmak ve kurumsal hızlanmayı sağlamak amacıyla alınan kesin kuralları barındırır. Bu kurallar özel olarak Frappe form yeteneklerine göre adapte edilmiştir.

## Kurallar

### 1. [RULE-F8G9T] Kompakt Modal Mimarisi
Frappe "Satır Düzenleme" (Child Table Modal) ekranları default olarak çok dar (tek sütun) açılır. Bu nedenle form 3 sütuna zorlanmaz, HTML vb. block elementler ile düzen BOZULMAZ. Bunun yerine alt-tablolar **SADECE 2 KOMPAKT SÜTUNA** bölünmelidir:
- **Yapı:** 1 adet `Section Break` açılır, hemen ardından içeriği tam ikiye bölecek 1 adet native `Column Break` atılır. 
- **Sonuç:** Ekranda CSS çatışması olmadan doğrudan Frappe'nin kendi sütun dağıtımına emanet edilir.

### 2. [RULE-K4L5P] Hızlı Giriş (Quick Entry) Zorunluluğu
Sayfa geçişleri kullanıcının akışını bozar. Eğer bir "Trip" (Seyahat) ekranında yeni bir "Yolcu" (Traveler) eklenecekse; ilgili DocType'ların (`traveler.json`, `customer.json` vb.) içinde kesinlikle `quick_entry: 1` bayrağı aktif edilmelidir. Kullanıcıyı başka sayfaya yönlendirmemek katı bir emirdir.

### 3. [RULE-V2W3N] Emojili Başlık Kuralı
Kullanıcının formlardaki onlarca alan içerisinde kaybolmaması için `Section Break` başlıklarında Evrensel Piktogramlar (Emojiler) kullanılır. Kurumsal yapıya zarar vermeyecek derecede zarif emojiler seçilmelidir.
- Operasyonel veya Detay: 🏨, 🛫, 🏷️, 🔖
- İletişim / Müşteri: 📋, 👤
- Finans / Muhasebe: 💰, 💳

### 4. [RULE-Q6R7M] Dinamik Metin Formatlama (Live UX Formatting)
Havacılık ve Turizm gibi hata affetmeyen sektörlerde klavye hatalarını (caps lock) önlemek için Client-Side (JS) anlık düzeltme yapılması zorunludur:
- **UPPERCASE (Tamamen Büyük):** PNR, Bilet No, Reservation Ref, Havayolu İstasyonları (IST, SAW vs).
- **LOWERCASE (Tamamen Küçük):** Email adresleri.
- **TITLE CASE (Baş Harf Büyük):** Yolcu İsmi, Otel Adı, Tedarikçi İsmi.
*Kullanıcı formdan alan dışına (blur) çıktığı an "Client Script" üzerinden anında değişiklik uygulanmalıdır.*

### 5. [RULE-X9Y8Z] Master Data (Referans) Standartı
Formlarda tekrar eden sabit, riskli veriler (Havalimanı, Havayolu, Ülke vb.) asla serbest metin ('Data') olarak bırakılamaz. Bu durum raporlama bütünlüğünü (IST vs. İST) bozar. Mutlaka IATA koduna veya tanımlı AutoName kuralına göre çalışan Özel DocType'lara ('Link' tipinde) bağlanmalıdır. Personel eğer bulamazsa "Yeni Yarat" özelliği ile standartlara uygun eklemelidir.

### 6. [RULE-D4B7C] İngilizce Mutasyon Kuralı (IATA Strict)
Global biletleme kod alanlarında (`airport_code`, `airline_code`, `icao_code`) Türkçe karakter (ş, ğ, ü, ç, ö, ı, İ) barındırılamaz. İlgili veri, Script yardımıyla Regex haritalaması yapılarak zorla İngilizce Karakter setine (S, G, U, C, O, I) ve UPPERCASE (Büyük Harf) moduna sokulmalıdır. 
- **Örnek:** 'ışık' -> 'ISIK', 'GÖKÇEN' -> 'GOKCEN'

### 7. [RULE-P1A2M] Akıllı Klonlama (+1 Duplicate Engine)
Grup rezervasyonu/Seri biletleme yapılan (Frappe Editable Grid) yapılarda personelin 50 kişilik bir kafileyi girerken tekrar eden fiyat/tedarikçi verilerini yazmasını engellemek için Client Script ile oto-kopya motoru devreye alınmalıdır:
- Bir satıra (Traveler) değer eklendiğinde sistem bir üst satırdaki finansal verileri aynen alt satıra kopyalar.
- `ticket_no` (Bilet Numarası) gibi ardışık dizileri Regex `(/(.*?)(\d+)$/)` ile yakalayıp "Son Rakam + 1" şeklinde arttırarak yazar.
