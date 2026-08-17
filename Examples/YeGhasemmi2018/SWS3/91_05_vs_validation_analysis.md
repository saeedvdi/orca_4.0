# SWS3 validation analysis: residual-cohesion case 91_05

## Scope

This report compares the following SWS3 HPC simulation with the digitized Ye and Ghassemi validation data shown in the figure:

- `91_05_sw3_bbfast_paperjrc_resc1p65_kernel_SV_biot0p6_hpc`

Case `91_05` is derived from `90_05_sw3_bbfast_paperjrc_L123p4_cohes1p67_kernel_SV_biot0p6`. It retains the measured JRC of 1.96, JCS of 150 MPa, peak cohesion of 1.67 MPa, and the remaining peak-envelope and hydraulic settings. Its single material change is an increase in residual cohesion from 0 to 1.65 MPa.

The purpose of this change is to preserve the accurately calibrated event onset while correcting the parent case's excessive post-failure weakening, excessive shear slip, and excessive negative normal displacement.

## Differential-stress channel

The differential-stress comparison uses `differential_stress_reaction_mpa_pp`, the load-cell reaction-based channel used in the current notebook and figure. The older `differential_stress_mpa_pp` channel mixes a skeleton axial stress with total confining stress and reads several MPa too low during pressurization. The reaction-based channel is consistent with the independent bulk-stress difference and is therefore used throughout this report.

## Main result

Case `91_05` is a strong SWS3 validation match. It reproduces the pressure history, event timing, flow and permeability evolution, dilation, effective normal stress, total shear slip, and shear-traction loss. Its mean normalized RMSE over the eight plotted observables is approximately **5.4%**.

The added residual cohesion successfully corrects the main defects of parent case `90_05`. The final shear slip changes from approximately 0.0902 to 0.0709 mm, compared with 0.0728 mm in the validation data. Final shear traction changes from about 0.10 to 2.77 MPa, compared with 2.33 MPa. Final normal dilation changes from -0.0498 to -0.0392 mm, compared with -0.0406 mm.

The correction is slightly too strong in the residual stress channels. Final differential stress is about 7.77 MPa versus 5.50 MPa measured, while final shear traction is about 2.77 MPa versus 2.33 MPa. Thus, `91_05` changes the parent from over-weakening to mild under-weakening, but the new error is much smaller and the coupled displacement response improves substantially.

## Quantitative goodness of fit

The simulation was linearly interpolated to the validation times. Data before 100 s were excluded to prevent initialization from dominating the score, and validation points beyond the final simulation time were not extrapolated. RMSE was normalized by the measured range of each observable; the aggregate score is the unweighted mean of the eight normalized errors.

| Observable | RMSE | NRMSE | Mean bias | Correlation |
|---|---:|---:|---:|---:|
| Differential stress | 3.06 MPa | 10.3% | +1.44 MPa | 0.991 |
| Injection pressure | 0.234 MPa | 1.1% | +0.021 MPa | 0.999 |
| Flow rate | 0.0289 mL/min | 3.4% | +0.0010 mL/min | 0.994 |
| Fracture permeability | 1.45e-14 m² | 5.9% | -0.004e-14 m² | 0.984 |
| Normal dilation | 0.00215 mm | 4.8% | +0.00091 mm | 0.999 |
| BB effective normal stress | 1.29 MPa | 7.5% | +1.10 MPa | 0.990 |
| Shear slip | 0.00168 mm | 2.3% | -0.00002 mm | 0.999 |
| Shear traction magnitude | 1.02 MPa | 8.1% | +0.44 MPa | 0.992 |
| **Mean over eight observables** |  | **5.4%** |  |  |

The best event-sensitive result is shear slip, with only 2.3% normalized error. Differential stress has the largest error at 10.3%, primarily because the simulated pre-event curve starts low and rises while the measured curve begins higher and gradually declines, and because the final modeled residual remains high.

## Coupled-event timing

The principal event was identified relative to the 200–900 s baseline using a 10 MPa differential-stress reduction, a 0.01 mm decrease in normal dilation, a 0.02 mm increase in shear slip, and a 5 MPa decrease in shear traction.

| Event indicator | Validation | `91_05` | Timing error |
|---|---:|---:|---:|
| Differential-stress drop | 2445 s | 2470 s | 25 s late |
| Normal-dilation decrease | 2450 s | 2432 s | 18 s early |
| Shear-slip increase | 2445 s | 2441 s | 4 s early |
| Shear-traction drop | 2445 s | 2472 s | 27 s late |

All four main-event indicators fall within approximately 27 s of the measurements. Slip onset is especially accurate. Small pre-event changes in modeled dilation and slip begin earlier, but the principal coupled transition remains correctly aligned. The residual-cohesion modification therefore achieves its intended purpose without materially displacing the peak-failure event.

