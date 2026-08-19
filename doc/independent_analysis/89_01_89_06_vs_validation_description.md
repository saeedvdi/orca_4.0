# Validation comparisons

## SWS4: cases 89_01 and 89_06 versus validation

Both simulations reproduce the overall hydro-mechanical evolution, but neither captures the distinctly stepwise validation response perfectly. The simulated transitions are generally smoother, and both underestimate the initial and final differential stress.

| Comparison | 89_01 paper-JRC | 89_06 theta30 |
|---|---:|---:|
| Mean normalized RMSE | 12.6% | **10.5%** |
| Event timing | Generally early | Generally late |
| Best agreement | Pressure, flow, normal/shear stress | Differential stress, dilation, shear slip |
| Final shear slip | 0.0877 mm | **0.0784 mm** |
| Validation shear slip | 0.0793 mm | 0.0793 mm |

### Case 89_01: paper-JRC

For `89_01`, slip begins about 125 seconds too early, dilation about 53 seconds early, and the differential-stress drop about 19 seconds early. It consequently accumulates too much shear slip and excessive negative dilation. Its final differential stress is only 0.48 MPa compared with the validated 5.14 MPa. However, it provides the better representation of effective normal stress, shear stress, injection pressure, and peak flow rate.

### Case 89_06: theta30

For `89_06`, the main mechanical transition occurs approximately 50–73 seconds later than in the validation. Despite this delay, it reproduces the magnitudes of shear slip and normal dilation much better. Its final shear slip is almost exact—0.0784 mm versus 0.0793 mm—and its final dilation is −0.0303 mm versus −0.0310 mm. It also improves the differential-stress prediction, although the final value of 2.97 MPa remains below validation. Its main weakness is that shear stress remains too high after failure, ending at 2.92 MPa compared with 2.25 MPa, while effective normal stress is also slightly overestimated.

### Hydraulic response

Both cases reproduce the injection-pressure history very well but remain approximately 1–2 MPa below validation through much of the experiment. Both capture the rise and decline of flow rate and permeability, although they underestimate the peak flow rate. Permeability agreement is strong for both, with `89_06` marginally closer overall.

### SWS4 conclusion

> Case `89_06` provides the better overall and kinematic match to the validation, particularly for shear slip, normal dilation, differential stress, and permeability. Case `89_01` predicts failure too early and overestimates the resulting slip and dilation, but it better reproduces the effective normal stress, shear-stress decay, and hydraulic flow response. Thus, `89_06` is the stronger overall candidate, while further adjustment is needed to advance its failure timing and reduce its post-failure shear stress.

---

## SWT2: four-case comparison versus validation

The four SWT2 simulations all reproduce the imposed injection-pressure sequence and the broad pre- and post-failure states, but they differ substantially in their ability to reproduce the timing and progression of the mechanical event. The digitized validation exhibits a long high-stress stage followed by rapid stress loss, dilation, permeability growth, and shear slip at approximately 2235–2255 s. The two sweep-21 cases retain this chronology, whereas cases `89_03` and `89_05` initiate the coupled mechanical transition several hundred seconds too early.

### Method and overall ranking

The normalized errors below were calculated by interpolating every simulation at the digitized validation times. RMSE was normalized by the observed range of each quantity, and the eight quantities were weighted equally. The first 100 s were excluded from this ranking so that the simulations' initial zero-to-load ramp did not dominate the comparison. Flow rate and permeability each contain 11 validation points; the other histories contain 547 post-initialization validation points.

| Rank | Case | Mean normalized RMSE | Mechanical-event timing | Main interpretation |
|---:|---|---:|---:|---|
| 1 | Sweep-21, Biot 0.6 | **9.8%** | 33–41 s late | Best full-history agreement |
| 2 | Sweep-21, baseline Biot | 10.9% | 52–60 s late | Similar response, but slightly later and less accurate |
| 3 | `89_03`, theta30 | 23.6% | 355–360 s early | Good pressure and peak hydraulic magnitude, but premature failure |
| 4 | `89_05`, theta30 with cohesion | 24.9% | 430–445 s early | Excellent final state, but poorest event chronology |

Including the initial loading point changes the mean normalized errors to 12.0%, 12.8%, 24.3%, and 25.5%, respectively, without changing the ranking.

### Error by measured quantity

