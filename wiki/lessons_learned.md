# 🧠 Ders Ã\u0087Ä±karÄ±lan Hatalar (Lessons Learned)

## 🪆 MatruÅ\u015fka KlasÃ¶r TuzaÄ\u011fÄ± (AÄ\u011fustos 2026)

### Sorun
Uygulama sunucuya gÃ¶nderildiÄ\u011finde `hooks.py` dosyasÄ±nÄ±n bulunamamasÄ± (`ModuleNotFoundError`) ve sol panelin (sidebar) boÅ\u015f gÃ¶rÃ¼nmesi.

### KÃ¶k Neden
KodlarÄ±n yereldeki dizin yapÄ±sÄ± (`CRM/izge_travel/izge_travel/izge_travel...`) ile Git repsounun birleÅ\u015fmesi sonucunda, sunucuda 4-5 kat derinliÄ\u011fe sahip bir yapı oluÅ\u015fmasÄ±. Frappe, Python import mantiÄ\u011fÄ± gereÄ\u011fi modÃ¼lÃ¼ (izge_travel) yÃ¼klerken en fazla 2 kat derinlikte `hooks.py` arar. Daha derindeyse sistemi kilitler.

### Ã\u0087Ã¶zÃ¼m (Forum & Saha OnaylÄ±)
- Dizin yapÄ±sÄ±nÄ± **Frappe StandartlarÄ±na** indirge. (Bkz: [raw/frappe_structure.md](../raw/frappe_structure.md))
- UygulamayÄ± sunucuda daima `pip install -e .` (Editable Mode) ile yÃ¼kle.
- `__init__.py` iÃ§inde `__version__` bilgisini ASLA unutma.

### AltÄ±n Ã\u0096Ä\u009freti
> "EÄ\u011fer sol panel yÃ¼klenmiyorsa veya 'No module named hooks' hatasÄ± geliyorsa, koda deÄ\u011fil dizin derinliÄ\u011fine bak!"

---
🔗 **Derin Teknik KÃ¶k Neden (Deep Dive):** [raw/frappe_structure.md](../raw/frappe_structure.md)
