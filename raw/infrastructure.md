# 🏗️ [INFRA-A1B9Z] Altyapı Referansı (Infrastructure)

## ☁️ Railway Ortamı
- **Project ID:** `ce5d08a8-d3c9-4c60-9cb7-c8e562f6c42b`
- **Site URL:** `https://erpnext-production-1b2e.up.railway.app`
- **Main Service:** `erpnext`
- **Storage:** persistent volumes mounted at `/home/frappe/bench/sites` and `/var/lib/mysql`.

## 📦 Custom App: `izge_travel`
- **Dizin:** `/home/frappe/bench/apps/izge_travel`
- **GitHub:** `https://github.com/ahmettas21/CRM`
- **Senkronizasyon Akışı:**
    1. Lokal Antigravity ortamında kod geliştirilir.
    2. GitHub'a push edilir.
    3. Railway SSH üzerinden `git fetch/reset` yapılarak konteynere çekilir.
    4. `bench migrate` ile veritabanı şeması güncellenir.

## 🛠️ Başlatma Komutu (Start Command)
Konteyner şu komutla ayağa kaldırılır:
`sh -c "su frappe -c 'cd /home/frappe/bench && /home/frappe/.local/bin/bench use erpnext-production-1b2e.up.railway.app' && sh /usr/local/bin/railway-cmd.sh"`

## 🔐 Güvenlik
- **Developer Mode:** Aktif (1).
- **Admin Password:** Railway `RFP_SITE_ADMIN_PASSWORD` değişkeninde saklıdır.
