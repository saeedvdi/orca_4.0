# Targeted simulations for strengthening the paper

This package contains the minimum additional simulation matrix recommended after the 109--111 mechanism tests. It contains 16 new runs: the original four batches of three plus four extended-depressurization diagnostics. Every run uses eight MPI ranks. Each input inherits a selected parent deck and changes only the axis stated in `case_manifest.tsv`.

## Scientific questions

### Numerical robustness (112 series)

- `112_01`: SW-T1 with `dtmax` reduced from 0.75 to 0.375 s.
- `112_02`: SW-T1 with tangential viscosity reduced from 4e11 to 2e11 Pa s/m.
- `112_03`: SW-S4 with `dtmax` reduced from 1.5 to 0.75 s.
- `112_04`: SW-S4 on the existing theta-30 nominal size-3 mesh instead of size 5.

The principal comparisons are against `111_01_swt1_floor1nm_control_ppfix` and `109_01_sw4_floor1nm_g028_ppfix`. The pre-registered acceptance target is less than 2% change in the peak and final hydraulic ratios for the time-step and viscosity tests, and less than 5% for the mesh test. Mechanical stage values and flow nRMSE must also remain within the experimental comparison tolerance.

### SW-S3 identifiability and loading-only selection (113 series)

The selected center is `110_01_sw3_floor1nm_g040_ppfix`:

- retained-dilation scale: 0.0304, 0.038, 0.0456;
- gouge-loss amplitude: 0.32, 0.40, 0.48 micrometres;
- hydraulic closure amplitude: 0.96, 1.20, 1.44 micrometres.

The six variants are a local one-at-a-time sensitivity study. They also define a pre-registered loading-only candidate set. Selection must use only stages 1--6 and the directly measured flow rate. After the best loading candidate is fixed, stages 7--11 are revealed and reported as the unloading prediction. If the best loading case lies at a bracket boundary, one additional confirmatory run beyond that boundary may be needed; this decision must be made without examining its unloading score.

### SW-T2 loading/unloading prediction (114 series)

The selected center is `111_03_swt2_floor1nm_control_ppfix`, with aperture scale 0.0177. The two new values are 0.01416 and 0.02124. The best of these three candidates is selected using only stages 1--6 flow nRMSE, then evaluated without adjustment on stages 7--11. This is a deliberately limited one-parameter tensile-fracture prediction test rather than a new full-cycle calibration.

### Extended post-slip depressurization (115 series)

The four 115-series decks retain every mechanical and hydraulic parameter from the selected controls:

- `115_01_swt1_extended_depressurization_ppfix`;
- `115_02_swt2_extended_depressurization_ppfix`;
- `115_03_sws3_extended_depressurization_ppfix`;
- `115_04_sws4_extended_depressurization_ppfix`.

After each original cycle, the final injection pressure is held and the inlet-to-outlet pressure difference is reduced to 50% and then 15% of its original final value. Each new pressure level includes a 200-s hold. Production pressure remains 5 MPa in every specimen, so the imposed flow direction does not reverse. The absolute inlet pressures are 8.00, 6.50, and 5.45 MPa for SW-T1 and SW-T2; 7.882927, 6.4414635, and 5.43243905 MPa for SW-S3; and 7.9704976, 6.4852488, and 5.4455746 MPa for SW-S4.

These runs test the claim discussed by Kalantar et al. (2025): post-slip permeability may decrease during depressurization because increasing effective normal compression elastically closes the fracture. Comparing the same normalized pressure path across the two tensile and two saw-cut specimens tests whether that sensitivity changes from rougher to smoother surfaces. The attribution is accepted only if cumulative plastic slip, cumulative dilation, and gouge aperture remain constant over the added path while effective normal compression increases and the normal-stress aperture contribution, total aperture, and permeability decrease. If slip or damage evolves, the change is a coupled reactivation response and cannot be assigned to elastic closure alone.

## Batch order

The local launchers are:

1. `run_compelling_batch_01_local.sh`: SW-T1 time step, SW-T1 viscosity, SW-S4 time step.
2. `run_compelling_batch_02_local.sh`: SW-S4 mesh, SW-S3 dilation -20%, SW-S3 dilation +20%.
3. `run_compelling_batch_03_local.sh`: SW-S3 gouge -20%, gouge +20%, closure -20%.
4. `run_compelling_batch_04_local.sh`: SW-S3 closure +20%, SW-T2 aperture scale -20%, aperture scale +20%.

5. `run_compelling_batch_05_local.sh`: extended-depressurization diagnostics for SW-T1, SW-T2, and SW-S3.
6. `run_compelling_batch_06_local.sh`: the SW-S4 extended-depressurization diagnostic.

Equivalent `submit_compelling_batch_XX_hpc.sh` launchers submit the individual Slurm scripts. Submit only one batch at a time if no more than three eight-core jobs should run concurrently. The size-3 mesh case is reserved for HPC and must not be launched locally on the workstation.

### One-command HPC submission of the remaining cases

`submit_all_remaining_hpc.sh` is the current recommended launcher. Submit it from the HPC copy of this package with:

```bash
sbatch submit_all_remaining_hpc.sh
```

It is a 14-task Slurm array with at most three simultaneous tasks (`--array=0-13%3`), and each task uses eight MPI ranks. It excludes `112_02_swt1_eta200gpa_s_ppfix` and `112_03_sw4_dt075_ppfix`, which completed locally. It includes the incomplete local runs, all previously unstarted 113--114 cases, the HPC-only size-3 mesh case, and all four 115-series elastic-closure tests. The tasks start from the beginning on HPC; partial workstation CSV and Exodus files are not restart files.

## Outputs

Each specimen writes to its own:

`proposed_inputs/paper_compelling_20260902/{csv,exodus,logs}`

The Exodus output is retained because it is required for the mesh comparison and the local-field audit. Checkpoint output is disabled in the launch scripts.

## Interpretation limits

- The 113 and 114 candidate sets are selected from loading data only. Unloading values must not be used to choose a candidate.
- The SW-S3 study is local and one-at-a-time; it is not a global uncertainty analysis.
- The viscosity test evaluates regularization sensitivity. It does not define viscosity as a measured material parameter.
- The mesh test changes spatial resolution while retaining all constitutive parameters. Any source-node or interface-area change must be checked from the mesh diagnostic postprocessors before comparing physics.
