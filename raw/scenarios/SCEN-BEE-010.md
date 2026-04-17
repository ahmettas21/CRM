# SCEN-BEE-010: Kur Farkı ve Multi-Currency Krizi (Test Case)

## 📌 Senaryo Açıklaması
Bilet satış anındaki döviz kuru ile tahsilat (veya iade/ödeme) anındaki döviz kuru farklı olduğunda; aradaki farkın (kârın/zararın) orijinal bilet maliyetini bozmadan, ERPNext tarafından `Exchange Gain/Loss` (Kur Farkı Gelir/Gider) hesabına otomatik (Realized) yansıtılmasının test edilmesi.

## 🧪 BDD Formatı (Given - When - Then)

### 1. GIVEN (Ön Koşullar)
- Sistemde "Exchange Gain/Loss" isimli bir GL (Defter-i Kebir) hesabı tanımlıdır.
- Tedarikçiye (Örn: Lufthans Turizm) 15 Ocak tarihinde bilet maliyeti olarak **1.000 EUR** tutarında bir Alış Faturası (Purchase Invoice) kesilmiştir.
- 15 Ocak tarihindeki "Currency Exchange" kuru: **1 EUR = 35,00 TRY**'dir. (Muhasebeye yansıyan maliyet yükü = 35.000 TRY).

### 2. WHEN (Eylem)
- Aylar sonra, 17 Nisan tarihinde (Bugün), bu tedarikçiye **1.000 EUR** tutarında tam ödeme (Payment Entry) yapılır.
- 17 Nisan tarihinde güncel döviz kuru: **1 EUR = 40,00 TRY**'dir. (Kasadan fiziksel olarak çıkacak tutar = 40.000 TRY).
- Ödeme makbuzu (Payment Entry) "Purchase Invoice" ile (Allocate edilerek) kapatılır.

### 3. THEN (Beklenen Sonuçlar)
- Tedarikçinin EUR bakiyesi **0 EUR**'a inmelidir (Borç kapandı).
- Tedarikçinin TRY bazlı bakiyesi de **0 TRY** olarak mühürlenmelidir.
- Sistem; fatura (35K) ile ödeme (40K) arasındaki **5.000 TRY** farkı GİZLİCE (arka planda otomatik bir Journal satırı olarak) algılamalıdır.
- `Exchange Gain/Loss` hesabına **5.000 TRY Borç (Zarar / Gider)** yazılmalıdır.
- "Cost of Goods Sold" (Satış Maliyeti) hesabı kesinlikle değişmemeli, 35.000 TRY olarak kalmalıdır (Çünkü biletin maliyeti değişmedi, finansal gecikme maliyeti oluştu).

## 📊 Ekstra (Unrealized Revaluation Testi)
Eğer 17 Nisan'da ödeme *yapılmasaydı* ve dönem sonu kapanışı alınsaydı:
- **Given:** Açık faturamız 1.000 EUR duruyor.
- **When:** `Exchange Rate Revaluation` modülü çalıştırılır (Bugünkü kur=40 üzerinden).
- **Then:** Sistem, ödenmemiş 5.000 TL fark için geçici "Unrealized Exchange Loss" faturası keserek mizanı gerçeğe uygun günceller.
