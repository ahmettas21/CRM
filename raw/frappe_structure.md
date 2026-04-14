# 🛠️ [TECH-F3M2Y] Frappe Uygulama Yapı Standardı (Teknik Referans)

## ❌ HATALI YAPI: Matruşka Modeli (Vak'a-i Matruşka)
Bu yapı `ModuleNotFoundError: No module named 'izge_travel.hooks'` hatası verir.

```text
apps/
  izge_travel/                <-- Repo Kök (Apps)
    izge_travel/              <-- Gereksiz Katman (Level 1)
      izge_travel/            <-- Gereksiz Katman (Level 2)
        hooks.py              <-- ASLA BURADA OLMAMALI
        izge_travel/          <-- Modül (Level 3)
          doctype/
```

## ✅ DOĞRU YAPI: Standart Frappe Modeli
Frappe'nin `bench` ve `pip install -e .` komutlarıyla tam uyumlu yapı şudur:

```text
apps/
  izge_travel/                <-- Uygulama Ana Dizini (Repo Kök)
    pyproject.toml            <-- Kurulum anahtarı (L0)
    izge_travel/              <-- Uygulama Paketi (L1)
      __init__.py             <-- Mutlaka '__version__ = "x.y.z"' olmalı
      hooks.py                <-- BURADA OLMALI (L1)
      modules.txt             <-- BURADA OLMALI (L1)
      izge_travel/            <-- Modül Klasörü (L2)
        __init__.py
        doctype/              <-- DocType'lar BURADA
        workspace/            <-- Workspace'ler BURADA
```

## 🔐 PIP Kurulum Kilidi
Kurulum daima `/home/frappe/bench/apps/izge_travel` dizini içindeyken şu şekilde yapılmalıdır:
`pip install -e .`

Eğer `flit_core.common.NoVersionError` alınıyorsa, hem L1 hem L2 dizinindeki `__init__.py` dosyalarındaki `__version__` değişkenleri kontrol edilmelidir.
