# SCEN-BEE-003: Tam İade (Full Void) - Taslak Aşama

## 🎯 Hedef
Bilet alındıktan kısa süre sonra, henüz faturalar onaylanmadan (Draft) yapılan iptallerin sistemi temiz bırakmasını doğrulamak.

## 📥 Senaryo
- Pegasus'tan bilet alındı (Void edilecek).
- Faturalar üretildi ama mühürlenmedi.
- Operatör Trip "Void" işlemini başlattı.

## ⚙️ Teknik Süreç
1. `status` = "Void" olarak güncellenir.
2. `on_cancel` tetiklendiğinde `Sales Invoice` ve `Purchase Invoice` taslakları (DocStatus=0) DB'den silinir (Delete).

## ✅ Onay Kriterleri
- Tedarikçi mizanında (GL) hiçbir hareket oluşmamalı.
- Cariler tertemiz kalmalı.
