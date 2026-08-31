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

---

# Part 9 — The 108 wave-2 results (arm C, closure creep; 6 of 6 downloaded)

Reproduce every number below with `python3 scripts/ye_series108_wave2.py`. All six runs
reached their target end time; none truncated.

## 9.1 The controls pass to the limit of the print precision

`108_01` (SW-T1) and `108_02` (SW-S4), unchanged parents held for 1e6 s:

| | a_h(T_p) | drift over 1e6 s | spread over the hold |
|---|---:|---:|---:|
| SW-T1 | 3.543165 µm | **0.00 ppm** | 0.00 ppm |
| SW-S4 | 0.760726 µm | **0.00 ppm** | 0.00 ppm |

Not "small" — *identical to every printed digit*, over four orders of magnitude in time
and three in step size. §0 predicted convergence rather than decay and this is the
strongest form of that: the held state is a fixed point of the whole coupled system, not
merely a slowly-moving one. Arms B and C are therefore reading physics, not integration
drift.

They also score **exactly** as their parents against Table 2 (Δ = ±0.0000 % on both), so
extending the schedule to 1e6 s does not perturb the calibrated window at all.

## 9.2 The rate law integrates correctly, and unlike arm B its time constant is honest

Model `closure_creep_aperture_um_pp` against the same ODE reintegrated offline from each
run's own `effective_normal_compression` trace:

| run | max rel. deviation | at t (s) | a_c/a_cmax there | at saturation |
|---|---:|---:|---:|---:|
| `108_15` τ_c = 1e4 | 3.48 % | 1.96e4 | 0.744 | 0.00 % |
| `108_11` τ_c = 1e5 | 4.26 % | 1.29e5 | 0.596 | 0.58 % |
| `108_16` τ_c = 1e6 | 4.35 % | 1.00e6 | 0.507 | 4.35 % |
| `108_12` SW-T2 | 7.92 % | 4.15e4 | 0.253 | 0.51 % |
| `108_13` SW-S3 | 0.85 % | 4.18e4 | 0.291 | 0.01 % |
| `108_14` SW-S4 | 0.76 % | 2.52e3 | 0.019 | 0.00 % |

The deviation peaks **mid-transient and vanishes at saturation**, which is the signature
of the known cause and not of an integration error: the material integrates the ODE
pointwise at each qp on the local N_eff, while the offline check can only use the
side-averaged postprocessor, and the *solution* is nonlinear in the rate even though the
rate law (q = 1) is linear in N_eff. Both curves are pinned to the same asymptote
`a_cmax`, so the discrepancy has to close. The verification in the run list measured
0.65 % over the first 26 s; over 1e6 s it reaches 4–8 %, which is the number to quote.

**The time constant is interpretable — this is the contrast with arm B.** Observed 63.2 %
time against the predicted τ_eff = τ_c·σ_ref/N_eff:

| run | N_eff(end) MPa | τ_pred (s) | t(63.2 %) | ratio |
|---|---:|---:|---:|---:|
| `108_15` | 45.96 | 1.425e4 | 1.562e4 | **1.096** |
| `108_11` | 46.05 | 1.422e5 | 1.549e5 | **1.090** |
| `108_16` | 46.22 | 1.416e6 | not reached | — |
| `108_12` | 46.51 | 1.435e5 | 1.635e5 | **1.139** |
| `108_13` | 26.78 | 1.199e5 | 1.238e5 | **1.033** |
| `108_14` | 25.37 | 1.222e5 | 1.245e5 | **1.019** |

2–14 % high, against arm B's **12–21×**. `normal_unload_retention_time` is not the
observed decay time; `closure_creep_time` is, to within 14 %. The difference is
structural: arm B's retained opening raises its own target through the frame (§4.2),
whereas creep subtracts from `a_h` only and its target `a_cmax` is fixed, so the only
feedback left is the weak pressure path of §9.4.

## 9.3 a_h does NOT return to a_h0 — the aperture floor stops it

`closure_creep_max_aperture` was set to each run's own retained gain precisely so that the
asymptote would be the pre-stimulation aperture and the deck would answer a pure timing
question (design decision 2). **It does not, on any of the four specimens:**

| run | a_h(T_p) | a_h(end) | a_h0 | a_min | a_c/a_cmax | gap to a_h0 | k(end)/k(T_p) |
|---|---:|---:|---:|---:|---:|---:|---:|
| `108_15` τ_c = 1e4 | 3.0835 | 1.8496 | 1.6300 | 1.5105 | 1.000 | **+0.2196** | 0.3598 |
| `108_11` τ_c = 1e5 | 3.4915 | 1.8490 | 1.6300 | 1.5105 | 0.993 | **+0.2190** | 0.2804 |
| `108_16` τ_c = 1e6 | 3.5379 | 2.6166 | 1.6300 | 1.5105 | 0.485 | +0.9866 | 0.5470 |
| `108_12` SW-T2 | 4.3592 | 2.1764 | 2.1100 | 2.0045 | 0.994 | **+0.0664** | 0.2493 |
| `108_13` SW-S3 | 1.5665 | 1.2338 | 1.2200 | 1.2200 | 1.000 | **+0.0138** | 0.6203 |
| `108_14` SW-S4 | 0.7602 | 0.7501 | 0.7400 | 0.7400 | 1.000 | **+0.0101** | 0.9736 |

