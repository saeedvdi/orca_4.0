# YeGhasemmi2018 final audit — 2026-08-28

Branch: `orca_v10`

## Final case manifest

| Sample | Final BBFast | Final tuned Mohr–Coulomb |
|---|---|---|
| SWT1 | `107_01_swt1_coh27p2_apscale0p01512_ppfix` | `SWT1_OrcaMohrCoulombContactTraction_pb04` |
| SWT2 | `100_04_swt2_apscale0p0177_ppfix` | `SWT2_OrcaMohrCoulombContactTraction_pb04` |
| SWS3 | `100_06_sw3_resc1p30_unld0p00_ppfix` | `SWS3_OrcaMohrCoulombContactTraction_pb06` |
| SWS4 | `93_07_sw4_final_theta30_jrc5_ppfix` | `SWS4_OrcaMohrCoulombContactTraction_center` |

The manifest now agrees in the four sample-validation notebooks, the final
MC-versus-BBFast notebook, the AGU manuscript notebook/export script, and the
current documentation. The 94-series MC names retained in historical text are
center-deck provenance, not final selected results.

## Artifact audit

| Artifact | Audit result |
|---|---|
| Four sample validation notebooks | Corrected to exactly one final BBFast and one final MC case per `cases` dictionary; nonexistent `_hpc.i` paths corrected; executed with no errors. |
| `All_fracture_samples_mc_vs_bbfast_comparison.ipynb` | Executed with no errors; independently reproduced all four MC winners; all 36 sweep CSVs finite and 11/11-stage complete. |
| `All_fracture_samples_validation_comparison.ipynb` | Reorganization roots, final MC names, paper channels, Table-2 path, and stage-1 displacement datum corrected; executed in core-results mode with no cell error. Six byte-identical result copies generate duplicate-stem warnings; four non-time-series archive summaries remain outside the final manifest. |
| `Ye2018_best_cases_hydromechanical.ipynb` | Ranking-manifest and result/deck resolvers corrected after reorganization; executed with no errors. |
| `AGU_manuscript_figure_exports.ipynb` and exporter | Retired 94-series MC names and missing ranking path corrected; executed with no errors and generated all five PDFs in an isolated temporary output directory. |
| BBFast generic input decks | Constitutive content matches the selected original decks. Differences are provenance comments and output base/pressure-synchronized Exodus controls only. |
| MC generic input decks and four array scripts | Present; array rows reproduce the selected `pb04`, `pb04`, `pb06`, and `center` parameter sets. Shell syntax passes. |
| Final BBFast array launcher | Present, shell syntax passes, and references the four generic final decks. |
| `submit_106.sh` | Its pre-reorganization working directory was broken; corrected to each sample's `Sweeps` directory. |
| Selected BBFast result copies | The four `results_csv/` copies are byte-identical to their canonical `Sweeps/results_csv_*` sources. |
| Documentation and memory | Final manifest and tuned MC outcomes added; the previously empty Aug. 28 memory file now contains the independent rebound diagnosis. |

### Superseded notebook copies

The following are not final-case entry points and were not executed as part of
the final workflow:

- `Output_Image_Comparison/All_fracture_samples_results.ipynb` and
  `All_fracture_samples_validation_comparison (Copy).ipynb` are 241–249 MB
  archival copies. They retain the removed `doc/independent_analysis` path and
  pre-reorganization sample-root discovery.
- The four `*/Sweeps/Ye2018_*_num_vs_validation.ipynb` files are older sample
  notebook copies. SWT2 and SWS3 still contain 94-series MC selections, and all
  four retain the old local-contact plotting configuration.
- `SWS4/Sweeps/SW4_back_analysis_after_run.ipynb` is an exploratory back-analysis
  notebook, not a final validation or manuscript entry point.

These files should be treated as archives. If they are intended to remain
executable, they require the same path/channel migration as the active copies;
otherwise a future cleanup should label them explicitly as superseded. They
were not deleted or bulk-rewritten in this audit.

### Remaining historical-script caveat

A literal audit of 207 fixed `-i` references in all archived shell scripts found
139 old per-case launchers whose `#SBATCH --chdir` still points to the specimen
root although their decks now live in `Sweeps/`. They are historical campaign
launchers and are not used by the final BBFast or MC workflows. If they are ever
reactivated, change their working directory to `.../<sample>/Sweeps` (or prefix
the input with `Sweeps/`). They were not bulk-edited because doing so would
touch 139 retired scripts unrelated to the selected results.

The four CSVs skipped by the all-results time-history loader are intentionally
not simulation histories: `...SWT1..._table2.csv`, `sws3_final_ab.csv`,
`sws3_stage6_ab.csv`, and `84_01..._table2.csv`. Each lacks a `time` column;
none is named by a final-case dictionary.

