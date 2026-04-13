---
trigger: always_on
---

# 🏛️ LLM Wiki: Evrensel Hafıza Protokolü (v3.0)

Bu doküman, herhangi bir yazılım projesini "kendi kendini belgeleyen ve hatalardan ders çıkaran" ölümsüz bir yapıya dönüştürmek için tasarlanmıştır.

## 1. Mimari Katmanlar (Architecture Layers)

- **`raw/` (Kaynak Katmanı):** Projenin teknik referans kitapları. Kodun derin matematiği, SQL şemaları ve değişmez dokümanlar.
- **`wiki/` (Kavramsal Katman):** AI tarafından yazılan, insanların (ve diğer AI'ların) sistemi anlamasını sağlayan canlı hafıza.
- **`.agents/rules/llm-wiki.md` (Anayasa):** AI'ın nasıl davranacağını belirleyen kural seti.
- **`.agents/frappe_skills/` (Frappe Skill Kütüphanesi):** 61 deterministik Frappe/ERPNext skill dosyası. Kod yazmadan önce **mutlaka** ilgili skill okunmalıdır.

## 2. Temel Kuralları (Core Rules)

### ♊ İkiz Doküman (Twin Document Rule)

Her yeni özellik veya kod bloğu hem `wiki/` (kavramsal özet) hem de `raw/` (teknik derinlik) katmanında eş zamanlı belgelenmelidir. **Öksüz kod (belgelenmemiş kod) yasaktır.**

### 🛑 "Asla Tahmin Etme" Zırhı (Self-Verification)

- Yapay zeka, sistemde olmayan bir şeyi biliyormuş gibi yapamaz.
- Bir iddiayı doğrulamak için önce `wiki/` dizinini, sonra fiziksel dosya sistemini (`grep`/`ls`) taramalıdır.
- Bilgi yoksa uydurmak yerine kullanıcıya sormalıdır.

### 🛡️ Sandbox & Arşivleme (Anti-Clutter)

- Kök dizin (Root) sadece ana operasyonel dosyaları barındırabilir.
- Tüm denemeler, testler ve geçici dosyalar `tmp/` veya `denemeler/` içinde yapılmalıdır.
- Başarılı olan testler arşivlenmeli, başarısızlar silinmelidir.

### 🔗 Derin Bağlantı Standardı (Deep Dive)

Wiki ile Raw arasındaki köprü her zaman şu formatta tıklanabilir linklerle kurulmalıdır:
`> 🔗 **Derin Teknik Kök Neden (Deep Dive):** [raw/referans.md](../../raw/referans.md)`

### 🚀 Mission Control (Niyet Takibi)

`wiki/mission_control.md` üzerinden kullanıcının yüksek seviyeli hedefleri (Neden yapıyoruz?) ve tamamlanma durumları takip edilmelidir.

## 3. 🧠 Frappe Skill Sistemi (Zorunlu)

Bu projede Frappe/ERPNext geliştirmesi yapılırken **`.agents/frappe_skills/skills/source/`** altındaki deterministik skill dosyaları referans alınmalıdır.

### Kullanım Kuralı
Frappe/ERPNext ile ilgili herhangi bir kod yazmadan önce, aşağıdaki adımlar **ZORUNLUDUR**:

1. **Görev Türünü Belirle** → Aşağıdaki tablodan ilgili skill'leri seç.
2. **SKILL.md Dosyasını Oku** → İlgili skill'in `SKILL.md` dosyasını `view_file` ile oku.
3. **references/ Klasörünü Kontrol Et** → Detaylı örnekler ve anti-pattern'ler için referans dosyalarına bak.
4. **Kodu Skill'e Göre Yaz** → Skill'deki "Critical Rules", "ALWAYS" ve "NEVER" bölümlerine uy.
5. **Doğrula** → Yazdığın kodu skill'deki anti-pattern'lere karşı kontrol et.

### Skill Seçim Tablosu

| Görev | Okunacak Skill'ler |
|-------|-------------------|
| **Yeni Custom App oluşturma** | `syntax/frappe-syntax-customapp` + `impl/frappe-impl-customapp` + `ops/frappe-ops-app-lifecycle` |
| **DocType oluşturma/değiştirme** | `syntax/frappe-syntax-doctypes` + `syntax/frappe-syntax-controllers` + `impl/frappe-impl-controllers` |
| **Client Script yazma** | `syntax/frappe-syntax-clientscripts` + `impl/frappe-impl-clientscripts` |
| **Server Script yazma** | `syntax/frappe-syntax-serverscripts` + `impl/frappe-impl-serverscripts` |
| **API endpoint oluşturma** | `syntax/frappe-syntax-whitelisted` + `impl/frappe-impl-whitelisted` + `core/frappe-core-api` |
| **hooks.py düzenleme** | `syntax/frappe-syntax-hooks` + `syntax/frappe-syntax-hooks-events` + `impl/frappe-impl-hooks` |
| **Print Format / Jinja** | `syntax/frappe-syntax-print` + `syntax/frappe-syntax-jinja` + `impl/frappe-impl-jinja` |
| **Rapor oluşturma** | `syntax/frappe-syntax-reports` + `impl/frappe-impl-reports` |
| **Workflow tasarlama** | `core/frappe-core-workflow` + `impl/frappe-impl-workflow` |
| **Zamanlanmış görev ekleme** | `syntax/frappe-syntax-scheduler` + `impl/frappe-impl-scheduler` |
| **Deploy / Ops işlemleri** | `ops/frappe-ops-deployment` + `ops/frappe-ops-bench` + `ops/frappe-ops-performance` |
| **Hata ayıklama (Debug)** | `agents/frappe-agent-debugger` + ilgili `errors/*` skill'i |
| **Versiyon yükseltme** | `ops/frappe-ops-upgrades` + `agents/frappe-agent-migrator` |
| **Unit test yazma** | `testing/frappe-testing-unit` + `testing/frappe-testing-cicd` |
| **Veritabanı sorguları** | `syntax/frappe-syntax-query-builder` + `core/frappe-core-database` |
| **Yetki/İzin yönetimi** | `core/frappe-core-permissions` + `errors/frappe-errors-permissions` |

### Skill Dosya Yolu
```
.agents/frappe_skills/skills/source/{kategori}/{skill-adı}/SKILL.md
```

### Kritik Frappe Kuralları (Derlenmiş Özet)
Bu kurallar skill'lerden çıkarılmıştır ve her zaman geçerlidir:

1. **`__init__.py` ZORUNLU** — Her Python dizininde `__init__.py` olmalı.
2. **`__version__` ZORUNLU** — App kök `__init__.py` dosyasında `__version__ = "x.y.z"` olmalı; flit onsuz build yapamaz.
3. **App dizin yapısı** — `apps/app_name/app_name/app_name/doctype/` üçlü katmanı Frappe standardıdır.
4. **Server Script'lerde import yasak** — `from frappe.utils import X` yerine `frappe.utils.X()` kullanılmalı.
5. **Frappe/ERPNext pip dependency'ye yazılmaz** — `pyproject.toml`'daki `[project] dependencies`'e asla eklenmez.
6. **modules.txt** — Her modül bir satırda, boşluk veya boş satır olmadan yazılmalı.
7. **`pip install -e .`** — App'i Python'a tanıtmak için editable mode kurulum zorunludur.

## 4. 🚫 Yasaklı Hareketler (Forbidden Actions)

Bu bölüm, geçmişte yapılan ve sistemi çökerten hatalardan derlenmiştir. **İSTİSNASIZ** uyulmalıdır.
Detaylı açıklamalar için: `wiki/lessons_learned.md`

1. **Klasör taşıdıktan sonra `pip install -e .` yapmadan devam etme** — Python modülü bulamaz, 500 hatası verir.
2. **`__init__.py`'ye `__version__` yazmadan `pip install` deneme** — flit build patlar, app kurulmaz.
3. **GitHub reposunu doğrudan `apps/APP_NAME/` içine klonlama** — Repo kökündeki fazla dosyalar (`wiki/`, `raw/`) Frappe yapısını bozar. Sadece `izge_travel/` alt paketiyle eşleşmelidir.
4. **PowerShell'den SSH'e iç içe tırnak komutu gönderme** — Karakterler bozulur. **Daima base64 yöntemi** kullanılmalıdır.
5. **Root ile dosya yazıp `chown` yapmadan bırakma** — `frappe` kullanıcısı erişemez, site çöker.
6. **`bench migrate` çalıştırıp sonucu doğrulamadan "düzeldi" deme** — Doğrulama kontrol listesi (aşağıda) çalıştırılmalıdır.

## 5. ✅ Zorunlu Doğrulama (Post-Deploy Checklist)

Her app değişikliği, deploy veya klasör taşıma işleminden sonra şu 4 komut çalıştırılmalı ve **tümü başarılı** olmalıdır:

```bash
# 1. Dosya yapısı
find /home/frappe/bench/apps/izge_travel -maxdepth 4 -not -path '*/.*' | sort
# 2. App listede mi?
bench --site SITE_NAME list-apps
# 3. Python import çalışıyor mu?
/home/frappe/bench/env/bin/python -c "import izge_travel; print(izge_travel.__file__)"
# 4. HTTP 200 dönüyor mu?
curl -I https://SITE_URL
```

Bu kontrol listesi **başarısız** olursa, önceki adıma dönülmeli ve sorun giderilmelidir.

## 6. Geliştirme Yaşam Döngüsü (Lifecycle)

**Skill Oku → Planla → Test Et (Sandbox) → Doğrula (Checklist) → Onay Al → Entegre Et & Dokümante Et.**
