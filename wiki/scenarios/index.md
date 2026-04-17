# 🎭 [SCEN-PLAN-001] Senaryo Planlama ve Yönetimi

Bu sayfa, İzge Travel sisteminin uçtan uca test edilmesi için kurgulanan iş senaryolarının merkezi yönetim alanıdır.

## 🎯 Planlama Stratejisi
Tüm senaryolar **[RULE-X1Y2Z] İkiz Doküman Kuralı** gereği hem kavramsal hem de teknik seviyede belgelenir.

| Katman | İçerik | Konum |
| :--- | :--- | :--- |
| **Wiki (Konsept)** | Senaryo özeti, hedefler ve başarı kriterleri. | `wiki/scenarios/` |
| **Raw (Teknik)** | Ham veri, payloadlar, beklenen vs gerçekleşen loglar. | `raw/scenarios/` |

## 🚀 Mevcut Senaryolar

1. **[SCEN-BEE-001] Bee Akademi**: 3+1 Yolcu, 30 Gün Vadeli Satış.
   - **Durum:** ✅ Tamamlandı
   - **Odak:** Çoklu yolcu maliyeti ve fatura otomasyonu.

2. **[SCEN-BEE-002] Kısmi İptal & Revizyon**: İade ve Rota Değişimi.
   - **Durum:** ✅ Tamamlandı
   - **Odak:** Amendment (Düzeltme) ve Refund (İade) muhasebesi.

## 🏛️ Sistem Rehberleri (User Guides)
- [Rezervasyon Yönetimi (Aqua -> ERPNext)](user_guide/reservation_management.md)
- [Finansal Senaryolar ve Testler](scenarios/index.md)
- [Gelecek Turizm Kriz Senaryoları (Draft)](../../raw/scenarios/edge_cases_brainstorm.md)

| Senaryo ID | Açıklama | Link | Durum |
| :--- | :--- | :--- | :--- |
| SCEN-BEE-001 | İlk Rezervasyon (3+1 Pax) | [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-002 | Kısmi İptal & Rota Değişimi | [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-003 | Tam İade (Full Void) | [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-004 | Şirket Kartı & Kesinleşik Void | [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-005 | Tarihsel İade (3 Ay Sonra) | [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-006 | Operatör Komisyonlu (Direct Pay)| [Detay](../../raw/scenarios/results.md) | ✅ Completed |
| SCEN-BEE-007 | Parçalı Tahsilat (Split Payment) + İkiz POS | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-007B | Payment on Behalf (Clearing Account) | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-008 | Yalnızca Vergi İadesi (No-Show) | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-010 | Kur Farkı Krizi (Multi-Currency Revaluation) | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-012 | Kısmi Kullanım (Pro-Rata İade) | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-015 | Agency Debit Memo (ADM) | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-BEE-016 | Chargeback (Ters İbraz) Krizi | [Detay](../../raw/scenarios/edge_cases_brainstorm.md) | ✅ Completed |
| SCEN-TRIP-001 | Trip Controller & Marjin Guardrail | [Detay](../../raw/scenarios/SCEN-TRIP-001_logic_success_log.txt) | ✅ Completed |
| SCEN-TRIP-002 | UI 'Make Invoice' Buton & API Tetikleyici | [Detay](../../raw/scenarios/SCEN-TRIP-002_success_log.txt) | ✅ Completed |
| SCEN-DASH-001 | Sales & Profitability Monitor SQL Doğrulama | [Detay](../../raw/scenarios/SCEN-DASH-001_success_log.txt) | ✅ Completed |
| SCEN-TRIP-HOTEL-001 | Yurtiçi Otel Konaklaması (KDV %10 + %20) | [Detay](../../raw/scenarios/SCEN-TRIP-HOTEL-001_brainstorm.md) | ⏳ Pending |
| SCEN-TRIP-TOUR-001 | Outgoing Paket Tur (KDV Matrah Dönüşümü) | [Detay](../../raw/scenarios/SCEN-TRIP-TOUR-001_brainstorm.md) | ⏳ Pending |
| SCEN-TRIP-SERVICE-001 | Vize + Diğer Ekstra Hizmetler | [Detay](../../raw/scenarios/SCEN-TRIP-SERVICE-001_brainstorm.md) | ⏳ Pending |
> 🔗 **Dashboard Blueprint:** [wiki/dashboard_blueprint.md](../dashboard_blueprint.md)

> 🔗 **Detaylı Sonuçlar:** [raw/scenarios/results.md](../../raw/scenarios/results.md)

> 🔗 **Detaylı Teknik Senaryolar:** [raw/scenarios/](../../raw/scenarios/)
