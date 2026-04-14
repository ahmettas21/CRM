import pandas as pd

# Try reading as CSV with different encodings
for enc in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1254', 'iso-8859-9']:
    try:
        df = pd.read_csv(r'c:\Users\asus\Desktop\crm\Aqua-TicketRezervasyon Listesi - 14.04.2026 (1).csv', encoding=enc, sep=None, engine='python')
        print(f'Encoding: {enc}, Shape: {df.shape}')
        print(f'Columns ({len(df.columns)}):')
        for i, c in enumerate(df.columns):
            print(f'  {i}: {c}')
        print()
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 250)
        pd.set_option('display.max_colwidth', 25)
        print('--- FIRST 10 ROWS ---')
        print(df.head(10).to_string())
        print()
        
        # Unique values for classification fields
        for col in df.columns:
            nuniq = df[col].nunique()
            if nuniq <= 15:
                print(f'{col} ({nuniq} unique): {list(df[col].dropna().unique())}')
        
        print()
        print('--- Misafir samples ---')
        if 'Misafir' in df.columns:
            for v in df['Misafir'].unique()[:20]:
                print(f'  {v}')
        
        print()
        print('--- Otel Adi samples ---')
        otel_col = [c for c in df.columns if 'otel' in c.lower() or 'Otel' in c]
        if otel_col:
            for v in df[otel_col[0]].unique()[:20]:
                print(f'  {v}')
        
        print()
        print('--- PNR group counts ---')
        pnr_col = [c for c in df.columns if 'Pnr' in c]
        if pnr_col:
            print(df[pnr_col[0]].value_counts().head(10))
        
        break
    except Exception as e:
        print(f'Failed with {enc}: {e}')
        continue
