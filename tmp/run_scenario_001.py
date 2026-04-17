import frappe
from frappe.utils import add_days, today, flt

def run_scenario():
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()
    print("--- Scenario SCEN-BEE-001 Execution Started ---")
    
    # 1. Customer
    cust_name = "Bee Akademi KOLAY BİLET"
    if not frappe.db.exists("Customer", cust_name):
        doc = frappe.get_doc({
            "doctype": "Customer",
            "customer_name": cust_name,
            "customer_group": "Ticari",
            "territory": "Turkey",
            "customer_type": "Company"
        })
        doc.insert(ignore_permissions=True)
        print(f"Customer created: {doc.name}")
    else:
        doc = frappe.get_doc("Customer", cust_name)
        print(f"Customer exists: {doc.name}")

    # 2. Supplier (THY)
    supp_name = "THY - Türk Hava Yolları"
    if not frappe.db.exists("Supplier", supp_name):
        supp = frappe.get_doc({
            "doctype": "Supplier",
            "supplier_name": supp_name,
            "supplier_group": "Hizmetler",
            "territory": "Turkey",
            "supplier_type": "Company"
        })
        supp.insert(ignore_permissions=True)
        print(f"Supplier created: {supp.name}")
    else:
        supp = frappe.get_doc("Supplier", supp_name)
        print(f"Supplier exists: {supp.name}")

    # 3. Payment Terms Template
    term_name = "30 Gün Vadeli"
    if not frappe.db.exists("Payment Terms Template", term_name):
        term = frappe.get_doc({
            "doctype": "Payment Terms Template",
            "template_name": term_name,
            "terms": [
                {
                    "payment_term": "30 Gün",
                    "invoice_portion": 100,
                    "credit_days": 30
                }
            ]
        })
        term.insert(ignore_permissions=True)
        print(f"Payment Terms Template created: {term.name}")
    else:
        term = frappe.get_doc("Payment Terms Template", term_name)
        print(f"Payment Terms Template exists: {term.name}")

    # 4. Travelers
    traveler_data = [
        ("MR", "Ahmet Bee Akademi"),
        ("MRS", "Ayşe Bee Akademi"),
        ("MR", "Mehmet Bee Akademi"),
        ("CHD", "Can Bee Akademi")
    ]
    traveler_ids = []
    for prefix, name in traveler_data:
        t_id = frappe.db.get_value("Traveler", {"full_name": name, "customer": doc.name}, "name")
        if not t_id:
            t_doc = frappe.get_doc({
                "doctype": "Traveler",
                "naming_series": "TRAV-.2026.-.#####",
                "title_prefix": prefix,
                "full_name": name,
                "customer": doc.name
            })
            t_doc.insert(ignore_permissions=True)
            t_id = t_doc.name
            print(f"Traveler created: {name} ({t_id})")
        else:
            print(f"Traveler exists: {name} ({t_id})")
        traveler_ids.append(t_id)

    # 5. Trip
    trip = frappe.new_doc("Trip")
    trip.naming_series = "TRIP-.2026.-.#####"
    trip.customer = doc.name
    trip.booking_reference = "BEE-AKAD-2026-001"
    trip.product_type = "Flight"
    trip.payment_method = "Credit (Vadeli)"
    trip.payment_terms_template = term.name
    trip.booking_date = today()
    trip.primary_traveler = traveler_ids[0]
    
    # Costs & Sales
    # 3 Adults (5000 / 6800), 1 Child (4000 / 5600)
    for i, t_id in enumerate(traveler_ids):
        cost = 5000 if i < 3 else 4000
        sale = 6800 if i < 3 else 5600
        service = sale - cost
        
        trip.append("trip_flight_segments", {
            "traveler": t_id,
            "direction": "Outbound",
            "flight_no": "TK1234",
            "origin": "IST",
            "destination": "ESB",
            "departure_date": today(),
            "cost_amount": cost,
            "service_amount": service,
            "sale_amount": sale,
            "supplier": supp.name,
            "tax_amount": flt(service / 1.20 * 0.20, 2)
        })

    trip.insert(ignore_permissions=True)
    trip.submit()
    print(f"Trip {trip.name} Submitted Successfully!")
    
    # 6. Check SI and PI
    si = frappe.db.get_value("Sales Invoice", {"remarks": ["like", f"%{trip.name}%"]}, "name")
    pi = frappe.db.get_value("Purchase Invoice", {"remarks": ["like", f"%{trip.booking_reference}%"]}, "name")
    
    print(f"Result -> Sales Invoice: {si}")
    print(f"Result -> Purchase Invoice: {pi}")
    print("--- Scenario SCEN-BEE-001 Completed ---")

if __name__ == "__main__":
    run_scenario()
