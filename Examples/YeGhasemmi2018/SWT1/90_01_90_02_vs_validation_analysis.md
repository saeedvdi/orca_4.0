# 90-series validation comparisons: SWT1, SWT2, SWS3, and SWS4

## Scope

This report compares the two SWT1 HPC simulations shown in the figure with the digitized Ye and Ghassemi validation data:

- `90_01_swt1_bbfast_cohesion_c26p4_kernel_SV_biot0p6_hpc`
- `90_02_swt1_bbfast_cohesion_c28p0_kernel_SV_biot0p6_hpc`

The two input decks form a focused cohesion bracket. Their peak-cohesion settings are `2.639e7 Pa` (26.39 MPa) and `2.800e7 Pa` (28.00 MPa), respectively. The residual cohesion remains `1.1176e7 Pa` in both decks, and the remaining constitutive settings are unchanged. Consequently, the large difference between the responses isolates the sensitivity of the predicted instability to the peak-cohesion setting.

## Main result

Case `90_01` is the successful member of this pair. It reproduces the observed coupled event: differential and shear stresses fall, normal dilation becomes negative, shear slip develops, and both flow rate and fracture permeability increase. Its average normalized RMSE over all eight observables is approximately **11.2%**.

Case `90_02` does not reproduce the experiment. Although it tracks the imposed injection-pressure history almost exactly, it remains mechanically locked over the full test. It therefore misses the stress drop, slip, dilation, permeability enhancement, and large flow-rate increase. Its average normalized RMSE is approximately **50.9%**.

The increase in peak cohesion from 26.39 to 28.00 MPa therefore crosses the modeled failure threshold. This is a regime change rather than a small, proportional adjustment to the curves.

## Quantitative goodness of fit

For each validation observable, the simulation was linearly interpolated to the digitized measurement times. RMSE was normalized by the measured range of that observable. The aggregate score is the unweighted mean of the eight normalized errors; the near-zero initialization interval before 100 s was excluded.

| Observable | `90_01` RMSE | `90_01` NRMSE | `90_02` RMSE | `90_02` NRMSE |
|---|---:|---:|---:|---:|
| Differential stress | 12.67 MPa | 14.6% | 57.95 MPa | 66.6% |
| Injection pressure | 0.192 MPa | 0.9% | 0.192 MPa | 0.9% |
| Flow rate | 0.254 mL/min | 4.1% | 2.337 mL/min | 37.9% |
| Fracture permeability | 1.03e-13 m² | 8.9% | 6.57e-13 m² | 56.7% |
| Normal dilation | 0.0243 mm | 14.9% | 0.0909 mm | 55.8% |
| BB effective normal stress | 5.71 MPa | 16.6% | 17.27 MPa | 50.3% |
| Shear slip | 0.0801 mm | 14.7% | 0.3678 mm | 67.6% |
| Shear traction magnitude | 5.77 MPa | 14.8% | 28.05 MPa | 71.7% |
| **Mean over eight observables** |  | **11.2%** |  | **50.9%** |

Both cases have the same excellent pressure score because pressure is prescribed by the loading schedule. The pressure agreement therefore does not, on its own, validate the mechanical or hydraulic response.

## Event timing

Event times were identified from departures relative to the 200–900 s pre-event baseline. The thresholds used were a 10 MPa differential-stress drop, a 0.01 mm decrease in normal dilation, a 0.02 mm increase in shear slip, and a 5 MPa shear-traction drop.

| Event indicator | Validation | `90_01` | Timing error | `90_02` |
|---|---:|---:|---:|---:|
| Differential-stress drop | 1720 s | 1620 s | 100 s early | Not reached |
| Normal-dilation decrease | 1725 s | 1615 s | 110 s early | Not reached |
| Shear-slip increase | 1650 s | 1610 s | 40 s early | Not reached |
| Shear-traction drop | 1725 s | 1621 s | 104 s early | Not reached |

Case `90_01` consistently initiates the mechanical transition somewhat too early. The error is modest compared with the duration of the experiment, but it is systematic. Case `90_02` never reaches any of the four event thresholds.

## Observable-by-observable interpretation

### Differential stress

The validation data remain near 150 MPa before failure and settle near 63 MPa afterward. Case `90_01` gives a similar pre-event level and the correct abrupt transition shape, but it drops about 100 s early and retains approximately 68 MPa at the end. Thus, it underpredicts the total stress release by about 5.4 MPa at the final validation time.

Case `90_02` remains near 146–147 MPa and finishes about 84 MPa above the validation value. It does not undergo the observed failure event.

### Injection pressure

Both simulations reproduce the stepped rise to about 28 MPa and the subsequent unloading sequence very closely. Their injection-pressure NRMSE values are both below 1%. This agreement confirms that the loading histories are aligned, so the contrasting mechanical responses arise from the model strength rather than a different pressure schedule.

### Flow rate

Case `90_01` captures the large flow-rate increase and its subsequent stepwise decline. Its maximum is approximately 5.74 mL/min, compared with 6.22 mL/min in the validation data, an underprediction of about 7.8%. The simulated maximum occurs near 1886 s, about 136 s later than the measured maximum near 1750 s.

Case `90_02` reaches only about 0.41 mL/min and then falls toward zero. The absence of a strong fracture-opening and slip event prevents the hydraulic transmissivity increase seen experimentally.

### Fracture permeability

Case `90_01` correctly produces a sharp permeability increase. Its peak is approximately `1.30e-12 m²`, about 5.4% below the measured `1.37e-12 m²`, and occurs about 136 s late. It finishes at approximately `1.14e-12 m²`, which is `2.01e-13 m²` above the last digitized value.

Case `90_02` remains close to its initial permeability, reaching only about `2.26e-13 m²`. It therefore misses both the magnitude and the physical cause of the observed permeability enhancement.

