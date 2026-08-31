# Bringing Kalantar et al. (2025) into the manuscript as a validation

**2026-08-31 · branch `orca_v11`.** Back-analysis of what the Kalantar campaign can actually
support as a published claim, and what has to happen first.

Regenerate everything here with:

```
python3 scripts/kalantar_gate.py --sample OG-SH Examples/Kalantar2025/OGSH/results_csv_hpc/110_13_og_sh_bbfast_r6_hpc.csv
python3 scripts/kalantar_gate.py --sample OG-SC Examples/Kalantar2025/OGSC/results_csv_hpc/110_15_og_sc_bbfast_r6_hpc.csv
python3 scripts/pedrosa_fit_kalantar_specimens.py
```

---

## 1. The headline: the campaign's "19 % / 29 %" is a friction score, not a hydraulic one

The mean nRMSE that the campaign has been tracking averages one force channel and one flow
channel. Splitting it changes the conclusion completely:

| specimen | τ | σ'ₙ | a_h | Q | campaign "mean" |
|---|---:|---:|---:|---:|---:|
| OG-SH `110_13` | **28.9 %** | 11.9 % | **15.9 %** | **9.3 %** | 19 |
| OG-SC `110_15` | **47.3 %** | 9.6 % | **10.5 %** | **11.0 %** | 29 |

**Everything hydraulic is at 9–16 %. Everything frictional is at 29–47 %.** The campaign has
been reporting a number dominated by the part of the model this manuscript is not about.

### These are not trivially-anchored numbers

