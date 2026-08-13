# Dollar Dynamics, Not Dollar Weaponization
### Reassessing the 2022 Russia Sanctions Effect on Onshore-Offshore RMB Pricing

---

## Overview

Did the February 2022 Russia sanctions cause a permanent structural shift in
offshore RMB pricing?

When the US and EU froze roughly $300 billion in Russian central bank reserves,
every government holding dollar reserves took notice. The economic logic of a
shift toward offshore RMB is straightforward: if dollar reserves can be frozen
unilaterally, the cost of holding them rises for any potential future target.
This paper tests whether that logic showed up in market prices.

**It did not.** Once concurrent dollar dynamics are controlled for, the sanctions
effect disappears entirely.

---

## Key Finding

The CNY-CNH basis spread is the most widely cited market indicator of
onshore-offshore RMB divergence. Its 2022 movement was a dollar story, not an
RMB story.

| | Coefficient | p-value | Verdict |
|---|---|---|---|
| Announcement (Feb 28, 2022) | −1.65 bps | 0.505 | Not significant |
| Implementation (Mar 14, 2022) | −0.85 bps | 0.735 | Not significant |
| ΔDXY | **−6.22 bps** | **<0.001** | **Dominant predictor** |

Every one-point DXY appreciation compresses the spread by 6.22 bps. 

**Secondary finding:** GARCH persistence of α + β = 0.993 indicates volatility
shocks to the spread do not decay within the sample. The sanctions produced a
volatility regime change without a level shift.

---

## Full Results

**AR(1)-GARCH(1,1), Student-t errors, robust covariance**

| Variable | Coef. | Std. Err. | p-value |
|---|---|---|---|
| Constant | 1.047 | 1.332 | 0.432 |
| AR(1) | 0.633 | 0.029 | <0.001 |
| Announcement (step) | −1.652 | 2.479 | 0.505 |
| Implementation (step) | −0.855 | 2.525 | 0.735 |
| VIX | −0.072 | 0.061 | 0.235 |
| ΔDXY | −6.218 | 0.777 | <0.001 |
| ΔUS 3M yield | −0.625 | 9.604 | 0.948 |
| GARCH α | 0.143 | 0.051 | 0.005 |
| GARCH β | 0.850 | 0.055 | <0.001 |
| ν (d.o.f.) | 4.239 | 0.500 | <0.001 |

N = 1,453. Adj. R² = 0.375. AIC = 11,130.6. BIC = 11,188.6. α + β = 0.993.

---

## Data

All series from Bloomberg Professional terminal, January 2, 2020 to
December 31, 2025.

| Variable | Ticker | Role |
|---|---|---|
| Onshore CNY | `CNY REGN Curncy` | Dependent (spread leg) |
| Offshore CNH | `CNH BGN Curncy` | Dependent (spread leg) |
| VIX | `VIX Index` | Control, risk sentiment |
| DXY | `DXY Curncy` | Control, dollar strength |
| US 3M yield | `USGG3M Index` | Control, Fed policy |

Chinese market closures (Chinese New Year, National Day) handled via LOCF (last observation carried forward) with a
two-day maximum gap tolerance, using the Shanghai Stock Exchange calendar.

---

## Methodology

- **Stationarity:** ADF plus Zivot-Andrews structural break testing. CNY-CNH is
  I(0) and modeled in levels; DXY and US 3M yield are I(1) and first-differenced
- **Model:** AR(1)-GARCH(1,1) with Student-t errors, following Engle (1982) and
  Bollerslev (1986)
- **Shock identification:** Step dummies in the mean equation, following the
  intervention analysis framework of Box and Tiao (1975)
- **Two shock dates:** announcement and implementation, each rolled to the first
  available trading day after the weekend announcement

Run `rmb_analysis_final.py` with the underlying Bloomberg data to reproduce all
results. Dependencies: Python 3.13, `arch`, `statsmodels`, `pandas`, `numpy`,
`exchange_calendars`.

---

## Limitations

- Identification rests on before-after variation in a single aggregate time
  series with no cross-sectional control group
- PBOC intervention in offshore CNH markets during 2022 is an unresolved
  confounder that could have suppressed spread movement independently

**Abandoned interbank specification.** A SHIBOR-HIBOR funding channel test was
attempted and dropped. The HIBOR series available on the terminal used is
HKD-denominated rather than CNH, making the spread cross-currency rather than
onshore-offshore. Because the HKD is pegged to the USD, the resulting spread
contains a US rate component by construction. The correct approach is a synthetic
offshore RMB rate built from USDCNH forward points under covered interest parity,
following Bahaj and Reis (2026). Left to future work.

---

## References

Bahaj, S. and Reis, R. (2026). "Jumpstarting an International Currency."
*Review of Economic Studies*, 00, 1–32.

Bollerslev, T. (1986). "Generalized Autoregressive Conditional
Heteroskedasticity." *Journal of Econometrics*, 31(3), 307–327.

Box, G.E.P. and Tiao, G.C. (1975). "Intervention Analysis with Applications to
Economic and Environmental Problems." *JASA*, 70(349), 70–79.

Chupilkin, M., Javorcik, B., Peeva, A. and Plekhanov, A. (2023). "Exorbitant
Privilege and Economic Sanctions." EBRD Working Paper No. 281.

Engle, R.F. (1982). "Autoregressive Conditional Heteroscedasticity with
Estimates of the Variance of United Kingdom Inflation." *Econometrica*, 50(4),
987–1007.

Perron, P. (1989). "The Great Crash, the Oil Price Shock, and the Unit Root
Hypothesis." *Econometrica*, 57(6), 1361–1401.

Zivot, E. and Andrews, D.W.K. (1992). "Further Evidence on the Great Crash, the
Oil-Price Shock, and the Unit-Root Hypothesis." *JBES*, 10(3), 251–270.

---

*Contact the author for data availability. All analysis in Python 3.13.*