`τ_c = 1e4` and `τ_c = 1e5` both end at 1.8490–1.8496 µm with a_c fully spent. They have
converged, to the *same* place, and it is **0.22 µm above** the aperture the budget says
they should reach. So the crossing time the run list asked for does not exist, and no
longer run produces it.

**The cause is the pointwise `min_hydraulic_aperture` clamp.** Reconstructing SW-T1's
budget term by term at t = 1e6 s from the exported postprocessors gives
`a_h0 + a_σ + χ a_m − a_gouge − a_c` = 1.6883 µm against an actual 1.8490 µm — a residual
of **+0.161 µm**, where the same reconstruction on the control leaves −0.040 µm. The
difference is the clamp: `a_min` = 1.5105 µm binds *pointwise* over part of the interface
while the reported aperture is a side average, so the average sits above the unclamped
budget. On SW-S3 and SW-S4 the effect is trivially visible because `a_min` was set equal
to `a_h0` — those two specimens **cannot** go below their initial aperture by
construction, and the +0.014/+0.010 µm gaps are the same averaging effect at a floor that
is already the target.

This is the third independent place a numerical guard is doing physical work: `a_max`
bounds retained aperture in the manuscript's §6.11.3 limitation, `computeStressAperture`'s
zero clamp killed arm A above the reference stress (§4.3), and `a_min` now bounds closure
in arm C. **Report the clamps as part of the constitutive law, because that is how they
behave.**

## 9.4 A hydraulic-only term is not hydraulically isolated

Design decision 1 said closure creep "subtracts from `a_h` and does not feed back on the
traction". That is true of the *direct* path and false of the coupled solution. SW-T1
`108_11` against its control at t = 1e6 s:

| | control `108_01` | creep `108_11` | change |
|---|---:|---:|---:|
| `a_h` | 3.5432 µm | 1.8490 µm | −1.694 |
| interface pressure | 5.896 MPa | 6.057 MPa | **+0.161** |
| σ'_n (BB) | 46.238 MPa | 46.046 MPa | **−0.192** |
| χ·a_m | 1.9526 µm | 1.9587 µm | +0.006 |
| Q | 0.5422 mL/min | 0.0771 mL/min | ×0.142 |
| k | 10.974 | 2.933 (1e-13 m²) | ×0.267 |

Closing the fracture lowers its transmissivity, which raises the pressure it holds against
the shared field, which lowers σ'_n, which opens it back. The loop is weak — 0.19 MPa and
0.006 µm — but it is present, it is the H→M direction of the manuscript's §3.6.2 coupling
tables, and it means **no term in this model is hydraulic-only once the pressure field is
shared.** State design decision 1 as "no direct Jacobian coupling", not as "no feedback".

The Q and k ratios confirm the cubic law is intact end to end:
(1.8490/3.5432)³ = 0.142 and (·)² = 0.272 against the measured 0.142 and 0.267.

## 9.5 The 3500 s protocol DOES bound τ_c — arm C is not unconstrained

The run list assumed arm C was unscoreable and purely exploratory. It is unscoreable
against `a_cmax`, which was imposed. It is **not** unconstrained in τ_c, because creep runs
during the protocol (design decision 3) and leaves a signature in the unloading-branch
flow rate. Scoring each arm-C run over its protocol window on the *parent's* stage clock
— the arm-C decks extend `injection_pressure` to 1e6 s, so their own schedule would sample
stage 11 a million seconds late:

