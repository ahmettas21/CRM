# SCEN-BEE-005: Tarihsel İade ve Dönemsel Koruma

## 🎯 Hedef
Geçmiş bir döneme (Örn: 3 ay önce) ait bir işlemin bakiye iadesinin, geçmiş mizanı bozmadan bugün üzerinden yapılmasını denetlemek.

## 📥 Senaryo
- İşlem Tarihi: Ocak 2026 (10.000 TL).
- İade Tarihi: Nisan 2026.
- Kural: Ocak mizanı "tutturulmuş" (Locked) kabul edilir.

## ⚙️ Teknik Süreç
1. **İade Faturası (Credit Note)** bugün tarihli kesilir.
2. **İade Ödemesi** bugün tarihli bankaya (Card) girilir.
3. Eski dokümanlar İPTAL EDİLMEZ (Cancel yasaktır).

## ✅ Onay Kriterleri
- Mart sonu mizanı değişmemeli (-10.000 TL).
- Nisan sonu mizanı 0 olmalı.
- "Ekstre Tutturma" (Reconciliation) hatasız çalışmalı.
