# The archived Mohr–Coulomb campaign, and the ceiling it puts on the baseline claim

2026-08-25. Branch `orca_v8`, repo `orca_4.0`.
Companion to `doc/MC_BASELINE_94_SERIES.md` (how the current baseline was built) and to
`doc/independent_analysis/Final_ye_ghaseemi_simulations.txt` §9–§12.

**Why this document exists.** The campaign's public claim is that a Barton–Bandis envelope
reduces mean Table-2 error by ~76 % relative to a Mohr–Coulomb baseline. That claim is only
as strong as the baseline. This document records what happens when the baseline is compared
against the *best Mohr–Coulomb result this project has ever produced* — which lives in
`orca_3.0_full`, was never carried forward, and beats the current baseline everywhere and the
current Barton–Bandis final on one specimen.

Everything below is scored with `scripts/table2_gate.py` on today's metric (five observables,
eleven stages, stage-1 datum, range-normalised RMSE), so the numbers are directly comparable to
`TABLE2_ERROR_ACCURACY_RANKING.csv`.

---

## 1. What is in the archive

`/media/geomechanics/Data4TB/projects/orca_3.0_full/Examples/YeGhasemmi2018` holds **52 completed
Mohr–Coulomb runs** — 32 on SW-S3 (series 70–83) and 20 on SW-S4 (series 61–68) — each with its
deck and its results CSV. They are an *independent calibration*: friction, cohesion, both dilation
angles, the weakening distance, the tangential viscosity and the secondary-weakening depth were
fitted to Table 2 directly, not transferred from anything.

**There is no tensile Mohr–Coulomb result in the archive.** `SelectionReview_2026-08-03`
marks both SW-T1 MC and SW-T2 MC as *blocked*: "No MC tensile input or result exists in the
working tree or repository history." Two decks were written
(`SWT{1,2}/mc_validation/Ye2018_SWT{1,2}_MC_validation_01.i`, documented in
`TENSILE_MC_VALIDATION.md`) but their `results_csv/` directories are **empty** — they were never
run to completion. So the tensile half of the current comparison has no historical competitor,
and the saw-cut half has a strong one.

---

## 2. What the archive scores

Best five per specimen, plus today's decks for reference. `mean_kin` is the corrected
(kinematic) d_n channel now used by the gate; `mean_tot` is the pre-2026-08-25 channel, kept
here because the gap between the two columns is itself a finding (§4).

### SW-S3 (JRC 1.96)

| case | Q | σ'ₙ | τ | d_n | d_s | **mean_kin** | mean_tot |
|---|---:|---:|---:|---:|---:|---:|---:|
| `83_11_sw3_mc_opening_gate5d30_m0` (3.0 selected) | 6.61 | 1.37 | 2.99 | 15.79 | 3.60 | **6.07** | 3.23 |
| `80_11`, `81_11`, `81_12`, `82_10`, `82_11`, `82_12`, `83_10` | 6.61 | 1.37 | 2.99 | 15.79 | 3.60 | **6.07** | 4.02–4.40 |
| `72_11_sw3_mc_peak1p22_ld45_dil29_eta5e11_m0` | 5.08 | 9.12 | 3.50 | 12.83 | 1.53 | 6.41 | 6.61 |
| `75_13` | 6.16 | 6.81 | 5.03 | 14.34 | 4.18 | 7.30 | 7.51 |
| `76_11` (3.0 "final calibration") | 6.48 | 6.88 | 4.70 | 15.40 | 3.47 | 7.38 | 5.84 |
| — | | | | | | | |
| **`94_05_sw3_mc_final` (current baseline)** | 9.59 | 8.18 | 19.55 | 26.27 | 27.54 | **18.23** | 18.47 |
| **`93_05_sw3_final_resc1p40_ppfix` (BB final)** | 3.00 | 3.33 | 8.01 | 7.42 | 1.11 | **4.57** | 4.57 |

### SW-S4 (JRC 1.19)