### Normal dilation

The validation curve changes rapidly to negative normal displacement during failure and then partially recovers. Case `90_01` reproduces that sign, transition, and recovery trend. Its most negative value is about -0.145 mm, compared with -0.161 mm in the validation data, so its peak displacement magnitude is about 10% too small. The simulated extremum occurs near 1886 s, approximately 141 s after the measured extremum.

At the end of the record, `90_01` remains slightly too negative (-0.129 mm versus -0.112 mm). Case `90_02` stays close to zero and entirely misses the measured normal-displacement response.

### BB effective normal stress

Before the event, both cases follow the stepped reduction reasonably well. During failure, `90_01` drops to about 38 MPa and then recovers stepwise, matching the measured response qualitatively. Its final value is about 48.3 MPa, approximately 7.2 MPa above the digitized value of 41.1 MPa. This is the largest normalized error among the eight `90_01` observables, although it remains far smaller than the error in `90_02`.

Case `90_02` does not show the event-related normal-stress drop. It instead rises during the later unloading steps and ends near 65.8 MPa, about 24.7 MPa too high.

### Shear slip

Case `90_01` captures the abrupt onset and persistent post-event slip. Its peak value is approximately 0.493 mm, about 0.049 mm or 9.1% below the measured maximum of 0.542 mm. The validation data continue to accumulate some slip after the main event, whereas the simulation settles at a lower level.

Case `90_02` develops less than 0.01 mm of slip. It is consequently incompatible with the approximately 0.52 mm final displacement measured in the experiment.

### Shear traction magnitude

Case `90_01` reproduces the sudden shear-traction loss and the low post-event plateau. Its final value is about 31.1 MPa, roughly 2.9 MPa above the digitized value. The curve shape and event timing are consistent with its differential-stress response.

Case `90_02` retains almost all of its shear traction and ends near 68.0 MPa, about 39.8 MPa above the validation data. It has the largest individual normalized error in this comparison, approximately 71.7%.

## Peak and final-value summary

| Quantity | Validation | `90_01` | `90_02` |
|---|---:|---:|---:|
| Peak flow rate | 6.22 mL/min | 5.74 mL/min | 0.41 mL/min |
| Peak fracture permeability | 1.37e-12 m² | 1.30e-12 m² | 2.26e-13 m² |
| Most negative normal dilation | -0.161 mm | -0.145 mm | -0.001 mm |
| Maximum shear slip | 0.542 mm | 0.493 mm | 0.010 mm |
| Final differential stress | 62.68 MPa | 68.10 MPa | 146.62 MPa |
| Final BB effective normal stress | 41.10 MPa | 48.35 MPa | 65.79 MPa |
| Final shear traction | 28.16 MPa | 31.08 MPa | 67.96 MPa |

## Interpretation of the cohesion bracket

The result places the transition between a slipping and a locked response somewhere between the two tested peak-cohesion values. At 26.39 MPa, the joint fails slightly too early; at 28.00 MPa, it does not fail at all. Because the residual cohesion and other constitutive parameters are fixed, the contrast demonstrates that the calibration is close to a discrete stability boundary.

The present pair does not justify a simple linear interpolation of every output value: the response is nonlinear and changes branch when failure is suppressed. It does, however, provide a useful bracket for a narrower search. A new peak-cohesion value between 26.39 and 28.00 MPa should be tested, with the primary acceptance condition being that the coupled mechanical event occurs near 1650–1725 s. Matching pressure alone should not be used as the selection criterion.

For any intermediate case, the following secondary features should then be checked:

1. The mechanical onset in `90_01` should be delayed by roughly 40–110 s.
2. The flow and permeability peaks should occur earlier than the `90_01` peaks while retaining their observed magnitudes.
3. The final shear slip should increase from approximately 0.493 mm toward 0.520 mm.
4. The final differential, effective-normal, and shear stresses should all decrease toward the digitized residual values.

## Conclusion

`90_01` is a credible, physically consistent SWT1 calibration and is decisively better than `90_02`. It captures all major couplings and achieves an approximately 11.2% mean normalized error, but it initiates failure early and retains slightly too much post-event stress. Its hydraulic extrema are also delayed relative to the digitized data, even though its mechanical onset is early, indicating that the simulated transition is more spread out than the measured event.

`90_02` should not be selected as a validation match. Its 28.00 MPa peak cohesion prevents the instability, leaving the joint locked and producing approximately 50.9% mean normalized error. The two cases together show that the best peak-cohesion setting lies within a narrow interval above 26.39 MPa but below the value at which failure is suppressed.

---

# SWT2 validation comparison: cohesion cases 90_03 and 90_04

## Scope

This section compares the following SWT2 HPC simulations with the digitized Ye and Ghassemi validation data:

- `90_03_swt2_bbfast_theta30_cohesion_c33p2_kernel_SV_biot0p6_hpc`
- `90_04_swt2_bbfast_theta30_cohesion_c35p0_kernel_SV_biot0p6_hpc`

The peak cohesion is `3.320e7 Pa` (33.20 MPa) in `90_03` and `3.500e7 Pa` (35.00 MPa) in `90_04`. Both retain a residual cohesion of `1.0695e7 Pa` (10.695 MPa), a 30-degree orientation, and the same remaining constitutive settings. This pair therefore tests whether a 1.80 MPa increase in peak cohesion moves the model across the SWT2 failure boundary.

## Main result

Case `90_03` provides a strong validation match. It reproduces the measured event timing, the abrupt mechanical changes, the hydraulic enhancement, and nearly all final values. Its average normalized RMSE across the eight plotted observables is approximately **6.7%**.

