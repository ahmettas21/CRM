# 🏗️ Altyapı Referansı (Infrastructure)

Bu doküman, projenin teknik altyapısını ve dış servis bağlantılarını tanımlar.

## 🚢 Railway Konfigürasyonu
- **Proje Adı:** considerate-magic
- **Proje ID:** ce5d08a8-d3c9-4c60-9cb7-c8e562f6c42b
- **Ana Servisler:**
  - `erpnext`: Ana uygulama (ID: bfece3b0-a6ae-4b71-a051-4fd4ddc5e1f5)
  - `mariadb`: Veritabanı (ID: 9cf78627-0ce8-4248-a49b-f13fb9ca3290)
  - `redis-cache` & `redis-queue`: Önbellek ve kuyruk yönetimi.

## 🔑 Yetkilendirme
- **Authentication:** API Token based.
- **Environment:** production

## 🛠️ Teknik Bilgiler
- **CLI Ver:** 4.36.1
- **ERPNext Docker Image:** `pipech/erpnext-docker-debian:version-15-latest`
- **Volume:** `erpnext-volume` (ID: 2ce13d21-c2d1-4969-ab8b-d4377ea3b2ea)
