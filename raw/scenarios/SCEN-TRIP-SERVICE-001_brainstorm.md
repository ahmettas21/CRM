# SCEN-TRIP-SERVICE-001: Vize & Diğer Ekstra Hizmetler

## Senaryo Tanımı (BDD Formats)

**Given:**
- Trip doc üzerinde `product_type` = `Service` (veya spesifik olarak Visa/Transfer vb.),
- Sistemde en az bir `HIZMET-BEDELI` item’ı (örneğin Vize Danışmanlık Ücreti) ve isteğe bağlı `EK-MASRAF-SATIS` item’ları tanımlanmış.
- Trip "Services" tablosunda bu hizmet kalemleri girilmiş.

**When:**
- Satışçı hizmet detaylarını girip tripten Save & Submit yapıyor,
- Fatura (Sales Invoice) oluşturuluyor (yalnızca hizmet kalemleri Item olarak faturaya ekleniyor),
- Peşin ödeme (Cash/Bank) veya KK tahsilatı (PE) yapılıyor.

**Then:**
- Bilet/Otel blokları opsiyonel olarak boş bırakıldığında sistem hata vermemeli (validate başarılı geçmeli).
- Tüm hizmet gelirleri (satış bedelleri) tek bir ana “Hizmet Geliri” hesabına veya alt kırılım hesaba aktarılmalı.
- KDV genel oran (%20) üzerinden uygulanmalı (Turizm KDV Blueprint'e istinaden Vize/Hizmet = %20).
- Trip kâr (profit) hesaplaması "toplam service sale - toplam service cost" olarak doğru çalışmalı.
- GL Entry ve Müşteri Outstanding = 0 (tahsilat sonrası) kontrolleri sağlamalı.

## 🌟 Demo Case: 2026 VIP Schengen Vize & Havalimanı CIP Hizmeti

**Paket Özeti:** Yüksek gelir grubundaki kurumsal müşteriler için Vize alımı ve CIP Lounge kullanımı.
- **Pax:** 1 Kurumsal Yetişkin
- **Hizmet 1 (Vize Harcı):** 4.000 TL (Gerçek konsolosluk bedeli, Exempt/Pass-through)
- **Hizmet 2 (Vize Danışmanlık):** 3.000 TL (Acente Kârı/Hizmeti)
- **Hizmet 3 (IST CIP Lounge):** Maliyet 2.000 TL, Satış 2.500 TL (Kâr 500 TL)
- **Toplam Hizmet Maliyeti:** 6.000 TL  (4.000 + 2.000)
- **Trip Toplam Satış (KDV Hariç):** 9.500 TL (4.000 + 3.000 + 2.500)
- **Trip Toplam Kâr:** 3.500 TL

**KDV & Fatura Kırılımı (Item Segmentation):**
1. `VIZE-HARCI` (Pass-through): 4.000 TL (KDV **%0**)
2. `VIZE-DANISMANLIK`: 3.000 TL (KDV **%20** = 600 TL)
3. `CIP-LOUNGE-HIZMETI`: 2.500 TL (KDV **%20** = 500 TL)
- **Sales Invoice Grand Total:** 10.600 TL (9.500 + 1.100 KDV)

## Muhasebe Hedef (GL Expected)

| Kayıt | Belge | Account | Debit | Credit | Açıklama |
|:---|:---|:---|:---|:---|:---|
| Müşteri Alacak | SI | `120.01 - Alıcılar` | 120 | - | Örneğin 100 TL hizmet + 20 TL KDV |
| Hizmet Geliri | SI | `600.xx - Vize/Hizmet Gelirleri`| - | 100 | Matrah |
| KDV (%20) | SI | `391.02 - Hesaplanan KDV (%20)`| - | 20 | |
| Tahsilat | PE | `102.xx - Banka/Kasa` | 120 | - | |
| Müşteri Borç Kap.| PE | `120.01 - Alıcılar` | - | 120 | |

## Riskler & Guardrail Önerileri
- **UX Riski:** Satışçının sadece vize satarken karşısında devasa Uçuş/Otel tabloları görüp kafasının karışması.
- **UI Çözümü:** `trip.js` içinde `product_type == 'Service'` olduğunda uçuş ve otel sekmelerini/tablolarını gizle (hide). Sadece yolcu ve service tablosu görünsün.
- **Guardrail:** Hizmet satışlarında maliyet faturası gelmesi gecikebilir (konsolosluk harcı vs.). Bu yüzden Purchase Invoice zorunluluğu bu type için esnetilebilir veya `service_cost` boş olsa bile kâr hesaplanabilmelidir.