| Quantity | Sweep-21 Biot 0.6 | Sweep-21 baseline Biot | `89_03` | `89_05` |
|---|---:|---:|---:|---:|
| Differential stress | **9.8%** | 11.9% | 33.8% | 36.0% |
| Injection pressure | 7.0% | 7.1% | **1.2%** | **1.2%** |
| Flow rate | 13.6% | **12.8%** | 14.6% | 14.7% |
| Fracture permeability | 7.7% | **7.3%** | 18.8% | 18.5% |
| Normal dilation | **8.7%** | 11.4% | 33.6% | 35.8% |
| Effective normal stress | **11.5%** | 12.6% | 21.5% | 23.2% |
| Shear slip | **9.4%** | 12.0% | 32.9% | 35.1% |
| Shear stress | **10.3%** | 12.6% | 32.3% | 34.5% |

This breakdown shows that the favorable endpoint agreement of `89_05` does not translate into a good history match. Its early transition produces large errors over several hundred seconds even though the curves later converge toward the correct final state.

### Final-state comparison

| Quantity | Validation | Sweep-21 Biot 0.6 | Sweep-21 baseline Biot | `89_03` | `89_05` |
|---|---:|---:|---:|---:|---:|
| Differential stress (MPa) | 62.84 | 56.65 | 61.01 | 53.52 | **63.87** |
| Injection pressure (MPa) | 7.993 | 8.000 | 8.000 | 8.000 | 8.000 |
| Flow rate (mL/min) | 0.910 | 1.508 | 1.464 | 1.014 | **0.903** |
| Fracture permeability (m²) | 1.480×10⁻¹² | 1.614×10⁻¹² | 1.585×10⁻¹² | 1.594×10⁻¹² | **1.489×10⁻¹²** |
| Normal dilation (mm) | −0.1293 | −0.1380 | −0.1356 | −0.1363 | **−0.1277** |
| Effective normal stress (MPa) | 39.22 | 48.81 | 49.07 | **45.85** | 47.20 |
| Shear slip (mm) | 0.5515 | 0.5987 | 0.5899 | 0.6038 | **0.5514** |
| Shear stress (MPa) | 27.21 | 24.92 | 25.34 | 22.93 | **27.89** |

The endpoint table should therefore be interpreted together with the history errors and event timing. Selecting a case from endpoints alone would favor `89_05`, but that choice would overlook its approximately 7.3-minute premature mechanical transition.

### Sweep-21 with Biot coefficient 0.6

The sweep-21 Biot-0.6 case provides the best balanced reproduction of the experiment. Its major differential-stress loss, dilation, slip, and shear-strength reduction occur only about 33–41 s later than the corresponding validation changes. It accurately retains the long pre-failure plateau and follows the observed sequence of coupled mechanical changes more closely than the other cases.

The main remaining discrepancies appear after failure. The final differential stress is underpredicted by 6.19 MPa, shear slip is overpredicted by 0.0472 mm, and dilation is 0.0087 mm more negative than measured. Effective normal stress is overpredicted by 9.60 MPa at the end, while shear stress is underpredicted by 2.28 MPa. Its peak flow rate is 10.02 mL/min compared with 11.1 mL/min in the validation, and its peak permeability is 1.805×10⁻¹² m² compared with 2.02×10⁻¹² m². Thus, its timing and curve shapes are strong, but the post-failure normal stress and displacement magnitudes still require refinement.

### Sweep-21 with baseline Biot coefficient

The baseline-Biot case is the second-best full-history match. Its response is close to the Biot-0.6 case, but its mechanical transition occurs approximately 52–60 s late and is therefore farther from the observed event. This delay increases the history errors in differential stress, dilation, shear slip, effective normal stress, and shear stress.

Its final residual values are somewhat better than those of the Biot-0.6 case: differential stress ends at 61.01 MPa, only 1.82 MPa below validation; final slip and dilation also have smaller errors. Nevertheless, the full histories are less accurate because the event is later and the transition shape is less well aligned. The baseline case slightly improves the flow-rate and permeability errors, but the improvement is modest. Overall, changing to Biot 0.6 improves the timing and joint mechanical history even though several baseline-Biot endpoints are closer.

### Case 89_03: theta30

