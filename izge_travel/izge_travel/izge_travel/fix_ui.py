import frappe
import json
import os

def fix_everything():
    print("Izge Travel Sistemi Tamir Ediliyor...")

    # 1. Kullanıcı Yetkileri (ia kullanıcısı için)
    try:
        if frappe.db.exists("User", "ia"):
            user = frappe.get_doc("User", "ia")
            user.add_roles("System Manager")
            print("ia kullanıcısına System Manager yetkisi tanımlandı.")
    except Exception as e:
        print(f"Yetki hatası: {e}")

    # 2. Workspace (Menü) - HARD INSERT
    try:
        # JSON dosyasının yolunu bul
        # apps/izge_travel/izge_travel/izge_travel/workspace/izge_travel/izge_travel.json
        ws_name = "Izge Travel"
        
        app_path = frappe.get_app_path("izge_travel")
        # Bizim yapımızda 3. katmanda: izge_travel/workspace/izge_travel/izge_travel.json
        json_path = os.path.join(app_path, "izge_travel", "workspace", "izge_travel", "izge_travel.json")
        
        if os.path.exists(json_path):
            with open(json_path, "r") as f:
                doc_data = json.load(f)
            
            # Eski kaydı SİL
            if frappe.db.exists("Workspace", ws_name):
                frappe.delete_doc("Workspace", ws_name, ignore_permissions=True, force=True)
                print(f"Eski {ws_name} Workspace kaydı silindi.")
            
            # Yeni kaydı ZORLA YAZ
            # V15 uyumluluğu için is_standard: 0 yapıyoruz (Custom olarak görünmesi hızlı düzelme sağlar)
            doc_data["is_standard"] = 0
            doc_data["public"] = 1
            
            new_doc = frappe.get_doc(doc_data)
            new_doc.insert(ignore_permissions=True)
            print(f"{ws_name} Workspace'i JSON'dan zorla (Hard Insert) içeri alındı.")
        else:
            print(f"HATA: Workspace JSON dosyası bulunamadı: {json_path}")
            
    except Exception as e:
        print(f"Workspace tamir hatası: {e}")

    frappe.db.commit()
    frappe.clear_cache()
    print("Sistem başarıyla tamir edildi ve önbellek temizlendi.")

if __name__ == "__main__":
    fix_everything()
