# Self-propping and cyclic stimulation — the complete argument

**Opened 2026-08-27, current to 2026-08-31 · branch `orca_v11`.** Everything from the
cyclic question through the 106/107 calibration results and the 108 wave-1 findings, in
the order the arguments were made, with what was verified and what was falsified.

---

# Part 1 — The cyclic question

## 1.1 Are the Ye & Ghassemi stimulations cyclic? No

The validation protocol is a **single up-down ramp**, not cycling:

```
5 -> 8 -> 12 -> 16 -> 20 -> 24 -> 28 -> 24 -> 20 -> 16 -> 12 -> 8 MPa
```

One loading limb, one unloading limb, eleven holds. Nothing is ever re-pressurised to a
level it has already seen. **So the calibration data constrain nothing about
cycle-to-cycle behaviour**, and any per-cycle parameter fitted to it would be
unfalsifiable against the data used to fit it.

## 1.2 Does cyclic loading need a more sophisticated hardening law? Only for a claim the data cannot support

The model already has the memory variables people mean by "sophisticated":
`cumulative_plastic_slip`, `irreversible_dilation`, `roughness_state`,
`bb_unload_min_closure`, gouge fill, unload retention. What it does not have is
**re-weakening** — every one of those is monotone in slip.

The 101-series measured the consequence directly:

| | equal-peak cycling (group A) | escalating peaks (group B, matched floor) |
|---|---|---|
| SW-T1 aperture | ×1.00000 | ×2.327 |
| SW-T1 Q | ×1.00001 | ×12.61 |
| SW-T2 Q | ×0.99999 | ×8.21 |

**It is not the number of cycles, it is whether a cycle exceeds the previous maximum.**
That is a Kaiser / preconsolidation statement for hydraulic stimulation, and it is a
defensible positive result — not a gap to be papered over with a fatigue law.

## 1.3 The null has two causes and the manuscript names only one

From `CYCLIC_REALISM_BACKANALYSIS_2026-08-25.md`, confirmed by reading the source:

- **A: the joint cannot re-weaken** — monotone-in-slip state variables. §6.6.6 says this.
- **B: the joint cannot re-load** — the displacement-controlled frame. Slip on an
  inclined joint relieves the shear stress driving it, so after cycle 1 the joint sits
  below yield and returning to the same pressure does not bring it back.

**B does not transfer to the field** and the manuscript does not mention it. The frame
ladder measures it: at ×2.0 frame stiffness SW-T1 ratchets exactly 0.0000 µm; at ×1.0,
0.0058 µm; at ×0.5, 0.367 µm — a **63× change in the increment** from halving one
parameter. The existing §5 claim that the null is "robust to the frame stiffness" is true
of the *ratio* and hides that 63×.

## 1.4 Cycling is a MEASUREMENT protocol for self-propping, not a stimulation mechanism

This is the reframe that matters. Kalantar's diagnostic is a Pedrosa fit
`k = k0 exp(-alpha sigma'_n)` before and after slip: k0 rises (propping is real) *and*
alpha rises (the gain is not retained). A cyclic protocol delivers that fit **once per
cycle, at a known cumulative slip**, instead of the two points a single ramp gives.

Demonstrated on `101_05` (SW-T1, escalating peaks 24/26/28 MPa), unload limbs only:

| limb | sigma'_n range (MPa) | k0 (m²) | alpha (1/MPa) | R² | cum. slip (mm) |
|---|---|---:|---:|---:|---:|
| cycle 1 unload | 58.0–66.0 | 2.223e-13 | 0.0001 | 0.985 | 0.0016 |
| cycle 2 unload | 56.4–65.6 | 2.279e-13 | 0.0002 | 0.986 | 0.0067 |
| cycle 3 unload | 36.1–46.9 | **2.547e-12** | **0.0163** | 0.986 | 0.5304 |

Two flat cycles, then the slip event: k0 jumps ×11.5 and alpha goes from
indistinguishable-from-zero to 0.0163. Qualitatively Kalantar's result, reproduced from a
run already on disk. Loading limbs fit at R² ≈ 0.24 and must not be used.

