import frappe

def fix_everything():
    # 1. Kullanıcı Yetkileri
    try:
        if frappe.db.exists("User", "ia"):
            user = frappe.get_doc("User", "ia")
            user.add_roles("System Manager")
            print("ia kullanıcısına System Manager yetkisi tanımlandı.")
    except Exception as e:
        print(f"Yetki hatası: {e}")

    # 2. Workspace (Menü) Sıfırlama ve Zorla Senkronizasyon
    # Mevcut kaydı silelim ki dosyadaki yeni 'Standard' hali temiz gelsin
    ws_name = "Izge Travel"
    if frappe.db.exists("Workspace", ws_name):
        frappe.delete_doc("Workspace", ws_name, ignore_permissions=True, force=True)
        print(f"{ws_name} Workspace'i sıfırlandı.")
    
    # MODÜLÜ ZORLA SENKRONİZE ET (JSON -> DB)
    from frappe.model.sync import sync_for
    sync_for("izge_travel", force=True)
    print("izge_travel modülü (Workspace dahil) zorla senkronize edildi.")
    
    frappe.db.commit()
    frappe.clear_cache()
    print("İşlem tamamlandı ve önbellek temizlendi.")

if __name__ == "__main__":
    fix_everything()
