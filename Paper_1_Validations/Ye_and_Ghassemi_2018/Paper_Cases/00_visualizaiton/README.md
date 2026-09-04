# 00_visualizaiton — figures, decks and scripts behind the manuscript

Everything the submitted paper and its supporting information display, together
with the input decks that produced the underlying results and the scripts that
drew each panel. Nothing here is a working copy. The decks are byte-identical to
the archived originals under `01_Main_Validation`, `02_Mechanism_Tests`,
`04_Protocol_Consistency_116_Under_Review` and `Examples/Validaitons/benchmarks`.

```
figures/main/               six image files, the five main-paper figures
figures/si/                 seven image files, the seven SI figures
inputs/mesh/                one copy of every mesh
inputs/used_in_paper/       decks a manuscript figure or table depends on
inputs/not_used_in_paper/   decks run and archived but not shown
scripts/                    the plotting and analysis scripts
```

Every campaign deck now lives here and nowhere else. The former campaign
folders keep their outputs and submit scripts and carry a `DECKS_MOVED.md`
pointer. Each deck folder has a `mesh` symlink into `inputs/mesh`, so decks
resolve their mesh from their new location. All 60 decks that declare
`mesh_file` were verified to resolve, and the submit scripts were repointed
and dry-run against the new layout.

## What is not used by the manuscript

| Folder | Decks | Why it is kept |
|---|---:|---|
| `03_extended_depressurization_115` | 4 | extended-unloading probe, no figure depends on it |
| `05_additional_sensitivity_112_114` | 16 | time-step, viscosity, dilation and gouge sensitivity |
| `06_loading_stiffness_sweep_130` | 7 | in progress, intended for the frame-compliance section |

## Main paper

| Fig | File | Produced from | Script |
|---|---|---|---|
| 1 | `Figure_1_Machine_Sketch.pdf` | drawn after Ye and Ghassemi (2018) | — |
| 2 | `Figure_Table2_Combined_All_Specimens.pdf` | `inputs/01_main_validation` (8 decks) | `figure_3d_table2_combined.py` |
| 3 | `Figure_Strength_Paths.pdf` | `inputs/01_main_validation` (8 decks) | `make_strength_path_figure.py` wrapping `plot_ye2018_table2_strength_paths.py` |
| 4 | `Figure_Hydraulic_Aperture_Budget.pdf` | the four BB decks in `inputs/01_main_validation` | `build_hydraulic_aperture_budget.py` |
| 5 | `Figure_Followup_110_111_Mechanism_Tests.pdf` and `Figure_SWS4_Hydraulic_Sensitivity.pdf` | `inputs/02_mechanism_tests` | `analyze_followup_110_111.py`, `analyze_sws4_sensitivity.py` |

Figure 5 is a single display item that stacks the two image files.

## Supporting information

| Fig | File | Produced from | Script |
|---|---|---|---|
| S1 | `SI_bench_sneddon.png` | `inputs/05_benchmarks/sneddon` | benchmark `*_analytical.py` |
| S2 | `SI_bench_shear.png` | `inputs/05_benchmarks/shear_compression` | benchmark `*_analytical.py` |
| S3 | `SI_bench_intersection.png` | `inputs/05_benchmarks/fracutre_interseciton_problem` | benchmark `*_analytical.py` |
| S4 | `SI_bench_fault.png` | `inputs/05_benchmarks/Induced_stress_along_a_fault_mesh` | benchmark `*_analytical.py` |
| S5 | `SI_bench_chi.png` | `inputs/05_benchmarks/effective_stress_coefficient` | benchmark `chi_analytical.py` |
| S6 | `Figure_SWS4_Fields.pdf` | SW-S4 BB Exodus output | `make_field_figures.py` |
| S7 | `Figure_Hydraulic_Response.pdf` | the four BB decks in `inputs/01_main_validation` | `figure_4_hydraulic_response.py` |

## Tables

Table 1 (both blocks) draws on `inputs/01_main_validation` for the calibrated
comparison and `inputs/04_protocol_transfer` for the no-refit transfer.
Table S3 draws on `inputs/02_mechanism_tests`. Table S4 reports the benchmark
agreement computed from `inputs/05_benchmarks`. Table S5 lists parameters read
directly from the eight main-validation decks.

## Selected cases

The primary calibrated reconstruction uses these members, and every figure that
shows a model curve uses the same set.

| Specimen | Barton-Bandis | Mohr-Coulomb member |
|---|---|---|
| SW-T1 | `107_01_swt1_coh27p2_apscale0p01512_ppfix` | `pb04` |
| SW-T2 | `100_04_swt2_apscale0p0177_ppfix` | `pb04` |
| SW-S3 | `100_06_sw3_resc1p30_unld0p00_ppfix` | `pb06` |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix` | `center` |

The renamed `<SPEC>_Orca*` decks in `inputs/01_main_validation` are those cases
with output controls changed so that Exodus states are written at the pressure
stages. The physics is unchanged.

## Caveat on the field figure

`Figure_SWS4_Fields.pdf` plots pore pressure and axial displacement only. The
in-plane displacement components in the current Exodus output are not physical,
reaching a uniform radial scaling of several percent of the specimen radius and
2700 percent for SW-S3, while the CSV postprocessors from the same runs give
about 0.02 mm and the stresses remain at the confining level. The solution is
correct and the defect is confined to the written displacement field, so no
scored result is affected. `make_field_figures.py` prints this check on every
run and refuses to plot those components until it passes.