**The catch:** alpha and sigma'_n level are confounded. Cycle 3's limb sits 20 MPa lower
because slip shed that much normal stress through the frame, and the Barton–Bandis
backbone is genuinely steeper at lower stress. The 101 decks cannot separate damage from
stress level because they were designed to test ratcheting, not this.

**Design requirement for any future cyclic-propping deck:** every unload limb must span a
*common* sigma'_n window, which means raising confining pressure between cycles to
compensate for what slip sheds.

---

# Part 2 — Self-propping in this model

## 2.1 The parameter named self-propping has never been switched on

```
self_propping_scale = 0.0     in all 155 decks that set it
retention_residual  = 0.28 / 0.715 / 0.747
```

`retention_residual` only multiplies `dilation_term`, which is **identically zero in
kinematic mode**. So:

| specimen | `use_kinematic_aperture` | `retention_residual` | propping pathway |
|---|---|---|---|
| SW-T1 | true | inert | kinematic gap carrying unload retention |
| SW-T2 | true | inert | kinematic gap carrying unload retention |
| SW-S3 | false | 0.28, active | gap + retained dilation term |
| SW-S4 | false | 0.28, active | gap + retained dilation term |

**The two specimen families do not share a propping pathway.** Worth stating before
attributing any specimen difference to roughness, and it may partly explain why retained
enhancement came out uncorrelated with the roughness parameters in §6.7.

## 2.2 The frame caveat — most apparent propping is the testing machine

`100_01` at its first 8 MPa hold and its last one, same injection pressure:

| | t = 200 s | t = 3500 s |
|---|---:|---:|
| axial command | −0.00073121 m | −0.00073121 m |
| differential stress | 150.19 MPa | 62.01 MPa |
| shear stress | 67.50 MPa | 27.87 MPa |
| sigma'_n | 65.68 MPa | 40.91 MPa |
| a_h | 1.630 µm | 3.543 µm |

**The piston never moved and 88 MPa of axial load disappeared** — 0.54 mm of slip
unloaded the machine spring. The raw ×2.17 in aperture and ×10.3 in Q are mostly retained
frame unloading. Only matched-sigma'_n comparisons may be quoted. Two different
matched-stress metrics are in play and they differ by ~2.5× in k — see §4.3.

## 2.3 The model has no time scale at all in the held state

Every term in the aperture budget is a function of the current stress, the current
mechanical gap, or a history variable monotone in slip. **No term contains `t` or `dt`.**
Measured on `100_01` over the last 300 s of its 8 MPa hold: slip identical to 10
significant figures, a_h 3.54317 → 3.54316 µm, Q 0.542246 → 0.542244 mL/min.

The 104-series showed the same from the other side: a ten-fold change in shut-in decay
time moved retained permeability by ≤1.6 %.

**So "how long until the fracture returns to its initial state" was answered by the input
file, not by the physics.** That is what the 108 series was built to change.

---

# Part 3 — The 108 series: design

Three arms plus controls. Full design rationale in `RUN_LIST_108_SERIES.md`.

- **Arm A, reconfinement** (108_03–06): step confining pressure ×1.5→×3.5 after the
  protocol; measures retained a_h vs sigma'_n against the virgin closure curve. No
  rebuild. Targets Kalantar's actual (stress-path) loss mechanism.
- **Arm B, retention lag** (108_07–10): switch on `normal_unload_retention_time`, which
  was implemented and set to `0.0` in all 164 decks. No rebuild.
- **Arm C, closure creep** (108_11–16): new opt-in `use_closure_creep` in
  `ADOrcaRoughnessDamageFracturePermeability`, supplying the pressure-solution /
  asperity-indentation time scale that the cyclic-realism back-analysis identified as the
  one genuinely absent mechanism. Requires `orca_v11`.
- **Controls** (108_01–02): parents unchanged, run the same 1e6 s.

**Source change verification.** Flag off is bit-compatible with the HPC baseline
(`hydraulic_aperture_um_pp` 1.659597423 and `differential_stress_reaction_mpa_pp`
6.142971516 identical to every printed digit). Flag on integrates its own ODE to better
than 0.65 %, the residual being pointwise-vs-side-averaged N_eff on a nonlinear rate law.

