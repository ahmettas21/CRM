# 🛠️ Frappe Uygulama YapÄ± StandardÄ± (Teknik Referans)

## ❌ HATALI YAPI: MatruÅ\u015fka Modeli (Vak'a-i MatruÅ\u015fka)
Bu yapÄ± `ModuleNotFoundError: No module named 'izge_travel.hooks'` hatasÄ± verir.

```text
apps/
  izge_travel/                <-- Repo KÃ¶k (Apps)
    izge_travel/              <-- Gereksiz Katman (Level 1)
      izge_travel/            <-- Gereksiz Katman (Level 2)
        hooks.py              <-- ASLA BURADA OLMAMALI
        izge_travel/          <-- ModÃ¼l (Level 3)
          doctype/
```

## ✅ DOÄ\u009eRU YAPI: Standart Frappe Modeli
Frappe'nin `bench` ve `pip install -e .` komutlarÄ±yla tam uyumlu yapÄ± Å\u015fudur:

```text
apps/
  izge_travel/                <-- Uygulama Ana Dizini (Repo KÃ¶k)
    pyproject.toml            <-- Kurulum anahtarÄ± (L0)
    izge_travel/              <-- Uygulama Paketi (L1)
      __init__.py             <-- Mutlaka '__version__ = "x.y.z"' olmalÄ±
      hooks.py                <-- BURADA OLMALI (L1)
      modules.txt             <-- BURADA OLMALI (L1)
      izge_travel/            <-- ModÃ¼l KlasÃ¶rÃ¼ (L2)
        __init__.py
        doctype/              <-- DocType'lar BURADA
        workspace/            <-- Workspace'ler BURADA
```

## 🔐 PIP Kurulum Kilidi
Kurulum daima `/home/frappe/bench/apps/izge_travel` dizini iÃ§indeyken Å\u015fu Å\u015fekilde yapÄ±lmalÄ±dÄ±r:
`pip install -e .`

EÄ\u011fer `flit_core.common.NoVersionError` alÄ±nÄ±yorsa, hem L1 hem L2 dizinindeki `__init__.py` dosyalarÄ±ndaki `__version__` deÄ\u011fiÅ\u015fkenleri kontrol edilmelidir.