Case `89_03` matches the imposed injection pressure exceptionally well, with a normalized pressure error of only 1.2%. It also produces comparatively strong hydraulic peak magnitudes: its maximum flow rate is 10.44 mL/min and its maximum permeability is 1.859×10⁻¹² m², the closest simulated peaks to the validated 11.1 mL/min and 2.02×10⁻¹² m².

Its principal weakness is premature failure. Differential-stress loss, dilation, shear slip, and shear-stress reduction begin about 355–360 s before the corresponding validation event. Consequently, the simulation remains in a post-failure state while the experiment is still on its high-stress plateau. This produces normalized errors of approximately 32–34% for the main mechanical quantities. The case also overpredicts peak slip and dilation magnitude, reaching 0.6040 mm of slip and −0.1508 mm of dilation compared with validated extrema of 0.5740 mm and −0.1420 mm. Its final differential and shear stresses are too low, while effective normal stress and slip remain too high.

### Case 89_05: theta30 with cohesion

Case `89_05` demonstrates the strongest distinction between endpoint calibration and history calibration. It gives remarkably accurate final differential stress, flow rate, permeability, dilation, shear slip, and shear stress. Its final shear slip differs from validation by less than 0.0001 mm, and its final flow rate and permeability are also nearly exact. The cohesion modification clearly improves the residual magnitudes relative to `89_03`.

However, its mechanical transition occurs about 430–445 s too early—earlier even than `89_03`. The model drops from the high-stress state near 1810 s, while the principal validation transition occurs near 2250 s. It therefore spends more than seven minutes in an incorrect post-failure state before the experiment fails. This timing error produces the largest differential-stress, dilation, slip, and shear-stress history errors of the four cases. It also underpredicts the hydraulic peaks, reaching only 8.55 mL/min and 1.644×10⁻¹² m². The final agreement is excellent, but the path to that endpoint is inconsistent with the experiment.

### Hydraulic comparison

All four simulations reproduce the imposed pressure steps, peak, and depressurization sequence. Cases `89_03` and `89_05` are closest to the digitized pressure values, whereas the two sweep-21 curves exhibit small offsets during several pressure plateaus. For flow and permeability, the sweep-21 cases provide the best overall histories because their growth occurs near the observed mechanical event. Case `89_03` has the closest peak magnitudes but begins the hydraulic enhancement too early. Case `89_05` improves the final flow and permeability values but underpredicts their maxima and also activates the enhancement prematurely.

### Mechanical comparison

The validation response is characterized by a long high differential- and shear-stress plateau, followed by rapid stress loss and simultaneous increases in slip, negative dilation, flow, and permeability. The sweep-21 cases preserve this sequence, with the Biot-0.6 case giving the closest timing. Both theta30 HPC cases break the coupling chronology by initiating slip and dilation well before the measured event. `89_03` produces excessive final slip and stress loss, while the cohesion in `89_05` corrects much of the final magnitude without correcting—and in fact further advancing—the failure time.

### SWT2 conclusion

> The sweep-21 Biot-0.6 simulation is the strongest SWT2 validation case when the complete experimental history is considered. It gives the lowest mean normalized error and the closest coupled mechanical-event timing. The baseline-Biot case is a credible second choice and provides several improved endpoints, but its transition is later and its overall history error is higher. Case `89_03` improves the imposed-pressure and hydraulic-peak predictions but fails approximately six minutes too early. Case `89_05` produces the best terminal state yet fails approximately seven minutes too early, demonstrating that endpoint agreement alone is insufficient for calibration. The most promising next step is to retain the residual-magnitude behavior of `89_05` while delaying its failure initiation toward 2235–2255 s, or to refine the sweep-21 Biot-0.6 case to improve its post-failure stress and displacement magnitudes without losing its successful timing.

---

## SWT1: six-case comparison versus validation

The SWT1 comparison contains six labeled cases, but only five have complete histories. The CSV for `87_01_swt1_bbfast_injfix_kernel_SV_biot0p6` ends at 264 s, far before the experimental event near 1650–1725 s and the validation endpoint near 3370 s. It can confirm only the initial loading response and must not be ranked against the five complete simulations.

Among the complete cases, the two sweep-19 simulations reproduce the observed coupled failure. Case `89_04` also reaches a post-failure state but initiates it far too early. Cases `88_02` and `88_03` do not undergo the observed failure: differential and shear stress remain high, permeability and flow remain near their pre-event levels, slip remains negligible, and normal displacement develops with the wrong sign.