---

# Part 4 — The 108 wave-1 results (10 of 10 downloaded)

## 4.1 The controls pass, harder than predicted

| | hold length | a_h drift | slip advance |
|---|---|---:|---:|
| `108_01` SW-T1 | 1e6 s, 540 steps | **0.00 ppm** | **0.0000 nm** |
| `108_02` SW-S4 | 1e6 s, 541 steps | **0.00 ppm** | **0.0000 nm** |

Not "a few ppm" — exactly zero, at time steps up to 2000 s. **The model has no time scale
whatsoever in the held state**, and every arm-B and arm-C signal is therefore fully
attributable to its own mechanism. This is now the definitive statement, not an inference
from a 130 s window.

## 4.2 Arm B — the prediction was WRONG, and the correction matters

Predicted in `RUN_LIST_108_SERIES.md` §3: *"a lag toward the propped state, never a decay
away from it… it cannot produce a closing fracture at any value of tau"*, converging in
about 3 tau.

**Half of that was wrong.** SW-T1 aperture during and after the hold:

| t (s) | tau=0 (control) | tau=150 | tau=1500 | tau=15000 |
|---:|---:|---:|---:|---:|
| 3370 | 3.543165 | 3.875658 | 4.084742 | 4.114554 |
| 5000 | 3.543165 | 3.722295 | 4.041134 | 4.109619 |
| 20000 | 3.543165 | 3.544816 | 3.778441 | 4.064097 |
| 60000 | 3.543165 | 3.543290 | 3.584174 | 3.962247 |

**Arm B does produce a time-dependent closing fracture** — 4.114 → 3.962 µm and still
falling at tau = 15000 s. What was right is the *destination*: all three converge back to
the tau = 0 state, so it is a delayed approach, not a healing mechanism, and it cannot
close below the propped equilibrium.

What was wrong is the *rate*. Effective relaxation times measured from the decay:

| nominal tau (s) | tau_eff (s) | ratio |
|---:|---:|---:|
| 150 | ~3 000–3 300 | **21×** |
| 1 500 | ~19 000–23 500 | **13–16×** |
| 15 000 | ~178 000–186 000 | **12×** |

**tau_eff ≈ 12–21× the input parameter.** The mechanism is a feedback the source reading
missed: `updateNormalUnloadState` relaxes toward `fraction × recovered_closure`, but
`recovered_closure` depends on `raw`, which is the *solved* closure — and a more-open
joint carries higher sigma'_n against the frame (46.2383 / 46.2389 / 46.2608 / 46.3431
MPa at t = 6e4 for tau = 0/150/1500/15000). That raises the target, partially sustaining
the retained opening.

**Practical consequence: `normal_unload_retention_time` is NOT the observed decay time.
It is roughly 1/15th of it.** Anyone calibrating it against data must not read it off a
decay curve directly.

## 4.3 Arm A — a real answer on the tensile pair, and a model-form wall

Retained a_h against the virgin (pre-slip) branch at matched sigma'_n:

| specimen | 55 MPa | 65 MPa | verdict |
|---|---:|---:|---|
| SW-T1 | ×2.088 | ×2.029 | propping survives full reconfinement to the datum stress |
| SW-T2 | ×2.060 | ×2.043 | same |
| SW-S3 | — | — | no usable range (see below) |
| SW-S4 | — | — | no usable range (see below) |

Stable at ~2.0× in aperture (≈4.1× in k) all the way back to the original datum stress.
**The propping is real and it is not undone by restoring the normal stress that slip shed.**

**But the ladder ran into a hard model-form limit.** `computeStressAperture` clamps:

```cpp
ADReal stress_aperture = V_m * (g_ref - g_n);
if (stress_aperture < 0) stress_aperture = 0;
```

Above `reference_effective_normal_stress` the closure term is negative and is clamped to
zero, so **the aperture cannot close any further with increasing normal stress**. The
reference stresses are SW-T1 65.47, SW-T2 66.74, SW-S3 32.1, SW-S4 31.0 MPa, and the
ladder ran to 87–105 MPa. Consequences:

