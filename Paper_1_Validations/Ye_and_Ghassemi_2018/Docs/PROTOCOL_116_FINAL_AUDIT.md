# Final audit of the 116-series protocol-transfer calculations

**Date:** 3 September 2026  
**Purpose:** support the final manuscript without requesting additional simulations

## Publication decision

The 116-series cases should be presented as a **no-refit protocol-transfer test**, not as replacements for the selected calibrated cases. The selected cases remain the primary BB--MC reconstruction because both models were calibrated and compared under matched conditions. The 116 series asks a different question: do those calibrated parameters transfer when the actuator command is fixed after preload, confinement remains at 30 MPa, and one common provisional machine stiffness is used?

The answer is mixed. Transfer is good for SW-T1, similar for the two models in SW-T2, and poor for the completed saw-cut transfers. This is publishable because it shows that the loading representation and post-yield constitutive calibration are coupled. It also prevents the paper from making a stronger claim than the evidence supports.

No additional simulation campaign is required for this conclusion.

## Status of the downloaded archive

| Specimen | Case | Status at audit | Table 2 stages |
|---|---|---:|---:|
| SW-T1 | 116_01 BB | Complete; final row is one output interval before the final schedule knot | 11/11 |
| SW-T1 | 116_02 MC | Complete | 11/11 |
| SW-T2 | 116_03 BB | Complete | 11/11 |
| SW-T2 | 116_04 MC | Complete | 11/11 |
| SW-T2 | 116_10 BB equilibrium-hold control | Complete | 11/11 |
| SW-T2 | 116_11 MC equilibrium-hold control | Complete | 11/11 |
| SW-S3 | 116_05 BB | Complete; final row is within one output interval of the final knot | 11/11 |
| SW-S3 | 116_06 MC | Partial in the downloaded archive at 4062.20 s | 9/11 |
| SW-S4 | 116_07 BB, measured JRC = 1.19 | Complete | 11/11 |
| SW-S4 | 116_08 MC | Complete | 11/11 |
| SW-S4 | 116_09 BB, JRC = 5 control | Complete | 11/11 |

All completed cases keep the axial command constant after 55 s. The reaction--spring comparison remains within approximately 0.58 MPa. Most of this small difference is explained by the use of nominal rather than discretized top-surface area in one reaction normalization.

## Completed no-refit transfer scores

Range-normalized RMSE is reported in percent. The mean gives equal weight to flow rate, effective normal stress, shear stress, normal displacement, and shear displacement.

| Specimen | Model | Flow | Effective normal stress | Shear stress | Normal displacement | Shear displacement | Mean of five |
|---|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | BB | 2.03 | 1.48 | 2.03 | 5.25 | 1.82 | **2.52** |
| SW-T1 | MC | 7.06 | 4.86 | 6.71 | 13.84 | 2.43 | 6.98 |
| SW-T2 | BB | 11.39 | 6.05 | 4.03 | 10.61 | 10.86 | **8.59** |
| SW-T2 | MC | 10.58 | 7.70 | 6.70 | 10.88 | 8.11 | 8.79 |
| SW-S3 | BB | 42.01 | 1.99 | 4.94 | 85.73 | 109.27 | 48.79 |
| SW-S4 | BB, JRC = 1.19 | 13.07 | 4.38 | 11.06 | 36.59 | 68.89 | 26.80 |
| SW-S4 | BB, JRC = 5 control | 16.88 | 12.94 | 33.71 | 33.50 | 47.87 | 28.98 |
| SW-S4 | MC | 18.85 | 13.18 | 34.29 | 26.78 | 38.91 | **26.40** |

The extended SW-T2 holds change the BB and MC means by less than 0.001 percentage points. The short unloading branch is therefore not responsible for the SW-T2 transfer error.

## Interpretation by specimen

### SW-T1

The calibrated parameters transfer well. BB remains clearly better than MC, with mean errors of 2.52% and 6.98%. This is the strongest evidence that the BB advantage for the rough tensile fractures is not only caused by the original loading representation.

### SW-T2

The two transferred models are nearly tied. BB is slightly better in the mean, while MC is better for flow and shear displacement. The long-hold controls show that this result is not caused by insufficient time for unloading equilibration.

### SW-S3

The completed BB transfer predicts the two stress channels closely, but it does not reproduce the displacement or flow response. This is a boundary--constitutive transfer failure. The currently downloaded MC result is incomplete and should not be assigned an eleven-stage nRMSE until its final file is copied.

### SW-S4

The measured-JRC BB case reaches 0.001 mm of slip at 16.06 MPa, almost equal to the digitized experimental value of 16.09 MPa. It then weakens and dilates too quickly. The JRC = 5 BB control and MC case remain too strong and reach the same slip threshold only near 27 MPa. Therefore, measured JRC identifies the onset well, while the weakening distance, residual strength, dilation, viscosity, and loading-system compliance control the post-yield path.

## Final manuscript position

The defensible manuscript claim is:

> Under matched calibrated reconstructions, BB gives the lower study-wide error, especially for the rough tensile fractures. No-refit protocol transfers show that this ranking is not universal and that the loading-system representation and post-yield constitutive parameters must be identified together.

The manuscript should not state that the 796 kN/mm stiffness is measured for the Ye--Ghassemi MTS 816. It is a provisional common value reported for the MTS 815 used by Kalantar et al. (2025). The manuscript should also distinguish the calibrated SW-S4 effective JRC of 5 from the measured JRC of 1.19.

## Reproducibility

Run the analysis-only script after replacing or updating any CSV:

```bash
python3 analyze_protocol_consistency_116.py --output-dir results
```

The script reads existing outputs only. It does not run Orca or modify a simulation.