| case | Q | σ'ₙ | τ | d_n | d_s | **mean_kin** | mean_tot |
|---|---:|---:|---:|---:|---:|---:|---:|
| `65_11_sw4_mc_dS0p45_s36_m0` | 4.09 | 2.42 | 5.62 | 3.60 | 6.29 | **4.40** | 4.40 |
| `67_11_sw4_mc_dS0p15_s28_w12_m0` (3.0 selected) | 4.44 | 2.62 | 6.80 | 4.39 | 3.89 | **4.43** | 4.43 |
| `66_11_sw4_mc_fcs070_m0` | 4.26 | 3.19 | 9.06 | 2.37 | 3.46 | 4.47 | 4.47 |
| `65_14` | 3.98 | 2.47 | 5.68 | 3.36 | 7.58 | 4.61 | 4.61 |
| `65_13` | 3.94 | 2.51 | 5.59 | 3.65 | 8.00 | 4.74 | 4.74 |
| — | | | | | | | |
| **`94_07_sw4_mc_final` (current baseline)** | 6.32 | 4.41 | 11.41 | 7.02 | 6.18 | **7.07** | 8.97 |
| **`93_07_sw4_final_theta30_jrc5_ppfix` (BB final)** | 5.01 | 3.87 | 10.10 | 4.63 | 7.08 | **6.14** | 6.14 |

### The number that matters

> **On SW-S4, a calibrated Mohr–Coulomb model reached 4.40 % where the campaign's
> Barton–Bandis final reaches 6.14 %.**

On SW-S3 the calibrated MC reaches 6.07 % against Barton–Bandis' 4.57 %, so Barton–Bandis still
wins there — by 1.3× rather than the 4.0× the current baseline implies.

---

## 3. Why the archived MC is so much better than the current baseline

Both use the same material, `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`.
The difference is entirely in what was fitted and what was switched on.

