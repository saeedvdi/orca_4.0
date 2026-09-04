# Data Set S1 manifest

This directory is the canonical numerical archive supporting the Ye and Ghassemi (2018) validation and the associated manuscript figures and tables.

## Included evidence

| Case family | Included result files | Interpretation |
|---|---:|---|
| Primary validation | 8 selected model CSV files; currently 2 selected solution Exodus files | Calibrated BB and MC reconstructions for four specimens. |
| Mechanism tests 109--111 | 10 complete CSV files | Counterfactual tests; no recalibration. |
| Extended depressurization 115 | 1 complete CSV file | SW-S4 only; reversible elastic-closure diagnostic. |
| Protocol transfer 116 | 11 CSV and 11 Exodus files | Ten complete cases and one explicitly partial SW-S3 MC case. |
| Available sensitivities 112--114 and 117 | 13 complete CSV and 1 Exodus files | Supporting robustness and identifiability tests; missing cases are not claimed. |
| Loading-stiffness sweep 130 | Inputs only | Not used in the manuscript. |

Experimental digitizations, meshes, selected input files, Python analysis scripts, derived CSV tables, and publication figures are stored with the relevant case family. CSV counts elsewhere in the directory include experimental digitizations and derived tables and should not be interpreted as additional simulation runs.

## Exclusions and limitations

- The early-failed SW-T1, SW-T2, and SW-S3 extended-depressurization CSV files are retained only under `03_Extended_Depressurization_115/incomplete_results_do_not_use`.
- The SW-S3 MC protocol-transfer CSV and Exodus files stop after 9 of 11 stages. No aggregate five-channel error is assigned to this case.
- Results for `113_06`, `114_01`, `114_02`, and the 130 series were not available in the final HPC download and are not used.
- Older sweeps and raw download directories outside `Paper_Cases` are development records, not alternative publication sources.

## Reproducibility entry point

Run the commands listed in `README.md` from the parent `Ye_and_Ghassemi_2018` directory. These commands analyze existing results and do not launch ORCA simulations. Generated tables and figures are written to the corresponding `analysis/results` and `analysis/figures` folders.

Before depositing Data Set S1, generate a recursive checksum list after the independent primary-case Exodus reruns have been added. This freezes the exact submitted archive without changing the manuscript results.
