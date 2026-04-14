import frappe

def fix_everything():
    # 1. Kullanıcı Yetkileri
    try:
        if frappe.db.exists("User", "ia"):
            user = frappe.get_doc("User", "ia")
            # Ensure "System Manager" role exists, otherwise this will fail
            user.add_roles("System Manager")
            print("ia kullanıcısına System Manager yetkisi tanımlandı.")
    except Exception as e:
        print(f"Yetki hatası: {e}")

    # 2. Workspace (Menü) Kontrolü
    # Force public visibility for the Izge Travel workspace
    if frappe.db.exists("Workspace", "Izge Travel"):
        ws = frappe.get_doc("Workspace", "Izge Travel")
        ws.public = 1
        ws.is_standard = 1
        # Set parent_page empty to ensure it's a top-level item
        ws.parent_page = ""
        ws.save(ignore_permissions=True)
        print("Izge Travel Workspace'i herkese açık hale getirildi.")
    
    frappe.db.commit()
    frappe.clear_cache()
    print("İşlem tamamlandı ve önbellek temizlendi.")

if __name__ == "__main__":
    fix_everything()