Compared with `90_05`, the 10 MPa differential-stress and 5 MPa shear-traction thresholds move about 23–24 s later, while the main dilation and slip thresholds move only about 8–10 s later. The event remains within the experimental timing band.

## Observable-by-observable interpretation

### Differential stress

The validation curve begins near 34.9 MPa and decreases gradually to about 33 MPa before failure. The simulation begins around 32–33 MPa and rises gradually toward 34–35 MPa. It therefore reproduces the magnitude of the pre-event state but not its exact trend.

The principal stress drop is correctly timed and the simulation reproduces a multistage post-event decline. Immediately after failure, however, the modeled stress remains higher and relaxes more gradually than the validation data. At 4802 s, the modeled value is 7.77 MPa compared with the interpolated validation value of 5.50 MPa, an overprediction of 2.27 MPa.

The residual-cohesion change brackets the target with its parent: `90_05` finishes at 1.60 MPa, 3.90 MPa too low, whereas `91_05` finishes 2.27 MPa too high. The correct residual-strength setting therefore lies between the two if differential stress is considered alone.

### Injection pressure

The complete pressure staircase, peak near 28 MPa, and unloading sequence are reproduced almost exactly. The normalized error is approximately 1.1%, and the final modeled pressure differs from the validation value by only about 0.11 MPa. This confirms that the mechanical and hydraulic differences are not caused by a loading-history mismatch.

### Flow rate

Case `91_05` captures the gradual pre-event rise, abrupt enhancement, and staged decline. Its peak is approximately 0.802 mL/min at 2699 s, compared with 0.860 mL/min at 2600 s. The peak is about 6.8% too low and approximately 99 s late.

At 4700 s, the modeled flow is 0.0439 mL/min compared with 0.0540 mL/min measured. The added residual strength therefore slightly suppresses the late hydraulic response. Nevertheless, the full-history flow NRMSE is only 3.4%, substantially better than the parent case because the parent overpredicted the event peak.

### Fracture permeability

The permeability curve has the correct pre-event evolution, event-related increase, and stepwise decline. Its modeled peak is approximately `3.51e-13 m²` at 2699 s, versus the measured `3.66e-13 m²` near 2595 s. The peak is about 4.1% low and approximately 104 s late.

Near 4703 s, the model gives `2.02e-13 m²`, about 10.3% below the measured `2.25e-13 m²`. As with flow rate, the residual-cohesion correction slightly over-suppresses the final hydraulic aperture, but the overall curve remains a good match.

### Normal dilation

Case `91_05` closely matches both the event-related negative displacement and its subsequent recovery. The minimum is approximately -0.0430 mm at 2699 s, compared with -0.0448 mm at 2725 s. Its maximum contraction magnitude is only about 4% too small, and the extremum occurs about 26 s early.

At 4802 s, the model gives -0.0392 mm compared with -0.0406 mm measured, an error of only +0.0014 mm. This is a major improvement over `90_05`, which remained at approximately -0.0498 mm and was about 0.0091 mm too negative.

### BB effective normal stress

The simulation reproduces the stepped pre-event decline, the failure-related trough, and the subsequent recovery. The modeled minimum is approximately 15.51 MPa, close to the measured 15.11 MPa. However, the modeled minimum occurs near 2699 s, about 139 s after the measured minimum near 2560 s.

The recovery is also somewhat too strong. At 4802 s, `91_05` gives 27.04 MPa compared with 24.76 MPa measured, an overprediction of 2.28 MPa. This is the clearest post-event tradeoff introduced by the residual-strength increase: arresting slip improves the displacement response but leaves more effective normal stress in the final state.

### Shear slip

Shear slip is the strongest aspect of this calibration. The onset is within about 4 s of the validation threshold, and the final magnitude is close. The model reaches a maximum of approximately 0.0713 mm, compared with 0.0734 mm measured, an underprediction of only about 2.9%.

At 4802 s, the modeled value is 0.07093 mm versus 0.07281 mm measured, a difference of -0.00188 mm. The parent case ended at 0.09018 mm, so adding residual cohesion removes approximately 0.0193 mm of excessive slip and nearly eliminates the endpoint error.

The remaining shape mismatch is that the simulation reaches its slip plateau near 2565 s, whereas the validation data continue accumulating a small amount of slip over a much longer period. Total displacement is accurate, but the modeled post-event evolution is more abrupt.

### Shear traction magnitude

The pre-event traction level and failure timing are reproduced well. The added residual cohesion prevents the traction from collapsing toward zero, correcting the parent case's principal residual-strength defect.