| sample | run | Q | σ'_n | τ | d_n | d_s | mean nRMSE % | vs parent |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SW-T1 | parent `100_01` | 4.5107 | 1.4400 | 1.9784 | 4.5836 | 0.9304 | 2.6886 | — |
| SW-T1 | control `108_01` | 4.5107 | 1.4400 | 1.9784 | 4.5836 | 0.9304 | 2.6886 | ±0.0000 |
| SW-T1 | τ_c = 1e4 | 5.5192 | 1.4142 | 1.9461 | 4.4470 | 0.9849 | 2.8623 | **+0.1737** |
| SW-T1 | τ_c = 1e5 | **3.3666** | 1.4351 | 1.9720 | 4.5710 | 0.9323 | **2.4554** | **−0.2332** |
| SW-T1 | τ_c = 1e6 | 4.3939 | 1.4395 | 1.9778 | 4.5824 | 0.9306 | 2.6648 | −0.0238 |
| SW-T2 | parent `100_04` | 4.3355 | 1.2742 | 1.7230 | 2.0669 | 1.2597 | 2.1319 | — |
| SW-T2 | τ_c = 1e5 | 4.4818 | 1.2486 | 1.6882 | 2.0584 | 1.2514 | 2.1457 | +0.0138 |
| SW-S3 | parent `100_06` | 3.0605 | 3.0697 | 7.3916 | 6.1740 | 2.0731 | 4.3538 | — |
| SW-S3 | τ_c = 1e5 | 2.9063 | 3.0394 | 7.3223 | 6.1346 | 2.2045 | 4.3214 | −0.0324 |
| SW-S4 | parent `93_07` | 5.0053 | 3.8723 | 10.1029 | 4.6332 | 7.0822 | 6.1392 | — |
| SW-S4 | control `108_02` | 5.0053 | 3.8723 | 10.1029 | 4.6332 | 7.0822 | 6.1392 | ±0.0000 |
| SW-S4 | τ_c = 1e5 | 5.0249 | 3.8712 | 10.0999 | 4.6357 | 7.0867 | 6.1437 | +0.0045 |

**SW-T1's Q channel brackets an optimum near τ_c = 1e5 s.** It falls 4.51 → 3.37 % at
1e5, rises to 5.52 % at 1e4, and is essentially unchanged at 1e6. The other four channels
move by ≤0.14 %, so this is a one-channel effect, and the mean improves by 0.23 pp
(accuracy 97.31 → 97.55 %) entirely on the back of it.

**Why, and how much to claim.** The parent over-predicts Q on the whole unloading branch —
errors +0.44, +0.43, +0.32, +0.21, +0.080 mL/min at stages 7–11, every one positive. Any
mechanism that removes aperture late in the run improves that channel. So the honest claim
is *not* "creep is confirmed". It is:

1. The calibration has a **systematic late-time flow excess**, and a slow closure process
   at τ_c ≈ 1e5 s removes it.
2. **τ_c ≤ 1e4 s is rejected** by the SW-T1 flow data: it over-corrects and costs
   0.17 pp.
3. τ_c and `a_cmax` are **not independently identified** here, because `a_cmax` was pinned
   to each run's own retained gain rather than fitted. The 1e5 result is a one-parameter
   result with the amplitude imposed.
4. The other three specimens have no resolving power (|Δ| ≤ 0.03 pp) — SW-S3 and SW-S4
   because their retained gain, and therefore their imposed `a_cmax`, is 0.36 and
   0.021 µm.

This connects directly to the manuscript's §6.11.3: the aperture budget's only saturating
term is the negative one, so retained aperture is monotone and unbounded in slip and needs
a bounding mechanism the law does not have. Arm C supplies a candidate for that mechanism,
and the SW-T1 flow channel weakly prefers it over having none. That is a genuinely new
line of evidence for a limitation the manuscript currently argues from structure alone.

## 9.6 A repository defect: a diagnostic postprocessor that silently reports zero

`effective_normal_compression` is only written when `_effective_normal_traction` is
non-null, and that pointer is fetched only if one of `normal_stress_aperture_compliance
> 0`, `use_nonlinear_normal_closure`, `compute_effective_normal_compression`, or
`use_closure_creep` is set. The source comment above the assignment says "the diagnostic
above is unconditional". **It is not.** A deck may declare
`effective_normal_compression_mpa_pp` and get a column of exact zeros with no warning.

Affected: the five SW-T1 wave-1 decks — `108_01`, `108_03`, `108_07`, `108_08`, `108_09` —
all of which report 0.000 where `bb_effective_normal_stress_pp` reports 46.2–105.3 MPa.
Every other 108 deck sets `use_nonlinear_normal_closure` or `use_closure_creep` and is
unaffected. Wherever both are live they agree to every printed digit.

**This did not corrupt any recorded result, and §4.3 is confirmed.** `108_03` is the
SW-T1 reconfinement arm, and §8 of the run list directs the analyst at exactly the zeroed
column. Recomputing the matched-σ'_n ratios from `bb_effective_normal_stress_pp` instead
reproduces the recorded table to the digit: SW-T1 ×2.088 at 55 MPa and ×2.029 at 65 MPa,
SW-T2 ×2.060 and ×2.042. The wave-1 analysis used the right column.

Two corrections to §4.3 while it is open: SW-T1's virgin curve is **flat at 1.6300 µm**,
not "1.6300→1.6655" — its stress-aperture term is identically zero, as the same sentence
says. And `scripts/ye_series108_checks.py` reads `effective_normal_compression_mpa_pp` at
three places and will silently produce zeros on any SW-T1 wave-1 deck; it should either
fall back to `bb_effective_normal_stress_pp` or refuse an all-zero column.