### Method and overall ranking

As in the SWT2 analysis, each simulation was interpolated at the digitized validation times. RMSE was normalized by the observed range of each quantity, and the eight quantities were weighted equally. Data before 100 s were excluded to avoid giving excessive weight to the initial zero-to-load ramp. The incomplete `87_01` result was excluded from the full-history ranking.

| Rank | Case | Coverage | Mean normalized RMSE | Principal-event timing | Main interpretation |
|---:|---|---:|---:|---:|---|
| — | `87_01` injfix | 264 s | Not ranked | Event not reached | Incomplete run |
| 1 | Sweep-19, Biot 0.6 | 3500 s | **15.3%** | 22–86 s late | Best complete history |
| 2 | Sweep-19, baseline Biot | 3500 s | 16.8% | 44–108 s late | Similar but consistently later |
| 3 | `89_04`, cohesion | 3500 s | 26.7% | 530–595 s early | Reasonable residuals, premature failure |
| 4 | `88_02`, vmopt | 3500 s | 52.6% | No principal failure | Remains mostly locked |
| 5 | `88_03`, vmopt-kni | 3500 s | 55.1% | No principal failure | Remains locked and dilates in the wrong direction |

The validation indicators do not all transition at exactly the same time. Validation shear slip first exceeds the selected event threshold at about 1650 s, while differential stress, negative dilation, and shear stress transition near 1720–1725 s. The timing ranges above therefore compare like-for-like thresholds rather than assuming a single event time.

### Error by measured quantity

| Quantity | `88_02` | `88_03` | Sweep-19 Biot 0.6 | Sweep-19 baseline Biot | `89_04` |
|---|---:|---:|---:|---:|---:|
| Differential stress | 58.2% | 54.8% | **8.3%** | 11.8% | 35.8% |
| Injection pressure | 0.9% | 0.9% | 6.0% | 6.0% | **0.9%** |
| Flow rate | 37.9% | 37.9% | 29.2% | 29.3% | **19.9%** |
| Fracture permeability | 56.7% | 56.7% | 31.9% | 32.1% | **28.3%** |
| Normal dilation | 95.1% | 125.1% | **12.1%** | 13.6% | 35.2% |
| Effective normal stress | 43.3% | 40.1% | **17.2%** | 18.1% | 24.2% |
| Shear slip | 65.9% | 66.5% | **8.5%** | 11.4% | 35.2% |
| Shear stress | 62.5% | 58.6% | **9.1%** | 11.7% | 33.9% |

The table separates two distinct behaviors. The sweep-19 cases dominate the mechanical histories, while `89_04`, `88_02`, and `88_03` reproduce the prescribed injection pressure almost exactly. Case `89_04` also has lower flow and permeability errors, but these improvements are partly associated with an early hydraulic/mechanical transition rather than the correct event chronology.

### Final-state comparison

Flow rate and permeability are compared at their final validation time of 3250 s; the other quantities are compared at 3370 s.

| Quantity | Validation | `88_02` | `88_03` | Sweep-19 Biot 0.6 | Sweep-19 baseline Biot | `89_04` |
|---|---:|---:|---:|---:|---:|---:|
| Differential stress (MPa) | 62.68 | 134.26 | 127.88 | **61.16** | 65.23 | 68.08 |
| Injection pressure (MPa) | 7.995 | 8.000 | 8.000 | 8.000 | 8.000 | 8.000 |
| Flow rate (mL/min) | 0.462 | 0.053 | 0.053 | 0.663 | 0.638 | **0.599** |
| Fracture permeability (m²) | 9.40×10⁻¹³ | 2.21×10⁻¹³ | 2.21×10⁻¹³ | 1.24×10⁻¹² | 1.21×10⁻¹² | **1.14×10⁻¹²** |
| Normal dilation (mm) | −0.1118 | +0.0844 | +0.1434 | −0.1391 | −0.1362 | **−0.1286** |
| Effective normal stress (MPa) | 41.10 | 62.10 | 59.86 | 52.32 | 52.57 | **48.36** |
| Shear slip (mm) | 0.5204 | 0.0225 | 0.0181 | 0.5339 | **0.5254** | 0.4930 |
| Shear stress (MPa) | 28.16 | 62.33 | 59.42 | 27.52 | **27.85** | 31.08 |