- SW-T1/SW-T2: rungs 1–2 (46–65 MPa) are inside the valid range and give the numbers
  above; rungs 3–5 are in the dead zone.
- SW-S3: a_h frozen at 1.5160–1.5165 µm across 45→85 MPa. The **entire** ladder is above
  its 32.1 MPa reference.
- SW-S4: pinned at exactly 0.7400 µm = `min_hydraulic_aperture` = a_h0. Clamped at the
  floor, nothing measured.

The clamp is correct for the calibration protocol — injection only ever *lowers* sigma'_n
below the datum — and wrong the moment the joint is reconfined above it. **This is a
design error in arm A, not a discovery about the rock**, and it is why the saw-cut pair
returned nothing.

Both tensile virgin curves are also nearly flat (SW-T1 1.6300→1.6655 µm because its
stress-aperture term is identically zero; SW-T2 delivers only 0.14 µm across 25.8→67.4
MPa because sigma0 = 15.0 MPa sits far below its stress range). **Arm A's ability to
measure alpha is limited by the very aperture-law defect the 106 series was built to
fix.**

Note the metric conflict: this section's matched-sigma'_n ratio (~4.1× in k against the
*virgin pre-slip* branch) is not the 101-series ×1.61 (against the *injection loading
path* at the end-state stress). They answer different questions and must not be quoted
interchangeably.

## 4.4 One run diverged

