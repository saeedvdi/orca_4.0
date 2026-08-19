# SWT1 validation analysis: cases 90_01, 91_01, and 91_02

## Scope

This report compares three SWT1 HPC simulations with the digitized Ye and Ghassemi validation data:

- `90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc`
- `91_01_swt1_bbfast_c26p9_resc7p21_kernel_SV_biot0p6_hpc`
- `91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc`

The cases form a controlled peak- and residual-cohesion study:

| Case | Peak cohesion | Residual cohesion | Purpose |
|---|---:|---:|---|
| `90_01` | 26.39 MPa | 11.176 MPa | 90-series parent; onset calibration |
| `91_01` | 26.88 MPa | 7.21 MPa | Full residual-cohesion reduction |
| `91_02` | 26.88 MPa | 9.19 MPa | Conservative half reduction |

The 0.49 MPa peak-cohesion increase in both 91-series cases is intended to delay the event slightly. Their different residual-cohesion settings then test how much post-failure interlock is needed to match the measured residual stress, dilation, slip, flow, and permeability.

## Differential-stress channel

The differential-stress analysis uses `differential_stress_reaction_mpa_pp`, the corrected reaction-based channel plotted in the current notebook. This channel is consistent with the load-cell reaction and bulk-stress difference. The older `differential_stress_mpa_pp` channel mixes skeleton and total stresses and reads several MPa too low during pressurization, so it is not used here.

## Main result

There is no single winner across every observable:

- `90_01` has the lowest overall mean normalized RMSE, approximately **11.26%**, because it best reproduces the flow, permeability, and much of the dilation history.
- `91_02` is almost tied overall at **11.37%** and gives the best balanced **mechanical residual state**. It substantially improves final differential stress, shear traction, shear slip, and effective normal stress.
- `91_01` has the highest mean normalized RMSE, approximately **14.03%**. Its full residual-cohesion cut is too large and causes excessive slip, contraction, flow, permeability, and stress release.

Case `91_02` is therefore the preferred residual-strength calibration if mechanical endpoints are the main criterion. Case `90_01` remains preferable if the full hydraulic history and aggregate unweighted score are given equal priority. Case `91_01` should be rejected as an overcorrection.

## Quantitative goodness of fit

Each simulation was linearly interpolated to the validation times. Data before 100 s were excluded, and RMSE was normalized by the measured range of each observable. The aggregate score is the unweighted mean of the eight NRMSE values.

| Observable | `90_01` NRMSE | `91_01` NRMSE | `91_02` NRMSE | Best case |
|---|---:|---:|---:|---|
| Differential stress | 15.14% | 14.60% | **12.73%** | `91_02` |
| Injection pressure | 0.92% | **0.92%** | **0.92%** | Tie |
| Flow rate | **4.12%** | 13.40% | 7.37% | `90_01` |
| Fracture permeability | **8.89%** | 20.58% | 14.24% | `90_01` |
| Normal dilation | **14.93%** | 19.27% | 15.67% | `90_01` |
| BB effective normal stress | 16.61% | **11.99%** | 13.83% | `91_01` |
| Shear slip | 14.72% | 15.95% | **13.22%** | `91_02` |
| Shear traction magnitude | 14.77% | 15.53% | **12.94%** | `91_02` |
| **Mean over eight observables** | **11.26%** | 14.03% | 11.37% | `90_01`, narrowly |

The mean score difference between `90_01` and `91_02` is only 0.11 percentage points and is not practically significant by itself. Their strengths differ by category. Averaging the five mechanical quantities other than prescribed pressure gives approximately 15.2% for `90_01`, 15.5% for `91_01`, and **13.7% for `91_02`**. Averaging flow and permeability gives approximately **6.5% for `90_01`**, 17.0% for `91_01`, and 10.8% for `91_02`.

## Coupled-event timing

The main event was detected relative to the 200–900 s baseline using a 10 MPa differential-stress reduction, a 0.01 mm normal-dilation decrease, a 0.02 mm shear-slip increase, and a 5 MPa shear-traction decrease.

| Indicator | Validation | `90_01` | Error | `91_01` | Error | `91_02` | Error |
|---|---:|---:|---:|---:|---:|---:|---:|
| Differential-stress drop | 1720 s | 1621 s | 99 s early | 1639 s | 81 s early | 1643 s | 77 s early |
| Normal-dilation decrease | 1725 s | 1615 s | 110 s early | 1634 s | 91 s early | 1638 s | 87 s early |
| Shear-slip increase | 1650 s | 1610 s | 40 s early | 1630 s | 20 s early | 1633 s | 17 s early |
| Shear-traction drop | 1725 s | 1621 s | 104 s early | 1639 s | 86 s early | 1643 s | 82 s early |

The higher peak cohesion in the 91-series delays the modeled event by approximately 18–23 s and improves all four timing indicators. Case `91_02` is marginally later than `91_01` by 3–4 s because its stronger residual response feeds back during the transition, even though both cases have the same peak envelope.

