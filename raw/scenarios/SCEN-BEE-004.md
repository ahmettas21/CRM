# SCEN-BEE-004: Şirket Kredi Kartı ve Kesinleşmiş Void

## 🎯 Hedef
Ödemesi kredi kartıyla yapılmış ve muhasebeleşmiş bir biletin iptal edilmesi durumunda, kart ekstresinde harcama/iade dengesini izlemek.

## 📥 Senaryo
- Bilet: 4000 TL (Maliyet).
- Ödeme: **İş Bankası 4846** kartından Pegasus'a yapıldı.
- Fatura Durumu: **Submitted** (Mühürlü).
- İptal Zamanı: Satıştan 4 saat sonra.

## ⚙️ Teknik Süreç
1. `Payment Entry` iptal edilir (Cancel).
2. `Sales/Purchase Invoice` iptal edilir.
3. Banka hesap mizanında ters kayıtlar (GL reversal) oluşur.

## ✅ Onay Kriterleri
- Kredi kartı ekstresinde -4000 TL (Giriş) ve +4000 TL (İade) hareketi görülmeli.
- Müşteri bakiyesi net 0 olmalı.
- Geçmiş kayıtlar "Cancelled" etiketiyle denetim için saklanmalı.
