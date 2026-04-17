# 🏛️ İzge Travel: Finansal Operasyon & Muhasebe Protokolü

Bu doküman, ERPNext üzerindeki seyahat operasyonlarının muhasebesel doğruluk ve insan tarafından okunabilirlik prensiplerine göre nasıl yönetildiğini açıklar. 

---

## 💎 1. Temel Muhasebe Mantığı (ERPNext Standartları)
Sistemimiz, karmaşık seyahat işlemlerini ERPNext'in standart **Cari (Customer/Supplier)** ve **Fatura (Invoice)** mantığına indirger. Bu sayede mali müşavirler ve operatörler için veri tutarlılığı sağlanır.

### A. Çift Taraflı Kayıt Sistemi
Her seyahat kaydı (`Trip`), iki ana finansal bacağı tetikler:
1.  **Satış Bacağı (Gelir):** Müşteriye kesilen Satış Faturası.
2.  **Maliyet Bacağı (Gider):** Operatörlere (THY, Otel vb.) kesilen Alış Faturaları.

---

## 🛫 2. Senaryo Uygulama Rehberi (Adım Adım)

### DURUM 1: Normal Satış (Booking)
*İnsan Gözüyle:* Bir müşteri bilet alır, parasını öder (veya borçlanır).
*Sistem Gözüyle:*
- `Trip` kaydı açılır.
- Onaylandığında (`Submit`), **ACC-SINV-001** (Satış) ve **ACC-PINV-001** (Alış) taslak olarak oluşur.
- **Sonuç:** Müşteri borçlanır, Tedarikçi alacaklanır.

---

### DURUM 2: İade ve İptal (Refund Management)
*İnsan Gözüyle:* Yolcu vazgeçti, havayolu ceza kesti, kalan para iade edildi.
*Sistem Gözüyle:*
- **Düzeltme (Amendment):** Orijinal Trip iptal edilir. Bu, eski faturaları da sistemden "temizler" (Accounting Confusion önlenir).
- **Yeni Kayıt:** Yeni bir sürüm oluşturulur. Sadece **net kalan tutarlar** faturalandırılır.
- **Kural:** Hizmet bedeli (Service Fee) genellikle iade edilmez; bu acentenin hakkı olarak sistemde kâr olarak kalır.

---

### DURUM 3: Değişiklik ve Ekstralar (Modifications)
*İnsan Gözüyle:* Yolcu rotasını değiştirdi, üzerine fark ödedi.
*Sistem Gözüyle:*
- Trip içerisindeki ilgili yolcunun satırında `Maliyet` ve `Satış` tutarları güncellenir.
- **Ekstra Gelir:** Müşteriden alınan fark, faturada ek bir kalem olarak görünür.
- **Ekstra Gider:** Havayoluna ödenen fark, alış faturasına yansır.

---

## 📈 3. Örnek Finansal Analiz (Tablo Görünümü)

Müşteriden alınan net 26.000 TL üzerinden bir örnek:

| İşlem Türü | Müşteri (Satış) | Operatör (Maliyet) | Acente Kârı | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| **Bilet Satışı** | 6.500 TL | 5.000 TL | 1.500 TL | Standart Satış |
| **İptal (Cezalı)** | 4.500 TL | 1.000 TL | 3.500 TL | 2.000 TL iade edildi, hizmet bedeli + ceza kaldı. |
| **Değişiklik** | 8.400 TL | 6.100 TL | 2.300 TL | Değişim ücreti farkı eklendi. |

---

## 🛠️ 4. Teknik Doğrulama (Hatasızlık Kontrolü)

1.  **Otomatik Hesap Eşleşmesi:** Tüm "Uçak Bileti" işlemleri otomatik olarak `600 - Yurt İçi Satışlar` hesabına akar.
2.  **Karışıklık Önleme:** Her revizyon kaydı (`-1`, `-2` ekleri ile) bir öncekine bağlıdır (`Amended From`). Geçmiş izlenebilir (Traceability).
3.  **Netleştirme:** Ekstralar ve cezalar, fatura kalemlerinde anlaşılır açıklamalarla yer alır (Örn: "İptal Cezası", "Rota Değişim Farkı").

### DURUM 4: Şirket Kredi Kartı ve Banka Mutabakatı
*İnsan Gözüyle:* Ödemeyi İş Bankası kartıyla yaptık, kart ekstresinde bu harcamayı görmek istiyoruz.
*Sistem Gözüyle:*
- Ödeme `102.01.001 - İŞ BANKASI 4846` hesabından `Payment Entry` ile yapılır.
- Banka mizanında (General Ledger) para çıkışı mühürlenir.
- **Void Durumunda:** Ödeme kaydı iptal edilir; defterde "Para Çıktı/Girdi" izi (cancelled mark) takip edilebilir hale gelir.

### DURUM 5: Geçmiş Dönem İadesi (Vade Farkı)
*İnsan Gözüyle:* Aylar önce aldığım bileti bugün iade ettim. Eski aylar bozulmasın.
*Sistem Gözüyle:*
- **Kural:** Geçmiş dönem mizanını bozmamak için eski bilet İPTAL edilmez.
- **Çözüm:** Bugün tarihli bir **Credit Note (İade Faturası)** kesilir.
- **Sonuç:** Eski ekstreler bakiye bazında korunur, iade hareketi bugünün raporlarına yansır.

---
> 🔗 **Uygulama Sonuçları:** [results.md](results.md)
> 🔗 **Sistem ID Haritası:** [../id_map.md](../id_map.md)
