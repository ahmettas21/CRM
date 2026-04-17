# SCEN-BEE-002: Kısmi İptal ve Rota Değişimi (Amendment)

## 🎯 Hedef
Kesinleşmiş bir rezervasyonda yolcu azalması ve rota değişimi sonrası faturaların "Amendment" (Düzeltme) mantığıyla revize edilmesini denetlemek.

## 🔄 Değişim Senaryosu
- **Eski Durum:** 4 Yolcu, IST-AMS (26k Satış / 19k Maliyet).
- **Yeni Durum:** 1 Yolcu İptal (-4k İade), Rota IST-AMS -> IST-BRU (+1.9k Fark).
- **Cezalar:** 1000 TL İptal Cezası (Tedarikçiye ödenen).

## ⚙️ Teknik Süreç
1. Mevcut `Trip` kaydı üzerinde **Cancel** ve **Amend** yapılır.
2. Yeni revizyon (PNR-REV) üzerinden `calculate_totals` çalıştırılır.
3. Eski faturalar iptal edilir, yeni net tutarlı faturalar oluşturulur.

## ✅ Onay Kriterleri
- Net Müşteri Borcu: 25.300 TL (Giriş/Çıkış Farkları Dahil).
- Net Tedarikçi Alacağı: 16.100 TL.
- Eski kayıtların "Amended From" ile takibi.
