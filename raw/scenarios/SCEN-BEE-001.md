# SCEN-BEE-001: İlk Rezervasyon Otomasyonu (3+1 Pax)

## 🎯 Hedef
Uçak bileti satışında 3 yetişkin ve 1 çocuk yolcu için Sales Invoice ve Purchase Invoice'ların otomatik, hatasız ve mühürlü (Draft) olarak oluşturulmasını doğrulamak.

## 📥 Girdi Verileri (Inputs)
- **Müşteri:** Bee Akademi KOLAY BİLET
- **Tedarikçi:** THY - Türk Hava Yolları
- **Yolcular:** Ahmet, Mehmet, Ayşe (Y) + Can (Ç)
- **Maliyet:** 19.000 TL
- **Satış:** 26.000 TL
- **Hizmet Bedeli:** Dahil

## ⚙️ Teknik Süreç
1. `Trip` dökümanı oluşturulur.
2. `Trip Flight Segment` tablosuna 4 yolcu işlenir.
3. `trip.submit()` tetiklenerek faturalar üretilir.

## ✅ Onay Kriterleri
- Satış Faturası (SI) 26.000 TL olmalı.
- Alış Faturası (PI) 19.000 TL olmalı.
- Muhasebe hesapları (120/320) doğru eşleşmeli.
