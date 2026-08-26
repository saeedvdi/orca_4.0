# The 106-series run list — aperture law, strength level, and shear stiffness

**2026-08-26.** Written after all ten 105-series arms finished and **every one of
them regressed**. This series does not continue any 105 axis. It replaces them
with three axes derived from Table 2 rather than swept, plus one source change.

Branch: `orca_v9`. Decks 106_12–106_15 **require that branch's `orca-opt`**;
106_01–106_11 run on any build.

---

## 0. Free first: three of the four published finals are already beaten on disk

Nothing here needs running. `TABLE2_ERROR_ACCURACY_RANKING.csv` (regenerated
today, now including all ten 105 arms) already ranks these first:

| specimen | published final | mean nRMSE | best on disk | mean nRMSE |
|---|---|---:|---|---:|
| SW-T1 | `93_01_swt1_final_c26p9_resc9p19_ppfix` | 4.435 | **`100_01_swt1_vm55um_ppfix`** | **2.689** |
| SW-T2 | `93_03_swt2_final_theta30_resc9p71_ppfix` | 2.428 | **`100_04_swt2_apscale0p0177_ppfix`** | **2.132** |
| SW-S3 | `93_05_sw3_final_resc1p40_ppfix` | 4.574 | **`100_06_sw3_resc1p30_unld0p00_ppfix`** | **4.354** |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix` | 6.139 | (unchanged) | 6.139 |

Campaign mean **4.394 → 3.828, −12.9 %, zero compute.** The four `*_FINAL.md`
files now carry this as a superseding block at the top.

---

## 1. What the 105 series actually established

| group | parent | arms | result |
|---|---|---|---|
| SW-T1 V_m | 93_01 (4.44) | 105_01 5.09 · 105_02 59.70 · 105_03 59.38 | bracket **closed**; 55 µm is the optimum |
| SW-S4 D_c / floor | 93_07 (6.14) | 105_04 13.93 · 105_05 9.10 · 105_06 20.35 | both already right; wrong lever |
| SW-S4 MC | 94_07 (7.07) | 105_07 8.84 · 105_08 11.46 | MC transfer does not calibrate |
| SW-S3 MC | 94_05 (18.23) | 105_09 24.90 · 105_10 19.75 | same |

At V_m = 90 and 110 µm **the slip event never fires** (0.0156 / 0.0120 mm of slip
against 0.537 measured). SW-T1 fires on a **1.31 MPa margin, 1.9 % of the
limit**, at stage 5. SW-T2's margin is thinner still, 0.97 MPa / 1.3 %. Every
deck below has to clear that gate before any channel is worth reading.

---

## 2. Axis A — the aperture law (106_01 · 106_02 · 106_05 · 106_10)

Table 2's flow is the cubic law, so `Q` is a direct readout of `a_h`, and every
finished run exports `hydraulic_aperture_um_pp`. Comparing the two stage by
stage (`scripts/retune_aperture_law.py`) puts the whole `Q` residual in the
aperture:

```
SW-T1 100_01   a_h error  0.000 +0.040 +0.010 -0.030 -0.090 | +0.121 +0.128 +0.172 +0.185 +0.199 +0.183  um
SW-T2 100_04   a_h error  0.000 -0.020 -0.049 -0.198 -0.575 | -0.142 +0.103 +0.164 +0.192 +0.207 +0.204  um
SW-S4 93_07    a_h error  0.000 +0.005 -0.010 -0.001 -0.021 | -0.061 -0.004 +0.026 +0.018 +0.020 +0.021  um
```

**SW-T1 has no stress-aperture term at all.** `normal_stress_aperture_compliance`
is 0.0 *and* `use_nonlinear_normal_closure` is false, and the two branches of
`computeStressAperture` are mutually exclusive, so `normal_stress_aperture_pp` is
identically zero at every timestep and `a_h` is frozen at 1.630 µm through
stages 1–5 while Table 2 opens to 1.72.

**SW-T2's is on but saturated.** σ₀ = V_h·K_h = 1.2 µm × 1.25e13 = **15.0 MPa**
against a **58–67 MPa** operating range, so it delivers 0.0023 µm where Table 2
opens 0.58. Those constants are SW-T1's, transplanted; they were never fitted on
either specimen.

### The refit, and why it is not another sweep

A free two-parameter fit of (V_h, σ₀) falls into a degenerate valley — widening
the σ₀ grid moves SW-T1 from (35.2 µm, 10.5 MPa) to (25.5 µm, 11.4 MPa) at
identical error. Pinning σ₀ to the deck's **own mechanical scale stress**
σ₀ = K_ni·V_m, and the exponent to the deck's **own mechanical exponent**
p = 3.28, leaves one free amplitude and removes the degeneracy. It also lands on
its own: SW-T2's free optimum is 11.60 MPa against a mechanical 11.216.

| deck | p | σ₀ (MPa) | V_h (µm) | K_h (Pa/m) | aperture_scale | Q nRMSE |
|---|---:|---:|---:|---:|---:|---|
| 106_02 SW-T1 | 4.0 → 3.28 | 13.4365 | 1.2 → **9.8398** | 1.25e13 → **1.3655e12** | 0.016 → **0.01236** | 4.511 → **0.306** |
| 106_05 SW-T2 | 4.0 → 3.28 | 11.2158 | 1.2 → **34.3624** | 1.25e13 → **3.2640e11** | 0.0177 → **0.01093** | 4.336 → **2.502** |
| 106_10 SW-S4 | 2.0 → 3.28 | 11.2158 | 1.05 → **1.8277** | 1.43e13 → **6.1366e12** | unchanged | 5.005 → **2.183** |

`106_01` is the no-new-terms version for SW-T1: `aperture_scale` alone, least
squares on stages 6–11, 0.016 → 0.01512, Q 4.511 → 1.125. Run it as the control
on 106_02 — if the two land together, the stress term is not earning its keep.

**SW-S3 is deliberately excluded.** The same fit makes 100_06 *worse*
(3.060 → 3.453 %): Table 2's SW-S3 pre-event apertures are flat inside their own
scatter (1.22, 1.21, 1.20, 1.26, 1.25 µm) and carry no closure signal. SW-S3's
worst channels are τ (7.392) and d_n (6.174), neither hydraulic.

**Caveat on every predicted number above:** the prediction re-maps `a_h` at the
parent's own σ'ₙ. Aperture feeds back into pressure diffusion and hence into
σ'ₙ, so these rank candidates; they do not forecast scores.

---

## 3. Axis B — unload reclosure (106_03 · 106_06)

SW-T1's worst channel is d_n (4.584 %) and the error is entirely on unloading:
−0.125 mm of held opening at stage 11 against Table 2's −0.113. The same
over-open joint puts σ'ₙ 0.15–0.23 MPa low and the flow 15–18 % high over stages
9–11 — one parameter, three channels. `updateNormalUnloadState` retains
`normal_unload_retention_fraction` of the recovered closure; SW-T1 is at **0.94**
and SW-T2 at **0.84**, so neither joint meaningfully recloses.

Precedent, stated honestly: SW-S3's best run sits at **0.00** on this parameter,
but it moved only 0.06 → 0.00 to get there, so the *step* is not the evidence —
the *level* is. SW-S3 scores its best at essentially zero unload retention and
shows none of the over-open unloading signature; SW-T1 and SW-T2 sit at 0.94 and
0.84 and show all of it. 0.70 and 0.60 are deliberately conservative first steps,
because of the margins in §1.

---

## 4. Axis C — the SW-S4 strength level (106_08 · 106_09)

SW-S4 is now the worst of the four. Its τ error is one spike:

```
-0.21 -0.16 +0.25 [+2.74] +1.06 +1.26 +0.89 +0.65 +0.47 +0.29 +0.05  MPa
```

**The joint is not stuck at stage 4.** `limit_tau_pp` there is 12.291 MPa against
a model τ of 12.121 — it is on its own yield surface, having slipped just enough
to reach it (0.0034 mm against Table 2's 0.017). So the lever is where the
surface sits. That corrects the earlier reading of stage 4 as delayed onset.

Inverting Table 2 at its own stage-4 slip: weakening consumed
(17/74.5)^1.10 = 0.1968, residual 22.92·tan(6.50°) = 2.611 MPa, so the peak that
delivers τ = 9.38 is (9.38 − 0.1968·2.611)/(1 − 0.1968) = **11.039 MPa**, i.e.
φ_peak = 25.717° where the deck gives 22.72 + 5·log₁₀(150/22.92) = 26.799°.
**1.083° too high.**

φ_r is the only lever: the JRC that would lower φ at 22.92 MPa while holding it at
26.5 solves to **−16.8**, and JCS is algebraically identical to φ_r over a span
this narrow (dφ/dlog₁₀JCS = JRC, constant) with 150 MPa the paper's own UCS.

| φ_r | τ_peak @ 22.92 | margin @ Table 2 stage 3 | margin @ model stage 3 |
|---:|---:|---:|---:|
| 22.72 (parent) | 11.577 | +1.068 | +0.865 |
| 22.10 (106_09) | 11.268 | +0.712 | +0.508 |
| 21.60 (106_08) | 11.020 | +0.427 | +0.222 |

D_c and the unloading floor are **left alone**: Table 2's own τ/d_s pairs imply
D_c = 55–98 µm (the parent's 74.5 is inside it) and the parent's unloading τ error
already decays to +0.05 MPa. 105_04 and 105_05 tested both and both regressed.

---

## 5. Axis D — stress-dependent shear stiffness (106_12–106_15) — **source change**

Every specimen creeps in shear before its event and this model does not:

```
SW-T1 Table 2 d_s  0.000 0.000 0.001 0.002 0.008 mm    model  0.000 0.000 0.000 0.000 0.001
SW-T2 Table 2 d_s  0.000 0.001 0.003 0.007 0.015 mm    model  0.000 0.000 0.000 0.000 0.003
```

and it happens while τ is **falling** (SW-T2: 74.87 → 73.40 MPa). What changes is
σ'ₙ, 66.7 → 57.9 MPa.

**No value of `penalty_tangent` fixes this.** With a constant tangential stiffness
the elastic shear jump is τ/k_t and τ is flat, so the modelled d_s is flat too —
0.02 µm of change across stages 1–5 at k_t = 1e13, and proportionally flat at any
other constant. Softening the penalty moves the datum, which stage-1 referencing
removes. This is structural, not a calibration miss.

Barton–Bandis give k_s = (100/L)·σ'ₙ·tan(φ_peak) — proportional to σ'ₙ. For these
50 mm specimens at σ'ₙ ≈ 66 MPa and φ_peak ≈ 46° that is **≈1.4e12 Pa/m, ~7×
softer than the 1e13 this campaign has used**, and 1e13 was chosen as a numerical
penalty and never checked against it.

### The change

`ADOrcaBartonBandisContactTractionFastAD` gains an **opt-in**
`use_stress_dependent_tangential_stiffness` (default **false** = byte-identical):

```
k_t(sigma'_n) = max(min_tangential_stiffness_fraction, (sigma'_n/sigma_ref)^m) * penalty_tangent
```

evaluated on the **start-of-step** effective normal stress, so k_t is constant
inside a step and every return-map expression keeps its algebra; only the
Jacobian's dependence of k_t on jump(0) is dropped. `penalty_tangent` becomes the
stiffness *at* σ_ref. `bb_tangential_stiffness` is exported for audit.

Verified locally on this workstation:
* flag **off**, 100_01 to t = 3.75 s at 10 ranks, against the 32-rank HPC CSV of
  the same deck: `differential_stress_reaction_mpa_pp` and
  `hydraulic_aperture_um_pp` identical to all printed digits, σ'ₙ agreeing to
  2.682589e7 vs 2.682396e7 — MPI-partition noise only;
* flag **on** (106_12), same steps: shear jump 0.914 µm against the control's
  0.051 µm, an 18× compliance increase matching τ/k_t at the implied
  k_t = 4.80e11 Pa/m, and the frame shedding load as expected
  (differential stress 1.045 → 0.870 MPa). Newton converged normally.

### Calibration, from Table 2

| deck | specimen | σ_ref | k_ref | Table 2 target | stage-1 shear datum |
|---|---|---:|---:|---|---:|
| 106_12 | SW-T1 | 65.47 MPa | **1.18e12** | 0.008 mm (full) | ≈57 µm |
| 106_13 | SW-T1 | 65.47 MPa | 3.0e12 | ≈40 % of it | ≈22 µm |
| 106_14 | SW-T2 | 66.74 MPa | **6.86e11** | 0.015 mm (full) | ≈109 µm |
| 106_15 | SW-T2 | 66.74 MPa | 2.0e12 | ≈34 % of it | ≈37 µm |

SW-T2 is the specimen this axis was built for: its 0.015 mm of pre-event creep is
the direct cause of the one residual `106_05` cannot touch — Table 2's aperture
kinks 2.31 → 2.69 µm between stages 4 and 5 while σ'ₙ falls only 2.1 MPa, which no
smooth function of stress reproduces.

**Gate both full arms on the slip event firing before scoring anything.** The mild
arms exist so the axis is bracketed rather than bet on.

---

## 6. Corners (106_04 · 106_07 · 106_11) — read last

| deck | combines | expected orthogonality |
|---|---|---|
| 106_04 SW-T1 | 106_02 + 106_03 | good — one changes how a_h is read off the mechanical state, the other changes that state |
| 106_07 SW-T2 | 106_05 + 106_06 | **poor** — both reduce a_h over stages 7–11; may overshoot |
| 106_11 SW-S4 | 106_08 + 106_10 | good — SW-S4's aperture law has no term feeding back into the envelope |

Precedent for the orthogonality claim: 99_01 → 100_02 added `aperture_scale` at
fixed V_m and moved **only** Q (6.15 → 4.03 %), leaving the other four channels
identical to three digits.

---

## 7. Submission order

Everything below is HPC (`*_hpc_nochk.sh`, 32 ranks, 24 h). Nothing in this
series may be run on the workstation — 16 physical cores, 30 GB, and this
campaign has already lost a 16-rank run to the OOM killer.

**Wave 1 — singles, 11 decks, no source dependency**

```
SWT1/106_01_swt1_apscale0p01512_ppfix_hpc_nochk.sh
SWT1/106_02_swt1_hydbb_vh9p84um_ppfix_hpc_nochk.sh
SWT1/106_03_swt1_unld0p70_ppfix_hpc_nochk.sh
SWT2/106_05_swt2_hydbb_vh34p36um_ppfix_hpc_nochk.sh
SWT2/106_06_swt2_unld0p60_ppfix_hpc_nochk.sh
SWS4/106_08_sw4_phir21p60_ppfix_hpc_nochk.sh
SWS4/106_09_sw4_phir22p10_ppfix_hpc_nochk.sh
SWS4/106_10_sw4_hydbb_vh1p83um_ppfix_hpc_nochk.sh
```

**Wave 2 — the source axis (needs `orca_v9` built on the cluster)**

```
SWT1/106_12_swt1_ktbb_kref1p18e12_ppfix_hpc_nochk.sh
SWT1/106_13_swt1_ktbb_kref3p0e12_ppfix_hpc_nochk.sh
SWT2/106_14_swt2_ktbb_kref6p86e11_ppfix_hpc_nochk.sh
SWT2/106_15_swt2_ktbb_kref2p0e12_ppfix_hpc_nochk.sh
```

**Wave 3 — corners, only after wave 1 scores**

```
SWT1/106_04_swt1_hydbb_unld0p70_ppfix_hpc_nochk.sh
SWT2/106_07_swt2_hydbb_unld0p60_ppfix_hpc_nochk.sh
SWS4/106_11_sw4_phir21p60_hydbb_ppfix_hpc_nochk.sh
```

All fifteen pass `--check-input` against the `orca_v9` binary.

---

## 8. Scoring

```
python scripts/update_table2_ranking.py            # verify
python scripts/update_table2_ranking.py --write    # publish
```

Add each finished run to `NEW_CASES` first. The ten 105 arms were added today;
the ranking is now complete through series 105.

Two reproducers back everything above and both run clean:

```
python scripts/retune_aperture_law.py          # §2, all four specimens
python scripts/refit_hydraulic_closure.py      # the pre-event-only cross-check
```

---

## 9. One thing that is *not* a score change

The 106 decks forked from 99–104 parents carry the **2026-08-24 flow-measurement
fix** (task #123), ported from 105_01: `inj_reaction_sum_pp` /
`prod_reaction_sum_pp` now sum `react_pore_pressure` instead of `inj_flux_aux`,
with the old sums retained as `*_saveiin_sum_legacy_pp`. This is **output-only
and not a scored channel** — the Table-2 flow channel is
`flow_rate_validation_ml_min_pp`, the cubic law built from
`hydraulic_aperture_pp` and `pp_drop_pp`, which never touched either quantity.
It is ported so the 106 diagnostics are comparable with the 93/94 finals and the
105 series, not because any score moves.
