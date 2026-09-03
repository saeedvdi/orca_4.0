# Ye and Ghassemi (2018) validation case archive

This directory is the authoritative paper-facing archive for the four Sierra White granite specimens used in the manuscript. It separates the cases that currently support reported paper results from diagnostic runs, unfinished runs, and calibration history.

## Specimen names

| Code | Fracture type | Role in the comparison |
|---|---|---|
| SW-T1 | Tensile fracture | Rough tensile-fracture validation |
| SW-T2 | Tensile fracture | Second rough tensile-fracture validation |
| SW-S3 | Saw-cut fracture | Rougher saw-cut validation |
| SW-S4 | Polished saw-cut fracture | Smoothest-fracture validation |

## Directory policy

- `Paper_Cases/01_Main_Validation` contains the eight BB and MC cases used for the numerical values and curves currently reported in the manuscript. Each model directory contains the exact run input, its result CSV, and, for MC, the array script that records the selected parameter override.
- `Paper_Cases/02_Mechanism_Tests` contains the 109, 110, and 111 counterfactual cases used in the mechanism tables and figures. These are not recalibrated validation cases.
- `Paper_Cases/03_Extended_Depressurization_115` contains the four planned elastic-closure tests. The available CSV files stopped at 7.5, 9.75, and 13.5 s rather than their required end times; they are quarantined as incomplete. No SW-S4 result was found.
- `Paper_Cases/04_Protocol_Consistency_116_Under_Review` contains the common-stiffness, corrected-protocol reruns. These cases do not yet support the values in the current manuscript. SW-S3 inputs exist, but its two results were not found in the copied or remaining example directories.
- `Paper_Cases/05_Additional_Sensitivity_112_114_Under_Review` contains parameter and time-step checks that are not directly reported in the current manuscript.
- `Discussion_Related_To_Validation_Paper_Exact` contains the paper figures and their analysis scripts.
- `Docs` contains the validation notes, audits, and the Table 2 stress-path figure source.
- The specimen-level `Sweeps` and result directories are retained as calibration and raw-output archives. They are not the paper-case index.

No Exodus or checkpoint files are duplicated in `Paper_Cases`. They remain in the specimen archives because they are large and are not required to reproduce the paper's tabulated stage values or line figures.

## Current paper-of-record cases

| Specimen | BB result | MC result | MC selection |
|---|---|---|---|
| SW-T1 | `107_01_swt1_coh27p2_apscale0p01512_ppfix.csv` | `SWT1_OrcaMohrCoulombContactTraction_pb04.csv` | array member `pb04` |
| SW-T2 | `100_04_swt2_apscale0p0177_ppfix_hpc.csv` | `SWT2_OrcaMohrCoulombContactTraction_pb04.csv` | array member `pb04` |
| SW-S3 | `100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv` | `SWS3_OrcaMohrCoulombContactTraction_pb06.csv` | array member `pb06` |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv` | `SWS4_OrcaMohrCoulombContactTraction_center.csv` | array member `center` |

The descriptive `Validation_Paper_Exact/*OrcaBartonBandisContactTractionFastADHardening.i` files have the same live model definition as the corresponding numbered BB run inputs. After comments and output paths are excluded, the only remaining difference is the Exodus output schedule. They can therefore document the model, but the numbered input is retained beside the CSV as the exact run provenance.

The selected MC CSVs are not all center runs. The `.sh` array files must stay with the MC input because they contain the `pb04` or `pb06` command-line overrides that produced the selected results.

## Important consistency warning

The current manuscript results and figures use the selected cases listed above. They must not be silently replaced by the 116 protocol-consistency results. Internal comments in the selected decks identify three protocol concerns that are relevant to the paper:

1. SW-T2 uses a compressed unloading schedule and does not provide the experimental equilibrium hold duration.
2. SW-S3 includes a fitted piston retreat during injection, although the reported experimental piston position was held fixed.
3. SW-S4 includes fitted piston motion and a small confining-pressure reduction, whereas the reported experiment used a fixed piston and 30 MPa confinement.

The 116 series was created to test these issues with a common system stiffness and corrected protocol. Once all eight BB/MC 116 runs are available and checked, either the paper must be updated to use them or the legacy deviations must be stated as calibrated boundary histories. Mixing numerical values from the two families would make the paper internally inconsistent.

## Audit

Run:

```bash
python3 audit_paper_cases.py
```

The audit checks required files, detects incomplete 115 results, and prints the status of the protocol-consistency set. It does not modify any files.

