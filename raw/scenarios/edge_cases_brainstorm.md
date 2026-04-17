# İleri Seviye Finansal ve Operasyonel "Edge Case" Senaryoları (Draft)

Bu doküman, İzge Travel'ın ilerleyen aşamalarda ERPNext üzerinde test edeceği, standart dışı ve potansiyel "kriz" senaryolarını içerir. Senaryolar ERPNext v14/v15 standartlarına (Immutable Ledger, Multi-currency revaluation vs.) uygun kurgulanmıştır.

## 🚧 Planlanan Test Senaryoları (Future Pipeline)

### [PASSED] SCEN-BEE-007 & 014: Parçalı Tahsilat (Split Payment) + İkiz POS
- **Precondition:** Tek bir Sales Invoice var, ödeme ikiye bölünecek. Kasa grubu (Group Account) kullanılamayacağı için alt 'Nakit Kasa' ve 'POS Banka Hesabı' tanımlı. POS için `Reference No` kuralları aktif.
- **Behavior:** ERPNext, Nakit Kasa için onay verirken, POS Banka işlemi için `Reference No` ve `Reference Date` zorunluluğu ile işlemi validasyona sokar. Düzeltme sonrası, iki farklı `Payment Entry` aynı faturaya bağlanır.
- **Result:** Satış faturasının "Outstanding Amount" hanesi tam olarak 0.0'a iner, Kasa'ya +2.000 TL, POS Banka hebasına +8.000 TL net GL kaydı atılarak test başarıyla geçer. (SCEN-BEE-007 & 014 = PASSED).

### [DRAFT] SCEN-BEE-007B: Split + Virman (Payment on Behalf)
- **Durum:** 8.000 TL'lik kısım doğrudan operatör POS'una gidiyor ve para acenteye hiç girmiyor.
- **Beklenen Çözüm:** Müşteri borcu bizde kapanır, aynı anda Supplier/Operatör'e karşı "Payment Entry (Internal Transfer)" veya "Mahsup" hesabından Payable oluşturulur (B2B Settlement).

### [PASSED] SCEN-BEE-008: Yalnızca Vergi İadesi (No-Show ve Yanmış Biletler)
- **Durum:** 10.000 TL bilet, yolcu uçmadığı için 800 TL vergi iadesi. Kalan 9.200 TL çöp.
- **Beklenen Çözüm:** Credit Note (is_return=1) sadece 800 TL "Airport Tax" kalemi için oluşturulur.
- **Doğrulama Sonucu:** Orijinal bilet Sales Invoice olarak mühürlendi. Credit Note, sadece `AIRPORT-TAX` kalemi ile (-800 TL) oluşturuldu. Sistemin P&L üzerindeki ana Bilet Gelirini muhafaza ettiği GL Ledger sorgusuyla (9.200 TL Müşteri bakiyesi) %100 doğrulandı. (SCEN-BEE-008 = PASSED).

### [DRAFT] SCEN-BEE-009: Ayrılmış Hizmet Bedeli Çekimi (Service Fee POS Separation)
- **Durum:** 9.000 TL bilet bedeli B2B Virman, 1.000 TL Hizmet bedeli Acente POS'u.
- **Beklenen Çözüm:** Tek Sales Invoice üzerinden 2 satır kalemi (Flight Ticket = 9000 TL, Service Fee = 1000 TL) açılır. 9000 TL, Supplier'a karşı `Payment Entry - Internal Transfer / Journal Entry` ile kapanır (Clearing hesabı). 1000 TL ise Customer Payment Entry ile Kasa'dan kapanır. GL'de net kâr Service Fee hesabına akar.

### [PASSED] SCEN-BEE-010: Kur Farkı Krizi (Multi-Currency Revaluation)
- **Precondition:** Company currency = TRY, Supplier currency = EUR, Supplier Account = 320.xx SATICILAR EUR, Company'de `exchange_gain_loss_account` tanımlı.
- **Behavior:** EUR faturayı 35,00 kurdan kaydedip, 40,00 kurdan ödediğimizde ERPNext:
  - İlk kaydedilen 35.000 TL maliyeti değiştirmedi,
  - 5.000 TL'yi otomatik Exchange Gain/Loss hesabına finansman gideri yazdı,
  - Supplier EUR bakiyesini 0'a indirdi.
- **Result:** Ledger immutability + realized FX difference davranışı, senaryoda beklediğimiz gibi tam çalıştı (SCEN-BEE-010 = PASSED).

### [DRAFT] SCEN-BEE-011: B2B Alt Acenta + Depozito
- **Durum:** Alt acenta İzge Travel sisteminden bilet almaktadır. Peşin 50.000 TL avans yatırmış (Customer Advance).
- **Beklenen Çözüm:** Alt acenta, "Customer (Is Internal Customer)" olarak görülür. Peşin ödeme `Payment Entry` avans olarak sisteme girer. `Trip` bazında kesilen Sales Invoice'a bu "Advance" allocate edilir.
- **Test Kriteri:** Alt acenta 60.000 TL bilet kestiğinde, 50.000 avanstan düşer, kalan 10.000 bakiye bırakır. Credit Limit Validation (Müşteri Kredi Limiti) aşıldığı durumlarda Sales Invoice submit işlemi bloklanır (Custom Script / Standard Feature).