## Selected CSV health

Required channels were `time`, `flow_rate_validation_ml_min_pp`,
`effective_normal_paper_frame_mpa_pp`, `shear_stress_paper_frame_mpa_pp`,
`frac_normal_dilation_paper_mm`, `czm_shear_slip_mm_pp`,
`injection_pressure_pp`, `pp_outlet_pp`, and
`differential_stress_reaction_mpa_pp`.

| Sample | Model | Rows | End / intended (s) | Missing required | Non-finite numeric | Stages |
|---|---|---:|---:|---:|---:|---:|
| SWT1 | BBFast | 2,140 | 3499.841 / 3500 | 0 | 0 | 11/11 |
| SWT1 | MC | 7,485 | 3500 / 3500 | 0 | 0 | 11/11 |
| SWT2 | BBFast | 3,805 | 2852.53 / 2852.53 | 0 | 0 | 11/11 |
| SWT2 | MC | 3,814 | 2852.53 / 2852.53 | 0 | 0 | 11/11 |
| SWS3 | BBFast | 6,404 | 4802 / 4802 | 0 | 0 | 11/11 |
| SWS3 | MC | 6,415 | 4802 / 4802 | 0 | 0 | 11/11 |
| SWS4 | BBFast | 2,335 | 3500 / 3500 | 0 | 0 | 11/11 |
| SWS4 | MC | 2,346 | 3500 / 3500 | 0 | 0 | 11/11 |

SWT1 MC contains two duplicated timestamp values (four rows involved). The
notebooks and authoritative scorer deterministically retain the last row at
each time. No selected result is stale relative to its selected input deck.

The authoritative five-channel mean nRMSE values are BBFast
`1.473, 2.132, 4.354, 6.139%` and MC `6.900, 3.780, 5.148, 7.000%` for SWT1,
SWT2, SWS3, and SWS4 respectively. Displacements use the global kinematic
normal jump and the stage-1 datum.

## Effective-normal-stress diagnosis

The apparent excessive rebound was a reporting-channel mismatch. The sample
notebooks plotted the internal `bb_effective_normal_stress_pp` contact-strength
diagnostic against the experimental paper-frame stress, while their scoring
cell correctly used `effective_normal_paper_frame_mpa_pp`. Main plots and local
Table-2 panels now use the paper-frame normal/shear channels, global kinematic
normal displacement, and the stage-1 displacement datum.

The correct compression-positive transformation is

\[
\sigma'_n = 30 - \frac{p_{in}+p_{out}}{2}·10^{-6}
            + \sin^2(\theta) q_{reaction}
          = 30-p_{mean}+\tan(\theta)\tau_{paper}.
\]

It is implemented as a parsed postprocessor in every selected input. Recomputing
it from the stored pressure and reaction channels agrees with the stored value
to numerical roundoff after initialization. The `t=0` parsed-postprocessor row
is zero-initialized by MOOSE and is not a Table-2 hold or scoring datum.

### All eleven stages

Values are `paper | BBFast (error) | MC (error)` in MPa.

#### SWT1

| Stage | Paper | BBFast | Error | MC | Error |
|---:|---:|---:|---:|---:|---:|
| 1 | 65.470 | 65.676 | +0.206 | 65.676 | +0.206 |
| 2 | 63.350 | 63.710 | +0.360 | 63.710 | +0.360 |
| 3 | 61.270 | 61.764 | +0.494 | 61.765 | +0.495 |
| 4 | 59.140 | 59.830 | +0.690 | 59.819 | +0.679 |
| 5 | 56.940 | 57.846 | +0.906 | 57.878 | +0.938 |
| 6 | 31.790 | 32.539 | +0.749 | 33.694 | +1.904 |
| 7 | 33.450 | 33.965 | +0.515 | 35.612 | +2.162 |
| 8 | 35.350 | 35.569 | +0.219 | 37.532 | +2.182 |
| 9 | 37.290 | 37.287 | -0.003 | 39.459 | +2.169 |
| 10 | 39.220 | 39.081 | -0.139 | 41.391 | +2.171 |
| 11 | 41.140 | 40.923 | -0.217 | 43.328 | +2.188 |

#### SWT2

| Stage | Paper | BBFast | Error | MC | Error |
|---:|---:|---:|---:|---:|---:|
| 1 | 66.740 | 66.144 | -0.596 | 66.144 | -0.596 |
| 2 | 64.530 | 64.193 | -0.337 | 64.193 | -0.337 |
| 3 | 62.370 | 62.246 | -0.124 | 62.246 | -0.124 |
| 4 | 60.190 | 60.306 | +0.116 | 60.303 | +0.113 |
| 5 | 57.880 | 58.229 | +0.349 | 58.361 | +0.481 |
| 6 | 29.360 | 30.200 | +0.840 | 31.006 | +1.646 |
| 7 | 31.260 | 31.956 | +0.696 | 32.942 | +1.682 |
| 8 | 33.230 | 33.780 | +0.550 | 34.876 | +1.646 |
| 9 | 35.230 | 35.643 | +0.413 | 36.812 | +1.582 |
| 10 | 37.180 | 37.532 | +0.352 | 38.751 | +1.571 |
| 11 | 39.140 | 39.438 | +0.298 | 40.669 | +1.529 |

