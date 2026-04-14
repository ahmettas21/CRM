# 🧠 Ders Çıkarılan Hatalar (Lessons Learned)

## 🪆 [MEM-001] Matruşka Klasör Tuzağı (Ağustos 2026 Vak'ası)

### Sorun
Uygulama sunucuya gönderildiğinde `hooks.py` dosyasının bulunamaması (`ModuleNotFoundError`) ve sol panelin (sidebar) boş görünmesi.

### Kök Neden
Kodların yereldeki dizin yapısı (`CRM/izge_travel/izge_travel/izge_travel...`) ile Git repsounun birleşmesi sonucunda, sunucuda 4-5 kat derinliğe sahip bir yapı oluşması. Frappe, Python import mantığı gereği modülü (izge_travel) yüklerken en fazla 2 kat derinlikte `hooks.py` arar. Daha derindeyse sistemi kilitler.

### Ã\u0087Ã¶zÃ¼m (Forum & Saha OnaylÄ±)
- Dizin yapÄ±sÄ±nÄ± **Frappe StandartlarÄ±na** indirge. (Bkz: [raw/frappe_structure.md](../raw/frappe_structure.md))
- UygulamayÄ± sunucuda daima `pip install -e .` (Editable Mode) ile yÃ¼kle.
- `__init__.py` iÃ§inde `__version__` bilgisini ASLA unutma.

### AltÄ±n Ã\u0096Ä\u009freti
> "EÄ\u011fer sol panel yÃ¼klenmiyorsa veya 'No module named hooks' hatasÄ± geliyorsa, koda deÄ\u011fil dizin derinliÄ\u011fine bak!"

---
🔗 **Derin Teknik KÃ¶k Neden (Deep Dive):** [raw/frappe_structure.md](../raw/frappe_structure.md)