## 🌪️ Karmaşık Operasyonel "Kabus" Senaryoları (Operational Nightmares)

### [PASSED] SCEN-BEE-012: Kısmi Kullanım (Partial Usage) ve Pro-Rata İade
- **Durum:** 10.000 TL Base (6K Gidiş, 4K Dönüş) Gidiş-Dönüş biletinden dönüş bacağı iptal ediliyor. Ayrıca 1.000 TL Service Fee var.
- **Beklenen Çözüm:** Pro-rata hesaplama: `İade Oranı = (Dönüş segmenti base_price / Toplam base_price)`. Service Fee bu oranla çarpılır.
- **Doğrulama Sonucu:** Credit Note (is_return=1), doğrudan Sales Invoice'a bağlandı. 4.000 TL bilet bedeli ve oranlanmış (400 TL) komisyon ile toplam -4.400 TL düşüldü. Müşterinin uçtuğu bacakların kârı P&L defterinde başarıyla ayrıştırıldı. (SCEN-BEE-012 = PASSED).

### [DRAFT] SCEN-BEE-013: Group Booking / Blok Rezervasyon (Kontenjan Krizleri)
- **Durum:** 40 kişilik tur kontenjanında 5 kişi son dakika iptal olur veya başkasına satılır (Resale).
- **Beklenen Çözüm:** 40 blok koltuk "Master Trip", her bir yolcu "Sub-trip" (Sales Invoice) olarak kaydedilir. İptallerde satış faturası silinir ama "Blok Maliyeti", Master Trip'in "Cost Center"ı üzerinde kalır. Bu sayede "Seat Spoilage" (Koltuk Zayiatı) grubun kârından düşer.
- **Test Kriteri:** P&L (Kâr Zarar) raporu Cost Center üzerinden çekildiğinde; Toplam Koltuk Zayiatı, Resale Gelirleri ve Grubun NET Kârı tek ekranda teyit edilebilmeli.

### [PASSED] SCEN-BEE-014: İkiz POS / Farklı Merchant (Multi-Payment)
> *Not: Bu senaryo SCEN-BEE-007 ile birleştirilerek test edilmiş ve ERPNext'in POS/Banka Referans Validasyonu (Reference No) üzerinden başarıyla geçmiştir.*

## 📉 Endüstriyel Turizm Klasikleri (Advanced Aviation Issues)

### [PASSED] SCEN-BEE-015: ADM / ACM (Agency Debit/Credit Memo)
- **Durum:** Bilet kesilmiş, aylar sonra havayolu "tarife farkı / hatalı komisyon / service fee cap aşıldı" diyerek dönemi kapanmış bilete ADM (Borç dekontu) keser.
- **Beklenen Çözüm:** İlave `Purchase Invoice` açılır ve ilgili Trip/Cost Center ile bağlanır. Cost Center üzerinden Kârlılık geriye dönük değil, **yeni dönemde** maliyet arttırılarak mizan düzeltilir.
- **Doğrulama Sonucu:** Orijinal Sales Invoice bozulmadan muhafaza edildi. ADM, yeni bir `Purchase Invoice` olarak işlendi. Cost Center (TRIP-ADM-999) bazında net kârın 1.000 TL'den 500 TL'ye düştüğü raporlarda ispatlandı. (SCEN-BEE-015 = PASSED).

### [PASSED] SCEN-BEE-016: Chargeback (Ters İbraz) Krizi
- **Durum:** Müşteri uçmuş, ancak bankasına sahtecilik bildirip ödemeyi zorla geri çekmiştir. Müşteri Faturası kapanmış durumdadır.
- **Beklenen Çözüm:** Asla fatura (Sales Invoice) iptal edilmez (Immutable Ledger). "Journal Entry" açılarak Banka ceza gideri (Expense) ve ana para bankadan (- Credit) çıkartılır. Aynı esnada Müşteri Hesabı (AR) (+ Debit) yapılarak müşteri borcu tekrar hortlatılır (Dispute).
- **Doğrulama Sonucu:** Kod doğrulandı. Müşteri AR raporunda anında 10.000 TL borçlandı ve banka hesabından 10.250 TL (Ana Para + 250 Ceza) çekilip P&L gider hanesine yazıldı. Invoice bozulmadan (Closed) muhafaza edildi. (SCEN-BEE-016 = PASSED).


### [DRAFT] SCEN-BEE-017: Üç Farklı Para Birimi (Triple-Currency Booking)
- **Durum:** Havayolu USD, Otel EUR, Müşteri tahsilatı TRY üzerinden yapılır.
- **Beklenen Çözüm:** Trip bazlı "Multi-Currency Margin Report" yeteneği devreye girer. Cost Center + Party + Currency kombinasyonları ile ERPNext GL'sinde doğan 3 ayrı Base Currency farklılığı tek bir Trip çatısı altında raporlanabilir (Proje bazlı veya Custom Report ile).

---
> 💡 *Not: Bu belge, İzge Travel mimarlarının ileride sistemi zorlayacağı stres testlerinin BDD (Behavior-Driven) yaklaşımıyla tasarlanan yol haritasıdır. Çözümler uygulanıp test edildikçe ana `scenarios/` listesine eklenecektir.*