Case `90_04` remains locked. It follows the imposed injection-pressure program but fails to produce the experimental stress release, dilation, slip, flow increase, or permeability increase. Its average normalized RMSE is approximately **37.5%**.

As in the SWT1 pair, the pressure history alone cannot distinguish the cases because it is externally prescribed. The mechanically and hydraulically coupled responses show that `90_03`, not `90_04`, represents the observed experiment.

## Quantitative goodness of fit

The calculation uses the same procedure as the SWT1 comparison: each simulation is linearly interpolated to the validation times, data before 100 s are excluded, and RMSE is normalized by the measured range of each observable. The aggregate score is the unweighted mean of the eight NRMSE values.

| Observable | `90_03` RMSE | `90_03` NRMSE | `90_04` RMSE | `90_04` NRMSE |
|---|---:|---:|---:|---:|
| Differential stress | 7.96 MPa | 7.2% | 46.44 MPa | 41.8% |
| Injection pressure | 0.266 MPa | 1.2% | 0.266 MPa | 1.2% |
| Flow rate | 0.834 mL/min | 7.6% | 4.065 mL/min | 37.0% |
| Fracture permeability | 1.43e-13 m² | 8.7% | 9.53e-13 m² | 57.8% |
| Normal dilation | 0.0103 mm | 7.1% | 0.0622 mm | 43.0% |
| BB effective normal stress | 3.10 MPa | 8.1% | 12.20 MPa | 31.7% |
| Shear slip | 0.0399 mm | 6.9% | 0.2507 mm | 43.5% |
| Shear traction magnitude | 3.20 MPa | 6.6% | 21.38 MPa | 44.4% |
| **Mean over eight observables** |  | **6.7%** |  | **37.5%** |

The largest error for `90_03` is only 8.7%, for fracture permeability. The error is also balanced across the observables rather than being dominated by a single good curve. In contrast, `90_04` obtains a low aggregate contribution only from its prescribed pressure match; all event-sensitive quantities have errors of approximately 32–58%.

## Coupled-event timing

To identify the principal instability rather than small pre-event drift, the same physical thresholds used for the SWT1 analysis were applied relative to the 200–900 s baseline: a 10 MPa differential-stress drop, a 0.01 mm decrease in normal dilation, a 0.02 mm increase in shear slip, and a 5 MPa decrease in shear traction.

| Event indicator | Validation | `90_03` | Timing error | `90_04` |
|---|---:|---:|---:|---:|
| Differential-stress drop | 2255 s | 2228 s | 27 s early | Not reached |
| Normal-dilation decrease | 2255 s | 2227 s | 28 s early | Not reached |
| Shear-slip increase | 2225 s | 2220 s | 5 s early | Not reached |
| Shear-traction drop | 2255 s | 2229 s | 26 s early | Not reached |

The four `90_03` indicators occur within 5–28 s of their experimental counterparts. This is excellent agreement relative to the approximately 2830 s test duration and is substantially better than the 40–110 s early transition in SWT1 case `90_01`. Case `90_04` reaches none of the thresholds and has no meaningful coupled failure event.

## Observable-by-observable interpretation

### Differential stress

The validation data stay near 174 MPa initially, decrease gradually to about 167 MPa, and then fall rapidly to a residual level near 63 MPa. Case `90_03` begins from a slightly lower plateau of about 167 MPa but accurately reproduces the abrupt transition and residual state. It finishes at 63.87 MPa, only 1.03 MPa above the measured 62.84 MPa.

Case `90_04` stays near 165–167 MPa throughout the test. Its final value is approximately 166.54 MPa, more than 103 MPa above the validation endpoint. The missing stress drop is direct evidence that the 35.00 MPa peak cohesion is too strong.

### Injection pressure

Both simulations closely reproduce every loading and unloading step, including the maximum pressure near 28 MPa. Their injection-pressure NRMSE is approximately 1.2%, and both finish within 0.01 MPa of the validation value. Because these curves are practically identical, the different material responses cannot be attributed to a pressure-history mismatch.

### Flow rate

Case `90_03` captures the rapid flow increase and the subsequent stepwise decline. Its peak is approximately 8.55 mL/min at 2487 s, compared with 11.10 mL/min at 2400 s in the digitized data. The peak is therefore about 23% too low and 87 s late. Despite this peak mismatch, its final flow rate is 0.903 mL/min, within 0.007 mL/min of the measured 0.910 mL/min.

Case `90_04` reaches only about 0.88 mL/min and finishes near 0.115 mL/min. It lacks the large transmissivity change required to reproduce the measured flow response.

### Fracture permeability

Case `90_03` produces the correct abrupt permeability enhancement and post-peak reduction. Its maximum is approximately `1.64e-12 m²` at 2487 s, about 19% below and 87 s later than the measured `2.02e-12 m²` peak at 2400 s. At 2760 s, however, its `1.489e-12 m²` value is within `0.009e-12 m²` of the measured `1.480e-12 m²`.

Case `90_04` remains near the initial permeability, around `3.7e-13 m²`, and finishes approximately `1.11e-12 m²` below the validation data. The slightly higher value at initialization is a startup feature, not a failure-related permeability gain.

### Normal dilation

Case `90_03` reproduces the sudden negative normal displacement and subsequent partial recovery. Its most negative value is about -0.137 mm, compared with -0.142 mm in the validation data, so the displacement magnitude is only about 3.7% too small. The modeled extremum occurs at 2487 s, approximately 87 s after the measured extremum. Its final value of -0.128 mm is within 0.002 mm of the digitized endpoint.

Case `90_04` remains close to zero and finishes at approximately +0.001 mm. It therefore misses both the sign and magnitude of the measured post-failure normal displacement.

### BB effective normal stress

