# Kalantar et al. (2025) final audit — 2026-08-28

> **SUPERSEDED FOR OG-T, 2026-08-31.** This audit lists `110_08_og_t_bbfast_r4` as OG-T's
> baseline at 17/17 with a "physically invalid preload". That is now measured: the run
> delivers **0.520** of the effective normal stress its joint is due and yields at
> σ_d = 64.9 MPa against the experiment's 160.43 MPa. **The OG-T rows below are not
> calibration data** — no OG-T constant has been fitted against a specimen that survived its
> own preload. OG-SH and OG-SC are unaffected (0.999 and 0.930). See
> `Doc/Memory/KALANTAR2025_ROUND3_BACKANALYSIS.md` §11 and round 11.


Branch: `orca_v10`

## Conclusion

The Kalantar study does **not** show the common excessive effective-normal-stress
rebound seen in the original Ye plots. The Kalantar gate and notebook already select
`effective_normal_paper_frame_mpa_pp`, which is the correct apparatus-frame observable.
From the peak-pressure hold to the final unloading hold, model minus measured rebound is
**+0.151 MPa for OG-SH, -3.675 MPa for OG-T, and -0.787 MPa for OG-SC**. Only OG-SH
slightly overpredicts rebound; OG-T and OG-SC underpredict it.

No effective-normal-stress source-code defect is demonstrated. No source file was changed,
no regression test is justified, and no simulation needs to be rerun for a reporting fix.
The remaining mismatches are specimen-specific loading/contact/model-form issues. OG-T is
not a valid constitutive calibration case because it undergoes the already-documented
pre-injection runaway.

This directory is not yet a finalized BBFast/MC comparison. Round 9 is diagnostic, one
Round 9 arm is incomplete, one submitted arm has no CSV, and no 111-series MC cases exist.

## Authoritative current manifest

Latest complete full-cycle baselines used for the rebound audit:

| specimen | current complete baseline | stages | result state |
|---|---|---:|---|
| OG-SH | `110_13_og_sh_bbfast_r6` | 9/9 | complete, 3600/3600 s |
| OG-T | `110_08_og_t_bbfast_r4` | 17/17 | complete, 6800/6800 s; physically invalid preload |
| OG-SC | `110_15_og_sc_bbfast_r6` | 13/13 | complete, 9100/9100 s |

Round 9 diagnostic manifest, now explicit in the notebook:

| arm | designed horizon | reached | gate result |
|---|---:|---:|---|
| OG-T `110_23_og_t_graded_preload_r8` | 60 s | **CSV missing** | not interpreted |
| OG-SC `110_24_og_sc_papermean_r9` | 4900 s / stage 7 | 4900 s, 7 holds | 4/5 gates; no promotion |
| OG-SH `110_25_og_sh_rsf_a010_b000_r9` | 2000 s / stage 5 | 2000 s, 5 holds | 1/3 gates; no promotion |
| OG-SH `110_26_og_sh_rsf_a010_b006_r9` | 2000 s / stage 5 | 408.189 s, 1 hold | incomplete; inconclusive |

The Round 9 launcher, decks, notebook manifest, and `MEMORY.md` change log agree on these
four arms after this audit.

## Artifact and path audit

Checked artifacts:

- `Kalantar2025_table2_validation.ipynb`: sole validation/comparison notebook; updated with
  all Round 9 arms, an explicit missing/incomplete-results table, preregistered Round 9 gate
  evaluation, and the rebound table below. It executes with zero cell errors.
- Validation data: `validation/kalantar2025_table2.csv` (39 holds: 9/17/13) and
  `validation/kalantar2025_figure8_pedrosa_fits.csv` both exist and load.
- Documentation: `MEMORY.md`, five files under `Doc/Memory/`, and the reading notes under
  `Doc/`. Stale `doc/KALANTAR...` links in `MEMORY.md`, the notebook, and the deck builder
  were corrected to `Doc/Memory/...`. Historical generated-deck comments still contain
  the old lowercase documentary paths; these do not affect execution.
- Builders/auditors: `kalantar_parameter_audit.py`, `kalantar_gate.py`,
  `build_110_kalantar_decks.py`, `build_110_kalantar_round8_decks.py`, and
  `build_110_kalantar_round9_decks.py` compile successfully. The parameter audit executes
  successfully and reproduces the paper-frame identities.
- Input decks: all **30** `110_*.i` files were inspected. Every deck has exactly one mesh
  reference, and all 30 referenced mesh paths exist. The five unique referenced meshes are
  the OG-SH 29-degree size-3, OG-SC 30-degree size-3, and OG-T 26-degree size-3,
  28-degree size-3, and 28-degree graded meshes.
- HPC scripts: all **22** shell scripts pass `bash -n`. All 30 concrete deck targets resolved
  from individual and array launchers exist. The current three baselines and four Round 9
  decks pass `orca-opt --check-input` with `Syntax OK`.
