# ☁️ Cloud & Deployment Operasyon Merkezi

Bu dÃ¶kÃ¼man, Izge Travel uygulamasÄ±nÄ±n Railway Ã¼zerindeki saÄ\u011flÄ±Ä\u011fÄ±nÄ± ve doÄ\u011fru deployment yÃ¶ntemlerini iÃ§erir.

## 🚀 AltÄ±n Deployment ProtokolÃ¼

Kodlar gÃ¼ncellendiÄ\u011finde izlenecek **tek ve sarsÄ±lmaz** yol Å\u015futur:

1.  **Yerelde Push:** `git push origin main`
2.  **Sunucuya BaÄ\u011flantÄ±:** `railway ssh -s erpnext --environment production`
3.  **GÃ¼ncelleme Komutu (Base64 S-Prototol):**
    ```powershell
    # Bu komut her zaman uygulamayÄ± en gÃ¼ncel hale getirir ve modÃ¼l yollarÄ±nÄ± dÃ¼zeltir
    cd /home/frappe/bench/apps/izge_travel
    git fetch origin main
    git reset --hard origin/main
    # Ã\u0096NEMLÄ°: Alt klasÃ¶rden kurulum Å\u015fart!
    /home/frappe/bench/env/bin/pip install -e ./izge_travel
    cd /home/frappe/bench
    bench migrate
    ```

## 🛠️ Acil Durum & Kurtarma

### 1. Dizin Labirenti (MatruÅ\u015fka) HatasÄ±
EÄ\u011fer `ModuleNotFoundError` alÄ±nÄ±yorsa, sunucuda klasÃ¶rler iÃ§ iÃ§e geÃ§miÅ\u015f demektir. 
**Ã\u0087Ã¶zÃ¼m:** `rm -rf /home/frappe/bench/apps/izge_travel/izge_travel` yapÄ±p `git reset --hard` ile tertemiz Ã§ekin.

### 2. Tablo/Sekme GÃ¶rÃ¼nmÃ¼yor
EÄ\u011fer "Trip List" aratÄ±ldÄ±Ä\u011fÄ±nda bulunamÄ±yorsa:
- `bench clear-cache`
- `bench clear-website-cache`
komutlarÄ±nÄ± ardÄ± ardÄ±na Ã§alÄ±Å\u015ftÄ±rÄ±n.

## 🔗 Sunucu Bilgileri
- **Host:** `monorail.proxy.rlwy.net`
- **DB Host:** `mariadb.railway.internal`
- **Redis:** `redis-cache.railway.internal`