Before failure, `90_03` follows the measured stepped decline closely. It captures the sharp drop during the event, including a minimum near 31 MPa, but its later recovery is too strong. The final modeled value is approximately 47.20 MPa, about 7.98 MPa above the measured 39.22 MPa. This late recovery is one of the clearest remaining discrepancies in an otherwise strong match.

Case `90_04` does not experience the event-related normal-stress loss. It instead rises during unloading and ends at 66.45 MPa, approximately 27.23 MPa too high.

### Shear slip

Case `90_03` closely reproduces the onset, magnitude, and persistence of shear slip. Its maximum is approximately 0.552 mm, only 0.023 mm or 3.9% below the measured 0.574 mm. Its final value is 0.55142 mm, effectively identical to the measured 0.55147 mm.

Case `90_04` develops only about 0.010 mm of displacement. This small drift is not a failure event and is inconsistent with the experimental permanent slip.

### Shear traction magnitude

Case `90_03` reproduces both the abrupt stress loss and the post-event residual plateau. It ends at 27.90 MPa, only 0.69 MPa above the measured 27.21 MPa, and has the lowest event-sensitive NRMSE of the case at approximately 6.6%.

Case `90_04` retains almost its full shear traction. Its endpoint of approximately 74.30 MPa exceeds the validation value by 47.09 MPa and confirms that the joint remains locked.

## Peak and final-value summary

| Quantity | Validation | `90_03` | `90_04` |
|---|---:|---:|---:|
| Peak flow rate | 11.10 mL/min | 8.55 mL/min | 0.88 mL/min |
| Peak fracture permeability | 2.02e-12 m² | 1.64e-12 m² | 4.22e-13 m² at startup; no event gain |
| Most negative normal dilation | -0.142 mm | -0.137 mm | -0.001 mm at startup |
| Maximum shear slip | 0.574 mm | 0.552 mm | 0.010 mm |
| Final differential stress | 62.84 MPa | 63.87 MPa | 166.54 MPa |
| Final flow rate | 0.910 mL/min | 0.903 mL/min | 0.115 mL/min |
| Final fracture permeability | 1.480e-12 m² | 1.489e-12 m² | 0.371e-12 m² |
| Final normal dilation | -0.129 mm | -0.128 mm | +0.001 mm |
| Final BB effective normal stress | 39.22 MPa | 47.20 MPa | 66.45 MPa |
| Final shear slip | 0.55147 mm | 0.55142 mm | 0.00963 mm |
| Final shear traction | 27.21 MPa | 27.90 MPa | 74.30 MPa |

## Interpretation of the SWT2 cohesion bracket

The 1.80 MPa peak-cohesion increase from `90_03` to `90_04` changes the solution from a well-timed failure to a locked response. Because residual cohesion and the other constitutive settings are identical, this is strong evidence that the SWT2 stability boundary lies between 33.20 and 35.00 MPa.

Unlike the SWT1 lower-bracket case, `90_03` does not require a substantial delay in failure. Its principal mechanical event is already aligned to within approximately half a minute. Increasing cohesion solely to alter onset time therefore has a significant risk of suppressing failure, as demonstrated by `90_04`.

The remaining discrepancies in `90_03` are mainly post-onset details:

1. The flow and permeability peaks are too low and occur about 87 s late.
2. The effective normal stress recovers too far after the main drop and ends about 8 MPa high.
3. The pre-event differential-stress plateau is several MPa below the validation data.
4. The slip, dilation, residual differential stress, residual shear traction, final flow, and final permeability are already very close to the measurements.

These features suggest retaining `90_03` as the preferred cohesion calibration and addressing any further peak-shape or recovery refinement through parameters governing post-failure hydraulic evolution and effective-normal-stress recovery. A further large increase in peak cohesion is not supported by this bracket.

## SWT2 conclusion

`90_03` is the clear validation choice. It captures the full coupled response, places the primary event within 5–28 s of the digitized timing, and achieves approximately 6.7% mean normalized error. Its strongest results are the nearly exact final slip, flow rate, permeability, differential stress, and shear traction. Its main remaining weakness is a delayed and underpredicted hydraulic peak, together with excessive recovery of effective normal stress.

`90_04` should be rejected as a validation match. The 35.00 MPa peak cohesion prevents failure, producing approximately 37.5% mean normalized error and leaving all event-dependent observables on the wrong response branch. Together, the cases bracket the SWT2 failure threshold between 33.20 and 35.00 MPa and show that `90_03` is already close to the desired calibration.

---

# SWS3 validation comparison: level and slope corrections 90_05 and 90_06

## Scope

This section compares the following SWS3 HPC simulations with the digitized Ye and Ghassemi validation data:

- `90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6_hpc`
- `90_06_sw3_bbfast_jrc5p69_L123p4_kernel_SV_biot0p6_hpc`

Unlike the SWT1 and SWT2 pairs, these are not simply lower- and upper-cohesion brackets. They are two alternative corrections designed to give similar strength at the expected failure state:

- `90_05` retains the measured paper JRC of 1.96 and adds 1.67 MPa of peak cohesion, with zero residual cohesion. This is primarily a **strength-level correction**.
- `90_06` applies no added cohesion and instead increases JRC from 1.96 to 5.69. This modifies the pressure dependence of strength and is primarily a **strength-slope correction**.

Both retain the same JCS of 150 MPa, residual friction angle of 29.756 degrees, and 123.4 mm loading setting. The decks were constructed to have similar strength near the anticipated crossing state, allowing the validation response to test whether a constant level correction or a pressure-dependent slope correction is preferable.

## Main result

Both cases reproduce the timing and shape of the SWS3 coupled event very well, and their curves nearly overlap. Case `90_05` has a mean normalized RMSE of approximately **11.4%**, while `90_06` gives approximately **11.8%**. The difference of only 0.4 percentage points is small, but `90_05` is consistently slightly better for most event-sensitive variables.

