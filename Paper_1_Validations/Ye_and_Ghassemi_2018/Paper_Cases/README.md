# Ye and Ghassemi (2018) publication-case archive

This directory is the canonical archive for the simulations used in the paper. The older sample-level `Sweeps`, `proposed_inputs`, and HPC-download directories are development archives and are not used by the final analysis scripts.

## Case families

| Folder | Purpose | Available outputs | Publication status |
|---|---|---|---|
| `01_Main_Validation` | Selected calibrated BB and MC reconstructions for SW-T1, SW-T2, SW-S3, and SW-S4 | Eight CSV files; BB Exodus files for SW-S3 and SW-S4 at the time of this audit | Primary results. The user is independently rerunning these cases to recover the remaining Exodus files. |
| `02_Mechanism_Tests` | Hydraulic and kinematic ablations, cases 109--111 | Ten complete CSV files | Supporting-mechanism evidence. No Exodus files were present in the final HPC download. |
| `03_Extended_Depressurization_115` | Post-slip pressure reduction | SW-S4 (`115_04`) complete; SW-T1, SW-T2, and SW-S3 stopped during initialization | Only SW-S4 may be interpreted. The three incomplete files are isolated under `incomplete_results_do_not_use`. |
| `04_Protocol_Consistency_116_Under_Review` | No-refit transfer to fixed actuator command and common finite system stiffness | Eleven CSV files and eleven Exodus files | Ten cases reach all eleven stages. SW-S3 MC reaches 9/11 stages and is retained only as an explicitly partial record. |
| `05_Additional_Sensitivity_112_114_Under_Review` | Time-step, regularization, identifiability, and protocol-recalibration checks | `112_01`, `112_02`, `113_01`--`113_05`, and `117_01`--`117_06` complete | Supporting sensitivity evidence. `113_06` and both 114 cases were not present in the final download and are not claimed. |
| `06_Loading_Stiffness_Sweep_130` | Planned system-stiffness sweep | Input files only | Not used in the paper because no completed outputs are available and no additional simulations are requested. |

## Canonical analysis commands

These commands read existing files only; they do not run ORCA.

```bash
python3 Paper_Cases/01_Main_Validation/analysis/figure_3b_table2_mechanical.py
python3 Paper_Cases/01_Main_Validation/analysis/figure_3c_table2_hydraulic.py
python3 Paper_Cases/01_Main_Validation/analysis/figure_3d_table2_combined.py
python3 Paper_Cases/01_Main_Validation/analysis/figure_4_hydraulic_response.py
python3 Paper_Cases/01_Main_Validation/analysis/build_hydraulic_aperture_budget.py
pvpython Paper_Cases/01_Main_Validation/analysis/render_sws4_fields.py
python3 Paper_Cases/02_Mechanism_Tests/analysis/analyze_followup_110_111.py
python3 Paper_Cases/02_Mechanism_Tests/SWS4_109/analysis/analyze_sws4_sensitivity.py
python3 Paper_Cases/04_Protocol_Consistency_116_Under_Review/analysis/analyze_protocol_consistency_116.py
python3 Paper_Cases/05_Additional_Sensitivity_112_114_Under_Review/analysis/analyze_available_sensitivity.py
python3 Paper_Cases/05_Additional_Sensitivity_112_114_Under_Review/SWS4_117_Protocol_Recalibration/analysis/score_sws4_recal_wave1.py --output Paper_Cases/05_Additional_Sensitivity_112_114_Under_Review/SWS4_117_Protocol_Recalibration/analysis/results/recalibration_117_ranking.csv
```

Run the commands from the `Ye_and_Ghassemi_2018` directory. Generated figures and derived CSV tables are written below the corresponding `analysis/figures` and `analysis/results` directories.

The first five primary-validation scripts read the selected-case ranking and the eight result CSV files from `01_Main_Validation`; they no longer depend on an older sweep copy of the ranking. The field renderer requires ParaView's `pvpython` and reads the selected SW-S4 BB Exodus file already stored with that case. None of these commands launches an ORCA simulation.

## Interpretation rules

1. The selected main cases are calibrated reconstructions, not blind forward predictions.
2. The 116 series is a no-refit protocol-transfer test and must be reported separately from the calibrated errors.
3. The incomplete SW-S3 MC protocol case must not be assigned an aggregate five-channel nRMSE.
4. The SW-S4 115 result supports only a specimen-specific elastic-closure statement: reducing injection pressure after slip decreased permeability by 4.74% while plastic slip, dilation, and gouge-loss state remained unchanged.
5. Missing 113, 114, 115, and 130 outputs are recorded as unavailable; they are not grounds for additional reruns in the final paper.