- CSV results: all **25** files under `*/results_csv_hpc/` have finite numeric values, no
  duplicate timestamps, monotonic time, and all eleven required audit channels:
  `time`, injection/outlet pressure, paper-frame normal/shear stress, validation flow,
  hydraulic aperture, reported shear slip, local BB normal stress, reaction differential
  stress, and paper-frame normal displacement. The two-row local `results_csv_probe`
  smoke-test file is finite but is not a scored result.

Local input checking repeatedly prints `JIT compile failed`/linker diagnostics before
returning `Syntax OK` with exit status zero. This is a local JIT/toolchain warning, not an
input-deck syntax failure; the study memory already warns about incompatible downloaded
JIT caches.

### Result completeness

| specimen | case(s) | state |
|---|---|---|
| OG-SH | `110_01`, `110_02`, `110_07`, `110_10`, `110_13` | complete full cycles, 9/9 holds |
| OG-SH | `110_17` | failed at t=0, 0/9 holds |
| OG-SH | `110_21`, `110_22`, `110_25` | complete stage-5 diagnostics, 5 holds |
| OG-SH | `110_26` | incomplete, 408.189/2000 s, 1/5 designed holds |
| OG-T | `110_03` | truncated, 2620.24/6800 s, 6/17 holds |
| OG-T | `110_04` | truncated, 34.21/6800 s, 0/17 holds |
| OG-T | `110_08` | complete, 17/17 holds |
| OG-T | `110_11` | truncated, 4015.39/6800 s, 10/17 holds |
| OG-T | `110_14`, `110_16` | complete 60 s preload diagnostics |
| OG-T | `110_23` | input exists; result CSV missing |
| OG-SC | `110_05` | truncated, 7284.28/9100 s, 10/13 holds |
| OG-SC | `110_06`, `110_09`, `110_12`, `110_15` | complete full cycles, 13/13 holds |
| OG-SC | `110_18` | failed at 72.76/4900 s, 0/13 holds |
| OG-SC | `110_19`, `110_20`, `110_24` | complete stage-7 diagnostics, 7 holds |

Completion and missing-file logic is restricted to entries explicitly present in the
notebook's `RUNS = {...}` dictionary. `LOADED` contains only complete full cycles; `SHOWN`
contains only listed cases with a CSV. A bounded diagnostic can be complete at its own
`end_time` without entering the full-cycle scorecard. Both the notebook and direct gate stop
at the last reached hold and do not recycle a truncated run's final row into missing stages.

### Repository packaging issue

Only 9 of the 25 HPC CSVs are tracked by Git. The other **16 result CSVs (Rounds 5-9 and
several probes) are present locally but ignored by `*.csv`**. The notebook references them,
so a fresh clone cannot reproduce the executed notebook. This is the main required
repository correction: explicitly force-add the selected/current result assets, or document
and provide an external immutable results package. This audit did not stage, move, rewrite,
or regenerate them.

## Effective-normal-stress definition

The paper and the selected postprocessor use the same transformation:

```text
Pp = (Pi + Po)/2
sigma_n' = 33 MPa - Pp + sin(theta)^2 * (sigma_1 - sigma_3)_reaction
tau      =                    sin(theta) cos(theta) * (sigma_1 - sigma_3)_reaction
```

The postprocessor coefficients are `sin²(29°)=0.2350403679` for OG-SH,
`sin²(28°)=0.2204035483` for the physical OG-T plane, and `sin²(30°)=0.25` for
OG-SC. The 33 MPa total confining stress is correct; the paper's 30 MPa statement is
effective confining stress at 3 MPa pore pressure. Mean inlet/outlet pressure is subtracted
once. There is no wrong sign, wrong reference pressure, duplicated pore-pressure term, or
total/skeleton/bulk-frame substitution in the scored observable.

The decks apply pressure traction mechanically with `fault_pressure_coefficient=1.0` and
set `pore_pressure_strength_coefficient=0.0`; this prevents pressure from being subtracted
again inside the strength calculation. Biot coupling (`biot_coefficient=0.6`) affects the
poroelastic solution, not the algebraic paper-frame subtraction above.

`bb_effective_normal_stress_pp` is the local contact/strength diagnostic. It is useful for
checking the constitutive state but is not the apparatus-frame Table 2 observable. Plotting it
as Table 2 stress would make OG-SC appear to over-rebound by 2.855 MPa even though the correct
paper-frame channel under-rebounds by 0.787 MPa.

## Stage-by-stage unloading audit

Errors are model paper-frame minus measured. OG-T measurements are consistently re-reduced
onto its physical 28-degree plane, as done by `kalantar_gate.py`; this is why they differ
slightly from the paper's printed 26-degree stress columns.

