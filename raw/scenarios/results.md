# 📈 [SCEN-RESULTS] Senaryo Test Sonuçları Arşivi

Bu dosya, icra edilen tüm senaryoların sonuçlarını ve varsa oluşan hataları (bug) kronolojik olarak tutar.

## 🗒️ Sonuç Tablosu

| ID | Senaryo Adı | Tarih | Durum | Notlar |
| :--- | :--- | :--- | :--- | :--- |
| SCEN-BEE-001 | İlk Rezervasyon (3+1 Pax) | 2026-04-17 | ✅ Başarılı | 26.000 TL Satış / 19.000 TL Maliyet faturası kesildi. |
| SCEN-BEE-002 | Kısmi İptal & Rota Değişimi | 2026-04-17 | ✅ Başarılı | Net Satış: 25.300 TL, Net Maliyet: 16.100 TL (Faturalar revize edildi). |
| SCEN-BEE-003 | Tam İade (Full Void) | 2026-04-17 | ✅ Başarılı | Taslak faturalar otomatik silindi, cari etkilenmedi. |
| SCEN-BEE-004 | Şirket Kartı & Kesinleşik Void | 2026-04-17 | ✅ Başarılı | İş Bankası 4846 kart ekstresinde harcama/iptal izi sağlandı. |
| SCEN-BEE-005 | Tarihsel İade (3 Ay Sonra) | 2026-04-17 | ✅ Başarılı | Ocak mizanı bozulmadan bugün tarihli iade kaydı oluşturuldu. |
| SCEN-BEE-006 | Operatör Komisyonlu (Direct Pay) | 2026-04-17 | ✅ Başarılı | Müşteri carisi sıfırlandı, Tedarikçi 1.000 TL komisyon borçlandırıldı (Journal Entry ile). |

## 🛠️ Hata Kayıtları (Bug Logs)
*Şu an için kaydedilmiş bir hata bulunmamaktadır.*

---
> 🔗 **Planlama Merkezi:** [wiki/scenarios/index.md](../../wiki/scenarios/index.md)
