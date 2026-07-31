import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.stattools import adfuller, zivot_andrews
from arch import arch_model

warnings.filterwarnings('ignore')

#load and rename
df = pd.read_csv('master_dataframe.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date').sort_index()

#bloomberg tickers -> readable names
df = df.rename(columns={
    'CNY REGN Curncy': 'CNY',
    'CNH BGN Curncy':  'CNH',
    'SHIF3M Index':    'SHIBOR',
    'HIHD01M Index':   'HIBOR',
    'VIX Index':       'VIX',
    'DXY Curncy':      'DXY',
    'USGG3M Index':    'US3M'
})

print(f"sample: {df.index.min().date()} → {df.index.max().date()}  ({len(df)} obs)")
print(f"columns: {df.columns.tolist()}\n")

#clean
#LOCF for holiday closures -> max 2 days so we don't carry stale prices too far
fill_cols = [c for c in ['CNY','CNH','SHIBOR','HIBOR','VIX','DXY','US3M'] if c in df.columns]
df[fill_cols] = df[fill_cols].ffill(limit=2)
df = df.dropna(subset=['CNY','CNH','SHIBOR','HIBOR'])
print(f"{len(df)} obs after holiday cleaning\n")

#spreads
#CNY-CNH: percentage deviation, in bps. negative = offshore at premium
df['cny_cnh'] = ((df['CNY'] - df['CNH']) / df['CNH']) * 10_000

#SHIBOR-HIBOR: rates are already %, multiply by 100 for bps
df['shibor_hibor'] = (df['SHIBOR'] - df['HIBOR']) * 100

print(df[['cny_cnh','shibor_hibor']].describe().round(2), "\n")

#dummies
#both announcements fell on saturdays-> roll to monday
#step dummies for levels model, impulse for differenced model
df['ann_step'] = (df.index >= '2022-02-28').astype(int)
df['imp_step'] = (df.index >= '2022-03-14').astype(int)
df['ann_imp'] = (df.index == '2022-02-28').astype(int)
df['imp_imp'] = (df.index == '2022-03-14').astype(int)

assert df['ann_imp'].sum() == 1, "announcement impulse should fire exactly once"
assert df['imp_imp'].sum() == 1, "implementation impulse should fire exactly once"
print(f"post-announcement obs: {df['ann_step'].sum()}")
print(f"post-implementation obs: {df['imp_step'].sum()}\n")

#stationarity
print("stationarity tests")
print("-" * 55)

test_vars = {
    'cny_cnh':      'CNY-CNH spread',
    'shibor_hibor': 'SHIBOR-HIBOR spread',
    'VIX':          'VIX',
    'DXY':          'DXY',
    'US3M':         'US 3M yield'
}

nonstat = []

for col, label in test_vars.items():
    if col not in df.columns:
        continue
    s = df[col].dropna()
    p = adfuller(s)[1]

    #ZA is slow
    za_str = ''
    if 'cny_cnh' in col or 'shibor' in col:
        za_p = zivot_andrews(s, regression='c')[1]
        za_str = f"  za={za_p:.4f}"

    tag = 'I(0)' if p < 0.05 else 'I(1)'
    print(f"  [{tag}]  {label:<25}  adf={p:.4f}{za_str}")
    if p >= 0.05:
        nonstat.append(col)

print()

#difference nonstationary controls
#main stationarity rule: can't mix I(1) regressors [nonstationary regressors] with stationary dependent var
controls = [c for c in ['VIX','DXY','US3M'] if c in df.columns]
nonstat_controls = [c for c in nonstat if c in controls]

for c in nonstat_controls:
    df[f'{c}_d'] = df[c].diff()
    p = adfuller(df[f'{c}_d'].dropna())[1]
    print(f"  differenced {c} → {c}_d  (adf={p:.4f})")

#build final control list -> differenced if needed, levels if already I(0)
ctrl = [f'{c}_d' if c in nonstat_controls else c for c in controls]
print(f"\n  controls going into both models: {ctrl}\n")

#model 1: CNY-CNH levels
#series is stationary so we can use step dummies directly
m1_cols  = ['cny_cnh','ann_step','imp_step'] + ctrl
m1_data  = df[m1_cols].dropna()

m1 = arch_model(
    m1_data['cny_cnh'],
    x=m1_data[['ann_step','imp_step'] + ctrl],
    mean='ARX', lags=1,
    vol='GARCH', p=1, q=1,
    dist='t'
)
r1 = m1.fit(disp='off')

#model 2: SHIBOR-HIBOR differenced
#series is I(1) -> difference it, use impulse dummies
#impulse in differences ≡ permanent level shift in the original series
df['shibor_hibor_d'] = df['shibor_hibor'].diff()

p_check = adfuller(df['shibor_hibor_d'].dropna())[1]
assert p_check < 0.05, f"shibor_hibor_d still nonstationary (p={p_check:.4f}) — something's wrong"

m2_cols = ['shibor_hibor_d','ann_imp','imp_imp'] + ctrl
m2_data = df[m2_cols].dropna()

m2 = arch_model(
    m2_data['shibor_hibor_d'],
    x=m2_data[['ann_imp','imp_imp'] + ctrl],
    mean='ARX', lags=1,
    vol='GARCH', p=1, q=1,
    dist='t'
)
r2 = m2.fit(disp='off')

#full model output
print("\n" + "="*65)
print("MODEL 1: CNY-CNH SPREAD (levels)")
print("="*65)
print(r1.summary())

print("\n" + "="*65)
print("MODEL 2: SHIBOR-HIBOR SPREAD (first difference)")
print("="*65)
print(r2.summary())

#clean results table
def row(label, params, pvals, ci):
    if label not in params.index:
        return
    c, p = params[label], pvals[label]
    lo, hi = ci.loc[label,'lower'], ci.loc[label,'upper']
    stars = '***' if p<.01 else '**' if p<.05 else '*' if p<.1 else ''
    print(f"  {label:<30}  {c:>8.4f}  {p:>8.4f}  [{lo:>8.4f}, {hi:>8.4f}]  {stars}")

ci1, ci2 = r1.conf_int(), r2.conf_int()

print("\n" + "="*75)
print("RESULTS")
print("="*75)
print(f"  {'variable':<30}  {'coef':>8}  {'p-val':>8}  {'95% ci':>20}  sig")
print("-"*75)

print("\nmodel 1 — CNY-CNH levels  [PRIMARY]")
for v in ['ann_step','imp_step'] + ctrl:
    row(v, r1.params, r1.pvalues, ci1)
print(f"  garch α+β={r1.params['alpha[1]']+r1.params['beta[1]']:.4f}  "
      f"ν={r1.params['nu']:.2f}  "
      f"n={len(m1_data)}  aic={r1.aic:.1f}")

print("\nmodel 2 — SHIBOR-HIBOR differenced  [SECONDARY]")
for v in ['ann_imp','imp_imp'] + ctrl:
    row(v, r2.params, r2.pvalues, ci2)
print(f"  garch α+β={r2.params['alpha[1]']+r2.params['beta[1]']:.4f}  "
      f"ν={r2.params['nu']:.2f}  "
      f"n={len(m2_data)}  aic={r2.aic:.1f}")

print("\n*** p<.01  ** p<.05  * p<.10")
print("AR(1)-GARCH(1,1), Student-t errors, robust covariance")