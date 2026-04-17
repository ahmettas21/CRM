# 📊 İzge Travel — Yönetim Dashboard Blueprint (v1.0)

> **Amaç:** Trip verilerinden türetilen 4 adet yönetim paneli ile acente müdürünün satış performansını, maliyet risklerini ve operasyonel sağlığı tek ekrandan izleyebilmesini sağlamak.
>
> **Teknik Yaklaşım:** Frappe `Script Report` + `Number Card` + `Dashboard Chart` kombinasyonu. Tüm veri kaynağı `tabTrip` (ve ilişkili GL/JE tabloları) üzerinden SQL sorguları ile çekilir. UI, ERPNext Workspace'e entegre edilir.

---

## Panel 1: 💰 Sales & Profitability Monitor

### Amaç
Günlük/haftalık/aylık bazda Trip satış hacmini, net kârı ve kâr marjını izlemek.

### Veri Kaynağı
| Tablo | Alanlar | Filtreler |
|:---|:---|:---|
| `tabTrip` | `total_sale_amount`, `cost_amount`, `profit`, `booking_date`, `product_type`, `customer`, `sales_owner`, `office` | `docstatus = 1` |

### SQL Sorgusu (Çekirdek)
```sql
SELECT
  booking_date,
  product_type,
  customer,
  sales_owner,
  COUNT(name) AS trip_count,
  SUM(total_sale_amount) AS total_sales,
  SUM(cost_amount) AS total_cost,
  SUM(profit) AS net_profit,
  ROUND(SUM(profit) / NULLIF(SUM(total_sale_amount), 0) * 100, 1) AS margin_pct
FROM `tabTrip`
WHERE docstatus = 1
  AND booking_date BETWEEN %(from_date)s AND %(to_date)s
GROUP BY booking_date, product_type
ORDER BY booking_date DESC
```

### Filtreler
| Filtre | Tip | Varsayılan |
|:---|:---|:---|
| `from_date` | Date | Son 30 gün |
| `to_date` | Date | Bugün |
| `product_type` | Select (Flight/Hotel/Package/…) | Tümü |
| `customer` | Link → Customer | Tümü |
| `sales_owner` | Link → User | Tümü |

