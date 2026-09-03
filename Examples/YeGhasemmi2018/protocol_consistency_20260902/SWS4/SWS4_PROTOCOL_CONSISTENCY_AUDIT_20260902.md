# SW-S4 protocol-consistency audit

Date: 2 September 2026

## Scope and scoring

This audit compares the three completed SW-S4 runs with the digitized Figure 7 histories and the eleven SW-S4 stages in Table 2 of Ye and Ghassemi (2018):

- `116_07`: Barton--Bandis (BB), measured JRC = 1.19;
- `116_08`: Mohr--Coulomb (MC), corrected protocol;
- `116_09`: BB, JRC = 5 control.

The `116_07` and `116_09` inputs differ only in JRC. Their difference therefore isolates the effect of changing JRC from 5 to the reported value of 1.19 under the corrected loading protocol. In contrast, comparison with the previously selected `93_07` run combines several changes: the machine stiffness, transformed preload command, fixed piston after 55 s, and constant confinement. It cannot identify the effect of each loading correction separately.

The headline score uses five independent observables: flow rate, effective normal stress, shear stress, normal displacement, and shear displacement. For each observable, nRMSE is RMSE divided by the experimental range. The two displacements are referenced to the first hold, and this constructed zero is excluded from their RMSE. Hydraulic aperture and permeability are not scored again because the paper derives them from the measured flow rate.

## Run-integrity result

All three runs are technically complete and suitable for interpretation:

- all runs reached 3500 s, beyond the last experimental stage at 3404.84 s;
- the five scored channels contain no NaN or infinite values;
- the axial command is exactly constant after 55 s in every run;
- the maximum absolute difference between reaction stress and machine-spring stress is 0.171 MPa;
- the corresponding reaction--spring RMSE is 0.131--0.147 MPa.

The disagreement discussed below is therefore not caused by a truncated simulation or a broken stress output. However, the common stiffness of 796 kN/mm was reported for the MTS 815 used by Kalantar et al. (2025), not measured for the MTS 816 used by Ye and Ghassemi (2018). These runs remain a common-stiffness sensitivity, not a fully verified reconstruction of the Ye and Ghassemi loading frame.

## Numerical comparison

### Range-normalized Table 2 RMSE

| Model | Flow | Effective normal stress | Shear stress | Normal displacement | Shear displacement | Mean of five |
|---|---:|---:|---:|---:|---:|---:|
| BB, measured JRC = 1.19 | 13.07% | 4.38% | 11.06% | 36.59% | 68.89% | 26.80% |
| MC, corrected protocol | 18.85% | 13.18% | 34.29% | 26.78% | 38.91% | 26.40% |
| BB, JRC = 5 control | 16.88% | 12.94% | 33.71% | 33.50% | 47.87% | 28.98% |

The similar mean errors of the measured-JRC BB and MC cases do not mean that they reproduce the same physics. Their errors occur in different parts of the loading path. The measured-JRC BB case represents slip initiation well but evolves too quickly after yield. The MC and JRC = 5 cases remain too strong during loading and slip too late.

### Actual values at peak injection and final unloading

| State and response | Experiment | BB, JRC = 1.19 | MC, corrected | BB, JRC = 5 |
|---|---:|---:|---:|---:|
| Peak flow rate (mL/min) | 0.113 | 0.0692 | 0.0525 | 0.0583 |
| Peak effective normal stress (MPa) | 15.31 | 15.68 | 19.71 | 19.98 |
| Peak shear stress (MPa) | 3.12 | 3.75 | 10.73 | 11.20 |
| Peak normal displacement (mm) | -0.041 | -0.0496 | -0.0150 | -0.0124 |
| Peak shear displacement (mm) | 0.075 | 0.1310 | 0.0325 | 0.0257 |
| Final flow rate (mL/min) | 0.005 | 0.00610 | 0.00512 | 0.00562 |
| Final effective normal stress (MPa) | 24.81 | 25.26 | 26.17 | 25.80 |
| Final shear stress (MPa) | 2.27 | 3.03 | 4.60 | 3.96 |
| Final normal displacement (mm) | -0.032 | -0.0474 | -0.0369 | -0.0445 |
| Final shear displacement (mm) | 0.079 | 0.1349 | 0.1129 | 0.1240 |

## Interpretation

### 1. The measured JRC gives the correct initiation pressure

Using a 0.001 mm displacement threshold, the digitized experiment begins to slip at about 930 s and 16.09 MPa. The measured-JRC BB case reaches the same threshold at 896 s and 16.06 MPa. This agreement is very strong and supports the use of the measured JRC for the onset of sliding under the corrected protocol.

The JRC = 5 BB and MC cases reach this threshold only at 27.00 and 26.79 MPa, respectively. They therefore miss the gradual experimental slip between approximately 16 and 28 MPa. Their stress and displacement histories are almost identical before the peak because both remain essentially locked.

### 2. Correct initiation does not give correct post-yield evolution

