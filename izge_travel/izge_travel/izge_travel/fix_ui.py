import frappe
import json
import os

def fix_everything():
    print("Izge Travel Sayfa Yapısı Yeniden İnşa Ediliyor...")
    ws_name = "Izge Travel"
    
    # 1. Eski tüm kayıtları temizle (Standard ve Custom)
    frappe.db.delete("Workspace", {"name": ws_name})
    frappe.db.delete("Workspace", {"label": ws_name})
    
    # 2. JSON dosyasını oku
    app_path = frappe.get_app_path("izge_travel")
    json_path = os.path.join(app_path, "izge_travel", "workspace", "izge_travel", "izge_travel.json")
    
    if os.path.exists(json_path):
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # V15 için en güvenli ayarlar
        data["is_standard"] = 0 # Custom olarak kalsın ki anında görünsün
        data["public"] = 1
        data["module"] = "Izge Travel"
        
        # İçeriği (content) kontrol et
        if isinstance(data.get("content"), str):
            # Eğer string ise ve bozuk geliyorsa temizle
            try:
                # String ise olduğu gibi kalsın, Frappe render eder
                pass
            except:
                pass

        doc = frappe.get_doc(data)
        doc.insert(ignore_permissions=True)
        print(f"BAŞARILI: {ws_name} sayfası sıfırdan ve hatasız oluşturuldu.")
    else:
        print("HATA: JSON dosyası bulunamadı!")

    frappe.db.commit()
    frappe.clear_cache()
    print("İşlem tamamlandı.")

if __name__ == "__main__":
    fix_everything()
