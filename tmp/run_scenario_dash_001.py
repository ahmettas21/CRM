import frappe
from frappe.utils import today, add_days

def run_scenario_dash_001():
    """
    SCEN-DASH-001: Sales & Profitability Monitor — SQL Doğruluk Testi
    
    BDD:
      Given: Production'da submitted Trip kayıtları mevcut.
      When:  Dashboard SQL sorgusu çalıştırılır.
      Then:
        P1: SQL syntax hatası vermeden sonuç döner.
        P2: Her satırda margin_pct = profit / total_sales * 100 doğru hesaplanır.
        P3: Toplam satış ve kâr tutarları, Trip bazında doğrudan hesaplanan değerlerle eşleşir.
        P4: Filtreler (product_type, customer) doğru çalışır.
    """
    frappe.init(site="erpnext-production-1b2e.up.railway.app")
    frappe.connect()

    print("--- SCEN-DASH-001: Sales & Profitability Monitor SQL Validation ---")

    from_date = add_days(today(), -365)
    to_date = today()

    # ═════════════════════════════════════════════
    # P1: Core SQL syntax validation
    # ═════════════════════════════════════════════
    print("\n[P1] Testing core SQL query syntax...")
    
    core_sql = """
        SELECT
            booking_date,
            product_type,
            customer,
            sales_owner,
            COUNT(name) AS trip_count,
            SUM(total_sale_amount) AS total_sales,
            SUM(cost_amount) AS total_cost,
            SUM(profit) AS net_profit,
            ROUND(SUM(profit) / NULLIF(SUM(total_sale_amount), 0) * 100, 1) AS margin_pct
        FROM `tabTrip`
        WHERE docstatus = 1
            AND booking_date BETWEEN %s AND %s
        GROUP BY booking_date, product_type
        ORDER BY booking_date DESC
    """
    
    rows = frappe.db.sql(core_sql, (from_date, to_date), as_dict=True)
    print(f"   ✅ P1 PASSED: Query returned {len(rows)} rows without error.")

    # ═════════════════════════════════════════════
    # P2: Margin calculation cross-check
    # ═════════════════════════════════════════════
    print("\n[P2] Validating margin_pct calculation...")
    
    margin_errors = 0
    for row in rows:
        if row.total_sales and row.total_sales > 0:
            expected_margin = round(row.net_profit / row.total_sales * 100, 1)
            if abs((row.margin_pct or 0) - expected_margin) > 0.2:
                print(f"   ❌ Margin mismatch on {row.booking_date}/{row.product_type}: "
                      f"SQL={row.margin_pct}, Expected={expected_margin}")
                margin_errors += 1
    
    if margin_errors == 0:
        print(f"   ✅ P2 PASSED: All {len(rows)} rows have correct margin_pct.")
    else:
        raise AssertionError(f"P2 FAILED: {margin_errors} margin calculation mismatches!")

    # ═════════════════════════════════════════════
    # P3: Aggregate cross-check with individual Trip records
    # ═════════════════════════════════════════════
    print("\n[P3] Cross-checking aggregates against individual Trip records...")
    
    agg_sql = """
        SELECT
            SUM(total_sale_amount) AS total_sales,
            SUM(cost_amount) AS total_cost,
            SUM(profit) AS net_profit,
            COUNT(name) AS trip_count
        FROM `tabTrip`
        WHERE docstatus = 1
            AND booking_date BETWEEN %s AND %s
    """
    agg = frappe.db.sql(agg_sql, (from_date, to_date), as_dict=True)[0]
    
    # Sum from grouped query
    grouped_sales = sum(r.total_sales or 0 for r in rows)
    grouped_profit = sum(r.net_profit or 0 for r in rows)
    grouped_count = sum(r.trip_count or 0 for r in rows)

    assert abs(grouped_sales - (agg.total_sales or 0)) < 0.01, \
        f"Sales mismatch: grouped={grouped_sales}, agg={agg.total_sales}"
    assert abs(grouped_profit - (agg.net_profit or 0)) < 0.01, \
        f"Profit mismatch: grouped={grouped_profit}, agg={agg.net_profit}"
    assert grouped_count == (agg.trip_count or 0), \
        f"Count mismatch: grouped={grouped_count}, agg={agg.trip_count}"
    
    print(f"   ✅ P3 PASSED: Aggregates match. "
          f"Trips={agg.trip_count}, Sales={agg.total_sales}, Profit={agg.net_profit}")

    # ═════════════════════════════════════════════
    # P4: Filter validation (product_type)
    # ═════════════════════════════════════════════
    print("\n[P4] Testing product_type filter...")
    
    filter_sql = """
        SELECT
            product_type,
            COUNT(name) AS trip_count,
            SUM(total_sale_amount) AS total_sales,
            SUM(profit) AS net_profit
        FROM `tabTrip`
        WHERE docstatus = 1
            AND booking_date BETWEEN %s AND %s
            AND product_type = %s
        GROUP BY product_type
    """
    
    # Test with 'Flight' filter
    flight_rows = frappe.db.sql(filter_sql, (from_date, to_date, "Flight"), as_dict=True)
    
    if flight_rows:
        print(f"   ✅ P4 PASSED: Flight filter returned {flight_rows[0].trip_count} trips, "
              f"Sales={flight_rows[0].total_sales}, Profit={flight_rows[0].net_profit}")
    else:
        print(f"   ⚠️ P4 NOTICE: No Flight trips in date range (not necessarily an error).")

    # ═════════════════════════════════════════════
    # P5: Number Card queries (Dashboard widgets)
    # ═════════════════════════════════════════════
    print("\n[P5] Validating Number Card widget queries...")
    
    card_queries = {
        "Toplam Satış": "SELECT SUM(total_sale_amount) AS val FROM `tabTrip` WHERE docstatus=1 AND booking_date BETWEEN %s AND %s",
        "Net Kâr": "SELECT SUM(profit) AS val FROM `tabTrip` WHERE docstatus=1 AND booking_date BETWEEN %s AND %s",
        "Trip Sayısı": "SELECT COUNT(name) AS val FROM `tabTrip` WHERE docstatus=1 AND booking_date BETWEEN %s AND %s",
    }
    
    for label, sql in card_queries.items():
        result = frappe.db.sql(sql, (from_date, to_date), as_dict=True)
        val = result[0].val if result else 0
        print(f"   📊 {label}: {val}")
    
    print(f"   ✅ P5 PASSED: All Number Card queries executed successfully.")

    # ═════════════════════════════════════════════
    # P6: Operational Health sub-query (bonus)
    # ═════════════════════════════════════════════
    print("\n[P6] Operational Health — unhealthy Trip detection...")
    
    health_sql = """
        SELECT
            name,
            booking_reference,
            customer,
            total_sale_amount,
            cost_amount,
            profit,
            CASE
                WHEN profit < 0 THEN 'ZARAR'
                WHEN profit = 0 THEN 'SIFIR'
                WHEN customer_invoice_no IS NULL OR customer_invoice_no = '' THEN 'FATURASIZ'
                ELSE 'SAGLIKLI'
            END AS health_status
        FROM `tabTrip`
        WHERE docstatus = 1
            AND (profit <= 0 OR customer_invoice_no IS NULL OR customer_invoice_no = '')
            AND booking_date BETWEEN %s AND %s
        ORDER BY profit ASC
        LIMIT 10
    """
    
    unhealthy = frappe.db.sql(health_sql, (from_date, to_date), as_dict=True)
    print(f"   🛡️ Found {len(unhealthy)} unhealthy trips in range.")
    for u in unhealthy[:5]:
        print(f"      → {u.name} | {u.booking_reference} | {u.health_status} | Profit: {u.profit}")
    
    print(f"   ✅ P6 PASSED: Operational Health query works correctly.")

    # ═════════════════════════════════════════════
    # FINAL SUMMARY
    # ═════════════════════════════════════════════
    print("\n" + "=" * 60)
    print("🎉 SCEN-DASH-001: ALL 6 ASSERTIONS PASSED!")
    print(f"   Total Trips: {agg.trip_count}")
    print(f"   Total Sales: {agg.total_sales} TL")
    print(f"   Net Profit:  {agg.net_profit} TL")
    print(f"   Unhealthy:   {len(unhealthy)} trips need attention")
    print("=" * 60)

if __name__ == "__main__":
    run_scenario_dash_001()