The two models share the same main deficiencies. They underpredict the pre-event differential stress, produce excessive post-event weakening, accumulate too much shear slip, and predict a normal displacement that remains too negative. Conversely, they reproduce injection pressure, flow evolution, permeability evolution, effective normal stress, and event timing quite closely.

## Quantitative goodness of fit

The same scoring procedure used for SWT1 and SWT2 was applied: simulation values were interpolated to digitized validation times, data before 100 s were excluded, and each RMSE was normalized by the measured range. Validation points beyond the final simulation time were excluded rather than extrapolated.

| Observable | `90_05` RMSE | `90_05` NRMSE | `90_06` RMSE | `90_06` NRMSE |
|---|---:|---:|---:|---:|
| Differential stress | 7.36 MPa | 24.9% | 7.49 MPa | 25.3% |
| Injection pressure | 0.234 MPa | 1.1% | 0.234 MPa | 1.1% |
| Flow rate | 0.0677 mL/min | 8.1% | 0.0704 mL/min | 8.4% |
| Fracture permeability | 2.81e-14 m² | 11.5% | 2.91e-14 m² | 11.9% |
| Normal dilation | 0.00626 mm | 13.8% | 0.00657 mm | 14.5% |
| BB effective normal stress | 0.733 MPa | 4.2% | 0.730 MPa | 4.2% |
| Shear slip | 0.0130 mm | 17.7% | 0.0136 mm | 18.4% |
| Shear traction magnitude | 1.24 MPa | 9.8% | 1.30 MPa | 10.2% |
| **Mean over eight observables** |  | **11.4%** |  | **11.8%** |

Case `90_05` has the lower error for seven of the eight observables. Case `90_06` is lower only for effective normal stress, and that advantage is negligible. Differential stress is the largest error in both cases because the modeled curve is shifted downward before the event and over-weakens afterward.

## Coupled-event timing

The event was identified relative to the 200–900 s baseline using the same thresholds as the preceding sections: a 10 MPa differential-stress drop, a 0.01 mm decrease in normal dilation, a 0.02 mm increase in shear slip, and a 5 MPa decrease in shear traction.

| Event indicator | Validation | `90_05` | `90_05` error | `90_06` | `90_06` error |
|---|---:|---:|---:|---:|---:|
| Differential-stress drop | 2445 s | 2438 s | 7 s early | 2435 s | 10 s early |
| Normal-dilation decrease | 2450 s | 2425 s | 25 s early | 2423 s | 27 s early |
| Shear-slip increase | 2445 s | 2431 s | 14 s early | 2429 s | 16 s early |
| Shear-traction drop | 2445 s | 2448 s | 3 s late | 2445 s | Exact |

Both cases place the event within 27 s of all four measured indicators. Case `90_05` is slightly closer for differential stress, dilation, and slip, while `90_06` exactly matches the shear-traction threshold. The timing differences between the two simulations are only 2–3 s and are too small to discriminate meaningfully between the level- and slope-correction strategies.

## Observable-by-observable interpretation

### Differential stress

The largest systematic mismatch is already present before failure. The validation plateau is approximately 34–35 MPa, whereas both simulations begin near 29 MPa and gradually decline to about 27–28 MPa. The models therefore start roughly 5.5 MPa too low.

Both cases accurately locate and reproduce the abrupt stress drop, but they release too much stress. The validation curve remains positive and ends near 5.50 MPa at the last common time, whereas `90_05` ends near -1.98 MPa and `90_06` near -2.18 MPa. This approximately 7.5–7.7 MPa endpoint deficit indicates excessive residual weakening. The nearly identical bias in the two cases also shows that changing the peak-envelope construction did not correct the residual differential-stress state.

### Injection pressure

The simulations reproduce the full pressure staircase, peak, and unloading path with approximately 1.1% normalized error. The two pressure curves are numerically indistinguishable, confirming that their small differences in mechanical response arise from the strength formulation rather than the applied loading.

### Flow rate

Both cases capture the gradual pre-event increase, rapid event-related rise, and subsequent staged decline. Case `90_05` peaks at approximately 0.981 mL/min and `90_06` at 0.988 mL/min, compared with the measured 0.860 mL/min. The peaks are therefore about 14–15% too high and occur near 2699 s, roughly 99 s after the validation peak at 2600 s.

The late-time agreement is excellent. At 4700 s, `90_05` gives 0.0519 mL/min and `90_06` gives 0.0523 mL/min, compared with the measured 0.0540 mL/min.

### Fracture permeability

Both simulations reproduce the permeability increase and its stepwise post-peak decline. The maximum is approximately `4.03e-13 m²` for `90_05` and `4.05e-13 m²` for `90_06`, around 10–11% above the measured `3.66e-13 m²`. The modeled maxima occur near 2699 s, approximately 104 s later than the corrected Table 2 validation maximum near 2595 s.

The final permeability is almost exact: about `2.255e-13 m²` for `90_05` and `2.265e-13 m²` for `90_06`, compared with `2.250e-13 m²`. Thus, the main hydraulic discrepancy is the height and timing of the transient peak rather than the residual permeability.

### Normal dilation

Both cases reproduce the abrupt negative displacement and the direction of its later recovery, but they overpredict its magnitude. Case `90_05` reaches -0.0542 mm and `90_06` reaches -0.0545 mm, compared with the measured minimum of -0.0448 mm. The contraction magnitude is therefore about 21–22% too large.

The simulated extrema occur near 2699 s, about 27 s before the validation minimum at 2725 s. At the final common time, the simulations remain near -0.050 mm while the validation data have recovered to approximately -0.0406 mm. Case `90_05` is marginally closer throughout this response.

### BB effective normal stress

