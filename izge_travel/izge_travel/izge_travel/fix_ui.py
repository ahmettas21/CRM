import frappe

def fix_everything():
    # 1. KullanÄ±cÄ± Yetkileri
    try:
        user = frappe.get_doc("User", "ia")
        user.add_roles("System Manager", "BiletÃ§i")
        print("ia kullanÄ±cÄ±sÄ±na yetkiler baÅ\u015farÄ±yla tanÄ±mlandÄ±.")
    except Exception as e:
        print(f"Yetki hatasÄ±: {e}")

    # 2. Workspace (MenÃ¼) KontrolÃ¼
    if frappe.db.exists("Workspace", "Izge Travel"):
        ws = frappe.get_doc("Workspace", "Izge Travel")
        ws.public = 1
        ws.is_standard = 1
        ws.save(ignore_permissions=True)
        print("Izge Travel Workspace'i herkese aÃ§Ä±k hale getirildi.")
    
    frappe.db.commit()
    print("Ä°Å\u015flem tamamlandÄ±.")

if __name__ == "__main__":
    fix_everything()