| specimen | stage | Pi MPa | measured MPa | paper-frame model MPa | error MPa | local BB MPa |
|---|---:|---:|---:|---:|---:|---:|
| OG-SH | 5 peak | 18 | 33.348 | 34.638 | +1.290 | 34.717 |
| OG-SH | 6 | 15 | 34.632 | 36.110 | +1.478 | 36.219 |
| OG-SH | 7 | 12 | 36.093 | 37.566 | +1.473 | 37.690 |
| OG-SH | 8 | 9 | 37.549 | 39.014 | +1.465 | 39.144 |
| OG-SH | 9 | 6 | 39.015 | 40.456 | +1.441 | 40.586 |
| OG-T | 9 peak | 30 | 28.091 | 21.423 | -6.668 | 16.274 |
| OG-T | 10 | 27 | 28.892 | 21.033 | -7.859 | 20.478 |
| OG-T | 11 | 24 | 30.369 | 21.687 | -8.682 | 22.150 |
| OG-T | 12 | 21 | 31.864 | 22.810 | -9.054 | 23.035 |
| OG-T | 13 | 18 | 33.364 | 23.984 | -9.380 | 23.836 |
| OG-T | 14 | 15 | 34.864 | 25.198 | -9.666 | 24.575 |
| OG-T | 15 | 12 | 36.364 | 26.443 | -9.921 | 25.267 |
| OG-T | 16 | 9 | 37.858 | 27.716 | -10.142 | 25.920 |
| OG-T | 17 | 6 | 39.353 | 29.010 | -10.343 | 26.539 |
| OG-SC | 7 peak | 24 | 25.118 | 24.202 | -0.916 | 20.327 |
| OG-SC | 8 | 21 | 26.595 | 25.612 | -0.983 | 22.125 |
| OG-SC | 9 | 18 | 28.037 | 27.017 | -1.020 | 24.023 |
| OG-SC | 10 | 15 | 29.485 | 28.421 | -1.064 | 26.004 |
| OG-SC | 11 | 12 | 30.944 | 29.822 | -1.122 | 28.036 |
| OG-SC | 12 | 9 | 32.404 | 31.222 | -1.182 | 30.059 |
| OG-SC | 13 | 6 | 33.869 | 32.166 | -1.703 | 31.933 |

### Rebound decomposition

| specimen | measured rebound MPa | model rebound MPa | model - measured MPa | pore-pressure contribution MPa | reaction contribution MPa | normal-displacement recovery mm |
|---|---:|---:|---:|---:|---:|---:|
| OG-SH | 5.667 | 5.818 | +0.151 | +6.000 | -0.182 | ~0.000 |
| OG-T | 11.262 | 7.587 | -3.675 | +12.000 | -4.413 | +0.161 |
| OG-SC | 8.751 | 7.964 | -0.787 | +9.000 | -1.036 | +0.005 |

The positive pore-pressure term is exactly the drop in mean pore pressure during unloading.
Reaction-stress relaxation offsets it in all three cases. The offset grows with the observed
normal-displacement recovery (negligible OG-SH, 0.005 mm OG-SC, 0.161 mm OG-T), which is a
physical loading/contact response, not a duplicated pressure contribution.

The three inherited unloading-retention fractions are very different (OG-SH 0.84, OG-T
0.94, OG-SC 0.06), yet they do not produce a common over-rebound: the correct channel is
slightly high for OG-SH and low for the other two. Retention can influence local closure and
the solved reaction, but the evidence does not support a universal retention-parameter bug.

## Source-code disposition

The Barton-Bandis source owns the local constitutive/contact state, including
`normal_unload_retention_fraction`; the deck postprocessor owns the paper-frame observable.
The two quantities intentionally differ. The stage identities, sign, pressure reference,
and source/postprocessor separation all check out.

Classification: **no reporting-channel problem in the active Kalantar notebook, no confirmed
source bug, and no common parameter-driven excessive rebound**. OG-SH's small rebound excess
is within a larger level offset; OG-SC's remaining under-rebound is a model/loading mismatch;
OG-T is dominated by its pre-injection loading/contact runaway. Further improvement requires
the already-planned specimen-specific loading/contact or constitutive-model development, not
an effective-stress code change.

## Changes made by this audit

- Updated and executed `Kalantar2025_table2_validation.ipynb` with Round 9 manifest, health,
  gate, and rebound sections.
- Corrected current documentation paths in the notebook, `MEMORY.md`, and deck-builder
  template.
- Corrected stale `MEMORY.md` claims that the direct gate lacked a completeness guard.
- Added this report.

No result, mesh, input deck, HPC launcher, or source/test file was moved, renamed, deleted,
regenerated, or overwritten.

## Post-audit next step: Round 10

After the audit, the unresolved Round-9 mechanism test was converted into a full-cycle
follow-up batch. OG-SH `110_27` and `110_28` bracket the incomplete `b=0.006` aging arm
at `rsf_b=0.002` and `0.004`; all other physics, loading, and solver controls are held
fixed while the horizon covers all nine stages to 3600 s. Graded OG-T `110_29` extends
the `110_23` preload probe through all 17 stages to 6800 s, retaining the graded mesh
and restoring the established full-cycle timestep/output settings. OG-SC is deliberately
omitted because its Round-9 arm failed the written promotion gate. The new CSV paths are
explicit diagnostic entries in the executed validation notebook and currently report
`PENDING CSV`.

Design evidence and pass criteria are recorded in
`Doc/Memory/KALANTAR2025_ROUND9_BACKANALYSIS.md`; the reproducible builder is
`scripts/build_110_kalantar_round10_decks.py`, and the launcher is
`submit_110_round10_array_hpc.sh`.
