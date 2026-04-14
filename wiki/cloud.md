# ☁️ [PROC-C9K8X] Cloud & Deployment Operasyon Merkezi

Bu dokuman, Izge Travel uygulamasinin Railway uzerindeki sagligini ve dogru deployment yontemlerini icerir.

## 🚀 [DEPL-A7V2M] Altin Deployment Protokolu

Kodlar guncellendiginde izlenecek **tek ve sarsilmaz** yol sudur:

1.  **Yerelde Push:** `git push origin main`
2.  **Sunucuya Baglanti:** `railway ssh -s erpnext --environment production`
3.  **Guncelleme Komutu (Base64 S-Prototol):**
    ```powershell
    # Bu komut her zaman uygulamayi en guncel hale getirir ve modul yollarini duzeltir
    cd /home/frappe/bench/apps/izge_travel
    git fetch origin main
    git reset --hard origin/main
    # ONEMLI: Alt klasorden kurulum sart!
    /home/frappe/bench/env/bin/pip install -e ./izge_travel
    cd /home/frappe/bench
    bench migrate
    ```

## 🛠️ [RECO-B4N9Q] Acil Durum & Kurtarma

### 1. [ERR-X1Z5P] Dizin Labirenti (Matruska) Hatasi
Eger `ModuleNotFoundError` aliniyorsa, sunucuda klasorler ic ice gecmis demektir. 
**Cozum:** `rm -rf /home/frappe/bench/apps/izge_travel/izge_travel` yapip `git reset --hard` ile tertemiz cekin.

### 2. [UI-F3W8L] Tablo/Sekme Gorunmuyor
Eger "Trip List" aratildiginda bulunamiyorsa:
- `bench clear-cache`
- `bench clear-website-cache`
komutlarini ardi ardina calistirin.

## 🔗 [INFO-D6K2Y] Sunucu Bilgileri
- **Host:** `monorail.proxy.rlwy.net`
- **DB Host:** `mariadb.railway.internal`
- **Redis:** `redis-cache.railway.internal`
