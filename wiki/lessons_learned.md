# 🧠 Ders Çıkarılan Hatalar (Lessons Learned)

## 🪆 [MEM-K3L4M] Matruşka Klasör Tuzağı (Ağustos 2026 Vak'ası)

### Sorun
Uygulama sunucuya gönderildiğinde `hooks.py` dosyasının bulunamaması (`ModuleNotFoundError`) ve sol panelin (sidebar) boş görünmesi.

### Kök Neden
Kodların yereldeki dizin yapısı (`CRM/izge_travel/izge_travel/izge_travel...`) ile Git repsounun birleşmesi sonucunda, sunucuda 4-5 kat derinliğe sahip bir yapı oluşması. Frappe, Python import mantığı gereği modülü (izge_travel) yüklerken en fazla 2 kat derinlikte `hooks.py` arar. Daha derindeyse sistemi kilitler.

### Çözüm (Forum & Saha Onaylı)
- Dizin yapısını **Frappe Standartlarına** indirge. (Bkz: [raw/frappe_structure.md](../raw/frappe_structure.md))
- Uygulamayı sunucuda daima `pip install -e .` (Editable Mode) ile yükle.
- `__init__.py` içinde `__version__` bilgisini ASLA unutma.

### Altın Öğreti
> "Eğer sol panel yüklenmiyorsa veya 'No module named hooks' hatası geliyorsa, koda değil dizin derinliğine bak!"

---
🔗 **Derin Teknik Kök Neden (Deep Dive):** [raw/frappe_structure.md](../raw/frappe_structure.md)
