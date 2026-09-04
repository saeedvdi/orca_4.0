# SW-S4 JRC revalidation audit

## Purpose

This audit asks whether the selected SW-S4 reconstruction can be supported using the JRC reported by Ye and Ghassemi (2018), rather than relying only on the calibrated value of 5.0 used by case `93_07_sw4_final_theta30_jrc5_ppfix`.

## Experimental provenance

Ye and Ghassemi (2018) did not determine JRC from a direct shear-strength inversion. They scanned both fracture surfaces with a three-dimensional laser system, reduced the surfaces to two-dimensional profiles using a 0.5 mm sampling span, calculated the root-mean-square slope parameter \(Z_2\), converted each profile using

\[
\mathrm{JRC}=61.79Z_2-3.47,
\]

and averaged the profile values from both surfaces. The reported SW-S4 mean is 1.19. Figure 3d places the SW-S4 profile distribution approximately between 0 and 2.5. A value of 5.0 is therefore outside the measured profile distribution and cannot be presented as a second roughness measurement.

## Reusable reported-JRC simulation

The older campaign contains a completed full-cycle case that was not included in the organized paper cases:

- Input: `89_01_sw4_bbfast_theta30_paperjrc_kernel_SV_biot0p6.i`
- Result: `89_01_sw4_bbfast_theta30_paperjrc_kernel_SV_biot0p6_hpc.csv`
- JRC: 1.19
- JCS: 150 MPa
- basic friction angle: 23.709 degrees
- slip-weakening tail angle: 6.50 degrees
- weakening exponent: 1.10
- characteristic slip distance: 74.5 micrometres
- complete simulation time: 3500 s
- Table 2 stages reached: 11 of 11

The basic friction angle was obtained by anchoring the Barton--Bandis envelope to the last pre-slip Table 2 state, \(\sigma'_n=26.51\) MPa and \(\tau=12.14\) MPa. It is therefore a calibrated strength parameter. The case uses the same fitted loading-system controls as the JRC 5 family. It is a reported-JRC constrained reconstruction, not an independent validation.

## Full-cycle comparison

All values below were recomputed with the authoritative `table2_gate.py` workflow, using the global kinematic normal jump, the stage-1 displacement datum, and all eleven Table 2 stages.

| Case | JRC | Flow nRMSE | Effective normal stress nRMSE | Shear stress nRMSE | Normal displacement nRMSE | Shear displacement nRMSE | Five-channel mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| `89_01`, reported-property reconstruction | 1.19 | 11.09% | 2.58% | 6.21% | 13.89% | 17.29% | 10.21% |
| `90_07`, peak-anchored bracket | 9.00 | 5.27% | 4.11% | 10.69% | 4.39% | 6.34% | 6.16% |
| `90_08` / `93_07`, selected calibrated reconstruction | 5.00 | 5.01% | 3.87% | 10.10% | 4.63% | 7.08% | 6.14% |
| `116_07`, reported JRC with common corrected protocol | 1.19 | 13.07% | 4.38% | 11.06% | 36.59% | 68.89% | 26.80% |
| `117_06`, best full-cycle weakening recalibration under the common protocol | 1.19 | 19.38% | 9.62% | 25.02% | 18.62% | 34.27% | 21.38% |

The identity of `90_08` and `93_07` in the scored response confirms that the `ppfix` changes do not alter the simulated mechanics or hydraulics used in this comparison.

## Peak and final values for the reported-JRC case

| Quantity | Experiment at peak | `89_01` at peak | Experiment at final stage | `89_01` at final stage |
|---|---:|---:|---:|---:|
| Flow rate (mL/min) | 0.113 | 0.07884 | 0.005 | 0.00413 |
| Effective normal stress (MPa) | 15.31 | 15.08 | 24.81 | 24.60 |
| Shear stress (MPa) | 3.12 | 3.79 | 2.27 | 1.75 |
| Normal displacement (mm) | -0.041 | -0.04518 | -0.032 | -0.03359 |
| Shear displacement (mm) | 0.075 | 0.08632 | 0.079 | 0.08646 |
| Permeability (\(10^{-12}\) m\(^2\)) | 0.095 | 0.09027 | 0.046 | 0.04908 |

The reported-JRC case reproduces the peak and final effective normal stress, normal displacement, and permeability reasonably well. It overpredicts accumulated slip by approximately 0.0075 mm at the final stage and underpredicts final shear stress by approximately 0.52 MPa. Its 0.001 mm slip threshold occurs at 14.30 MPa injection pressure, whereas the experiment begins gradual slip above approximately 16 MPa.

## Meaning of JRC = 5 in the selected case

The selected value of 5.0 was generated during a peak-envelope reparameterization. When JCS was corrected from 300 to 150 MPa, JRC and the basic friction angle were changed together so that the peak envelope remained close to a prescribed strength anchor. In `93_07`,

\[
\phi_p=22.72^\circ+5.0\log_{10}\left(\frac{150}{\sigma'_n}\right).
\]

In the reported-JRC case,

\[
\phi_p=23.709^\circ+1.19\log_{10}\left(\frac{150}{\sigma'_n}\right).
\]

Across the SW-S4 experimental stress range, the JRC 5 parameterization is approximately 0.93 to 1.07 MPa stronger in peak shear resistance than the reported-JRC parameterization. The resulting improvement is therefore a combined strength-envelope calibration. It is not independent evidence that the physical JRC equals 5.

## Revalidation verdict

Case `89_01` provides a defensible reported-JRC reconstruction using already completed results. It is substantially better than the common-protocol 116/117 measured-JRC cases and is accurate enough to demonstrate that the Barton--Bandis implementation can reproduce the principal SW-S4 response without changing the measured JRC. It does not match the selected calibrated reconstruction as closely.

The recommended manuscript treatment is to retain `93_07` as the best calibrated reconstruction and add `89_01` as a reported-property robustness case. JRC = 5 should be denoted \(\mathrm{JRC}_{\mathrm{eff}}\) and described as an effective strength-envelope coefficient. The value must not be presented as a measured surface property. If complete consistency of measured JRC across all four primary cases is prioritized over the lowest numerical error, `89_01` is the existing case that should replace `93_07`. That replacement would require recalculating the paper tables and figures and separating the existing `93_07`-based mechanism tests from the primary validation set.

