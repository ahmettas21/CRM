import pandas as pd

dfs = pd.read_html(r'c:\Users\asus\Desktop\crm\Aqua-TicketRezervasyon Listesi - 14.04.2026.xls', encoding='utf-8')
df = dfs[0]

# Filter out summary rows
df_clean = df[df['Yön Durum'].isin(['GIDIS','DONUS'])].copy()
print(f'Clean rows: {len(df_clean)} (total was {len(df)})')

# Find charge/service rows (non-person Yolcu entries)
charge_keywords = ['KOLTUK', 'BEDELI', 'CIP', 'UCRETI', 'EKS', 'BAGAJ', 'BUNDLE', 'TRANSFER']
def is_charge(yolcu):
    if pd.isna(yolcu):
        return False
    y = str(yolcu).upper()
    return any(kw in y for kw in charge_keywords)

charges = df_clean[df_clean['Yolcu'].apply(is_charge)]
travelers = df_clean[~df_clean['Yolcu'].apply(is_charge)]

print(f'Traveler rows: {len(travelers)}')
print(f'Charge rows: {len(charges)}')
print()

print('--- CHARGE ROW YOLCU VALUES ---')
for v in charges['Yolcu'].unique():
    print(f'  {v}')
print()

pnr_col = 'Pnr.No'
print('--- UNIQUE COUNTS ---')
print(f"Total unique PNRs: {df_clean[pnr_col].nunique()}")
print(f"Total unique Musteri: {df_clean['Müşteri'].nunique()}")
print(f"Total unique Yolcu (travelers): {travelers['Yolcu'].nunique()}")
print()

print('--- DIRECTION distribution ---')
print(df_clean['Yön Durum'].value_counts())
print()

# Sample a multi-row PNR to see structure
print('--- SAMPLE: PNR 180720 (24 rows) ---')
sample = df_clean[df_clean[pnr_col] == 180720]
print(sample[['Yön Durum', 'Nereden', 'Nereye', 'Müşteri', 'Yolcu', 'Bilet No', 'Satış']].to_string())
print()

print('--- SAMPLE: PNR 180791 (has charges) ---')
sample2 = df_clean[df_clean[pnr_col] == 180791]
print(sample2[['Yön Durum', 'Nereden', 'Nereye', 'Müşteri', 'Yolcu', 'Bilet No', 'Satış']].to_string())
