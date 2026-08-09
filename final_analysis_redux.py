import pandas as pd
import numpy as np
import warnings
from statsmodels.tsa.stattools import adfuller, zivot_andrews
from arch import arch_model
import os

os.chdir("c:/Users/Sean/OneDrive/Desktop/Python/RMB_project")

#load and rename
df = pd.read_csv('master_dataframe.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date').sort_index()

df = df.rename(columns={
    'CNY REGN Curncy': 'CNY',
    'CNH BGN Curncy':  'CNH',
    'SHIF3M Index':    'SHIBOR',
    'HIHD01M Index':   'HIBOR',
    'VIX Index':       'VIX',
    'DXY Curncy':      'DXY',
    'USGG3M Index':    'US3M'
})


#LOCF for chinese holiday closures, max 2 day gap
fill_cols = ['CNY', 'CNH', 'SHIBOR', 'HIBOR', 'VIX', 'DXY', 'US3M']
valid_cols = [c for c in fill_cols if c in df.columns]
df[valid_cols] = df[valid_cols].ffill(limit=2)
df = df.dropna(subset=['CNY', 'CNH', 'SHIBOR', 'HIBOR'])

print(len(df), "obs after holiday cleaning\n")

#construct spreads
df['cny_cnh'] = ((df['CNY'] - df['CNH']) / df['CNH']) * 10000
df['shibor_hibor'] = (df['SHIBOR'] - df['HIBOR']) * 100

print(df[['cny_cnh', 'shibor_hibor']].describe().round(2), "\n")

#event dummies
df['ann_step'] = (df.index >= '2022-02-28').astype(int)
df['imp_step'] = (df.index >= '2022-03-14').astype(int)
df['ann_imp'] = (df.index == '2022-02-28').astype(int)
df['imp_imp'] = (df.index == '2022-03-14').astype(int)

print("Post-announcement obs:", df['ann_step'].sum())
print("Post-implementation obs:", df['imp_step'].sum())
print("Announce impulse fires:", df['ann_imp'].sum())
print("Implement impulse fires:", df['imp_imp'].sum())

#stationarity tests
adf_cny = adfuller(df['cny_cnh'].dropna())[1]
za_cny  = zivot_andrews(df['cny_cnh'].dropna(), regression='c')[1]
print("CNY-CNH spread ADF:", round(adf_cny, 4), "ZA:", round(za_cny, 4))

adf_shibor = adfuller(df['shibor_hibor'].dropna())[1]
za_shibor  = zivot_andrews(df['shibor_hibor'].dropna(), regression='c')[1]
print("SHIBOR-HIBOR spread ADF:", round(adf_shibor, 4), "ZA:", round(za_shibor, 4))

adf_vix = adfuller(df['VIX'].dropna())[1]
adf_dxy = adfuller(df['DXY'].dropna())[1]
adf_us3 = adfuller(df['US3M'].dropna())[1]

print("VIX ADF:", round(adf_vix, 4))
print("DXY ADF:", round(adf_dxy, 4))
print("US3M ADF:", round(adf_us3, 4), "\n")

#differencing the known failures (DXY and US3M)
df['DXY_d'] = df['DXY'].diff()
df['US3M_d'] = df['US3M'].diff()

check_dxy = adfuller(df['DXY_d'].dropna())[1]
check_us3 = adfuller(df['US3M_d'].dropna())[1]
print("Differenced DXY ADF:", round(check_dxy, 4))
print("Differenced US3M ADF:", round(check_us3, 4))

#hardcode the final control list since we know exactly what we are using
ctrl_vars = ['VIX', 'DXY_d', 'US3M_d']
print("Controls going into models:", ctrl_vars)

#model 1: CNY-CNH levels
m1_vars = ['cny_cnh', 'ann_step', 'imp_step'] + ctrl_vars
m1_data = df[m1_vars].dropna()

m1 = arch_model(
    m1_data['cny_cnh'],
    x=m1_data[['ann_step', 'imp_step'] + ctrl_vars],
    mean='ARX', lags=1,
    vol='GARCH', p=1, q=1,
    dist='t'
)
r1 = m1.fit(disp='off')

#model 2: SHIBOR-HIBOR differenced
df['shibor_hibor_d'] = df['shibor_hibor'].diff()
check_shibor = adfuller(df['shibor_hibor_d'].dropna())[1]
print("Differenced SHIBOR-HIBOR ADF:", round(check_shibor, 4))

m2_vars = ['shibor_hibor_d', 'ann_imp', 'imp_imp'] + ctrl_vars
m2_data = df[m2_vars].dropna()

m2 = arch_model(
    m2_data['shibor_hibor_d'],
    x=m2_data[['ann_imp', 'imp_imp'] + ctrl_vars],
    mean='ARX', lags=1,
    vol='GARCH', p=1, q=1,
    dist='t'
)
r2 = m2.fit(disp='off')

#full summaries
print("MODEL 1: CNY-CNH SPREAD (levels)")
print(r1.summary())

print("MODEL 2: SHIBOR-HIBOR SPREAD (first difference)")
print(r2.summary())

#output clean results using pandas DataFrames instead of building an ASCII table
print("RESULTS SUMMARY")

res1 = pd.DataFrame({
    'Coefficient': r1.params,
    'P-Value': r1.pvalues,
    'CI_Lower': r1.conf_int()['lower'],
    'CI_Upper': r1.conf_int()['upper']
})
print("\nMODEL 1 (CNY-CNH):")
print(res1.round(4))

res2 = pd.DataFrame({
    'Coefficient': r2.params,
    'P-Value': r2.pvalues,
    'CI_Lower': r2.conf_int()['lower'],
    'CI_Upper': r2.conf_int()['upper']
})
print("\nMODEL 2 (SHIBOR-HIBOR):")
print(res2.round(4))