The final modeled traction is approximately 2.77 MPa compared with 2.33 MPa measured, an overprediction of 0.44 MPa. The minimum modeled value is about 2.77 MPa, while the measured curve reaches about 2.15 MPa. Thus, the correction is slightly too strong, but it is much closer than the parent result of approximately 0.10 MPa at the final common time.

## Peak and final-value summary

| Quantity | Validation | `91_05` | Difference |
|---|---:|---:|---:|
| Peak flow rate | 0.860 mL/min | 0.802 mL/min | -0.058 mL/min |
| Peak fracture permeability | 3.66e-13 m² | 3.51e-13 m² | -0.15e-13 m² |
| Most negative normal dilation | -0.0448 mm | -0.0430 mm | +0.0018 mm |
| Minimum BB effective normal stress | 15.11 MPa | 15.51 MPa | +0.40 MPa |
| Maximum shear slip | 0.0734 mm | 0.0713 mm | -0.0021 mm |
| Final differential stress at 4802 s | 5.50 MPa | 7.77 MPa | +2.27 MPa |
| Final flow rate at 4700 s | 0.0540 mL/min | 0.0439 mL/min | -0.0101 mL/min |
| Final fracture permeability near 4703 s | 2.250e-13 m² | 2.019e-13 m² | -0.231e-13 m² |
| Final normal dilation at 4802 s | -0.0406 mm | -0.0392 mm | +0.0014 mm |
| Final BB effective normal stress at 4802 s | 24.76 MPa | 27.04 MPa | +2.28 MPa |
| Final shear slip at 4802 s | 0.07281 mm | 0.07093 mm | -0.00188 mm |
| Final shear traction at 4802 s | 2.33 MPa | 2.77 MPa | +0.44 MPa |

## Effect of adding 1.65 MPa residual cohesion

The single-parameter change from parent case `90_05` produces a clear and physically coherent response:

| Metric | `90_05` parent | `91_05` | Validation |
|---|---:|---:|---:|
| Mean NRMSE | 9.2% | **5.4%** | 0% target |
| Final differential stress | 1.60 MPa | 7.77 MPa | 5.50 MPa |
| Final normal dilation | -0.0498 mm | -0.0392 mm | -0.0406 mm |
| Final shear slip | 0.09018 mm | 0.07093 mm | 0.07281 mm |
| Final shear traction | 0.10 MPa | 2.77 MPa | 2.33 MPa |
| Peak flow rate | 0.981 mL/min | 0.802 mL/min | 0.860 mL/min |
| Peak permeability | 4.03e-13 m² | 3.51e-13 m² | 3.66e-13 m² |

Residual cohesion improves six important coupled behaviors simultaneously: it raises residual differential stress, raises residual shear traction, arrests slip sooner, reduces excessive contraction, lowers the excessive flow peak, and lowers the excessive permeability peak. The response confirms that these parent-case errors were different manifestations of insufficient residual strength rather than unrelated calibration problems.

The change also produces mild overcorrections. Residual differential and shear stresses become high, final flow and permeability become low, and effective normal stress recovers too far. These errors are mutually consistent with slightly excessive residual interlock.

## Calibration interpretation

Case `91_05` validates the residual-cohesion hypothesis, but the 1.65 MPa value is probably just above the best compromise. Linear interpolation between the parent and `91_05` endpoint responses gives different preferred values depending on the target:

- Final differential stress suggests approximately 1.0 MPa residual cohesion.
- Final shear traction suggests approximately 1.4 MPa.
- Final normal dilation suggests approximately 1.4 MPa.
- Final shear slip suggests approximately 1.5 MPa.

Because the coupled response is nonlinear, these are only bracketing estimates rather than direct parameter solutions. A narrow follow-up test around **1.3–1.5 MPa residual cohesion** would likely retain the excellent onset and displacement match while reducing the remaining stress and hydraulic overcorrection.

If only one existing case must be selected, `91_05` should be preferred over `90_05`. Its overall error is substantially lower, its event timing remains accurate, and its slip and dilation responses are much closer to the experiment. The modestly high residual stresses are a smaller defect than the parent's near-loss of residual shear resistance and excessive deformation.

## Conclusion

`91_05` is a successful SWS3 residual-strength correction. Its approximately 5.4% mean normalized error makes it a stronger validation result than the preceding SWS3 90-series cases. The model captures the principal event within 4–27 s across the four mechanical indicators and closely reproduces the measured slip, dilation, flow, permeability, and normal-stress evolution.

Adding 1.65 MPa residual cohesion fixes the parent case's over-weakening and excessive deformation without destroying the calibrated onset. The correction is slightly stronger than necessary: final differential stress, shear traction, and effective normal stress are high, while final flow and permeability are low. A residual-cohesion bracket around 1.3–1.5 MPa is the most logical next refinement, but `91_05` is already a credible and well-balanced validation case.