#### SWS3

| Stage | Paper | BBFast | Error | MC | Error |
|---:|---:|---:|---:|---:|---:|
| 1 | 31.650 | 31.136 | -0.514 | 31.136 | -0.514 |
| 2 | 29.580 | 29.218 | -0.362 | 29.218 | -0.362 |
| 3 | 27.530 | 27.341 | -0.189 | 27.341 | -0.189 |
| 4 | 25.480 | 25.487 | +0.007 | 25.487 | +0.007 |
| 5 | 23.420 | 23.664 | +0.244 | 23.689 | +0.269 |
| 6 | 15.250 | 16.342 | +1.092 | 16.362 | +1.112 |
| 7 | 17.270 | 17.954 | +0.684 | 17.970 | +0.700 |
| 8 | 19.140 | 19.621 | +0.481 | 19.635 | +0.495 |
| 9 | 21.010 | 21.442 | +0.432 | 21.456 | +0.446 |
| 10 | 22.860 | 23.216 | +0.356 | 23.231 | +0.371 |
| 11 | 24.790 | 25.094 | +0.304 | 25.108 | +0.318 |

#### SWS4

| Stage | Paper | BBFast | Error | MC | Error |
|---:|---:|---:|---:|---:|---:|
| 1 | 30.750 | 30.595 | -0.155 | 30.594 | -0.156 |
| 2 | 28.730 | 28.632 | -0.098 | 28.632 | -0.098 |
| 3 | 26.510 | 26.624 | +0.114 | 26.624 | +0.114 |
| 4 | 22.920 | 24.489 | +1.569 | 24.432 | +1.512 |
| 5 | 19.250 | 19.804 | +0.554 | 19.699 | +0.449 |
| 6 | 15.310 | 16.048 | +0.738 | 16.270 | +0.960 |
| 7 | 17.130 | 17.679 | +0.549 | 17.920 | +0.790 |
| 8 | 19.000 | 19.388 | +0.388 | 19.640 | +0.640 |
| 9 | 20.890 | 21.160 | +0.270 | 21.419 | +0.529 |
| 10 | 22.820 | 23.029 | +0.209 | 23.293 | +0.473 |
| 11 | 24.810 | 24.855 | +0.045 | 25.120 | +0.310 |

### Rebound decomposition, stages 6 to 11

| Sample | Paper rebound | BBFast rebound | BB minus paper | Pressure contribution | Shear/reaction contribution | Normal-displacement recovery |
|---|---:|---:|---:|---:|---:|---:|
| SWT1 | 9.350 | 8.385 | -0.965 | +10.000 | -1.615 | +0.04401 mm |
| SWT2 | 9.780 | 9.238 | -0.542 | +10.000 | -0.762 | +0.01054 mm |
| SWS3 | 9.540 | 8.752 | -0.788 | +10.342 | -1.590 | +0.01083 mm |
| SWS4 | 9.500 | 8.807 | -0.693 | +9.997 | -1.190 | +0.01076 mm |

The correctly reported BBFast rebound is lower than the experiment in every
sample. It scales primarily with the approximately 10 MPa decrease in mean pore
pressure, not with normal-displacement recovery. The local BB strength channel,
by contrast, rebounds by 16.398, 15.261, 11.535, and 9.757 MPa; that is the
source of the visual impression in the old plots.

## Source-code assessment

`ADOrcaBartonBandisContactTractionFastAD.C` defines unloading retention at
lines 117–130, updates the retained closure at lines 668–706, and computes the
internal strength effective stress at lines 762–782. These equations act on
the local contact/strength state. They do not define the paper-frame
postprocessor.

The selected BBFast retention fractions are 0.94, 0.84, 0.00, and 0.04. Their
wide range does not produce excessive paper-frame rebound in all four samples.
`pore_pressure_strength_coefficient = 0` is intentional: pressure enters the
mechanical interface kernels, and a second material-level subtraction would
double count it. The paper-frame postprocessor then applies the experimental
mean-pressure correction once.

**Disposition:** reporting-channel problem. No source-code bug is demonstrated,
so no source change or source regression test was added. No simulations need
rerunning. Further improvement of local contact recovery or displacement would
be parameter/model-form work; improvement of the tuned MC unloading bias,
especially SWT1 and SWT2, is likewise calibration/model-form work.
