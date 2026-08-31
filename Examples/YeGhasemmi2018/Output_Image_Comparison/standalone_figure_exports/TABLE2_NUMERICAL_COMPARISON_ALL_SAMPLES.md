# Ye and Ghassemi (2018) Table 2 versus numerical results

## Scope

This report compares the selected Barton-Bandis (BB) and Mohr-Coulomb (MC)
numerical results with Ye and Ghassemi (2018), Table 2, for all four specimens:
SW-T1, SW-T2, SW-S3, and SW-S4.

Each comparison uses all eleven ordered hold stages:

- Loading: 8, 12, 16, 20, 24, and 28 MPa.
- Unloading: 24, 20, 16, 12, and 8 MPa.

Eight Table 2 quantities are reported:

1. Injection pressure.
2. Effective normal stress.
3. Shear stress.
4. Normal dilation.
5. Shear displacement.
6. Flow rate.
7. Hydraulic aperture.
8. Fracture permeability.

Injection pressure is the prescribed control variable rather than an independent
response measurement. Effective normal stress, shear stress, normal dilation,
shear displacement, and flow rate are the five independent validation channels.
Hydraulic aperture is back-calculated from flow, and fracture permeability is
then derived from aperture; consequently, the last two quantities must not be
counted as additional independent validation evidence.

## Selected numerical cases