`108_04_swt2_reconf3p5x` reached 5164 of 5552.53 s and then **diverged** during the
×3.0→×3.5 confining ramp: cumulative slip runs 0.005 → 0.078 → 0.18 → 0.55 → 2.9 → 112 →
269 → 901 m within one time value, with a_h pinned at a_h0. Usable to t = 5100 s (the
×3.0 hold, sigma'_n 92.1 MPa, a_h 2.5212 µm, slip 0.5661 mm) — 4 of 5 rungs. The
divergence is downstream of the aperture floor being reached.

---

# Part 5 — The 106 and 107 calibration results

## 5.1 SW-T1 is now at 1.473 %, and the bracket is closed

| deck | cohesion (MPa) | aperture_scale | mean nRMSE | Q | sigma_n | tau | d_n | d_s |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 100_01 (Aug-26 best) | 26.88 | 0.016 | 2.689 | 4.51 | 1.44 | 1.98 | 4.58 | 0.93 |
| 106_01 | 26.88 | 0.01512 | 2.030 | 1.16 | 1.45 | 1.99 | 4.63 | 0.93 |
| **107_01** | **27.20** | **0.01512** | **1.473** | 1.16 | 1.46 | 2.00 | **1.80** | 0.94 |
| 107_04 | 27.35 | 0.01512 | 1.894 | 1.16 | 1.46 | 2.01 | 3.89 | 0.95 |

**Interior minimum at cohesion 27.20 MPa — the bracket is closed** (26.88 → 2.030,
27.20 → 1.473, 27.35 → 1.894). The aperture rescale bought Q (4.51 → 1.16) and the
cohesion bought d_n (4.63 → 1.80). Published final was 4.435; this is a **67 % reduction**.

`107_02` (27.5) and `107_03` (27.8) are **partial, 5/11 stages** — higher cohesion delays
or suppresses the slip event and the runs do not reach the post-event stages. That is the
physical edge of the bracket, and it is consistent with the minimum being interior.

## 5.2 Campaign standing

| | SW-T1 | SW-T2 | SW-S3 | SW-S4 | mean |
|---|---:|---:|---:|---:|---:|
| published finals | 4.435 | 2.428 | 4.574 | 6.139 | 4.394 |
| best-on-disk, 2026-08-26 | 2.689 | 2.132 | 4.354 | 6.139 | 3.829 |
| **now** | **1.473** | 2.132 | 4.354 | 6.139 | **3.525** |

**−19.8 % against the published finals, −7.9 % since 26 August.** All of the recent gain
is SW-T1; the other three specimens are unmoved.

## 5.3 Three predictions of mine were falsified by the 106 results

**(a) The hydraulic Barton–Bandis refit failed on every specimen.**

| deck | predicted Q nRMSE | actual Q | actual mean | baseline mean |
|---|---:|---:|---:|---:|
| 106_02 SW-T1 | 0.314 % | **42.1** | 14.903 | 2.689 |
| 106_05 SW-T2 | 2.502 % | **33.0** | 10.151 | 2.132 |
| 106_10 SW-S4 | 2.183 % | **43.2** | 18.135 | 6.139 |

`scripts/retune_aperture_law.py` predicted these by **exact substitution** —
`Q_new = Q_model (a_h_new/a_h_model)³` — holding everything else fixed. Turning on
`use_nonlinear_normal_closure` changes the coupled solution: aperture feeds flow, flow
feeds pressure, pressure feeds sigma'_n, which feeds aperture. **The substitution
assumption is invalid for the BB branch and the tool must not be used to predict it.**
The one arm it got approximately right (106_01, the pure `aperture_scale` rescale,
predicted 1.125 % and delivered 1.16 %) is the one where nothing else changes.

**(b) The unload-reclosure hypothesis is wrong on both tensile specimens.**
106_03 (SW-T1, retention 0.94→0.70) scored 6.147 against 2.689. 106_06 (SW-T2,
0.84→0.60) scored 2.584 against 2.132. Both worse; the hypothesis is dropped.

**(c) The SW-S4 residual-friction correction is wrong.**
The stage-4 envelope inversion said phi_peak was 1.083° too high and phi_r was the only
lever. 106_08 (21.60°) scored 6.594 and 106_09 (22.10°) 6.308, against 6.139. Both worse.
**SW-S4 remains at 6.139 and is unimproved by anything attempted since the 93 series.**

## 5.4 The stress-dependent shear stiffness (orca_v9) does not run

All four k_t decks **stalled at t ≈ 57–71 s**, in the axial preload ramp (t = 2–55 s),
before injection begins — thousands of output rows for 57 s of simulated time, i.e. the
solver crawling at `dtmin`.

| deck | penalty_tangent | floor | k_t at preload end |
|---|---:|---:|---:|
| parent 100_01 | 1e13 | — | 1e13 |
| 106_12 | 1.18e12 | 0.05 | ~5.4e11 (**18× softer**) |
| 106_13 | 3.0e12 | 0.05 | ~1.4e12 (7× softer) |

The source change itself is verified correct (18× shear compliance, converging, in the
local check). **The decks are mis-parameterised for the preload path**: the joint is far
too compliant in shear while the frame is being loaded, before the stress that the law
keys on has built up. The floor is not the binding constraint at the stall point —
sigma'_n/sigma_ref ≈ 0.46 there, well above 0.05 — so the problem is the calibrated
stiffness itself being unreachable during preload.

**Fix for the next attempt:** activate the softening only after preload (a slip- or
time-gated ramp, exactly like `_reversible_normal_opening_activation_slip` does for the
normal branch), so the joint is stiff while mated and soft once sheared. That is also the
more defensible physics.

---

# Part 6 — Coverage audit

## 6.1 Ye & Ghassemi

| series | decks | complete results | gap |
|---|---:|---:|---|
| 106 | 15 | 11 | 106_12–106_15 stalled at preload (§5.4) |
| 107 | 4 | 2 | 107_02, 107_03 partial at 5/11 stages |
| 108 wave 1 | 10 | 9 | 108_04 diverged at 93 % (§4.4) |
| 108 wave 2 | 6 | running | — |

## 6.2 Kalantar 2025 — OG-T is systematically under-run

| round | OG-SH | OG-SC | OG-T |
|---|---|---|---|
| r1, r3, r4, r5, r7 | OK | OK | OK |
| r6 | OK | OK | **MISSING** |
| r8 | OK ×2 | OK ×2 | **MISSING** |
| r9 | OK | OK | *no deck* |
| r10 | OK ×2 | — | **MISSING** |

Genuinely missing: `110_14_og_t_bbfast_r6`, `110_23_og_t_graded_preload_r8`,
`110_29_og_t_graded_full_r10`. OG-T also has no r9 deck at all, so it effectively stops
at r5 plus two probes while the other two specimens ran through r9/r10.

**This matters for a self-propping study specifically.** In Kalantar's paper the shear
fracture *loses* permeability to gouge, and it is the **tensile and saw-cut** fractures
that self-prop. OG-T is the specimen the self-propping claim rests on, and it has the
thinnest coverage.

Also present: three unrun duplicate decks — `110_04_og_t_preload_probe`,
`110_08_og_t_preload_probe`, `110_11_og_t_preload_probe` — colliding on indices already
used by `og_t_bbfast_r3/r4/r5`. Only the copy at index 14 was ever run. These are index
collisions to clean up, not real gaps.

---

# Part 7 — Repository defects found and fixed

1. **`submit_106.sh` would have failed on all fifteen decks.** It `cd`s to
   `<spec>/Sweeps` and runs `-i <stem>.i`, but MOOSE resolves relative paths against the
   *input file's* directory, so `mesh_file = mesh/...` resolved to `Sweeps/mesh/`, which
   does not exist. Reproduced with `--check-input`. Fixed: 106 decks use `../mesh/...`,
   and their per-deck scripts now chdir to `Sweeps`. The 108 decks carry the fix from
   birth. *(This was found before the 106 runs; the results in §5 are from the fixed decks.)*
2. **Five scripts pointed at the deleted `doc/independent_analysis/`** after the
   2026-08-27 reorganisation: `analyze_101.py`, `analyze_104.py`,
   `update_table2_ranking.py`, `build_mc_bbfast_comparison_notebook.py`,
   `audit_analysis_coverage.py`. Repointed to `Examples/YeGhasemmi2018/Docs/Memory/`.
3. **The ranking rebuild was broken by the same reorganisation** — 14 of 97 recorded
   `source_csv` paths were stale, and several results now exist in two places where only
   one has the deck beside it (which `table2_gate` needs). `update_table2_ranking.py` now
   resolves by basename, preferring the copy whose deck is findable, and writes the
   resolved path back so the CSV self-heals.
4. **`94_05_sw3_mc_final.i` no longer exists anywhere in the tree** — only its submission
   script and its results survive. The rebuild now flags that row
   `deck_missing_scores_not_recomputed` instead of aborting. **This deck should be
   recovered from git history if the SW-S3 Mohr–Coulomb baseline is to be quoted.**
5. The 106 series is now in the ranking (112 rows, was 97).

---

# Part 8 — What to do next, in priority order

1. **Close SW-T1.** Nothing further is needed — 107_01 at 1.473 % has an interior minimum
   and a closed bracket. Adopt it and record the adoption as a calibration decision in
   the methods, not the results.
2. **Re-run 107_02/107_03 only if the upper edge matters.** They are partial because the
   slip event does not fire at cohesion ≥ 27.5 MPa. That is a reportable physical edge and
   may not need a completed run.
3. **Fix and re-run the k_t arms** with a slip- or time-gated activation so the preload
   stays stiff. This is the only route to the shear-creep behaviour that no constant
   tangential stiffness can reproduce.
4. **Redesign arm A below the reference stress.** The reconfinement ladder must stay
   inside each specimen's valid closure range — 46→65 MPa for the tensile pair, and for
   the saw-cut pair the ladder needs to start *below* 31 MPa, which means reducing
   confinement, not raising it. As built, the saw-cut arms measured nothing.
5. **Run the three missing OG-T rounds** (r6, r8, r10) before leaning on Kalantar for the
   self-propping comparison. It is the specimen the claim depends on.
6. **Do not pursue** the BB hydraulic refit (§5.3a), the unload-reclosure hypothesis
   (§5.3b), or the SW-S4 phi_r correction (§5.3c). All three are falsified.
7. **Retire or re-scope `scripts/retune_aperture_law.py`.** Its exact-substitution
   assumption is only valid when nothing else in the coupled solution changes.
