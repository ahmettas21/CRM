# 🚨 Ders Çıkarılan Hatalar (Lessons Learned)

Bu doküman, geliştirme sürecinde karşılaşılan **kritik hataları** ve çözümlerini kaydeder.
Aynı hataların tekrar yapılmasını engellemek için AI tarafından **her Frappe işleminden önce** kontrol edilmelidir.

---

## 1. `ModuleNotFoundError: No module named 'izge_travel'`

**Tarih:** 2026-04-14
**Kök Neden:** `pip install -e .` yapılmadan app klasörü elle taşındı. Python'un `sys.path`'inde kayıt yoktu.
**Çözüm:**
```bash
cd /home/frappe/bench/apps/izge_travel
su frappe -c '/home/frappe/bench/env/bin/pip install -e .'
```
**Kural:** Frappe app dosyaları elle taşındığında veya GitHub'dan çekildiğinde **mutlaka** `pip install -e .` çalıştırılmalıdır.

---

## 2. `NoVersionError: Cannot package module without a version string`

**Tarih:** 2026-04-14
**Kök Neden:** `__init__.py` dosyasında `__version__ = "x.y.z"` satırı yoktu veya bozuk yazılmıştı.
**Çözüm:**
```python
# apps/izge_travel/izge_travel/__init__.py
__version__ = "0.0.1"
```
**Kural:** Her Frappe app'inin kök `__init__.py`'sinde `__version__` **ZORUNLUDUR**. Flit build sistemi bunu okur.

---

## 3. Yanlış Dizin Yapısı (Nested Folder Chaos)

**Tarih:** 2026-04-14
**Kök Neden:** GitHub reposu (`CRM`) doğrudan `apps/izge_travel/` içine klonlandı. Repo kökünde `wiki/`, `raw/` gibi ekstra klasörler vardı ve bunlar Frappe app yapısını bozdu.
**Doğru Yapı (Frappe v15 Standardı):**
```
apps/izge_travel/                    # Repo kökü
├── pyproject.toml
├── izge_travel/                     # Python paketi (Inner Package)
│   ├── __init__.py                  # __version__ = "0.0.1" ZORUNLU
│   ├── hooks.py
│   ├── modules.txt
│   ├── patches.txt
│   ├── izge_travel/                 # Varsayılan modül
│   │   ├── __init__.py
│   │   └── doctype/
│   │       ├── traveler/
│   │       ├── trip/
│   │       ├── trip_segment/
│   │       └── traveler_emergency_contact/
│   ├── public/
│   ├── templates/
│   └── www/
```
**Kural:** GitHub repo yapısı ile Frappe app yapısı **birebir örtüşmeli**. Repoya `wiki/`, `raw/` gibi Frappe dışı dosyalar koyulacaksa, `.gitignore`'a yazılmak yerine ayrı bir repo veya branch kullanılmalı.

---

## 4. PowerShell ↔ SSH Tırnak İşareti Karmaşası

**Tarih:** 2026-04-14
**Kök Neden:** PowerShell `\`, `"`, `$` karakterlerini kendi değişkenleri sanıp yorumladı. SSH üzerinden gönderilen Python veya bash komutları bozuldu.
**Çözüm:** Karmaşık komutları `.sh` dosyasına yaz, `base64` ile encode et, konteyner içinde decode edip çalıştır:
```powershell
$bytes = [System.IO.File]::ReadAllBytes("fix.sh")
$b64 = [System.Convert]::ToBase64String($bytes)
railway ssh -s erpnext --environment production "echo $b64 | base64 -d > /tmp/fix.sh && sh /tmp/fix.sh"
```
**Kural:** Railway SSH üzerinden **asla** iç içe tırnak işareti kullanılmamalı. Kompleks komutlar için **daima base64 yöntemi** tercih edilmeli.

---

## 5. `Permission denied` — chown Eksikliği

**Tarih:** 2026-04-14
**Kök Neden:** Root olarak yazılan dosyalar, `frappe` kullanıcısının erişimine kapatıldı.
**Çözüm:**
```bash
chown -R frappe:frappe /home/frappe/bench/apps/izge_travel
```
**Kural:** Konteyner içinde dosya oluşturulduktan sonra **her zaman** `chown frappe:frappe` çalıştırılmalı.

---

## Doğrulama Kontrol Listesi

Her deployment veya app değişikliğinden sonra şu 4 komut çalıştırılmalı ve hepsinin başarılı olması gerekmektedir:

```bash
# 1. Dosya yapısı doğru mu?
find /home/frappe/bench/apps/izge_travel -maxdepth 4 -not -path '*/.*' | sort

# 2. App yüklü mü?
bench --site SITE_NAME list-apps

# 3. Python bulabiliyor mu?
/home/frappe/bench/env/bin/python -c "import izge_travel; print(izge_travel.__file__)"

# 4. Site çalışıyor mu?
curl -I https://SITE_URL
```

> 🔗 **Derin Teknik Referans:** [raw/infrastructure.md](../raw/infrastructure.md)