The endpoint comparison confirms that `88_02` and `88_03` remain in the wrong mechanical state. The baseline-Biot sweep gives the closest final slip and shear stress, while the Biot-0.6 sweep gives the closest final differential stress. Case `89_04` gives the closest final flow, permeability, dilation, and effective normal stress, but these endpoint improvements must be weighed against its large timing error.

### Case 87_01: incomplete injfix run

Case `87_01` contains only 353 rows and terminates at 264 s. It does not reach the injection peak, hydraulic enhancement, stress drop, dilation, or shear-slip event. Its visible portion overlaps the other simulations during initial loading, but no conclusion can be drawn about its validation quality after that stage. The CSV is also older than its input deck, so this case should be rerun before it is used for calibration or compared quantitatively with the complete simulations.

### Case 88_02: vmopt

Case `88_02` tracks the injection-pressure schedule very accurately but never develops the observed coupled failure. Differential stress remains near 134 MPa instead of falling to approximately 63 MPa, and shear stress remains near 62 MPa instead of falling to 28 MPa. Final shear slip is only 0.0225 mm compared with 0.5204 mm in the validation, while permeability remains at 2.21×10⁻¹³ m² rather than increasing toward 9.40×10⁻¹³ m².

Its normal displacement is also inconsistent with the experiment: it evolves toward +0.084 mm while the digitized curve reaches −0.112 mm. The model therefore captures the imposed hydraulic loading but does not convert it into the required mechanical instability or fracture opening/closure response.

### Case 88_03: vmopt-kni

Case `88_03` behaves similarly to `88_02` and also remains mechanically locked. The kni modification slightly lowers the residual differential, normal, and shear stresses, but the changes are insufficient to initiate the observed slip event. Its final slip is only 0.0181 mm, and flow and permeability remain at nearly the same low levels as `88_02`.

The largest additional problem is normal displacement: `88_03` reaches approximately +0.143 mm, opposite in sign to the validated −0.112 mm. This produces the largest normal-dilation error of all complete cases. Relative to `88_02`, the kni change modestly reduces several stress errors but worsens dilation and does not solve the missing-failure problem.

### Sweep-19 with Biot coefficient 0.6

The sweep-19 Biot-0.6 case provides the best complete SWT1 history. Differential-stress loss, negative dilation, and shear-stress reduction occur approximately 22–34 s after validation; the selected slip threshold is reached about 86 s late. Despite this modest delay, the case preserves the correct long pre-failure plateau and reproduces the coupled transition much more faithfully than the other configurations.

Its peak flow rate is 6.69 mL/min versus 6.22 mL/min in validation, and peak permeability is 1.424×10⁻¹² m² versus 1.37×10⁻¹² m². These peaks occur near 1955 s, about 205 s later than the hydraulic validation peak. Maximum slip is 0.5341 mm, close to the validated 0.5425 mm, and minimum dilation is −0.1565 mm versus −0.1612 mm. At the end, differential stress and shear stress are also close, but effective normal stress remains 11.2 MPa too high and negative dilation is overpredicted by 0.0273 mm.

### Sweep-19 with baseline Biot coefficient

The baseline-Biot sweep is the second-best case and follows essentially the same mechanism as the Biot-0.6 run. Its event is consistently later: the stress and dilation indicators lag validation by approximately 44–57 s, and the slip threshold lags by about 108 s. These delays raise every principal mechanical-history error relative to the Biot-0.6 case.

The baseline case nevertheless improves several final and peak magnitudes. Its final shear slip is 0.5254 mm and final shear stress is 27.85 MPa, both very close to validation. Its peak flow rate of 6.50 mL/min and peak permeability of 1.397×10⁻¹² m² are also closer in magnitude than the Biot-0.6 peaks. Thus, baseline Biot improves some magnitudes, whereas Biot 0.6 gives the better event timing and overall mechanical history.

### Case 89_04: cohesion

Case `89_04` reaches the correct general post-failure regime and improves several hydraulic and residual values, but its principal transition occurs approximately 530–595 s too early. Slip begins near 1120 s and the stress/dilation transitions occur near 1130–1140 s, whereas the validation changes occur near 1650–1725 s. The simulation therefore remains in an evolved damage/slip state for roughly nine minutes before the experiment undergoes its main failure.

