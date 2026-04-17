# SCEN-BEE-006: Operatör Komisyonlu - Müşteri Kartıyla Direkt Tedarikçi Ödemesi

## 🎯 Hedef
Müşterinin kredi kartıyla doğrudan tedarikçi (Havayolu/Operatör) posundan tahsilat yapıldığı durumlarda (Operatör Komisyonlu), aradaki komisyon farkının tedarikçiye "Acenta Alacağı" olarak yansıtılmasının (B2B Virman) muhasebesel kontrolü.

## 📥 Girdi Verileri (Inputs)
- **Müşteri:** Doğrudan Tahsilat Müşterisi (Direct Pay)
- **Tedarikçi:** Jolly Tur Operatörü
- **Müşteriden Tedarikçiye Çekilen Tutar (Kart):** 10.000 TL
- **Operatör Fiyatı / Maliyet:** 9.000 TL
- **Acenta Beklenen Komisyonu:** 1.000 TL

## ⚙️ Teknik Süreç (ERPNext Virman Mekanizması)
1. **Satış (SI):** Müşteriye 10.000 TL tutarında Satış Faturası mühürlenir.
2. **Maliyet (PI):** Tedarikçiden 9.000 TL tutarında Alış Faturası işlenir.
3. **Tahsilat Aktarımı (Journal Entry - Mahsup):**
   - **Kredi:** Müşteri Carisi (10.000 TL) 👉 *Müşterinin borcu kapanır.*
   - **Borç:** Tedarikçi Carisi (10.000 TL) 👉 *Tedarikçiye nakit giriş gösterilir.*

## ✅ Onay Kriterleri
- Müşterinin net borcu 0 TL olmalı.
- Tedarikçinin net borcu (Acentaya ödemesi gereken komisyon) +1.000 TL olmalı.
- Kasaya / Bankamıza fiziksel para girişi/çıkışı OLMAMALI (Net Nakit Akışı = 0).