This is the best event-sensitive match in the SWS3 comparison. Both cases reproduce the pre-event staircase, the drop to approximately 14.5 MPa, and the later recovery to about 25.7–25.8 MPa. The final measured value is about 24.76 MPa, leaving errors of only 1.02 MPa for `90_05` and 0.97 MPa for `90_06`. The normalized error is approximately 4.2% for both cases.

### Shear slip

The onset is correctly timed, but the modeled displacement jump is too large and too abrupt. Case `90_05` reaches approximately 0.0905 mm and `90_06` reaches 0.0912 mm, whereas the validation data reach a maximum of about 0.0734 mm. The simulations overpredict total slip by roughly 23–24% and settle almost immediately, while the digitized response continues to evolve gradually after the main event.

At the final common time, `90_05` exceeds the validation value by about 0.0174 mm and `90_06` by about 0.0180 mm. The level-correction case is therefore slightly better, but neither resolves the excessive slip accumulation.

### Shear traction magnitude

Both simulations match the pre-event traction and the abrupt event timing, but their post-event traction continues decreasing below the observed residual. At the final common time, the validation value is approximately 2.33 MPa, compared with 0.097 MPa for `90_05` and 0.029 MPa for `90_06`. This is consistent with the excessive slip and negative differential-stress residuals.

Case `90_05` retains slightly more residual shear strength and consequently has the lower shear-traction error. The difference remains small compared with the shared model-to-validation residual mismatch.

## Peak and final-value summary

| Quantity | Validation | `90_05` | `90_06` |
|---|---:|---:|---:|
| Peak flow rate | 0.860 mL/min | 0.981 mL/min | 0.988 mL/min |
| Peak fracture permeability | 3.66e-13 m² | 4.03e-13 m² | 4.05e-13 m² |
| Most negative normal dilation | -0.0448 mm | -0.0542 mm | -0.0545 mm |
| Maximum shear slip | 0.0734 mm | 0.0905 mm | 0.0912 mm |
| Final differential stress at 4802 s | 5.50 MPa | -1.98 MPa | -2.18 MPa |
| Final flow rate at 4700 s | 0.0540 mL/min | 0.0519 mL/min | 0.0523 mL/min |
| Final fracture permeability near 4703 s | 2.250e-13 m² | 2.255e-13 m² | 2.265e-13 m² |
| Final normal dilation at 4802 s | -0.0406 mm | -0.0498 mm | -0.0501 mm |
| Final BB effective normal stress at 4802 s | 24.76 MPa | 25.78 MPa | 25.73 MPa |
| Final shear slip at 4802 s | 0.0728 mm | 0.0902 mm | 0.0908 mm |
| Final shear traction at 4802 s | 2.33 MPa | 0.10 MPa | 0.03 MPa |

## Direct comparison of the two correction strategies

The two predictions are much closer to each other than either is to the remaining validation discrepancies. Across the full matched time grid, their RMS differences are only approximately 0.19 MPa in differential stress, 0.0037 mL/min in flow rate, `1.4e-15 m²` in permeability, 0.00035 mm in normal dilation, 0.00061 mm in shear slip, and 0.081 MPa in shear traction. Their event times differ by no more than 3 s.

This loading history therefore does not strongly identify whether the missing peak strength should be represented by a constant cohesion contribution or by a larger effective JRC. The two formulations were matched at the failure state, and the experiment samples too narrow a stress path for their different pressure-dependent slopes to separate appreciably.

Case `90_05` is the preferable result for this comparison because:

1. It has the lower aggregate error, 11.4% versus 11.8%.
2. It is closer for seven of the eight observables.
3. It preserves the independently measured JRC of 1.96 instead of treating JRC as an effective fitted value of 5.69.
4. It produces slightly less excessive dilation, slip, differential-stress loss, and shear-traction loss.

This preference is modest rather than decisive. If JRC is intentionally interpreted as an effective parameter representing additional pressure-dependent interlock, `90_06` remains a viable phenomenological model. Distinguishing the formulations would require validation over a broader effective-normal-stress range or an additional loading path.

## SWS3 conclusion

Both `90_05` and `90_06` reproduce the SWS3 event with excellent timing and credible hydraulic behavior. `90_05` is the marginally better and more directly interpretable calibration, with approximately 11.4% mean normalized error compared with 11.8% for `90_06`.

The remaining calibration need is not the onset time or the final hydraulic state. It is the residual mechanical state: both cases underpredict the initial differential-stress level, weaken differential and shear stresses too far after failure, accumulate about 23–24% too much slip, and retain about 0.009–0.010 mm too much negative normal displacement. Further refinement should therefore preserve the present peak-event timing while increasing residual strength and reducing post-event slip and contraction.

---

# SWS4 validation comparison: fixed-peak JRC cases 90_07 and 90_08

## Scope

This section compares the following SW-S4 HPC simulations with the digitized Ye and Ghassemi validation data:

- `90_07_sw4_bbfast_theta30_jrc9_kernel_SV_biot0p6_hpc`
- `90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc`

The decks test JRC as a pressure-slope and residual-response parameter while approximately preserving the same peak strength near the anticipated crossing state:

- `90_07` uses JRC = 9.0, JCS = 150 MPa, and a re-anchored friction-angle setting of 19.54 degrees.
- `90_08` uses JRC = 5.0, JCS = 150 MPa, and a re-anchored friction-angle setting of 22.72 degrees.

Both are anchored to an effective peak friction angle of approximately 26.70 degrees near 24 MPa effective normal stress. They therefore test whether reducing JRC can improve the residual shear state without substantially changing the peak-failure condition.

## Main result

Both cases are strong SW-S4 validation matches and are very close to one another. Case `90_07` has an average normalized RMSE of approximately **7.75%**, while `90_08` gives approximately **7.84%**. The 0.09-percentage-point difference is too small to regard either case as globally superior based on aggregate error alone.