| | `67_11` (archive, SW-S4) | `94_07` (current, SW-S4) |
|---|---|---|
| envelope source | fitted to Table 2 | tangent transfer of the BB envelope at σ'ₙ\* |
| `friction_coefficient_rough` | **1.17** | 0.9804 |
| `friction_coefficient_smooth` | **0.055** | 0.1139 |
| `cohesion_rough` / `_smooth` | **0 / 0**, exponent 2 | 3.225 MPa / 0, exponent 1 |
| `roughness_decay_distance` | **1.15e-4 m** | 8.0e-5 m (BB's roughness distance) |
| `dilation_angle_peak/residual` | **50° / 22°** | copied from the BB sibling |
| `secondary_weakening_strength` | **0.15 MPa** | not used |
| `use_rate_and_state` | **true** | not used |
| `tangential_viscosity` | **5.0e12** | copied from the BB sibling |
| `reversible_normal_compliance` | 0.0 (explicitly disabled) | 0.0 (default) |

The archived model has roughly **eight free parameters per specimen**; the current baseline has
**zero** — every one of its numbers is derived from the Barton–Bandis fit. That is the honest
description of the difference, and it is the one the paper has to use.

**Disqualifying caveats for reusing the archived runs as-is.** These are why the numbers above
cannot simply replace Table 6, and they were already recorded in `doc/MC_BASELINE_94_SERIES.md` §1:

1. **Superseded geometry.** `83_11` ran on `sw3_mesh_size5.e` at **L = 124.40 mm** against
   Table 1's 123.40 mm. `67_11` ran on `ye2018_sw_s4_low_mesh.e` at **θ = 28.9904°** with the
   fracture plane **2.85 mm off centre**, against Table 1's 30.000° and a centred plane.
2. **Reporting frame.** The SW-S4 archive decks emit no paper-frame σ'ₙ or τ postprocessor, so
   the gate falls through to the local Barton–Bandis frame. Measured on `94_07`, which emits
   both, the legacy frame scores **worse**, not better (mean 7.64 % vs 7.07 %), so `67_11`'s
   4.43 % is if anything conservative — the frame is not what is flattering it.
3. **`biot_coefficient = 1e-12`** on the SW-S3 archive decks, i.e. the pre-Biot-study poroelastic
   setting.
4. **Rate-and-state is on.** A model with RSF, two dilation angles and a secondary weakening
   stage is not the linear baseline the paper says it is comparing against.

None of these turns 18.2 % into 6.1 %. They are reasons the archived runs cannot be quoted as
Table 6; they are not reasons to believe the gap is an artefact.

---

## 4. The d_n reporting defect the archive exposed

Reading the archive decks side by side with the 94-series surfaced a scoring bug that had been
invisible since the MC baseline was built.

Two postprocessors in every deck claim to be normal displacement in the paper's sign convention:

```
czm_normal_dilation_paper_mm_pp   <- normal_opening_total     (constitutive decomposition)
frac_normal_dilation_paper_mm     <- global normal jump       (kinematic)
```

The two materials decompose `normal_opening_total` differently:

```
ADOrcaBartonBandisContactTractionFastAD.C:706
    _normal_opening_total = irreversible_opening + reversible_opening + elastic_opening
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.C:832
    _normal_opening_total = state.normal_plastic_jump + reversible_opening
```

**The Mohr–Coulomb material has no elastic term in that total.** Its `reversible_normal_opening`
is an output-only surrogate (it enters `_normal_opening_total` and nothing else — it never
reaches the traction), and the 94-series leaves `reversible_normal_compliance` at its default of
zero. So the MC d_n column was the plastic normal jump alone: monotone by construction, reporting
**exactly zero** recovery on the unloading branch regardless of what the mechanics did.

Recovery on the unloading branch, measured on the 94-series finals:

| specimen | `normal_opening_total` | global jump | BB sibling |
|---|---:|---:|---:|
| SW-S3 | 0.00 µm | **12.74 µm** | 11.38 µm |
| SW-S4 | 0.00 µm | **9.64 µm** | 10.97 µm |
| SW-T1 | 0.00 µm | 0.84 µm | 19.94 µm |
| SW-T2 | 0.00 µm | 1.27 µm | 10.61 µm |

For the ppfix Barton–Bandis finals the two channels are numerically identical, so this was a
one-sided penalty on the baseline. `scripts/table2_gate.py` now defaults to the kinematic
channel — the quantity the experiment's LVDTs actually measure and the only one both materials
emit on the same definition — with `--dn-channel total` retained to regenerate historical scores,
and it prints the two channels' recovery gap on every run so the asymmetry cannot hide again.

**This changes a physics claim.** "Mohr–Coulomb produces no normal recovery at all" was a
statement about the reporting, and it is wrong for the saw cuts: on SW-S3 and SW-S4 the MC
mechanics recovers 12.74 and 9.64 µm against Barton–Bandis' 11.38 and 10.97 µm — i.e. *the same*.
The genuine failure is confined to the tensile fractures, where MC recovers 0.84 and 1.27 µm
against 19.94 and 10.61 µm. The corrected statement scales with roughness, which is stronger than
the universal one it replaces.

### Effect on the ranking

`TABLE2_ERROR_ACCURACY_RANKING.csv` was regenerated. Nineteen of 86 rows moved; **all four
Barton–Bandis finals are unchanged**.

| specimen | MC before | MC after | BB (unchanged) | gain before | gain after |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 25.27 | 25.31 | 4.44 | 5.70× | 5.71× |
| SW-T2 | 23.14 | 23.18 | 2.43 | 9.53× | 9.55× |
| SW-S3 | 18.47 | 18.23 | 4.57 | 4.04× | 3.98× |
| SW-S4 | 8.97 | **7.07** | 6.14 | 1.46× | **1.15×** |

Four-specimen means: Barton–Bandis 4.39 %, Mohr–Coulomb 18.45 %, a **76.2 %** reduction (was
76.8 %). The headline is intact; **SW-S4's margin is not.**

A second consequence, on SW-S3: on the corrected channel `83_11`, `83_10`, `82_10`, `82_11`,
`82_12`, `81_11`, `81_12`, `80_11` and `80_12` all score **6.07 %, identically**. The entire
80→83 "improvement" recorded in the 3.0 campaign (4.40 → 3.23 on the old channel) was produced by
the output-only opening transform and **changed no mechanics whatsoever**. Any figure or claim
inherited from that ladder should be re-checked.

---

## 5. What the paper may and may not claim

**May not:** that Mohr–Coulomb cannot reproduce this dataset. It can, on both saw cuts, and on
SW-S4 it does so better than the Barton–Bandis final.

**May not:** that the 102-series settles it. The 102-series only shows that *Barton–Bandis-derived
refinements* do not help Mohr–Coulomb — which is unsurprising, since they act on a roughness
description MC does not have. It says nothing about calibrating MC in its own right.

**May, and should:**

1. **Parameter economy, stated as a number.** The Barton–Bandis finals use the paper's own
   measured JRC, JCS and φ_r plus one aperture scale. Matching them with Mohr–Coulomb required
   eight per-specimen fitted parameters — friction rough and smooth, both cohesions and their
   exponent, the weakening distance, two dilation angles, a secondary-weakening depth, a
   tangential viscosity — plus rate-and-state. Same data, one-eighth the freedom.
2. **Transferability.** The archived Mohr–Coulomb fits are per-specimen and do not transfer: the
   SW-S3 and SW-S4 calibrations share no parameter value, and neither could be applied to the
   tensile specimens, where **no Mohr–Coulomb result was ever completed** in either repository
   (two decks were written in `orca_3.0_full`; neither produced a CSV).
3. **Roughness scaling, now on corrected numbers.** Barton–Bandis is 1.15× better on SW-S4
   (JRC 1.19), 3.98× on SW-S3 (JRC 1.96), 5.71× on SW-T1 (JRC 15.32) and 9.55× on SW-T2
   (JRC 14.63). The gain separates the two saw cuts (JRC < 2) from the two tensile fractures
   (JRC ~ 15) by nearly an order of magnitude and is ~1 at the polished end — which is what the
   physics predicts and is more convincing than a uniform "MC failed". Do **not** claim
   monotonicity in JRC: SW-T1 is the rougher tensile specimen and has the *smaller* ratio, so the
   defensible statement is a two-population separation.
4. **Timing and recovery, scoped correctly.** MC reaches final slip within 3–8 % but initiates
   275–389 s early and smears a 39–41 s event over 225–343 s on the tensiles, against 33 s and
   1.05× on SW-S4. Normal recovery fails **on the tensiles only** (0.8–1.3 µm against 10.6–19.9 µm);
   on the saw cuts the two laws recover the same amount (§4).

**The defensible sentence** is not "Barton–Bandis captured the behaviour and Mohr–Coulomb failed."
It is:

> Mohr–Coulomb matches the two saw-cut specimens when each is given eight independently fitted
> parameters, and on the polished saw cut it matches better than Barton–Bandis; it does not
> transfer between specimens, it was never made to reproduce either tensile fracture, and under
> the matched, non-refitted transfer used here its error separates the two saw cuts from the two
> tensile fractures by roughly an order of magnitude — 1.15× and 4.0× the Barton–Bandis error at
> JRC below 2, against 5.7× and 9.6× at JRC near 15.

---

## 6. Two leads this opens

1. **SW-S4's τ is not at a floor.** `Final_ye_ghaseemi_simulations.txt` §8 flags τ = 10.10 % as
   the campaign's largest recoverable error and, on the evidence then available, guessed the
   loading frame. The archive says otherwise: **`65_13` reached τ = 5.59 % and `65_11` 5.62 % on
   this specimen**, with a cohesionless envelope weakening from µ = 1.17 to 0.055 over 115 µm and
   a tangential viscosity of 5.0e12. That is a deeper, slower drop than the Barton–Bandis final's.
   The lever is the *weakening path*, not the frame, and about 4.5 pp of SW-S4's τ error is
   demonstrably reachable on this mesh.
2. **A defensible calibrated-MC arm.** If a referee asks for a fairly-calibrated baseline, the
   cheapest honest answer is four decks: port `65_11`/`67_11` (SW-S4) and `83_11` minus its
   output-only transform (SW-S3) onto the corrected meshes and the ppfix reporting frame, and
   report them *alongside* the transfer baseline as an upper bound on Mohr–Coulomb. That converts
   the weakness in §5 into a result. The tensiles have no archived starting point and would need
   a fresh calibration or an explicit statement that none exists.
