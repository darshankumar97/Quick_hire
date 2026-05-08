"""Check forecast completeness"""
import pandas as pd

df = pd.read_csv('c:/Projects/forecasting-system/outputs/forecasts.csv')
print(f'Total forecasts: {len(df)}')
print(f'Unique states: {df["state"].nunique()}')
print(f'\nStates:')
for s in sorted(df['state'].unique()):
    count = len(df[df['state'] == s])
    model = df[df['state'] == s]['best_model'].iloc[0]
    print(f'  {s:20s} - {count:3d} forecasts (Model: {model})')

print(f'\nModel distribution:')
print(df['best_model'].value_counts())
print(f'\nDate range: {df["date"].min()} to {df["date"].max()}')
print(f'\nSample forecasts:')
print(df.head(10).to_string())