Their tradeoff is nevertheless physically informative. The lower-JRC `90_08` produces a residual shear traction closer to the measurement, supporting the intended role of JRC as a residual-strength control. The higher-JRC `90_07` is slightly better for differential stress, normal dilation, and shear slip, all of which are already over-weakened or over-deformed in the simulations.

## Quantitative goodness of fit

The same scoring method was used as in the preceding sections: interpolation to validation times, exclusion of data before 100 s, range-normalized RMSE, and an unweighted mean across the eight observables.

| Observable | `90_07` RMSE | `90_07` NRMSE | `90_08` RMSE | `90_08` NRMSE |
|---|---:|---:|---:|---:|
| Differential stress | 4.04 MPa | 16.8% | 4.26 MPa | 17.7% |
| Injection pressure | 0.059 MPa | 0.3% | 0.059 MPa | 0.3% |
| Flow rate | 0.00615 mL/min | 5.7% | 0.00586 mL/min | 5.4% |
| Fracture permeability | 3.35e-15 m² | 6.8% | 3.30e-15 m² | 6.7% |
| Normal dilation | 0.00230 mm | 5.6% | 0.00235 mm | 5.7% |
| BB effective normal stress | 1.26 MPa | 7.7% | 1.23 MPa | 7.5% |
| Shear slip | 0.00607 mm | 7.5% | 0.00660 mm | 8.2% |
| Shear traction magnitude | 1.21 MPa | 11.6% | 1.16 MPa | 11.2% |
| **Mean over eight observables** |  | **7.75%** |  | **7.84%** |

Case `90_07` is better for differential stress, normal dilation, and shear slip. Case `90_08` is better for flow rate, permeability, effective normal stress, and shear traction. Injection pressure is identical. Differential stress is the largest error in both cases because its pre-event level is too low and its final residual is also underpredicted.

## Staged-event timing

SW-S4 does not contain one isolated displacement jump. The validation data show several stages: an initial mechanical response near 1025–1040 s, intermediate slip and contraction around 1320–1425 s, and the largest transition around 1680–1695 s. A single onset number therefore hides important timing behavior.

### Initial detectable response

Using small departures from the pre-900 s baseline gives:

| Indicator | Threshold | Validation | `90_07` | `90_08` |
|---|---:|---:|---:|---:|
| Differential-stress reduction | 2 MPa | 1025 s | 1101 s | 1101 s |
| Normal-dilation decrease | 0.002 mm | 1040 s | 1092 s | 1092 s |
| Shear-slip increase | 0.002 mm | 1025 s | 1101 s | 1101 s |
| Shear-traction reduction | 1 MPa | 1030 s | 1353 s | 1352 s |

Both simulations delay the first differential-stress and slip response by about 76 s and the first normal-displacement response by about 52 s. The first clear shear-traction reduction is delayed by more than 320 s. This occurs because the simulations redistribute the early measured weakening into a smoother, later transition.

### Intermediate and main transition

| Indicator | Threshold | Validation | `90_07` | `90_08` |
|---|---:|---:|---:|---:|
| Shear slip | 0.020 mm | 1320 s | 1404 s | 1403 s |
| Shear slip | 0.040 mm | 1410 s | 1500 s | 1496 s |
| Shear slip | 0.070 mm | 1695 s | 1692 s | 1683 s |
| Normal-dilation decrease | 0.010 mm | 1330 s | 1389 s | 1388 s |
| Normal-dilation decrease | 0.020 mm | 1425 s | 1494 s | 1490 s |
| Normal-dilation decrease | 0.035 mm | 1685 s | 1674 s | 1667 s |
| Differential-stress reduction | 20 MPa | 1680 s | 1688 s | 1679 s |

The intermediate stages are generally 59–90 s late, but the largest transition is accurately aligned. At the 0.070 mm slip level, `90_07` is 3 s early and `90_08` is 12 s early. At the 20 MPa differential-stress reduction, `90_07` is about 8 s late and `90_08` is about 2 s early. Thus, both cases reproduce the timing of the final major stage while missing some of the earlier staged evolution.

## Observable-by-observable interpretation

### Differential stress

The validation data begin near 29 MPa, whereas the simulations begin near 25 MPa after initialization. This approximately 4 MPa offset persists through much of the pre-event interval. Both cases capture the sequence and timing of the major reductions, particularly the final drop near 1680 s, but they release too much differential stress.

At 3410 s, the measured value is 5.14 MPa, compared with 2.16 MPa for `90_07` and 1.81 MPa for `90_08`. Case `90_07` is therefore the better differential-stress result. Reducing JRC to 5.0 in `90_08` lowers the residual still further, worsening an existing over-weakening bias.

### Injection pressure

Both cases reproduce the complete pressure staircase, the peak near 28 MPa, and all unloading steps almost exactly. Their normalized pressure error is only about 0.3%, and the two simulated pressure curves are identical. The mechanical differences therefore reflect the constitutive settings rather than different loading histories.

### Flow rate

Both simulations closely reproduce the gradual rise, intermediate shoulder, main peak, and staged decline. Case `90_07` peaks at approximately 0.0949 mL/min and `90_08` at 0.0959 mL/min, compared with the measured 0.113 mL/min. The peak is underpredicted by about 15–16% and occurs around 1788–1790 s, roughly 38–40 s late.

At 3250 s, both modeled values are close to the measured 0.0050 mL/min: 0.00527 mL/min for `90_07` and 0.00531 mL/min for `90_08`. Case `90_08` has the slightly lower full-history flow error, although the difference is small.

### Fracture permeability

