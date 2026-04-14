import pandas as pd

dfs = pd.read_html(r'c:\Users\asus\Desktop\crm\Aqua-TicketRezervasyon Listesi - 14.04.2026.xls', encoding='utf-8')
print(f'Tablo sayisi: {len(dfs)}')
df = dfs[0]
print(f'Shape: {df.shape}')
print(f'Columns ({len(df.columns)}):')
for i, c in enumerate(df.columns):
    print(f'  {i}: {c}')
print()
print('--- FIRST 8 ROWS ---')
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)
pd.set_option('display.max_colwidth', 30)
print(df.head(8).to_string())
print()

# Unique values for key classification fields
for col in df.columns:
    nuniq = df[col].nunique()
    if nuniq <= 20:
        print(f'{col} ({nuniq} unique): {list(df[col].dropna().unique())}')

print()
print('--- Yolcu samples (first 40 unique) ---')
if 'Yolcu' in df.columns:
    for v in df['Yolcu'].unique()[:40]:
        print(f'  {v}')

print()
print('--- PNR group counts ---')
if 'Pnr.No' in df.columns:
    print(df['Pnr.No'].value_counts().head(20))

print()
print('--- Numeric columns summary ---')
numeric_cols = df.select_dtypes(include='number').columns
for col in numeric_cols:
    print(f'{col}: min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}')