The measured-JRC BB case reaches 0.075 mm shear displacement at about 1198 s and 20.00 MPa. The experiment reaches the same displacement near 1745 s and 27.97 MPa. Consequently, the simulation releases strength and accumulates dilation much too rapidly after slip starts. By the peak stage, it predicts 0.131 mm shear displacement rather than 0.075 mm and -0.0496 mm normal displacement rather than -0.041 mm.

This distinction is important. JRC controls the initial BB envelope, but the rate of post-yield evolution also depends on the residual friction, characteristic weakening distance, mobilized-roughness evolution, viscosity, dilation law, and loading-system compliance. Those parameters were inherited from a calibration built around JRC = 5 and the earlier boundary treatment. Changing only JRC to 1.19 is therefore a clean diagnostic, but it is not expected to remain a calibrated complete model.

### 3. The corrected MC and JRC = 5 cases slip too late

At the peak Table 2 stage, the corrected MC and JRC = 5 BB cases retain shear stresses of 10.73 and 11.20 MPa, compared with 3.12 MPa experimentally. Their peak shear displacements are only 0.0325 and 0.0257 mm, compared with 0.075 mm. Most of their slip occurs near the end of the peak hold and during early unloading. They therefore cannot reproduce the progressive loading-branch response of SW-S4 without recalibration.

The BB JRC = 5 case ends with lower shear stress than MC, but both retain too much shear displacement after their late slip event. The remaining difference between them does not repair the incorrect timing.

### 4. The hydraulic response confirms a coupled calibration problem

All three cases underpredict the measured peak flow of 0.113 mL/min. The measured-JRC BB case is the closest at 0.0692 mL/min, but it still underpredicts the peak by about 39%, even though it overpredicts mechanical dilation and shear displacement. This combination suggests that the inherited retained-dilation, stress-closure, and slip-damage/gouge terms are compensating for one another. In particular, the large early slip activates aperture-loss terms while the fitted dilation transfer remains small. Hydraulic agreement should therefore not be repaired by changing the initial aperture alone.

### 5. The previous good fit depended on the previous loading representation

The current manuscript reports much lower errors for the previously selected SW-S4 cases, approximately 6.03% for BB and 7.00% for MC when the five channels are averaged. Under the combined corrected protocol, the errors rise to 26.80% and 26.40%. This is a major result. It shows that the previous constitutive calibration is not transferable to the corrected boundary conditions without re-evaluation.

The corrected package changes several loading features together, so the present result does not prove that any single earlier feature was responsible. It does show that the constitutive parameters and boundary representation were coupled in the calibration. The paper should not present the old SW-S4 fit as protocol-independent.

## Verdict

None of the three corrected-protocol runs should replace the selected SW-S4 validation case without further work. The measured-JRC BB result is scientifically the most informative because it captures the experimental onset almost exactly. Its failure is mainly the post-yield evolution, not the initial failure threshold. The MC and JRC = 5 cases fail mainly by delaying slip until near peak pressure.

For the final physical model, the preferred direction is to keep JRC = 1.19 fixed as measured and recalibrate only the post-initiation parameters. This provides a stronger parameter hierarchy than returning immediately to an effective JRC of 5: measured JRC controls initiation, while independently identified weakening and dilation parameters control the evolution after initiation.

## Recommended next checks

1. Complete the same protocol-consistency runs for SW-T1, SW-T2, and SW-S3 before changing the manuscript conclusions. SW-S4 alone cannot show whether the issue is sample-specific or systematic.
2. For SW-S4, fit the mechanical path before the hydraulic path. Keep JRC = 1.19 fixed and target three independent features: onset near 16 MPa, 0.075 mm slip only near 28 MPa, and final shear stress near 2.27 MPa.
3. Examine the residual friction/strength floor, characteristic weakening distance, and viscosity first. The present measured-JRC case needs slower post-yield weakening, not a higher onset threshold.
4. Refit the dilation evolution only after the shear path is correct. Then revisit retained dilation and slip-damage/gouge loss using flow rate as the independent hydraulic target.
5. Run a small boundary-condition ablation if the paper must explain why the result changed: legacy boundary treatment; common stiffness only; fixed piston and constant confinement with the legacy stiffness; and the complete corrected protocol. This separates machine stiffness from the removed post-55 piston and confinement adjustments.
6. Treat 796 kN/mm as a sensitivity until an MTS 816 stiffness is measured, obtained from the authors, or inferred with an uncertainty range. A useful first uncertainty study is 0.5, 1.0, and 2.0 times 796 kN/mm, with constitutive parameters fixed.

## Reproducibility files

- `sws4_protocol_consistency_check.py` performs the complete audit.
- `SWS4_protocol_consistency_metrics.csv` contains the nRMSE values.
- `SWS4_protocol_consistency_stage_values.csv` contains every sampled Table 2 value.
- `SWS4_protocol_consistency_health.csv` contains completion, frame-consistency, and slip-timing checks.
- `SWS4_protocol_consistency_Table2.png` and `SWS4_protocol_consistency_histories.png` contain the stage and time-history comparisons.
- `Ye2018_SW4_num_vs_validation.ipynb` now loads the three protocol cases and executes the same audit.
