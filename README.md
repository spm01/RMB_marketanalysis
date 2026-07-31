# Sanctions and Regime Shifts: Offshore RMB Demand in Spot and Interbank Markets
### High-Frequency Evidence from the 2022 Russia Sanctions
---

## Overview

This paper examines whether the February 2022 Russia sanctions — the largest 
peacetime asset freeze in history — caused a permanent structural shift in 
offshore RMB market conditions.

When the US and EU froze approximately $300 billion in Russian central bank 
reserves, every government holding dollar reserves watched. The economic logic 
of a shift toward offshore RMB is straightforward: if dollar reserves can be 
frozen unilaterally, the cost of holding them rises for any potential future 
target. This paper asks whether that logic translated into measurable market 
behavior.

This is **Part 1 of a two-part research project** on RMB internationalization.  
Part 2 will test whether PBOC bilateral currency swap lines mitigated the 
demand shock identified here, using a staggered difference-in-differences 
design with causal forest heterogeneous treatment effects.

---

## Key Finding: Channel Decomposition

The result depends entirely on which market you look at.

| Channel | Instrument | Sanctions Effect | Dominant Driver |
|---|---|---|---|
| Spot FX | CNY-CNH spread | **Not significant** | Dollar appreciation (DXY) |
| Interbank funding | SHIBOR-HIBOR spread | **Highly significant** | Offshore RMB demand |

**The spot exchange rate story that dominated 2022 headlines was a dollar 
story, not an RMB story.** Once Federal Reserve tightening is controlled for, 
the CNY-CNH sanctions effect disappears entirely.

**The interbank funding market tells a different story.** The SHIBOR-HIBOR 
differential compressed permanently following both shock dates, with dollar 
dynamics playing no role (DXY p = 0.615). This is consistent with global 
institutions shifting offshore RMB liquidity exposures after observing Russian 
reserves frozen.

---

## Results

**Model 1 — CNY-CNH Spread (levels, step dummies)**

- Announce (step): β = −1.65 bps, p = 0.505 — *not significant*
- Implement (step): β = −0.85 bps, p = 0.735 — *not significant*
- ΔDXY: β = −6.22 bps, p < 0.001*** — *dominant predictor*
- GARCH persistence α + β = 0.993

**Model 2 — SHIBOR-HIBOR Spread (first difference, impulse dummies)**

- Announce (impulse): β = −1.02 bps, p < 0.001***
- Implement (impulse): β = −0.78 bps, p < 0.001***
- ΔDXY: β = −0.047, p = 0.615 — *irrelevant in this channel*
- GARCH persistence α + β = 1.000 (permanent volatility shift)

Both models use AR(1)-GARCH(1,1) with Student-t errors (ν = 4.24 and 2.97 
respectively), appropriate for the fat-tailed behavior of high-frequency 
financial spreads.

---

## Data

All data sourced from Bloomberg Professional terminal.

| Variable | Bloomberg Ticker | Role |
|---|---|---|
| Onshore CNY | `CNY REGN Curncy` | Dependent (spread) |
| Offshore CNH | `CNH BGN Curncy` | Dependent (spread) |
| 3M SHIBOR | `SHIF3M Index` | Dependent (spread) |
| 3M CNH HIBOR | `HIHD01M Index` | Dependent (spread) |
| VIX | `VIX Index` | Control — global risk sentiment |
| DXY | `DXY Curncy` | Control — dollar strength |
| US 3M Yield | `USGG3M Index` | Control — Fed policy |

**Sample:** January 2, 2020 — December 31, 2025 (1,454 trading day 
observations after cleaning)

Holiday treatment: Chinese market closures (Chinese New Year, National Day) 
handled via last-observation-carried-forward with a maximum two-day gap 
tolerance, using the Shanghai Stock Exchange calendar.

---

## Methodology

- **Stationarity:** ADF + Zivot-Andrews structural break tests on all 
  variables; nonstationary series first-differenced before inclusion
- **Model:** AR(1)-GARCH(1,1), Student-t errors, robust covariance — 
  following Engle (1982), Bollerslev (1986), Box and Tiao (1975)
- **Shock identification:** Step dummies for the stationary CNY-CNH model; 
  impulse dummies for the differenced SHIBOR-HIBOR model (mathematically 
  equivalent permanent level shift interpretation per Lütkepohl 2004)
- **Two shock dates:** Announcement (Feb 28, 2022) and implementation 
  (Mar 14, 2022), shifted to first available Monday after weekend announcements

---

## Repository Structure
The pipeline is self-contained and reproducible. Running `rmb_analysis_final.py` 
with the underlying Bloomberg data produces all results in the paper.

**Dependencies:** Python 3.13, `arch`, `statsmodels`, `pandas`, `numpy`, 
`exchange_calendars`

---

## Limitations

- Identification rests on before-after variation in a single aggregate time 
  series; no cross-sectional control group
- PBOC intervention in offshore CNH markets during 2022 is an unresolved 
  confounder that could independently affect HIBOR dynamics
- SHIBOR-HIBOR result should be treated as strongly suggestive rather than 
  definitive given near-unit-root persistence

These limitations motivate Part 2 of this project directly.

---

## Part 2: Future Work

Part 2 will exploit the staggered rollout of PBOC bilateral currency swap lines 
to test whether swap-line countries were insulated from the offshore RMB demand 
shock identified here. 

The basis design is as follows:

- **Identification:** Staggered DiD
  comparing swap-line vs non-swap-line countries using SWIFT payment data
- **Heterogeneous effects:** Identify which country 
  characteristics predict differential shock exposure
- **Connecting to literature:** Direct extension of Bahaj and Reis (2026) 
  into the post-2022 sanctions regime

---

## References

Bahaj, S. and Reis, R. (2026). "Jumpstarting an International Currency." 
*Review of Economic Studies*, 00, 1–32.

Bollerslev, T. (1986). "Generalized Autoregressive Conditional 
Heteroskedasticity." *Journal of Econometrics*, 31(3), 307–327.

Box, G.E.P. and Tiao, G.C. (1975). "Intervention Analysis with Applications 
to Economic and Environmental Problems." *JASA*, 70(349), 70–79.

Chupilkin, M., Javorcik, B., Peeva, A. and Plekhanov, A. (2023). "Exorbitant 
Privilege and Economic Sanctions." EBRD Working Paper No. 281.

Engle, R.F. (1982). "Autoregressive Conditional Heteroscedasticity with 
Estimates of the Variance of United Kingdom Inflation." *Econometrica*, 
50(4), 987–1007.

Lütkepohl, H. (2004). *Applied Time Series Econometrics*. Cambridge 
University Press.

Perron, P. (1989). "The Great Crash, the Oil Price Shock, and the Unit Root 
Hypothesis." *Econometrica*, 57(6), 1361–1401.

Zivot, E. and Andrews, D.W.K. (1992). "Further Evidence on the Great Crash, 
the Oil-Price Shock, and the Unit-Root Hypothesis." *JBES*, 10(3), 251–270.

---

*Contact the author for data availability. All analysis in Python 3.13.*