The slip onset in `91_02` is only about 17 s early, but its stress and dilation drops remain roughly 77–87 s early. This reveals a model-form limitation: the experiment transitions progressively from first slip near 1650 s to the main stress and dilation changes near 1720–1725 s, whereas the simulations complete these coupled changes almost simultaneously. Static peak cohesion can move the onset but cannot reproduce the measured 70 s transition duration.

## Observable-by-observable interpretation

### Differential stress

All three cases reproduce the approximately 150 MPa pre-event plateau. The 91-series peak-cohesion increase delays the abrupt drop and therefore improves event timing. Their post-event behavior separates according to residual cohesion.

At 3370 s, the measured differential stress is 62.68 MPa. Case `90_01` remains high at 71.52 MPa, an error of +8.83 MPa. The full residual cut in `91_01` overshoots to 57.58 MPa, an error of -5.10 MPa. Case `91_02` finishes at 64.58 MPa, only +1.90 MPa high, and gives the best full-history differential-stress error.

This result confirms that the parent residual cohesion is too large but that the full 3.97 MPa cut in `91_01` is excessive. The half-step in `91_02` brackets the observed residual much more successfully.

### Injection pressure

All three simulations reproduce the pressure staircase, peak, and unloading history nearly exactly. Their normalized pressure errors are approximately 0.92%, and all finish within 0.01 MPa of the validation endpoint. Pressure therefore does not distinguish the material calibrations.

### Flow rate

All cases capture the abrupt hydraulic response and staged decline, but their magnitudes increase as residual cohesion decreases. The measured peak is 6.22 mL/min at 1750 s:

- `90_01` peaks at 5.74 mL/min, about 7.8% low.
- `91_02` peaks at 6.67 mL/min, about 7.2% high.
- `91_01` peaks at 7.71 mL/min, about 24% high.

The modeled peaks occur near 1886–1900 s, about 136–150 s late. Case `91_02` gives the closest peak magnitude, but `90_01` has the lowest full-history error because its later flow plateaus are lower. At 3250 s, the measured flow is 0.462 mL/min, compared with 0.598, 0.666, and 0.733 mL/min for `90_01`, `91_02`, and `91_01`, respectively.

### Fracture permeability

The permeability response follows the same ordering as flow rate. The measured maximum is `1.37e-12 m²` at 1750 s. Case `90_01` reaches `1.30e-12 m²`, `91_02` reaches `1.43e-12 m²`, and `91_01` reaches `1.58e-12 m²`. Thus, `91_02` gives the closest peak magnitude, but all modeled peaks occur about 136–150 s late.

The residual values remain too high in all cases. At 3250 s, the validation value is `0.94e-12 m²`, versus `1.14e-12 m²` for `90_01`, `1.23e-12 m²` for `91_02`, and `1.32e-12 m²` for `91_01`. Reducing residual cohesion improves mechanical residuals but increases persistent hydraulic aperture beyond the measured level.

### Normal dilation

The measured minimum is -0.1612 mm near 1745 s. Case `90_01` underpredicts the contraction magnitude at -0.1446 mm, `91_01` overpredicts it at -0.1700 mm, and `91_02` gives the closest extremum at -0.1572 mm. The modeled minima occur near 1886–1900 s, roughly 141–155 s late.

Despite the good peak magnitude in `91_02`, all simulations recover too little by the end of the test. At 3370 s, the validation value is -0.1118 mm, compared with -0.1285 mm for `90_01`, -0.1372 mm for `91_02`, and -0.1453 mm for `91_01`. Lower residual cohesion increases permanent contraction and worsens the endpoint. This is why `90_01` retains the lowest full-history dilation error.

### BB effective normal stress

All cases capture the stepped pre-event reduction, event-related trough, and subsequent recovery. The measured minimum is 31.56 MPa. Case `90_01` remains too high at 37.72 MPa, while `91_01` improves it to 34.54 MPa and `91_02` gives 36.14 MPa. The minima occur around 1886–1900 s, 26–40 s after the measured minimum at 1860 s.

At 3370 s, the measured normal stress is 41.10 MPa. The modeled values are 48.35 MPa for `90_01`, 46.84 MPa for `91_02`, and 45.22 MPa for `91_01`. Reducing residual cohesion improves this observable, and the full cut in `91_01` gives the lowest normal-stress error. Even that case still recovers about 4.1 MPa too high.

### Shear slip

The measured maximum is approximately 0.5425 mm. Case `90_01` underpredicts it at 0.4930 mm, while `91_01` overpredicts it at 0.5748 mm. Case `91_02` reaches 0.5339 mm and is closest to the measured maximum.

At 3370 s, the validation value is 0.5204 mm. Case `90_01` is 0.0276 mm low, `91_01` is 0.0541 mm high, and `91_02` is only 0.0133 mm high. The half residual-cohesion reduction therefore provides the best slip calibration and confirms that the parent joint arrests too early while the full-cut case arrests too late.

### Shear traction magnitude