Its peak flow rate, permeability, dilation magnitude, and slip are all somewhat low: 5.74 mL/min, 1.296×10⁻¹² m², −0.1446 mm, and 0.4931 mm, respectively. However, its final flow, permeability, dilation, and effective normal stress are the closest of the complete cases. Cohesion therefore helps control the residual magnitudes, but the initiation criterion is too weak or the pre-failure strength evolution is too rapid. This case should not be preferred over the sweep-19 cases until its event is delayed without losing its improved residual behavior.

### Hydraulic comparison

All complete cases reproduce the injection-pressure program, with `88_02`, `88_03`, and `89_04` giving the closest pressure histories. The pressure agreement alone is not sufficient: `88_02` and `88_03` generate almost no permeability enhancement or event-scale flow, while `89_04` activates both too early. The sweep-19 cases best preserve the experimentally observed coupling between failure, permeability increase, and flow increase, although their hydraulic maxima occur approximately 200 s late and remain imperfect in the declining stage.

### Mechanical comparison

The SWT1 validation requires a transition from high differential and shear stress to a slipped, negatively dilated, higher-permeability state. Only the two sweep-19 cases reproduce that transition near the correct time. Case `89_04` reaches a comparable state far too early. Cases `88_02` and `88_03` remain locked and end with the wrong stresses, negligible slip, insufficient permeability, and positive rather than negative normal displacement. The Biot-0.6 sweep gives the best timing and history, while the baseline-Biot sweep gives slightly better final slip, shear stress, and hydraulic peak magnitudes.

### SWT1 conclusion

> The sweep-19 Biot-0.6 simulation is the strongest SWT1 calibration case because it gives the lowest full-history error and the closest combined timing of stress loss, negative dilation, and shear slip. The baseline-Biot sweep is a close second and improves several endpoint and peak magnitudes, but its failure is later and its history errors are consistently higher. Case `89_04` is useful for its improved residual hydraulic and normal-response values, yet its roughly nine-minute premature failure prevents it from being a valid full-history match. Cases `88_02` and `88_03` should not be retained as calibration candidates in their present form because they never reproduce the observed instability. Case `87_01` must be completed or rerun before it can be assessed. A productive next step would preserve the sweep-19 Biot-0.6 timing while reducing its late effective-normal-stress and dilation errors, potentially borrowing the residual-magnitude behavior of `89_04` without adopting its premature initiation.

---

## SWS3: five-case comparison versus validation

The SWS3 comparison contains five labeled cases, but `86_02_sw3_bbfast_biot0p6_phir9p00_m0_kernel_SV` is incomplete. Its CSV ends at 1304.25 s, well before the principal experimental transition at approximately 2435–2445 s and the validation endpoint near 4800 s. The case is therefore excluded from the full-history ranking.

The quantitative comparison uses the corrected Table-2 permeability validation series, `permeability_m2_vs_time_sw3_corrected.table2`, currently selected by the SWS3 notebook. This is important because the older digitized permeability series was approximately three times too low and inconsistent with the measured flow-rate evolution.

### Method and overall ranking

Each complete simulation was interpolated at the digitized validation times. RMSE was normalized by the observed range of each quantity, and the eight measured quantities were weighted equally. Data before 100 s were excluded to prevent the initial zero-to-load ramp from dominating the comparison.

| Rank | Case | Coverage | Mean normalized RMSE | Principal-event timing | Main interpretation |
|---:|---|---:|---:|---:|---|
| — | `86_02`, φr = 9.00° | 1304.25 s | Not ranked | Event not reached | Incomplete run |
| 1 | `84_01`, baseline Biot | 4802 s | **4.0%** | −29 to +6 s | Best timing and amplitudes by a wide margin |
| 2 | `86_01`, φr = 8.45° | 4802 s | 10.0% | −3 to +30 s | Excellent timing, but stresses and slip magnitudes need correction |
| 3 | `84_01`, Biot 0.6 | 4802 s | 20.0% | 327–362 s early | Premature failure and excessive post-event response |
| 4 | `89_02`, paper-JRC | 4802 s | 21.7% | 360–390 s early | Earliest and strongest complete post-event response |

The validation differential-stress and dilation transitions occur at about 2445 s, the selected shear-slip threshold is reached near 2435 s, and shear stress begins its principal decline near 2440 s. Both the baseline-Biot case and `86_01` reproduce this event window closely. The other two complete cases transition approximately six minutes too early.