### Widget'lar
| Widget | Tip | Metrik |
|:---|:---|:---|
| **Toplam Satış** | Number Card (₺) | `SUM(total_sale_amount)` |
| **Net Kâr** | Number Card (₺, yeşil/kırmızı) | `SUM(profit)` |
| **Kâr Marjı** | Number Card (%) | `AVG(margin_pct)` |
| **Trip Sayısı** | Number Card (#) | `COUNT(name)` |
| **Günlük Satış Trendi** | Line Chart | `booking_date` × `total_sales` |
| **Ürün Tipi Dağılımı** | Donut Chart | `product_type` × `total_sales` |
| **Müşteri Bazlı Top 10** | Table | `customer` × `total_sales` × `profit` |

---

## Panel 2: ✈️ ADM Alert Panel

### Amaç
Havayollarından gelen ADM (Agency Debit Memo) borç dekontlarının adedini, tutarını ve havayolu bazlı dağılımını izlemek.

### Veri Kaynağı
| Tablo | Alanlar | Filtreler |
|:---|:---|:---|
| `tabPurchase Invoice` | `supplier`, `grand_total`, `posting_date`, `cost_center`, `remarks` | `docstatus = 1`, `remarks LIKE '%ADM%'` |

### SQL Sorgusu (Çekirdek)
```sql
SELECT
  pi.supplier AS airline,
  COUNT(pi.name) AS adm_count,
  SUM(pi.grand_total) AS adm_total,
  MAX(pi.posting_date) AS last_adm_date
FROM `tabPurchase Invoice` pi
WHERE pi.docstatus = 1
  AND pi.remarks LIKE '%%ADM%%'
  AND pi.posting_date BETWEEN %(from_date)s AND %(to_date)s
GROUP BY pi.supplier
ORDER BY adm_total DESC
```

### Filtreler
| Filtre | Tip | Varsayılan |
|:---|:---|:---|
| `from_date` | Date | Son 90 gün |
| `to_date` | Date | Bugün |
| `supplier` | Link → Supplier | Tümü |

### Widget'lar
| Widget | Tip | Metrik |
|:---|:---|:---|
| **Açık ADM Adedi** | Number Card (#, turuncu) | `COUNT(*)` |
| **Toplam ADM Tutarı** | Number Card (₺, kırmızı) | `SUM(grand_total)` |
| **Havayolu Bazlı ADM** | Bar Chart | `supplier` × `adm_total` |
| **ADM Detay Tablosu** | Table | `supplier`, `adm_count`, `adm_total`, `last_adm_date` |

---

## Panel 3: 💳 Chargeback Risk Tracker

### Amaç
Kredi kartı ile tahsil edilmiş ve hâlâ açık kalan (veya ters ibraz riski taşıyan) tutarları yaşlandırma bazında izlemek.

### Veri Kaynağı
| Tablo | Alanlar | Filtreler |
|:---|:---|:---|
| `tabTrip` | `payment_method`, `cc_bank`, `total_sale_amount`, `booking_date`, `customer`, `payment_status` | `docstatus = 1`, `payment_method = 'Credit Card'` |
| `tabJournal Entry` | `remark LIKE '%Chargeback%'` | Chargeback JE'leri |

### SQL Sorgusu (Çekirdek)
```sql
SELECT
  t.cc_bank,
  t.customer,
  COUNT(t.name) AS cc_trip_count,
  SUM(t.total_sale_amount) AS total_cc_sales,
  SUM(CASE WHEN t.payment_status != 'Paid' THEN t.total_sale_amount ELSE 0 END) AS open_risk,
  DATEDIFF(CURDATE(), MIN(t.booking_date)) AS oldest_days
FROM `tabTrip` t
WHERE t.docstatus = 1
  AND t.payment_method = 'Credit Card'
  AND t.booking_date BETWEEN %(from_date)s AND %(to_date)s
GROUP BY t.cc_bank, t.customer
ORDER BY open_risk DESC
```

### Filtreler
| Filtre | Tip | Varsayılan |
|:---|:---|:---|
| `from_date` | Date | Son 180 gün |
| `to_date` | Date | Bugün |
| `cc_bank` | Select (Garanti/İş Bankası/…) | Tümü |
| `customer` | Link → Customer | Tümü |

### Widget'lar
| Widget | Tip | Metrik |
|:---|:---|:---|
| **Toplam KK Satışı** | Number Card (₺) | `SUM(total_cc_sales)` |
| **Açık Risk Bakiyesi** | Number Card (₺, kırmızı) | `SUM(open_risk)` |
| **Banka Bazlı Dağılım** | Pie Chart | `cc_bank` × `total_cc_sales` |
| **Risk Yaşlandırma** | Table | `cc_bank`, `customer`, `open_risk`, `oldest_days` |

---

## Panel 4: 🛡️ Operational Health

### Amaç
Guardrail'e takılan, zararda olan veya faturası kesilmemiş Trip'leri anında tespit etmek.

### Veri Kaynağı
| Tablo | Alanlar | Filtreler |
|:---|:---|:---|
| `tabTrip` | `name`, `booking_reference`, `customer`, `profit`, `total_sale_amount`, `cost_amount`, `customer_invoice_no`, `status`, `booking_date` | `docstatus = 1` |

### SQL Sorgusu (Çekirdek)
```sql
-- Zararda veya faturasız Trip'ler
SELECT
  name,
  booking_reference,
  customer,
  total_sale_amount,
  cost_amount,
  profit,
  CASE
    WHEN profit < 0 THEN '🔴 Zarar'
    WHEN profit = 0 THEN '🟡 Sıfır Marj'
    WHEN customer_invoice_no IS NULL OR customer_invoice_no = '' THEN '🟠 Faturasız'
    ELSE '🟢 Sağlıklı'
  END AS health_status,
  booking_date
FROM `tabTrip`
WHERE docstatus = 1
  AND (
    profit <= 0
    OR customer_invoice_no IS NULL
    OR customer_invoice_no = ''
  )
  AND booking_date BETWEEN %(from_date)s AND %(to_date)s
ORDER BY profit ASC
```

### Filtreler
| Filtre | Tip | Varsayılan |
|:---|:---|:---|
| `from_date` | Date | Son 30 gün |
| `to_date` | Date | Bugün |
| `status` | Select | Tümü |

### Widget'lar
| Widget | Tip | Metrik |
|:---|:---|:---|
| **Zarardaki Trip Sayısı** | Number Card (#, kırmızı) | `COUNT(WHERE profit < 0)` |
| **Faturasız Trip Sayısı** | Number Card (#, turuncu) | `COUNT(WHERE invoice IS NULL)` |
| **Sağlık Durumu Dağılımı** | Donut Chart | `health_status` × `COUNT(*)` |
| **Detay Tablosu** | Table (tıklanabilir) | Tüm sütunlar, Trip sayfasına link |

---

## Uygulama Sırası

| Faz | Panel | Script Report Adı | Öncelik |
|:---|:---|:---|:---|
| 1 | Sales & Profitability Monitor | `Trip Profitability Report` | 🔴 Kritik |
| 2 | Operational Health | `Trip Health Report` | 🔴 Kritik |
| 3 | ADM Alert Panel | `ADM Tracking Report` | 🟡 Orta |
| 4 | Chargeback Risk Tracker | `Chargeback Risk Report` | 🟡 Orta |

## Regresyon Test Planı

| Senaryo | Kapsam | Script |
|:---|:---|:---|
| SCEN-DASH-001 | Sales & Profitability Monitor SQL doğruluk testi | `run_scenario_dash_001.py` |
| SCEN-DASH-002 | Operational Health — zararlı/faturasız Trip tespiti | `run_scenario_dash_002.py` |
| SCEN-DASH-003 | ADM Panel — Purchase Invoice ADM filtreleme | `run_scenario_dash_003.py` |
| SCEN-DASH-004 | Chargeback Risk — KK yaşlandırma doğrulaması | `run_scenario_dash_004.py` |

---

> 🔗 **Derin Teknik Referans:** [raw/scenarios/edge_cases_brainstorm.md](../raw/scenarios/edge_cases_brainstorm.md)
> 🔗 **Senaryo İndeksi:** [wiki/scenarios/index.md](scenarios/index.md)