All cases reproduce the pre-event traction plateau. The 91-series peak-cohesion increase delays the main drop, while residual cohesion controls the final level.

At 3370 s, the validation value is 28.16 MPa. Case `90_01` remains high at 31.08 MPa, case `91_01` falls too low to 24.61 MPa, and case `91_02` ends at 27.85 MPa, only 0.30 MPa low. This is the clearest evidence that 9.19 MPa residual cohesion is a much better SWT1 residual-strength setting than either 11.176 or 7.21 MPa.

## Peak and final-value summary

| Quantity | Validation | `90_01` | `91_01` | `91_02` |
|---|---:|---:|---:|---:|
| Peak flow rate | 6.22 mL/min | 5.74 mL/min | 7.71 mL/min | 6.67 mL/min |
| Peak fracture permeability | 1.37e-12 m² | 1.30e-12 m² | 1.58e-12 m² | 1.43e-12 m² |
| Most negative normal dilation | -0.1612 mm | -0.1446 mm | -0.1700 mm | -0.1572 mm |
| Minimum BB effective normal stress | 31.56 MPa | 37.72 MPa | 34.54 MPa | 36.14 MPa |
| Maximum shear slip | 0.5425 mm | 0.4930 mm | 0.5748 mm | 0.5339 mm |
| Final differential stress | 62.68 MPa | 71.52 MPa | 57.58 MPa | 64.58 MPa |
| Final flow rate | 0.462 mL/min | 0.598 mL/min | 0.733 mL/min | 0.666 mL/min |
| Final fracture permeability | 0.940e-12 m² | 1.141e-12 m² | 1.322e-12 m² | 1.233e-12 m² |
| Final normal dilation | -0.1118 mm | -0.1285 mm | -0.1453 mm | -0.1372 mm |
| Final BB effective normal stress | 41.10 MPa | 48.35 MPa | 45.22 MPa | 46.84 MPa |
| Final shear slip | 0.5204 mm | 0.4928 mm | 0.5745 mm | 0.5337 mm |
| Final shear traction | 28.16 MPa | 31.08 MPa | 24.61 MPa | 27.85 MPa |

## Interpretation of the residual-cohesion bracket

The three cases demonstrate a monotonic residual-strength tradeoff:

- High residual cohesion in `90_01` retains too much differential and shear stress and suppresses slip, dilation, flow, and permeability.
- Low residual cohesion in `91_01` releases too much stress and produces excessive displacement and hydraulic enhancement.
- Intermediate residual cohesion in `91_02` provides the best mechanical compromise and closely matches final differential stress, shear traction, and shear slip.

Linear interpolation of endpoint responses gives approximate preferred residual-cohesion values of:

- About 8.7 MPa from final differential stress.
- About 9.4 MPa from final shear traction.
- About 9.8 MPa from final shear slip.

These values are only local estimates because the response is nonlinear and hydraulically coupled. Nevertheless, they consistently place the useful range near **9–10 MPa**, strongly supporting `91_02` over the full-cut `91_01` case.

The remaining mismatches cannot all be removed with residual cohesion alone. Raising residual cohesion would reduce the excessive final flow, permeability, and contraction, but it would also move differential stress and shear traction back above their targets and reduce slip. The hydraulic and normal-displacement residuals therefore require a separate post-event aperture or dilation adjustment rather than another large residual-cohesion change.

## Recommended case and next refinement

For a single mechanically representative SWT1 case, select **`91_02`**. It has:

1. The best differential-stress history of the three.
2. Final shear traction within 0.31 MPa of validation.
3. Final differential stress within 1.90 MPa.
4. Final shear slip within 0.013 mm.
5. Better event timing than `90_01`.

Retain `90_01` as the better hydraulic-history reference and as evidence that simply increasing residual cohesion is not a complete solution. Do not select `91_01`; the 7.21 MPa residual cohesion overcorrects the parent and produces the worst aggregate error.

A narrow residual-cohesion refinement around 9.3–9.7 MPa could further balance differential stress, shear traction, and slip, but it will not by itself fix the late and persistent hydraulic response. That response should be calibrated through post-event hydraulic aperture, permeability decay, or dilation-recovery controls while preserving the `91_02` peak envelope and event timing.

## Conclusion

The 91-series peak-cohesion increase improves SWT1 event timing, and the residual-cohesion bracket identifies `91_02` as the best mechanical calibration. Its 9.19 MPa residual cohesion avoids both the parent case's under-slip and the full-cut case's excessive weakening. It closely matches the key residual stress and displacement targets while retaining an aggregate error almost identical to `90_01`.

The full residual cut in `91_01` is too aggressive and should be rejected. `90_01` and `91_02` expose a remaining separation between mechanical and hydraulic calibration: `91_02` is mechanically superior, while `90_01` better matches the complete flow and permeability histories. The next useful change is therefore not another broad strength adjustment, but a targeted reduction of persistent post-event hydraulic aperture and contraction in the `91_02` framework.