### Error by measured quantity

| Quantity | `84_01` Biot 0.6 | `84_01` baseline Biot | `86_01` | `89_02` |
|---|---:|---:|---:|---:|
| Differential stress | 33.3% | **4.0%** | 23.3% | 37.4% |
| Injection pressure | 1.1% | **1.1%** | **1.1%** | 1.1% |
| Flow rate | 14.1% | **3.6%** | 6.6% | 15.6% |
| Corrected fracture permeability | 19.6% | **5.8%** | 7.9% | 23.4% |
| Normal dilation | 27.8% | **2.8%** | 10.3% | 30.3% |
| Effective normal stress | 9.7% | 8.0% | **5.8%** | 8.7% |
| Shear slip | 33.1% | **2.7%** | 15.5% | 34.5% |
| Shear stress | 21.4% | **3.8%** | 9.5% | 22.8% |

The baseline-Biot case is best for seven of the eight observables and is second only to `86_01` for effective normal stress. Its advantage is not produced by a single favorable endpoint: it follows the complete time histories closely. Case `86_01` also has strong pressure, flow, permeability, normal-stress, and event-timing performance, but its differential stress and post-event displacement magnitudes are less accurate.

### Final-state comparison

Flow rate is compared at 4700 s, permeability at approximately 4703 s, and the other quantities at 4800 s.

| Quantity | Validation | `84_01` Biot 0.6 | `84_01` baseline Biot | `86_01` | `89_02` |
|---|---:|---:|---:|---:|---:|
| Differential stress (MPa) | 5.512 | −2.714 | **6.105** | −1.077 | −3.056 |
| Injection pressure (MPa) | 7.971 | 7.881 | 7.881 | 7.881 | 7.881 |
| Flow rate (mL/min) | 0.0540 | 0.0528 | 0.0448 | 0.0503 | **0.0537** |
| Fracture permeability (m²) | 2.250×10⁻¹³ | **2.254×10⁻¹³** | 2.029×10⁻¹³ | 2.192×10⁻¹³ | 2.306×10⁻¹³ |
| Normal dilation (mm) | −0.04065 | −0.05060 | **−0.04116** | −0.04822 | −0.05158 |
| Effective normal stress (MPa) | 24.75 | 26.50 | 27.39 | 26.62 | **25.56** |
| Shear slip (mm) | 0.07276 | 0.09303 | **0.07432** | 0.08825 | 0.09351 |
| Shear stress (MPa) | 2.355 | 0.219 | **2.065** | 0.519 | 0.366 |

The endpoint comparison reinforces the history-based ranking. The baseline-Biot case is closest for differential stress, dilation, slip, and shear stress. Other cases match individual hydraulic or normal-stress endpoints, but their post-event mechanical states are generally too severe.

### Case 86_02: incomplete φr = 9.00° run

Case `86_02` contains 1740 rows and stops at 1304.25 s. It does not reach the pressure maximum, stress drop, dilation, permeability enhancement, or shear-slip event. Its early response alone cannot establish whether φr = 9.00° would improve the complete SWS3 behavior. The CSV is also older than its corresponding input deck, so the case should be rerun before it is used in calibration decisions.

### Case 84_01 with baseline Biot coefficient

The baseline-Biot `84_01` case is the strongest SWS3 result. Differential stress begins its principal drop only 2.25 s before validation, dilation begins about 29 s early, slip about 22 s early, and shear-stress loss about 6 s late. These small offsets reproduce the coupled event far more accurately than the early-failing cases.

It also captures the response magnitudes. Peak flow is 0.871 mL/min versus 0.860 mL/min in validation, peak permeability is 3.663×10⁻¹³ m² versus 3.660×10⁻¹³ m², and minimum dilation is −0.04520 mm versus −0.04479 mm. Final slip is 0.07432 mm compared with 0.07276 mm, and final differential stress is 6.11 MPa compared with 5.51 MPa. Its largest remaining endpoint discrepancy is effective normal stress, which finishes 2.64 MPa too high. The hydraulic peaks occur near 2699 s, approximately 100 s later than the digitized maxima, but their amplitudes and subsequent decline are very close.

### Case 86_01: φr = 8.45°