Each channel against the best possible no-skill constant (the paper's own mean) and against
the model frozen at its stage-1 value:

| specimen | channel | model | frozen at stage 1 | best constant | r | verdict |
|---|---|---:|---:|---:|---:|---|
| OG-SH | Q | **9.3 %** | 38.7 % | 29.4 % | +0.958 | skill |
| OG-SH | a_h | **15.9 %** | 66.5 % | 31.3 % | +0.881 | skill |
| OG-SH | σ'ₙ | **11.9 %** | 61.5 % | 29.8 % | +0.989 | skill |
| OG-SC | a_h | **10.5 %** | 31.3 % | 24.6 % | +0.950 | skill |
| OG-SC | Q | **11.0 %** | 40.9 % | 27.7 % | +0.966 | skill |
| OG-SC | σ'ₙ | **9.6 %** | 55.9 % | 28.3 % | +0.982 | skill |
| OG-SC | τ | 47.3 % | 69.0 % | 46.1 % | +0.928 | **no skill over the null** |

Every hydraulic channel beats the best constant by 2–3×. OG-SC's τ does not beat it at all.

---

## 2. Why this is a strong claim: the hydraulic constants were never fitted

Tracking every aperture-law constant across all five OG-SH and OG-SC rounds:

**OG-SH — all thirteen unchanged since round 1.** `initial_hydraulic_aperture`,
`reference_effective_normal_stress`, `aperture_scale`, `normal_stress_aperture_compliance`,
`bb_max_aperture_closure`, `bb_initial_normal_stiffness`, `bb_stress_exponent`,
`dilation_scale`, `retention_residual`, both slip-damage constants and both aperture clamps.
Five rounds of iteration were **all** on the friction side — φ_peak, D_c, the frame penalty.
**OG-SH's Q = 9.3 % and a_h = 15.9 % are a blind prediction.**

**OG-SC — eleven of thirteen unchanged; two changed once**, in round 4:
`bb_max_aperture_closure` (V_m, 1.2 → 2.6545 µm) and `bb_initial_normal_stiffness`
(K_ni, 1.25e13 → 1.3698e13), both re-derived from Kalantar's own σ₀/V_m relation. So
OG-SC's a_h = 10.5 % is a two-constant fit over thirteen aperture points.

**And the shape constants are Ye's, unchanged.** Numerically identical, not merely similar:

| constant | OG-SC | equals | OG-SH | equals |
|---|---|---|---|---|
| `aperture_scale` χ | 0.001 | SW-S3/SW-S4 | 0.0165 | between SW-T1's 0.01512 and SW-T2's 0.0177 |
| `dilation_scale` λ | 0.038 | **SW-S3 exactly** | 0.0 | SW-T1/SW-T2 (kinematic) |
| `retention_residual` r_res | 0.28 | **SW-S3/SW-S4 exactly** | 0.747330960854 | **SW-T2 exactly, 12 digits** |
| `normal_stress_aperture_compliance` | 2.0e-14 | SW-S3/SW-S4 | 0.0 | SW-T1/SW-T2 |
| `bb_stress_exponent` p | 4.0 | all four | 4.0 | all four |
| `self_propping_scale` | 0.0 | all four | 0.0 | all four |

Only the four quantities a new specimen must supply were re-anchored: a_h0 and σ_ref to
Kalantar's Table 2 stage 1, and (OG-SC only) the closure amplitude and stiffness.

**So the claim available is transferability, which is stronger than a refit:** the aperture
law's shape, calibrated on Ye & Ghassemi's granite, predicts a different group's granodiorite
to 9–16 % with only its two anchor points moved. `self_propping_scale = 0.0` on all six
specimens in both campaigns, so no explicit propping term is doing any of this work.

---

## 3. The self-propping comparison: use α, not k₀

Kalantar Figure 8 panels (a) and (d) fit `k = k₀ exp(−α σ'ₙ)` pre- and post-slip to their
own OG-T and OG-SC. Reproducing it requires fitting **their printed `k_D` column**, not
`a_h²/12` — that was got wrong once and the error is large:

| OG-SC pre-slip | k₀ (D) | α (1/MPa) |
|---|---:|---:|
| fitting `k_D` | **0.813** | **0.0450** |
| fitting a_h²/12 | 6.025 | 0.1156 |
| **Kalantar Figure 8, published** | **0.82** | **0.05** |

`k_D` reproduces the published fit; `a_h²/12` is wrong by 7× and 2.3×. The two agree wherever
`k_D` has resolution and diverge where it does not — `k_D` is printed to 2 dp and pins at
0.17 across OG-SC's first three stages and at 0.02–0.03 across OG-T's first six.

### The OG-SC comparison, three ways

| | k₀ pre | k₀ post | **k₀ gain** | α pre | α post | **α ratio** |
|---|---:|---:|---:|---:|---:|---:|
| Kalantar Fig. 8, published | 0.82 | 5.25 | **6.40** | 0.050 | 0.110 | **2.20** |
| our reduction of their Table 2 | 0.813 | 6.476 | **7.97** | 0.0450 | 0.1219 | **2.71** |
| **MODEL** | 1.767 | 14.671 | **8.30** | 0.0757 | 0.1620 | **2.14** |

The model's α ratio (2.14) lands between the published 2.20 and our own reduction 2.71, and
its k₀ gain (8.30) is within 4 % of our reduction of the same data. **Neither number was
available to the calibration** — Table 2 tabulates neither.

### But k₀ is an extrapolation, and the matched-stress number says something different

k₀ is the fit evaluated at σ'ₙ = 0, which is 25–60 MPa outside every branch in the dataset.
Evaluating the same fits **inside** the common data window instead:

| σ'ₙ (MPa) | measured | published | model |
|---:|---:|---:|---:|
| 28.48 | 0.89 | 1.16 | 0.71 |
| 30.32 | 0.77 | 1.04 | 0.61 |
| 32.17 | 0.67 | 0.93 | 0.52 |

**At matched effective normal stress OG-SC's permeability gain is about 1, not 6–8.** The
apparent enhancement lives entirely in the extrapolation. The model agrees, and is if
anything more pessimistic (0.52–0.71).

This is the manuscript's own frame caveat — that most apparent propping is stress path, not
retained aperture — demonstrated on **another group's published fit to another group's rock**.
It is the single most useful thing this campaign can contribute to the self-propping argument,
and it costs no new runs.

---

## 4. What each specimen contributes, and whether OG-T is needed

| specimen | type | stages | contributes | status |
|---|---|---:|---|---|
| **OG-SH** | natural shear | 9 | **blind hydraulic prediction** — Q 9.3 %, a_h 15.9 %, zero fitted hydraulic constants. No Figure 8 entry (it never slipped in one event), so no propping comparison. | **ready** |
| **OG-SC** | saw cut | 13 | **the self-propping comparison** — α ratio 2.14 model / 2.20 published, and the matched-σ'ₙ result above. | **ready** |
| **OG-T** | tensile | 17 | the richest trajectory: a_h **0.10 → 1.11 → 0.00 µm** and τ 66.5 → 20.4 MPa. | **blocked**, see §5 |

**A correction to an earlier note of mine.** I previously wrote that OG-T carries little
information because only 8 of its 17 stages clear the Q floor. That is true of Q and false of
the specimen: a_h is printed to 0.01 µm on all seventeen stages and spans the full range, which
is why `kalantar_gate` already scores OG-T on a_h rather than Q. **OG-T is the richest of the
three, not the poorest.**

**But OG-T cannot supply a matched-stress propping number, and this is a property of the
experiment, not of our model.** Its pre-slip branch spans σ'ₙ = 51.47–59.33 MPa and its
post-slip branch 27.50–37.96 MPa. **The two branches are disjoint** — the slip event moved
σ'ₙ by 20 MPa and they never share a stress. Any pre/post comparison on OG-T is therefore an
extrapolation of one branch into the other's range, which is why our reduction gives an α ratio
of 5.03 against Kalantar's published 2.00, and why their own OG-T r² reads 0.42 pre-slip and
0.06 post-slip.

**So the paper section stands on OG-SH + OG-SC alone.** What OG-T would add, if fixed, is one
thing the other two cannot give: a fracture that opens elevenfold and then returns to **0.00 µm**,
i.e. a specimen that retains nothing. That is the direct experimental test of the manuscript's
limitation that retained aperture is unbounded because the only saturating term is the negative
one. It is worth one probe deck. It is not worth another five rounds.

---

## 5. What to do, in order

1. **No run needed — write the section from OG-SH and OG-SC.** Everything in §1–§3 is on
   disk and reproducible today.
2. **Half an hour, local, no HPC** — resolve the +0.277 slope offset flagged in
   `KALANTAR2025_ROUND11_BACKANALYSIS.md` §6. It is common-mode across specimens and most
   likely a definition mismatch in `effective_normal_paper_frame_mpa_pp`. It does not affect
   the hydraulic channels, but it should not be left open under a published table.
3. **One HPC probe — round 12, OG-T only.** Preload ramp 53 s → ≥1e4 s; gates in the
   round-11 back-analysis §5. If it passes, add OG-T's a_h trajectory as the retention test.
   If it fails, report OG-T as a documented protocol limit and publish §1–§3 without it.
4. **Do not submit round-11 wave B.** `110_33`/`110_34`/`110_35` were gated on `110_30`.

---

## 6. What the section must say plainly

- The friction envelope **does not transfer**. OG-SH's residual is ~2.6 MPa too strong on the
  depressurization branch (though r = 0.996 on shape — it is an offset, not a shape error);
  OG-SC's slip event fires **one stage early**, at stage 6 instead of 7, which is most of its
  47 % τ error. Both are reportable with sign and magnitude.
- OG-SC's two closure constants were fitted; OG-SH's nothing was. Say which is which.
- The matched-σ'ₙ gain of ≈1 is a result **about the experiment**, not about the model — it
  falls out of Kalantar's own published fit. The model's contribution is that it reproduces it.
- `self_propping_scale = 0.0` in all six specimens across both campaigns.