| Sample | Barton-Bandis case | Mohr-Coulomb case |
|---|---|---|
| SW-T1 | `107_01_swt1_coh27p2_apscale0p01512_ppfix` | `SWT1_OrcaMohrCoulombContactTraction_pb04` |
| SW-T2 | `100_04_swt2_apscale0p0177_ppfix` | `SWT2_OrcaMohrCoulombContactTraction_pb04` |
| SW-S3 | `100_06_sw3_resc1p30_unld0p00_ppfix` | `SWS3_OrcaMohrCoulombContactTraction_pb06` |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix` | `SWS4_OrcaMohrCoulombContactTraction_center` |

## Error measures

For every sample, quantity, and model, the error is defined as:

`error = numerical value - Table 2 value`

The tables report:

- **RMSE:** root-mean-square error over the eleven hold stages.
- **MAE:** mean absolute error over the eleven hold stages.
- **Bias:** mean signed error. Positive values mean that the numerical result is
  higher than Table 2; negative values mean that it is lower.
- **nRMSE:** `100 x RMSE / (maximum Table 2 value - minimum Table 2 value)`.

The displacement channels use the stage-1 datum convention employed by the
authoritative Table 2 scorer. The average nRMSE values below are unweighted
descriptive averages across the four samples, not a new calibration objective.

## Across-sample summary

| Criterion | Mean BB nRMSE | Mean MC nRMSE | Lower mean error | Main observation |
|---|---:|---:|---|---|
| Injection pressure | 0.30% | 0.30% | Equivalent | Exact for SW-T1 and SW-T2; below 1% for SW-S3 and SW-S4. |
| Effective normal stress | 2.42% | 3.91% | BB | BB has lower RMSE for all four samples. |
| Shear stress | 5.31% | 7.51% | BB | BB has lower RMSE for all four samples; SW-S4 is the most difficult case. |
| Normal dilation | 3.50% | 7.86% | BB | BB has lower RMSE for all four samples, with the largest advantage for SW-T1 and SW-S3. |
| Shear displacement | 2.71% | 3.37% | BB overall | BB is lower for SW-T1 and SW-T2; MC is lower for SW-S3 and SW-S4. |
| Flow rate | 3.39% | 5.34% | BB overall | BB is lower for SW-T1, SW-T2, and SW-S4; MC is slightly lower for SW-S3. |
| Hydraulic aperture | 5.83% | 8.33% | BB overall | The result follows the flow comparison because aperture is derived from flow. |
| Fracture permeability | 5.20% | 8.74% | BB | BB has lower RMSE for all four samples; permeability is derived rather than independent. |

Overall, the selected BB cases reproduce Table 2 more closely for most responses.
The largest BB advantages occur for SW-T1 normal dilation and the SW-T1 hydraulic
quantities. The two laws are much closer for SW-S3, where MC is slightly better
for shear displacement, flow rate, and hydraulic aperture. For SW-S4, MC is
better for shear displacement, while BB is better for the remaining physical
quantities.

## Per-sample comparison

### SW-T1

| Criterion | Unit | Table 2 range | BB RMSE | BB MAE | BB bias | BB nRMSE | MC RMSE | MC MAE | MC bias | MC nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Injection pressure | MPa | 8 to 28 | 0 | 0 | 0 | 0.00% | 0 | 0 | 0 | 0.00% |
| Effective normal stress | MPa | 31.79 to 65.47 | 0.4911 | 0.4088 | 0.3436 | 1.46% | 1.624 | 1.405 | 1.405 | 4.82% |
| Shear stress | MPa | 28.23 to 67.16 | 0.7799 | 0.653 | 0.5465 | 2.00% | 2.591 | 2.245 | 2.245 | 6.66% |
| Normal dilation | mm | -0.157 to 0 | 0.002701 | 0.002153 | -0.001536 | 1.72% | 0.01891 | 0.0128 | -0.01142 | 12.04% |
| Shear displacement | mm | 0 to 0.539 | 0.004825 | 0.003581 | -0.0009439 | 0.90% | 0.01985 | 0.01517 | -0.01517 | 3.68% |
| Flow rate | mL/min | 0.053 to 6.22 | 0.07168 | 0.05239 | 0.0214 | 1.16% | 0.4025 | 0.286 | 0.1535 | 6.53% |
| Hydraulic aperture | µm | 1.59 to 4.05 | 0.0562 | 0.04499 | 0.01967 | 2.28% | 0.2558 | 0.1824 | 0.1341 | 10.40% |
| Fracture permeability | 10^-12 m² | 0.21 to 1.37 | 0.01659 | 0.0128 | -0.008086 | 1.43% | 0.1531 | 0.1061 | 0.08061 | 13.20% |

SW-T1 shows the clearest separation between constitutive laws. BB has lower
error for every physical response and remains below 2.3% nRMSE for all eight
reported quantities. MC particularly overpredicts the magnitudes of effective
normal stress and shear stress, while its negative displacement biases indicate
greater-magnitude closure/slip offsets relative to Table 2 under the adopted
sign convention.

### SW-T2

| Criterion | Unit | Table 2 range | BB RMSE | BB MAE | BB bias | BB nRMSE | MC RMSE | MC MAE | MC bias | MC nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Injection pressure | MPa | 8 to 28 | 0 | 0 | 0 | 0.00% | 0 | 0 | 0 | 0.00% |
| Effective normal stress | MPa | 29.36 to 66.74 | 0.4763 | 0.4246 | 0.2324 | 1.27% | 1.217 | 1.028 | 0.8357 | 3.26% |
| Shear stress | MPa | 27.09 to 74.87 | 0.8233 | 0.735 | 0.4052 | 1.72% | 2.108 | 1.78 | 1.45 | 4.41% |
| Normal dilation | mm | -0.142 to 0 | 0.002798 | 0.002317 | 0.001665 | 1.97% | 0.003573 | 0.002999 | 0.0009515 | 2.52% |
| Shear displacement | mm | 0 to 0.572 | 0.00687 | 0.005716 | -0.002877 | 1.20% | 0.01561 | 0.01253 | -0.01253 | 2.73% |
| Flow rate | mL/min | 0.115 to 11.1 | 0.4763 | 0.3644 | 0.0167 | 4.34% | 0.6297 | 0.4563 | -0.0006928 | 5.73% |
| Hydraulic aperture | µm | 2.11 to 4.92 | 0.2239 | 0.1685 | -0.01044 | 7.97% | 0.258 | 0.2026 | 0.005787 | 9.18% |
| Fracture permeability | 10^-12 m² | 0.37 to 2.02 | 0.1225 | 0.09758 | 0.006888 | 7.43% | 0.153 | 0.1198 | 0.01588 | 9.27% |

BB also has lower RMSE for every SW-T2 response. Both models reproduce the
mechanical channels well, while the larger normalized errors occur for the two
derived hydraulic quantities. Their absolute aperture and permeability errors
remain small relative to their physical units, but the narrow Table 2 ranges
increase the normalized percentages.

### SW-S3

| Criterion | Unit | Table 2 range | BB RMSE | BB MAE | BB bias | BB nRMSE | MC RMSE | MC MAE | MC bias | MC nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Injection pressure | MPa | 8 to 28 | 0.1826 | 0.09878 | 0.01843 | 0.91% | 0.1826 | 0.09886 | 0.01839 | 0.91% |
| Effective normal stress | MPa | 15.25 to 31.65 | 0.5034 | 0.4241 | 0.2305 | 3.07% | 0.5146 | 0.4348 | 0.2412 | 3.14% |
| Shear stress | MPa | 2.31 to 14.7 | 0.9158 | 0.7568 | 0.4101 | 7.39% | 0.9356 | 0.7762 | 0.4294 | 7.55% |
| Normal dilation | mm | -0.044 to 0 | 0.00259 | 0.002064 | 0.0003363 | 5.89% | 0.004623 | 0.003466 | 0.00253 | 10.51% |
| Shear displacement | mm | 0 to 0.073 | 0.001443 | 0.00105 | 0.000838 | 1.98% | 0.0008574 | 0.0006666 | -0.0004901 | 1.17% |
| Flow rate | mL/min | 0.022 to 0.86 | 0.02565 | 0.01784 | 0.009657 | 3.06% | 0.02344 | 0.01778 | 0.004127 | 2.80% |
| Hydraulic aperture | µm | 1.2 to 2.1 | 0.05317 | 0.04424 | 0.01731 | 5.91% | 0.05298 | 0.04619 | 0.006158 | 5.89% |
| Fracture permeability | 10^-12 m² | 0.121 to 0.366 | 0.01378 | 0.01109 | 0.003823 | 5.62% | 0.01391 | 0.01172 | 0.0006533 | 5.68% |

The SW-S3 BB and MC results are close for pressure, effective normal stress,
shear stress, hydraulic aperture, and permeability. MC is more accurate for
shear displacement and slightly more accurate for flow, whereas BB provides a
substantially better normal-dilation match. This sample therefore gives the
most balanced model-to-model comparison.

### SW-S4

| Criterion | Unit | Table 2 range | BB RMSE | BB MAE | BB bias | BB nRMSE | MC RMSE | MC MAE | MC bias | MC nRMSE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Injection pressure | MPa | 8 to 28 | 0.05717 | 0.04801 | -0.0001144 | 0.29% | 0.05692 | 0.04764 | 0.00009129 | 0.28% |
| Effective normal stress | MPa | 15.31 to 30.75 | 0.5979 | 0.4264 | 0.3804 | 3.87% | 0.6803 | 0.5483 | 0.5022 | 4.41% |
| Shear stress | MPa | 2.27 to 12.56 | 1.04 | 0.7314 | 0.6627 | 10.10% | 1.174 | 0.9426 | 0.8739 | 11.41% |
| Normal dilation | mm | -0.041 to 0 | 0.001811 | 0.001034 | -0.000004908 | 4.42% | 0.002615 | 0.002212 | 0.001535 | 6.38% |
| Shear displacement | mm | 0 to 0.079 | 0.005335 | 0.003779 | 0.001297 | 6.75% | 0.004665 | 0.002698 | -0.001061 | 5.91% |
| Flow rate | mL/min | 0.005 to 0.113 | 0.005406 | 0.002632 | -0.001388 | 5.01% | 0.006811 | 0.002985 | -0.00251 | 6.31% |
| Hydraulic aperture | µm | 0.74 to 1.07 | 0.02363 | 0.01704 | -0.0005665 | 7.16% | 0.02594 | 0.01541 | -0.008395 | 7.86% |
| Fracture permeability | 10^-12 m² | 0.046 to 0.095 | 0.003088 | 0.002235 | 0.0003715 | 6.30% | 0.003331 | 0.001938 | -0.000795 | 6.80% |

SW-S4 has the largest shear-stress nRMSE for both laws because the Table 2 shear
stress range is relatively small and the numerical curves are systematically
high. MC gives the lower shear-displacement error, but BB is lower for effective
normal stress, shear stress, normal dilation, flow rate, hydraulic aperture,
and permeability.

## Interpretation and limitations

- The results quantify agreement only at the eleven Table 2 hold stages; they do
  not measure agreement over every transient point in the full time histories.
- Range normalization makes comparisons dimensionless, but a narrow Table 2
  range can produce a noticeable nRMSE from a small absolute error.
- Bias must be interpreted with each channel's sign convention. In particular,
  normal dilation is negative under the paper-frame convention used here.
- Hydraulic aperture and permeability follow the flow-rate calculation and are
  useful consistency checks, not independent evidence of model accuracy.
- Model selection should therefore emphasize the five independent response
  channels rather than averaging all eight quantities as though they were
  statistically independent.

## Reproducibility

The numerical stages and Table 2 values were read through the repository's
authoritative `scripts/table2_gate.py` workflow using `datum="stage1"`,
`preload_time=55.0`, `tol_mpa=0.15`, and the kinematic normal-displacement
channel. Both selected runs reached all 11/11 stages for every sample.

The corresponding standalone plotting scripts are:

- `figure_3b_table2_mechanical.py`
- `figure_3c_table2_hydraulic.py`

Report generated from the selected results on 2026-08-31.