The simulated permeability evolution closely follows the measured curve. Case `90_07` peaks at approximately `8.71e-14 m²` and `90_08` at `8.77e-14 m²`, versus the measured `9.50e-14 m²`. The peaks are about 8% low and occur around 1799–1800 s, approximately 49–50 s late.

The final values are also close: `4.79e-14 m²` for `90_07` and `4.81e-14 m²` for `90_08`, compared with `4.60e-14 m²`. The JRC change has very little hydraulic effect in this pair.

### Normal dilation

Both cases capture the staged negative displacement, the principal minimum, and the gradual recovery. The measured minimum is -0.0410 mm at 1750 s. Case `90_07` reaches -0.0422 mm and `90_08` reaches -0.0428 mm at about 1821 s, making the modeled minimum 71 s late and slightly too negative.

At 3410 s, `90_07` is within 0.00037 mm of the validation endpoint, while `90_08` is within 0.00083 mm. The higher-JRC case is therefore marginally better for normal displacement.

### BB effective normal stress

Both simulations capture the full stepped decline, the trough, and the recovery. Their minima after initialization are approximately 15.70 MPa for `90_07` and 15.61 MPa for `90_08`, close to the measured 15.28 MPa. The simulated trough occurs near 1800 s, about 20 s after the measured minimum.

At 3410 s, the cases finish at 25.46 and 25.38 MPa, respectively, compared with 24.78 MPa in the validation data. Case `90_08` is slightly closer, consistent with its marginally lower normal-stress NRMSE.

### Shear slip

The simulations reproduce the total slip reasonably well but smooth and delay the early measured stages. Their first detectable slip is about 76 s late, their 0.020–0.040 mm levels are 84–90 s late, and their final large transition is nearly on time.

Case `90_07` reaches approximately 0.0816 mm and `90_08` reaches 0.0829 mm, compared with the measured maximum of 0.0800 mm. At 3410 s, the errors are +0.0022 and +0.0035 mm, respectively. Lowering JRC therefore increases the already slight slip overprediction, making `90_07` the better slip match.

### Shear traction magnitude

Both simulations begin at the correct level near 12.5–12.7 MPa, but their early reductions lag the validation data. The measured curve starts declining near 1030 s, while the first 1 MPa modeled reduction does not occur until about 1352–1353 s. The later main drop is reproduced more closely, although the modeled post-event decay is smoother than the measured sequence.

The final validation value is 2.25 MPa. Case `90_07` finishes at 2.55 MPa and `90_08` at 2.39 MPa. The lower-JRC case therefore improves the residual shear traction, reducing the final error from 0.30 to 0.14 MPa. This supports the deck-design hypothesis that JRC can adjust the residual shear state while the re-anchored friction angle protects the peak crossing.

## Peak and final-value summary

| Quantity | Validation | `90_07` | `90_08` |
|---|---:|---:|---:|
| Peak flow rate | 0.113 mL/min | 0.0949 mL/min | 0.0959 mL/min |
| Peak fracture permeability | 9.50e-14 m² | 8.71e-14 m² | 8.77e-14 m² |
| Most negative normal dilation | -0.0410 mm | -0.0422 mm | -0.0428 mm |
| Minimum BB effective normal stress | 15.28 MPa | 15.70 MPa | 15.61 MPa |
| Maximum shear slip | 0.0800 mm | 0.0816 mm | 0.0829 mm |
| Final differential stress at 3410 s | 5.14 MPa | 2.16 MPa | 1.81 MPa |
| Final flow rate at 3250 s | 0.0050 mL/min | 0.00527 mL/min | 0.00531 mL/min |
| Final fracture permeability at 3250 s | 4.60e-14 m² | 4.79e-14 m² | 4.81e-14 m² |
| Final normal dilation at 3410 s | -0.0310 mm | -0.0314 mm | -0.0318 mm |
| Final BB effective normal stress at 3410 s | 24.78 MPa | 25.46 MPa | 25.38 MPa |
| Final shear slip at 3410 s | 0.0793 mm | 0.0814 mm | 0.0828 mm |
| Final shear traction at 3410 s | 2.25 MPa | 2.55 MPa | 2.39 MPa |

## Direct comparison of JRC = 9 and JRC = 5

The two simulations remain close because their friction-angle settings were re-anchored to preserve peak strength. Across the common time grid, their RMS differences are approximately 0.264 MPa in differential stress, 0.00036 mL/min in flow, `3.1e-16 m²` in permeability, 0.00040 mm in normal dilation, 0.00102 mm in shear slip, 0.066 MPa in effective normal stress, and 0.120 MPa in shear traction.

Reducing JRC from 9 to 5 has the intended effect on residual shear traction, but it also causes slightly greater total slip, contraction, and differential-stress loss. The aggregate scores are consequently almost tied:

- Choose `90_07` if the priority is the best balanced overall response and limiting mechanical over-weakening.
- Choose `90_08` if matching the final shear traction is the primary objective.

Neither case fully resolves the staged early-time response. Both postpone the first mechanical change and compress several measured steps into smoother later transitions. This timing-shape discrepancy is shared by the formulations and cannot be removed by choosing between JRC = 9 and JRC = 5 alone.

## SWS4 conclusion

Both `90_07` and `90_08` are credible SW-S4 validation cases. Their approximately 7.8% mean normalized errors are lower than those of the selected SWT1 and SWS3 cases, and their pressure, hydraulic, dilation, normal-stress, and final-slip predictions are strong.

`90_07` is the marginally preferred balanced calibration because it has the lower aggregate error and less excessive differential-stress loss, dilation, and slip. `90_08` provides the better final shear-traction match and confirms that reducing JRC lowers the residual shear response without materially shifting the largest event. Further refinement should retain the present main-event timing while raising the differential-stress residual and reproducing the earlier staged weakening more explicitly.