Case `86_01` gives the second-best complete history and arguably the most precise onset timing. Its dilation and slip thresholds differ from validation by only −3 s and +7 s, while differential- and shear-stress changes lag by approximately 14 s and 30 s. It also produces the lowest effective-normal-stress history error of the tested cases.

The remaining problem is event magnitude. Pre-event differential stress is already too low, and final differential stress falls to −1.08 MPa rather than remaining near 5.51 MPa. Final slip reaches 0.08825 mm, dilation reaches −0.04822 mm, and shear stress falls to 0.52 MPa, indicating excessive post-event weakening and deformation. Its peak flow and permeability are also moderately high at 0.949 mL/min and 3.878×10⁻¹³ m². The φr = 8.45° formulation therefore places the event correctly but needs a stronger residual response.

### Case 84_01 with Biot coefficient 0.6

The Biot-0.6 `84_01` case initiates failure approximately 327–362 s too early. It begins the coupled transition near 2075–2115 s instead of the observed 2435–2445 s window. This produces large history errors even though the pressure schedule and several final hydraulic values are reasonable.

The early event is also too strong. Peak flow reaches 0.979 mL/min, peak permeability reaches 3.953×10⁻¹³ m², minimum dilation reaches −0.05465 mm, and maximum slip reaches 0.09341 mm. Final differential and shear stresses fall to −2.71 MPa and 0.22 MPa, both well below validation. Relative to the baseline-Biot version, setting Biot to 0.6 substantially advances failure and increases post-event weakening, slip, dilation, flow, and permeability. For SWS3, that change clearly worsens the validation match.

### Case 89_02: paper-JRC

Case `89_02` is now a complete 4802 s run, even though older notebook output recorded a partial endpoint. Its current CSV was therefore evaluated over the full validation interval. The case begins its mechanical transition approximately 360–390 s too early, slightly earlier than the Biot-0.6 `84_01` case, and has the largest mean error among the complete simulations.

It produces the largest hydraulic and deformation peaks: flow reaches 1.016 mL/min, permeability 4.124×10⁻¹³ m², minimum dilation −0.05608 mm, and maximum slip 0.09387 mm. Its final flow rate and effective normal stress are very close to validation, but final differential stress is −3.06 MPa, final slip is 0.09351 mm, and final shear stress is only 0.37 MPa. The paper-JRC configuration therefore weakens too early and too strongly; its good isolated endpoints do not compensate for the incorrect chronology and excessive post-event response.

### Hydraulic comparison

All complete cases reproduce the prescribed injection-pressure history closely. The baseline-Biot `84_01` case best reproduces the measured flow and corrected permeability histories, including their peak magnitudes and declining stages. Case `86_01` is a credible second choice but modestly overpredicts both peaks. The Biot-0.6 `84_01` and paper-JRC `89_02` cases activate hydraulic enhancement too early and overpredict the maxima, reflecting their premature and excessive mechanical transitions.

### Mechanical comparison

The validation requires a stress drop near 2440 s followed by approximately 0.073 mm of slip, about −0.041 mm of final dilation, and residual differential and shear stresses near 5.5 MPa and 2.36 MPa. The baseline-Biot case reproduces both timing and magnitude. Case `86_01` reproduces timing but weakens too much. The Biot-0.6 and paper-JRC cases fail roughly six minutes early and reach an excessively weakened residual state. These results indicate that event initiation and residual strength must be assessed together: correct timing alone does not make `86_01` optimal, while isolated endpoint agreement does not rescue `89_02`.

### SWS3 conclusion

> The `84_01` baseline-Biot simulation is the clear SWS3 calibration choice. It has the lowest mean normalized error by a large margin, reproduces the coupled event within roughly half a minute, and closely matches flow, corrected permeability, dilation, slip, and residual stress magnitudes. Case `86_01` is the best alternative when onset timing is prioritized, but it requires increased residual differential and shear strength and reduced post-event slip and dilation. The Biot-0.6 `84_01` and paper-JRC `89_02` configurations should not be preferred in their present form because both fail approximately six minutes early and overpredict post-event weakening. Case `86_02` must be completed or rerun before φr = 9.00° can be evaluated. The most productive refinement path is to retain the baseline-Biot timing and magnitude balance, with only modest adjustment to its late effective normal stress and approximately 100 s hydraulic-peak delay.
