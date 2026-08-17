# Orca 4.0 — project memory

**What this file is.** The running memory of the `orca_4.0` validation effort: every
change made since the `orca_v1` branch, every formulation that was replaced and what
replaced it, every hypothesis that was tested — including the ones that failed — and
the current calibration state of each sample.

**How to use it.** Read §1 for what is open. Read §4 before touching the source: it
records what the old formulations were and why they were wrong, so a "fix" is not
re-applied backwards. Read §7 before trusting any figure: several of the reported
model problems turned out to be defects in the validation data.

**How to keep it.** Append to the section that fits; do not start a new file. Every
entry states what was measured, not just what was concluded. When a claim here is
later shown wrong, correct it **in place and say so** — §6 exists precisely because
wrong hypotheses are worth as much as right ones, and rediscovering a dead end costs
more than recording it. Update §1 whenever a task opens or closes, and add a line to
§10.

Last updated: 2026-08-16.

---

## 1. TODO — what is open right now

Ordered by what unblocks the most. Numbers are the session task IDs.

### Blocking

| # | item | state |
|---|---|---|
| **#70** | ~~Score the SW-T1 normal-closure stiffness bracket `88_01`/`88_02`/`88_03` (§5.6)~~ | **RETIRED 2026-08-16 — Saeed: the SW-T1 results are wrong.** `88_02`/`88_03` ran to completion (t = 3500, 0 non-convergences) and are NOT to be scored; `88_01` never ran and must not be submitted. See §5.10. |
| **#68** | ~~Score `87_01`/`87_02` (SW-T1/SW-T2 injection-schedule refit, §5.5)~~ | **`87_01` RETIRED with the same call** — it is the parent of the 88 bracket and shares whatever the defect is. `87_02` (SW-T2) not covered by the call; still open. See §5.10. |
| **#67 / #60** | **Refit SW-S3 slip onset at α = 0.6.** The only remaining SW-S3 problem. Decks `86_01` (φ_r 8.45) and `86_02` (φ_r 9.00) bracket it. | both running, ~10 h left each |
| **#59** | **Rebuild `orca-opt`** and runtime-verify the three compile-checked-only fixes (§4.2, §4.3, §4.4). Register the `alpha_eff_lagged` test case and generate its gold. | blocked on the campaign draining |
| **#55 / #52** | Finish scoring the Biot A/B pairs; SW-T2 α = 0.6 arm still running (decelerating through its slip event). | running |

**#66 (broken SW-T1 digitized files) is CLOSED** by the 2026-08-16 re-extraction —
see §7.2, which also records that the prediction made there was confirmed to three
digits. The SW-T friction question (§6.5) is therefore unblocked.

### Open, not blocking

| # | item |
|---|---|
| ~~#71~~ | **DONE 2026-08-16** — refit applied; decks `89_01`, `89_02`. See §5.8. |
| ~~#72~~ | **DONE 2026-08-16** — corrected meshes ported and independently re-verified; decks `89_01`, `89_03`, `89_05`, `89_06`. See §5.8. |
| ~~#73~~ | **DECIDED 2026-08-16** — option (a): scope it, do not drop it. The bound stays in §1, stated as (i) enforced in the Mohr–Coulomb law and (ii) used as an admissibility diagnostic on Table 2. Draft rewritten in §1 and §3.5.3. |
| ~~#74~~ | **DONE 2026-08-16** — the 89-series SW-S4 decks carry `effective_normal_paper_frame_mpa_pp` and `shear_stress_paper_frame_mpa_pp`. |
| **#75** | **Score the six 89-series decks.** `89_01`/`89_06` (SW-S4) and `89_03`/`89_05` (SW-T2) are controlled pairs that separate the mesh effect from the strength effect. `89_04`/`89_05` are **candidates, not corrections** — they change dτ/dσ′ₙ by ~40 % and have to beat `87_01`/`87_02` on Table 2 before replacing them. |
| ~~#76~~ | **DONE 2026-08-16** — Saeed built it in Cubit at sizes 3 and 5. Verified L 123.40 / D 50.53 / θ 29.000; source nodes re-derived and on the interface at 0.0 µm; deck renamed `89_02_..._L123p4_...`. The 124.40 mm meshes are **kept** — eleven pre-audit decks use them. See §5.9. |
| **#77** | **Re-gate SW-S3's `axial_pres_final`** on the 123.40 mm mesh. The piston is displacement-controlled and the deck's sizing note has L explicit (`4.13e11*(100.28/L)`), so the rock-compliance part of the −6.41358437936e-5 m gate scales by 123.40/124.40 while the joint and penalty parts do not. Bounded: the correction is between 0 and −0.52 µm, i.e. **at most 0.25 MPa** of preload, so the run is not invalid without it — but it sits right at the 0.5 MPa tolerance. Gate against Table 2 stage 1 (σ′ₙ 31.65, τ 14.70 MPa). |
| #65 | Unify the rock parameters (§5.1). E is settled. φ_r is now explained rather than open (§5.7 item 2) but the T/S split stands. **Add `normal_unload_retention_fraction` to the list** — it is 0.94 / 0.84 / 0.04 across SW-T1 / SW-T2 / SW-S4 (§4.7) and it is a joint property, not a free knob. Also re-gate SW-S3's `axial_pres_final`, whose comment still reads `# E=75 GPa`. |
| #69 | Refresh SW-S3's injection schedule from the re-extraction (RMSE 0.243 MPa, lags up to +24 s — acceptable, not ideal). Fold into the next SW-S3 iteration *after* the φ_r bracket resolves, so it does not invalidate `86_01`/`86_02` mid-flight. |
| #13 | Make the flow measurement mesh-independent |
| #15 | Correct the slip-onset strength envelopes (superset of #60) |
| #14 / #19 | SW-S3/SW-S4 non-convergence at the slip/arrest event. New lead in §6.4: not the aperture law — look at the disabled negative-feedback stack |
| #50 | Decide the fate of the stale split mass-balance kernel pair (TODO §N1) |
| #20 | Explain SWT2_BBFast's 800 s LU regression |
| #21 | Re-run SWS4_MC mesh3 LU retry with more memory |
| #31 | Launch queued decks — on hold pending #14 |
| #42 | Commit the v26/v27 work in `orca_3.0_full` |

### Known but deliberately not done

- **`orca-opt` has not been relinked at any point in this work.** Every run in the
  campaign is against one unchanging shared library, which is what makes the A/B
  comparisons mean anything. The cost is that four source fixes are compile-checked
  only. This is a deliberate trade, not an oversight — see #59.
- **Cohesion is not implementable today.** `computeCohesionEffective()` returns a
  hard-coded `0.0` with no input parameter and no subclass override (§6.5).

---

## 2. Version map

Branch per unit of work; source changes never land on `main`.

| branch | commits | span | content |
|---|---|---|---|
| `orca_v1` | 5 | `2f24990` → `8a1aa0f` | initial import of the 93-file source tree; `OrcaTHMaterial` self-containment; Bakhtar permeability material; velocity aux kernels |
| `orca_v2` | +6 | `7fe8589` → `242ba51` | 17-deck set completed and normalised, SLURM generated, `doc/SOURCE_COMPARISON.md`, kernel_SV deck set (18 decks), mesh-size-3 set, local Biot A/B runner |
| `orca_v3` | +3 | `0cbc441` → `cfd5f60` | four-sample Table-2 gate, Biot α A/B campaign method + analytical justification, A/B scorer |
| `orca_v4` | +26 | `ba43f88` → `2a4a473` | the regression/verification suite, four source defects found and fixed, the Bakhtar negative result, the cross-sample parameter audit, the validation-data audit, the SW-S3 refit |

Total 40 commits ahead of `main`.

---

## 3. What this project is trying to do

Reproduce the Ye & Ghassemi (2018) hydraulic-shearing experiments on Sierra White
granite in Orca, well enough to publish. Four specimens:

| sample | fracture | notes |
|---|---|---|
| SW-S3 | shear | best-calibrated; within 4% on every channel at α = 1e-12 |
| SW-S4 | **saw-cut** (documented) | the reference calibration; already at physical α = 0.6 |
| SW-T1 | (type not confirmed — see §6.5) | τ and stresses good; kinematics unscoreable, see §7.2 |
| SW-T2 | as SW-T1 | running |

Eleven Table-2 injection hold stages per sample. Five observables: Q, σ'ₙ, τ, dₙ, d_s.

---

## 4. Source formulations: what was there, what is there now

**This is the section to read before editing the source.** Four defects were found in
`orca_v4`. Every one of them was *silent*: the run converged cleanly and produced a
plausible answer with a physical term missing.

### 4.1 The storage term read like a multiplication — `ba43f88`

`OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel.C`. The material stores **M**,
not 1/M, and the comment said the opposite:

```cpp
// OLD — comment claimed the property might hold (1/M); code multiplied
_storage_rate_p = dpdt * 1/_biot_modulus[_qp];

// NEW
_storage_rate_p = dpdt / _biot_modulus[_qp];
```

The two forms evaluate identically — `(dpdt*1)/M` by left-associativity — so this was
**not a behaviour change**. It was a correctness-of-reading change: the expression read
as a multiplication by a property holding M, and the next person to "simplify" it would
have introduced a factor of M² ≈ 1e22. Locked by `test/tests/kernels/mass_storage`,
which checks `p(t) = M q t` in closed form.

`OrcaTHMaterial::computeBiotModulus` builds the compliance
`1/M = (1-α)(α-φ)/Kd + φ/Kf` and stores its **reciprocal**.

### 4.2 `vol_strain_rate` lost on the total-strain path — `7596413`

`OrcaMechMaterial::computeTotalSmallStrain()` never called `computeVolumetricStrain()`.
`computeIncrementalStrain()` did.

```cpp
// NEW — must be called on BOTH strain paths
computeVolumetricStrain();
```

With `strain_model = total`, `vol_strain_rate` stayed at the `0.0` set in
`initQpStatefulProperties`, so any HydroMechanical mass kernel **silently lost its
`α·div(du/dt)` coupling**. No production deck was affected — all use `incremental`.
Covered by `test/tests/verification/terzaghi` (`total_strain` case).

### 4.3 α < φ was accepted in silence — `e4230e5`

`OrcaTHMaterial::computeBiotModulus`. Biot's coefficient cannot physically be below the
porosity: `(α − φ)` goes negative and the grain-compressibility term **subtracts** from
fluid storage instead of adding to it. `1/M` stays positive because the fluid term
dominates, so there is no other symptom. SW-S3/SW-T1/SW-T2 carried α = 1e-12 against
φ = 1e-3 for a long time on exactly that silence.

Now `mooseDoOnce(mooseWarning(...))` — a warning, not an error, because the value is a
legitimate thing to explore deliberately and erroring would break decks mid-study.

### 4.4 Lagged α_T was never seeded — `63fab01`

`OrcaTHMaterial::computeSolidEffectiveThermalExpansionCoefficient`:

```cpp
// OLD
_alpha_eff_T[_qp] = _alpha_eff_T_old[_qp];

// NEW
_alpha_eff_T[_qp] = (_t_step > 0) ? _alpha_eff_T_old[_qp] : alpha_eff_computed;
```

`initQpStatefulProperties()` routes through `computeQpProperties()`, so the "hold the
previous value" branch also ran at t = 0 and read the zero-initialised property. That
zero became the old value for step 1, and so on: **α_eff was pinned at 0 for the whole
run**, and the kernel's `−α_T dT/dt` term was deleted rather than held constant.
Measured against the shipped binary: p stayed at exactly 0.0 where the closed form
called for 3.58 MPa per step.

No production deck affected — the default is `computed`, and nothing under `Examples/`
couples `temperature` to `OrcaTHMaterial` at all, so the whole thermal path ships
unexecuted.

### 4.5 The bug family — the general lesson

**4.2 and 4.4 are the same defect twice.** Any "lagged / hold the previous value"
branch is *also* executed during `initQpStatefulProperties`, where the `...Old`
property is still zero. The property is then pinned at 0 forever.

**The correct pattern already existed one function away**, in
`OrcaTHMaterial::computeBiotModulus`:

```cpp
const Real Mold = _biot_modulus_old[_qp];
_biot_modulus[_qp] = (Mold > 0.0) ? ADReal(Mold) : M_new;   // seeded fallback
```

**When reviewing any Orca material:** grep for `getMaterialPropertyOld` reads inside
`computeQpProperties`, and check what that branch does on the init pass. Guard on
`_t_step > 0` or use the `(old > 0) ? old : computed` fallback. The symptom is never an
error — it is a plausible result with one physical term missing, so only a closed-form
test catches it.

### 4.6 `OrcaTHMaterial` is self-contained — permanent design decision (`a82a09f`)

Confirmed by the author. Fluid properties come from `OrcaTHMaterial`'s own input
parameters; `SinglePhaseFluidProperties` was removed and stays removed.

**Consequence:** the `orca_4.0` and `HPC_backup/orca_3.0_claude_edits` versions of
`OrcaTHMaterial` are permanently unmergeable. Porting anything between them —
`one_over_biot_modulus_qp` is the live case — must be a hand-picked hunk, **never a
file copy or a merge.**

### 4.7 The rebound: what is constitutive and what is only reported

Asked directly, and the answer is split.

**σ'ₙ rebound — constitutive.** The chain is
`bb_effective_normal_stress_pp = -czm_sigma_n_pp` (a sign flip, nothing more)
← `czm_sigma_n` = component 0 of `interface_traction`
← `OrcaComputeGlobalTractionSmallStrain`
← `OrcaBartonBandisContactTractionFastADHardening`.

`updateNormalUnloadState()` (line 604) feeds the traction directly at line 1077:

```cpp
const ADReal closure_old_candidate =
    raw_closure_old_ad
  + ADReal(..._normal_reclosure_stiffness_multiplier - 1.0...) * recovered_raw_closure
  - ADReal(retained_opening_old);          // the rebound, inside the return mapping
```

Controlled by `normal_unload_retention_fraction`. Called at lines 1084, 1189, 1318,
1503, 1538 — all before the traction is finalised.

**Normal-dilation rebound — still reporting-only.** `updateReportedNormalOpening()`
(line 640) is called at 1107, 1192, 1321, 1530, 1570, always *after* the matching
constitutive update, and its own header says it "cannot perturb traction, displacement,
hydraulic aperture, permeability, or flow."
`reported_reversible_normal_opening_retention_fraction` is documented **"OUTPUT ONLY"**
(line 159).

So `reversible_normal_compliance` and the `reported_reversible_normal_opening_*` family
are **the old postprocessor formula relocated into the material**. It moved house; it
did not become physics. Only the four SW-S4 `68_0*` decks set it. The earlier
`orca_3.0_full` audit predicted this and recommended the replacement, which has **not**
been done:

> Output-only elastic normal rebound … Keep as diagnostic; replace by auto-computed
> normal compliance or nonlinear normal closure in a primary law

---

## 5. Calibration state

### 5.1 Rock parameters across the four decks — and against the paper

Two different questions. Columns SW-S3…SW-T2 answer "are the decks consistent with
each other?"; the **paper** column answers "is the value the one Ye & Ghassemi
report?" The second question is the one that matters and it was not asked until
2026-08-16 — see §5.7. State below is the current production decks (`86_01`,
`68_01`, `87_01`, `87_02`), re-read on 2026-08-16.

| parameter | SW-S3 | SW-S4 | SW-T1 | SW-T2 | paper | verdict |
|---|---|---|---|---|---|---|
| `youngs_modulus` | 67e9 | 67e9 | 67e9 | 67e9 | 67 GPa §2.1 | ✅ settled — was 75e9 in SW-S3 |
| `poissons_ratio` | 0.32 | 0.32 | 0.32 | 0.32 | 0.32 §2.1 | ✅ |
| `biot_coefficient` | 0.6 | 0.6 | 0.6 | 0.6 | not reported | ✅ shared; literature value |
| `initial_porosity` | 0.001 | 0.001 | 0.001 | 0.001 | not reported | assumed; granite is 0.005–0.01 |
| `matrix_permeability` | 5e-19 | 5e-19 | 5e-19 | 5e-19 | 5e-19–1e-18 §2.1 | ✅ low end |
| fluid ρ / μ | identical everywhere | | | | μ 1.002e-3 §2.5 | ✅ |
| `fluid_bulk_modulus` | 4.784e9 everywhere | | | | not reported | **2.17× water (2.2e9)** |
| `confining_pressure` | 30e6 | 30e6 | 30e6 | 30e6 | 30 MPa §2.4 | ✅ |
| `jcs` | **3.0e8** | **3.0e8** | 1.5e8 | 1.5e8 | UCS 150 MPa §2.1 | **S-family 2× — §5.7** |
| `jrc` | **23.35** | **17.5** | 15.32 | 14.63 | 1.96 / 1.19 / 15.32 / 14.63 §2.2 | **S-family 12–15× — §5.7** |
| `residual_friction_angle_degrees` | **8.45** | **7.5** | **44.1** | **46.3** | not reported (intact φ = 46°) | **all four unphysical — §5.7** |
| `dilation_angle_peak_degrees` | 26.0 | 24.0 | 16.44 | 13.97 | Table 2 → 31.8 / 28.7 / 16.44 / 13.97 | T ✅ exact; **S under-set — §5.7** |
| `normal_unload_retention_fraction` | 0.06 | 0.04 | **0.94** | **0.84** | — | see §4.7 |
| Kni / Vm / exponent / offset | identical across all four | | | | — | consistent |

**Young's modulus is settled.** All SW-S3 decks use 75e9, everything else 67e9, and
both carry the *identical* comment `# --- mechanics (OrcaMechMaterial) : DD02
reference values ---`. `orca_3.0_full` still holds the provenance:

```
youngs_modulus = 67e9                       # Pa, paper Sec. 2.1
youngs_modulus = 80e9            # CASE F: reference DD02 value (was 67e9)
```

So **67 GPa is the paper value**, 80 GPa is what "DD02" actually means, and 75 GPa is
neither — it has no provenance anywhere in any repo. The section comment is wrong in
all four decks as well as the SW-S3 number.

### 5.2 Two different aperture laws

| | SW-S3 | SW-T1 |
|---|---|---|
| `use_kinematic_aperture` | false | true |
| `dilation_scale` | **0.038** | 0.0 |
| `use_slip_damage` | true | false |
| `normal_stress_aperture` | active | 0 |

SW-S3 runs the additive path with a **0.038 multiplier on cumulative dilation** — a 26×
discount on the term meant to drive permeability growth. SW-T1 runs the kinematic path
where dilation is already in the mechanical gap. Two different models of the same
fracture.

*Not* a bug: SW-T1's `cumulative_dilation_pp`, `slip_damage_aperture_pp` and
`normal_stress_aperture_pp` are all identically zero because those three terms are
switched off in that deck.

### 5.3 Scorecard — `scripts/sample_scorecard.py`

Peak ratios sim/exp. **SW-S3 at α = 1e-12 is within 4% on every channel.**

| observable | S3 α=1e-12 | S3 α=0.6 | T1 α=1e-12 | T1 α=0.6 |
|---|---|---|---|---|
| differential stress | 0.996 | 0.921 | 0.999 | 0.980 |
| injection pressure | 1.000 | 1.000 | 0.999 | 0.999 |
| flow rate | 1.039 | **1.168** | 1.041 | 1.072 |
| fracture permeability | 1.001 | 1.080 | 1.014 | 1.034 |
| normal dilation | 0.987 | **1.193** | *unscoreable* | *unscoreable* |
| effective normal stress | 1.008 | 1.006 | 1.002 | 0.994 |
| shear slip | 1.010 | **1.265** | *unscoreable* | *unscoreable* |
| shear stress | 0.989 | 1.061 | 0.999 | 1.010 |

### 5.4 The single remaining SW-S3 problem

α = 0.6 breaks the slip calibration, and **every other symptom follows from it**:

| | α=1e-12 | α=0.6 | experiment |
|---|---|---|---|
| onset, 5% of final slip | 2394 s | **2062 s** | 2451 s |
| final slip | 0.0743 mm | **0.0930 mm** | 0.0737 mm |
| diff-stress nRMSE | 15.8% | **42.9%** | |

Dilation is not an independent error: `dilation/slip = tan(dilation angle)` identically
in the output, so fixing slip fixes dilation, and the aperture fixes flow and
permeability behind it.

**Sizing.** In the 330 s before onset the α=0.6 run closes its strength margin
(`limit_tau − tau`) at −0.00150 MPa/s. Delaying onset by the required 389 s needs about
**0.58 MPa** more `limit_tau`. At the operating σ'ₙ of 24.9 MPa,
`d(tau_limit)/d(phi_r) = 0.613 MPa/deg`, so **Δφ_r ≈ 0.95 deg**.

**φ_r, not JRC.** JRC would need only +0.88, but SW-S3 already runs JRC = 23.35, above
the Barton scale's 0–20 range, while φ_r = 7.5° is far below any measured granite basic
friction angle. Raising φ_r moves toward the physical value.

**Why a bracket and not a single answer.** The margin used for sizing is a *side
average* over the whole fracture, while yield begins locally. A side-averaged
extrapolation gives a magnitude, not a prediction. Hence `86_01` (8.45) and `86_02`
(9.00).

### 5.5 The injection schedule is a DRIVER — check it before tuning anything

**Fix the boundary condition before fitting a constitutive parameter to the
response.** SW-T1 and SW-T2 carried hand-built idealised staircases with the right
hold levels (5/8/12/16/20/24/28 MPa) and the wrong transition times. Lag at first
up-crossing of each level, against the 2026-08-16 re-extraction:

| sample | 8 | 12 | 16 | 20 | 24 | 28 MPa | RMSE | verdict |
|---|---|---|---|---|---|---|---|---|
| SW-S4 | −2 | +1 | +2 | −4 | −5 | +0 | 0.060 MPa | densely digitised — fine |
| SW-S3 | +24 | +9 | +22 | +17 | +5 | +1 | 0.243 MPa | acceptable |
| SW-T1 | +48 | +87 | +77 | +102 | +72 | **+155** | **1.240 MPa** | idealised staircase |
| SW-T2 | +53 | +77 | +72 | +55 | +70 | +56 | **1.536 MPa** | idealised staircase |

SW-T1 was worse than its RMSE suggests: the 28 MPa peak hold ran 1824–1955 (131 s)
against a measured 1640–1895 (255 s) — **184 s late and 0.51× the duration**, so the
specimen spent half the time at peak pressure the experiment did and entered the
unload branch from a different state. Note the pressure–time *integral* was within
1% the whole time (0.9906): an integral check would have passed this. Timing errors
hide from integral metrics.

**Why this had to come first, measured not assumed.** Scoring the finished SW-T1
α=0.6 run, every peak ratio was already within 2–8%; the misfit was phase. Re-scoring
under an optimal uniform time shift separates the two:

| observable | nRMSE | best | shift | reading |
|---|---|---|---|---|
| flow rate | 29.2% | **2.5%** | −220 s | pure timing |
| fracture permeability | 31.9% | **13.3%** | −295 s | mostly timing, ~13% real |
| shear slip | 8.4% | **1.5%** | −38 s | pure timing |
| normal dilation | 12.0% | 8.1% | −40 s | **real shape error** |
| effective normal stress | 19.9% | 16.0% | −43 s | **real shape error** |

So flow rate needed *no* permeability retuning — the 29% was entirely phase. Anyone
who had "fixed" it by changing `dilation_scale` would have broken a correct model to
compensate for a wrong BC. The dilation and σ'ₙ rebound misfits survive the shift and
are the real remaining targets.

Fixed in `87_01` (SW-T1) and `87_02` (SW-T2): plateau **values** snapped to nominal,
measured **transition times** adopted. Snapping matters — the raw trace carries ±0.3
MPa extraction jitter (SW-T2 wobbles 11.34–11.68 inside its 12 MPa hold) and feeding
that in as a pressure BC would excite spurious transients. RMSE 1.240 → 0.195 and
1.536 → 0.266. `87_01` also shifts `event_dt_cap` −210 s to follow the earlier peak.

### 5.6 The two SW-T1 rebound complaints are ONE number: the joint is 6.3× too stiff on unload

Saeed reported these as separate problems — "the normal dilation rebound is a bit
smaller than the validation set, the effective normal stress rebound is too much."
They are the same defect seen from two sides. On a matched window (each record's own
peak-open → t = 3000 s), scoring the finished SW-T1 α = 0.6 run:

| | Δ dilation | Δ σ'ₙ | k = Δσ/Δd |
|---|---|---|---|
| measured | +44.21 µm | +5.98 MPa | **0.135 MPa/µm** |
| model | +16.23 µm | +13.94 MPa | **0.859 MPa/µm** |

A joint too stiff on unload cannot open (dilation rebound 0.35×) and over-transmits
the stress change (σ'ₙ rebound 1.82×). Because SW-T1 sets `use_kinematic_aperture =
true`, the hydraulic aperture *is* the mechanical gap, so the same defect surfaces a
third time: fracture permeability decays only **1.15×** from peak to end of unload
against **1.46×** measured — while the *peak* permeability is fine (1.04×). The
residual permeability misfit that survived the time-shift decomposition (§5.5) is
entirely the unload branch, and it is this.

**Where the stiffness comes from.** The closure law is
σₙ = (K_ni·V_m)·[c/(V_m − c)]^(1/p) (`include/utils/OrcaNormalClosure.h`), and all
four decks share K_ni = 2.443e11 Pa/m, V_m = 4.591e-5 m, p = 3.28,
`normal_closure_offset` = 4.433e-5 m. **The pre-seating offset alone is 96.6% of
V_m** — the joint is placed on the vertical part of the curve before any load is
applied. Evaluated through the actual law:

| σ'ₙ | c/V_m | tangent k_n |
|---|---|---|
| 67 MPa (preload) | 0.9972 | 157 MPa/µm = **646× K_ni** |
| 35 MPa (event min) | 0.9766 | 10.2 MPa/µm = **42× K_ni** |

The law's scale stress is σ₀ = K_ni·V_m = **11.2 MPa** and the specimen runs at
30–67 MPa, 3–6× past it. The joint is effectively rigid for the whole experiment.

**Why `normal_unload_retention_fraction` was never going to fix this.** At f = 0.94
it is already suppressing 94% of the reclosure — the gain (m − f) is 0.06 — and the
σ'ₙ rebound is *still* 1.82× too big. Series-spring inference from the scored run
gives k_frame ≈ 0.94 MPa/µm, so f modulates a spring ~12× stiffer than the one it
sits in series with. **It is the wrong knob, not a knob set wrong.** Retiring this
as a lever is the main practical consequence.

**V_m alone provably cannot fix it either.** Substituting x = c/(V_m − c) collapses
V_m out of the tangent entirely:

> **k_n = (K_ni/p)·x^(1/p−1)·(1+x)²**

so V_m only slides the joint along a fixed curve. That curve has a minimum at
x\* = −a/(a+2) with a = 1/p − 1, giving **k_n,min = 0.271 MPa/µm** at the current
K_ni — above the 0.158 MPa/µm the series pair needs. **K_ni (or p) must move.**

**Bracket built** (`scripts/make_swt1_vm_bracket.py`, decks `88_01`/`88_02`/`88_03`,
all `--check-input` clean). Each re-solves `normal_closure_offset` so the pre-seated
stress at zero mechanical overlap stays 31.00 MPa, keeping the preload state and the
Table-2 aperture fit invariant so the arm varies **tangent stiffness alone**:

| arm | V_m | K_ni | k_joint @35 MPa | predicted k_sys |
|---|---|---|---|---|
| 87_01 (parent) | 1.00× | 1.000× | 10.18 | 0.859 |
| `88_01` | 2.00× | 1.000× | 0.759 | 0.420 |
| `88_02` | 3.78× | 1.000× | 0.271 | 0.210 |
| `88_03` | 6.50× | 0.582× | 0.158 | **0.135** (target) |

k_frame is fitted to one scored run under a series assumption — one equation, one
unknown — so it is a magnitude, not a prediction. Score all three and interpolate.

**Do not reach for `reversible_normal_compliance` here.** It is declared OUTPUT ONLY
(it adds C_n·⟨σ_ref − σ'ₙ⟩₊ to the reported opening and cannot touch traction,
aperture, permeability or flow). It would make the dilation panel match while
leaving σ'ₙ and the permeability unload branch exactly as wrong — one panel of a
three-panel symptom. Fix the stiffness first, then decide if anything cosmetic is
still warranted.

**Applies to all four samples**, since the closure constants are shared. SW-T1/T2
expose it worst because kinematic aperture ties the hydraulics directly to the
mechanical opening. Note also that `maximum_closure_fraction` defaults to 0.999,
which the law reaches at σₙ ≈ 92 MPa — and there the tangent is set to **zero**.
The current fit runs to 67 MPa, so the cliff is not hit, but it is 1.4× away.

### 5.7 The four decks were never checked against the paper itself — 2026-08-16

Every earlier parameter audit compared the decks **to each other**. That finds drift
and is structurally blind to a value that is wrong in all four, or wrong in exactly
the two that were tuned together. Reading the source PDF and transcribing Tables 1–3
and Sections 2.1/2.4/2.5 found six discrepancies.

Reproduce: `python3 scripts/paper_parameter_audit.py`. Full write-up:
`doc/paper_vs_model_audit_2026-08-16.md`. The script re-reads the decks at run time,
so it fails loudly rather than silently going stale.

**1 — The saw cuts' joint constants are not the paper's, and they hide each other.**
JRC 23.35 (SW-S3) and 17.5 (SW-S4) against measured 1.96 and 1.19 — 11.9× and 14.7×.
SW-S3's is outside Barton's 0–20 scale. JCS 300 MPa against a measured UCS of
150 MPa. φ_r 8.45° and 7.50°, below anything physical for granite, which is the
compensation. All three cancel at the calibration point, so both still hit their
measured peak τ. **dτ/dσ'ₙ does not cancel: 0.423 vs 0.589 (SW-S3) and 0.322 vs
0.447 (SW-S4) — 28% too flat on both.** That derivative is the point of an
experiment where injection halves σ'ₙ, and SW-S4 is the specimen the manuscript
calls discriminating. Refit at the paper's JRC/JCS puts φ_r at 29.76° and 23.71° —
ordinary numbers, which is good evidence the paper's constants are the right ones.

**2 — The T-family's 44–46° φ_r is not fixable by refitting** and is not the same
kind of error. Both already use the measured JRC and JCS. They need μ = 1.17–1.27
*while still stuck* — that is the interlock of a mated Mode-I surface, and
`computeCohesionEffective()` returns hard-coded `0.0`, so φ_r is the only place it
can go. SW-T2's 46.29° ≈ the paper's **intact-rock** φ of 46°. Supersedes the
"unresolved" verdict in §6.5: the split is now explained, not open.

**3 — Two meshes disagree with the data, and the fixes exist in another repo.**
θ recovered from Table 2 alone via tanθ = (σ'ₙ − σ₃ + P_p)/τ, over all 11 stages:
SW-T1 32.00 ✅, SW-T2 **30.00 (Table 1 prints 31)**, SW-S3 29.03 ✅, SW-S4 30.02.
The meshes: SW-T2 cut at 31°, SW-S4 at **28.990° and 2.85 mm off centre** (its
journal is a copy of SW-S3's — the fracture-plane z-span is bit-identical,
`0.09115854`). Cost at fixed σ_d: τ 2.1% low / 2.0% high, deviatoric σ'ₙ 6.0%.
**Corrected journals exist in `orca_3.0_claude_edit/.../final_simulation_runs_v3|v4/
meshes/` and were never ported to orca_4.0.** The theory doc claimed they were fixed
"in both campaign directories" — true there, never true here. Porting invalidates
every SW-S4 and SW-T2 result on disk, so it is a campaign decision.

**4 — The manuscript claims a dissipation bound the validated model doesn't have.**
`dissipation_margin` is declared in exactly one material,
`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`. All four
production decks run `OrcaBartonBandisContactTractionFastADHardening`, which has no
dissipation inequality — it clamps ψ with `min/max_dilation_angle_degrees`, neither
of which is set anywhere. The only decks that set `dissipation_margin` are the MC
baselines `67_11` and `83_11`. So the bound lives exclusively in the law §0.2 of the
draft demotes to "baseline, not a coequal candidate", while §1 and §3.5.3 claim it
as a contribution of the model and assert it is "frequently the active constraint".

**5 — But the bound is a good diagnostic, and this is a result worth keeping.**
arctan(|d_n|/d_s) from Table 2 vs each specimen's mobilised arctan μ:
SW-T1 16.4° vs 49.4° and SW-T2 14.0° vs 51.7° — fine; **SW-S3 31.8° vs 31.3° and
SW-S4 28.7° vs 24.6° — the published dilation angle exceeds the friction angle.**
Read as pure shear dilation that is inadmissible. The resolution is the draft's own
§2.3.1 decomposition: on a low-μ saw cut the measured d_n contains elastic joint
decompression, not just dilation. A tensile fracture with μ > 1 has headroom; a
lapped saw cut with μ ≈ 0.46 does not. This is why the S-family decks carry ψ = 26°
and 24° and under-predict dilation — turns an apparent calibration miss into a
statement about what the measurement contains.

**6 — Smaller.** `fluid_bulk_modulus = 4.784e9` is 2.17× water; negligible in the
matrix at φ = 1e-3, not negligible in the fracture during the burst. SW-S3's
`axial_pres_final` comment still reads `# E=75 GPa` while E is now 67e9 — the
constant was derived at the old modulus and the preload has not been re-gated.
**SW-S4 reports the raw interface traction where the other three report the
paper-frame reduction** (eq 3 with P_p = ½(P_i+P_o)); different operators, likely
why SW-S4 alone needs `fault_pressure_coefficient = 0.86`, and its σ'ₙ score is not
comparable with its siblings'.

**What was verified correct**, and should not be re-litigated: E, ν, matrix
permeability, σ₃, P_o, μ_f, the injection protocol, the T-family's JRC/JCS, the
T-family's dilation angles (exactly the Table-2 values), the specimen L and D for
T1/T2/S4, and the flow geometry factor W/L — inverting the paper's own eq (9) on its
own tabulated Q, a_h and ΔP returns each deck's W/L to better than 0.5%. The
normal-closure law in `include/utils/OrcaNormalClosure.h` also matches the theory
manual line for line: σₙ = (K_ni V_m)[c/(V_m−c)]^(1/p), its tangent, the f_max·V_m
cap and the min(1e-9, 0.01 V_m) linearisation threshold.

SW-S3's mesh is 124.40 mm against a published 123.40 mm (+0.81%). Wrong in every
journal on the machine and in the manuscript's Table 1. Below the noise of
everything else — record it, don't re-run for it alone.

### 5.8 The §5.7 findings, applied — 2026-08-16, branch `orca_v5`

Six new decks, one source change, three scripts. Every constant is a closed-form
solve of the paper's own equations against Tables 1–2; nothing is tuned to a run.

```bash
python3 scripts/paper_parameter_audit.py            # states the problem (pre-audit decks)
python3 scripts/refit_joint_constants_from_paper.py # derives every new constant
python3 scripts/build_paper_corrected_decks.py      # regenerates the six decks
```

| deck | sample | controlled axis | class |
|---|---|---|---|
| `89_01` | SW-S4 | 30° mesh **and** paper JRC/JCS/φ_r | correction |
| `89_06` | SW-S4 | 30° mesh only | correction + attribution control for `89_01` |
| `89_02` | SW-S3 | paper JRC/JCS/φ_r | correction |
| `89_03` | SW-T2 | 30° mesh only | correction + control for `89_05` |
| `89_04` | SW-T1 | cohesion refit | **CANDIDATE — must be scored** |
| `89_05` | SW-T2 | 30° mesh **and** cohesion refit | **CANDIDATE — must be scored** |

All six pass `--check-input`, and all six carry `_hpc_nochk.sh` in the
`results_*_hpc_rorqual/` convention of commit `9a5f081`.

**The refit is the fix for the "LOCK".** Four deck generations (54_20 → 54_24)
fought a Barton envelope whose μ *rises* as injection unloads the joint. That rise
was an artefact of the invented JRC: at JRC = 17.5 / JCS = 300 MPa, SW-S4's μ runs
0.462 → 0.580 across the sweep; at the paper's 1.19 / 150 MPa it runs 0.456 → 0.464,
essentially the straight Coulomb line the paper's own SW-S4 data show. It also
moves SW-S4's onset weakening slope from **1.326e11**, just *above* the measured
k_sys = 1.25e11 Pa/m, to **1.224e11**, just below — off the strength cliff.

**Source change: `cohesion` + `residual_cohesion` on the Barton–Bandis law.**
Barton's roughness term is mobilisation-limited (it → 0 as σ′ₙ → JCS), so at the
tensile specimens' σ′ₙ/JCS ≈ 0.38 the measured JRC buys only 6.4°, and μ = 1.17 had
nowhere to live but φ_r. Asperity shear-through is a *cohesion*. Refitting at
φ_r = 29.756° (the basic angle measured on this campaign's own saw cut) gives
c = 24.65 / 31.65 MPa against the 30.30 MPa intact-rock cohesion implied by the
paper's UCS and φ = 46° — the two straddle it, and nothing in the derivation knows
about it. Both parameters default to 0, so every existing calibration is
bit-identical; `test/tests/materials/bb_cohesion/` pins c_eff = c·W to 2.4e-12 %
and keeps the cohesionless case as a legacy guard.

**Two traps this hit, worth not re-learning:**

1. **The SW-S4 nodeset rename.** The old SW-S4 mesh names its boundaries
   `top`/`bottom`/`sides`; every other mesh, including the corrected SW-S4 one, uses
   `top_nodeset`/`bottom_nodeset`/`sides_nodeset`. A mesh swap without the rename
   fails at setup — the good case.
2. **The source node landed in the bulk.** On the corrected SW-S4 size-5 mesh the
   *ideal* borehole position (6.00 mm inside the sidewall) has a bulk node 1.734 mm
   away and the nearest interface node 1.776 mm away. `use_closest_node = true`
   would have silently pinned injection into the matrix. The 89-series decks carry
   **exact interface-node coordinates** instead. `scripts/check_source_nodes.py` is
   the check, it is not optional after any mesh rebuild, and it also confirmed the
   four pre-existing decks were fine.

**One earlier claim was wrong and is retracted:** §5.7 said the 4.78 GPa fluid bulk
modulus "is handed to the fracture fluid, where storage is not negligible during
the burst". It is read in exactly one place, the matrix `OrcaTHMaterial`; the
fracture flow uses `fracture_transmissivity`. Real effect ~6 % on matrix storage.

### 5.9 SW-S3 mesh rebuilt, and what a full sweep of the mesh estate showed — 2026-08-16

Saeed built `sw3_mesh_L123p4.jou` in Cubit at sizes 3 and 5, closing #76. Verified
with the new `scripts/check_mesh_geometry.py`, which measures L, D and θ **out of
the built Exodus file** rather than trusting a journal header: L 123.40, D 50.53,
θ 29.000, plane-fit residual 0.00 µm, node/interface counts 11425/457 — identical
to the old mesh, so it is a pure axial rescaling of the same discretisation.

**The 1.00 mm error had never been fixed anywhere.** A sweep of every SW-S3 `.e`
on the machine — 20-odd files across `orca_3.0`, `orca_3.0 (Copy)`,
`orca_3.0_claude_edit` v1–v4, `orca_3.0_full`, `orca_3.0_full_13_AUG` and both
`HPC_backup` trees — returned 124.40 mm for all of them. There was no "good copy"
sitting in another repo, which is what the file-name variety suggested.

The same sweep settled the SW-T2 question by measurement. `ye2018_sw_T2_theta30_
mesh_*.e` is at 30° while Table 1 prints 31°, which looks like the ported mesh
introduced an error into a mesh that was already right. It did not. The
θ-recovery identity on Table 2 returns 30.001° for SW-T2 at all eleven hold
stages (spread 29.991–30.008), while the same test reproduces Table 1 to three
decimals for SW-T1 (31.995), SW-S3 (29.00) and SW-S4 (30.029). Not a systematic
bias in the reduction — specific to SW-T2. `check_mesh_geometry.py` therefore
encodes 30° as SW-T2's expected angle and flags 31° as the error.

**Old meshes are kept, deliberately.** The rebuild arrived with the 124.40 mm
meshes deleted, which would have broken the eleven pre-audit SW-S3 decks
(`83_11`, `84_01`, `84_02`, `86_01`, `86_02` and their `_mesh3` variants) that
were left untouched precisely so their results stay reproducible. Restored from
git; the new mesh sits alongside under its own name.

`89_02` renamed to `89_02_sw3_bbfast_paperjrc_L123p4_kernel_SV_biot0p6`. Source
coordinates re-derived on the new mesh (`-0.023159583 0 0.019919005` /
`0.023159583 0 0.103480995`, both 0.0 µm from an interface node); the old
coordinates were 500 µm off the new fracture plane, which `use_closest_node`
would have absorbed silently. Still open: `axial_pres_final` is displacement
control on a core that is now 0.8 % shorter (#77).

### 5.10 The SW-T1 87/88 lineage is retired — 2026-08-16

Saeed's call: *"cancel sws1 cases, all of the results are wrong."* Nothing had to
be cancelled — `88_02` and `88_03` had already finished cleanly (t = 3500,
7522 steps, **zero** non-convergences, 27196 s / 26701 s on 8 ranks), and the
machine was idle. So this is a **retirement of finished results, not an aborted
run**. `88_01` (the `vm2x` arm) had never been launched and must not be.

**The cause is not yet identified, and the usual suspects are ruled out.** The
SW-T1 mesh measures L = 128.80 mm, D = 50.52 mm, θ = 32.000°, plane residual
0.00 µm — exactly Table 1. `check_source_nodes.py` returns "the closest node IS
on the fracture interface" for both the injector and the producer on both decks.
So this is **not** the bulk-node trap (§5.9, [[source-node-pinning-rule]]) and
**not** a geometry error.

**What the outputs do show** — recorded as evidence, not as a diagnosis:

| deck | e_h range (µm) | k range (1e-13 m²) | mech. aperture max |
|---|---|---|---|
| `87_01` | 1.630 – 1.648 | 2.214 – 2.261 | 1.07 µm |
| `88_02` | 1.630 – 1.879 | 2.214 – 2.935 | 15.4 µm |
| `88_03` | 1.630 – 2.033 | 2.214 – 3.437 | 25.1 µm |
| older `sweep_19` | 1.630 – **4.152** | 2.214 – **14.24** | 157 µm |

The bracket does move in the intended direction (softer joint → more opening),
but the whole 87/88 lineage delivers roughly **an order of magnitude less
permeability enhancement** than the earlier SW-T1 sweep it replaced. `87_01`, the
parent, barely opens at all — 18 nm of hydraulic aperture across the entire
injection history. Since `87_01` is the parent of both 88 arms, retiring the
bracket without retiring `87_01` would be incoherent, so #68's SW-T1 half goes
with it. **`87_02` (SW-T2) is a different specimen and is not covered by this
call.**

Results are **kept on disk**, not deleted — they are the evidence for whatever
the defect turns out to be. Next SW-T1 work should start from the `87_01`
regression against `sweep_19`, since that is the narrowest reproducer.

### 5.11 The 89-series back-analysis: failure is quantized by injection step — 2026-08-17

Saeed scored all four specimens against the digitized validation. Summary of his ranking, and
what a back-analysis of the CSVs says caused it.

**The single organising fact.** Every scored case fails at the injection step where its strength
margin `m = (tau_lim - tau)/tau_lim` crosses zero. Margin measured as the minimum over each 1-MPa
bin of injection pressure:

| specimen | case | m @5 MPa | crosses 0 at | timing vs validation | mean nRMSE |
|---|---|---|---|---|---|
| SW-T1 | sweep19 b0.6 | +11.9% | **26 MPa** | +22..86 s | 15.3% |
| SW-T1 | `89_04` +cohesion | +4.4% | 19-20 | −530..595 s | 26.7% |
| SW-T2 | sweep21 b0.6 | +12.4% | **25-26** | +33..41 s | 9.8% |
| SW-T2 | `89_03` | +11.5% | 23-24 | −355..360 s | 23.6% |
| SW-T2 | `89_05` +cohesion | +5.1% | 21 | −430..445 s | 24.9% |
| SW-S3 | `84_01` baseline | +23.8% | **25-26** | −29..+6 s | 4.0% |
| SW-S3 | `86_01` phir8.45 | +28.7% | **26-27** | −3..+30 s | 10.0% |
| SW-S3 | `89_02` paperJRC | +28.1% | 22-23 | −360..390 s | 21.7% |
| SW-S4 | `89_06` | +13.5% | 17-18 | +50..73 s | 10.5% |
| SW-S4 | `89_01` paperJRC | +13.1% | 14-15 | early | 12.6% |

The experiment fails at the **top** of the staircase. Because the load is a staircase, a small
strength deficit does not advance failure proportionally — it advances it by a **whole step**,
~290 s on SW-T1/T2 and ~350 s on SW-S3. **The 89-series is not mistimed; it is one step too
weak.** Stop reading "430 s early" as a timing error to be tuned continuously.

**Two independent defects, not one.**

1. *Level* — the SW-T1/T2 cohesion refit (`89_04`, `89_05`). Trading phi_r 44.1/46.29 deg for a
   constant cohesion is exact at only one sigma'_n, and the refit anchored it at the **failure**
   stress. At the much higher pre-injection sigma'_n the flat cohesion line sits ~7 percentage
   points below the steep friction line it replaced: starting margin falls +11.9 -> +4.4 (SW-T1)
   and +12.4 -> +5.1 (SW-T2). Cohesion adds level but **no slope**.
2. *Slope* — the paper-JRC collapse (`89_02`, `89_01`). Same starting margin as the incumbent
   (+28.1 vs +28.7; +13.1 vs +13.5) but steeper decay: 3.20 vs 2.93 %/MPa (SW-S3), 1.35 vs 1.15
   (SW-S4). `JRC*log10(JCS/sigma'_n)` is the **negative feedback** that strengthens the joint as
   injection unloads it, `dphi/dsigma'_n = -JRC/(ln10 * sigma'_n)`. Collapsing JRC 23.35 -> 1.96
   and 17.5 -> 1.19 removes ~92% of it. **This is the missing negative feedback flagged on
   2026-08-16 — it is on the STRENGTH side, not the aperture side.** See §6 note on the Bakhtar
   law: that hunt was looking in the wrong place.

**The 1 deg mesh correction, not the constitutive model, is what moved SW-T2.** `89_03` has
*identical* strength parameters to sweep_21 (JRC 14.63, JCS 1.5e8, phi_r 46.29182452, same
closure constants). It differs only in the mesh (31 -> 30 deg), the re-digitized schedule, and
the fluid bulk modulus. Resolving the same (sigma_d, P_p) at 30 deg instead of 31:
tau 0.441474 -> 0.433013 sigma_d (−1.9%) but sigma'_n +0.265264 -> +0.25 sigma_d (−5.8% of that
term), so tau/sigma'_n goes 1.2463 -> 1.2776 at sweep21's own onset state — **+2.5% closer to
failure from geometry alone**. Plus the corrected schedule runs 80-100 s ahead of the old
idealised staircase at every step. 2.5% is enough to cross one 4-MPa step earlier (~290 s), and
290 + 90 = 380 s, matching the observed 355-360.

**Therefore: sweep-19/21's win is not evidence that they are right.** Their phi_r = 44.1/46.29 deg
was fitted on geometry that under-resolved shear by 2%; the calibration absorbed the mesh error.
On the correct mesh they would fail early too. **Do not revert to them.**

**Two candidate confounds tested and REJECTED.**
- *SW-S3's un-regated 123.40 mm preload (#75) is exonerated.* `86_01` reaches a pre-event
  differential stress of 28.29 MPa and `89_02` reaches 28.52 — within 0.23 MPa — yet `86_01` is
  on time and `89_02` is 360-390 s early. Identical preload, opposite timing.
- *SW-S4's "injection pressure is wrong" is a postprocessor bug, not a model error.* See below.

**The SW-S4 stale-PointValue bug (fixed 2026-08-17, commit on `orca_v5`).** `injection_pressure_pp`
and `pp_outlet_pp` in `89_01`/`89_06` were `PointValue` at `-0.019255 0 0.021745` and
`0.019255 0 0.091255` — the **old 28.99 deg / 2.85 mm off-centre mesh's borehole**. The theta30
swap updated the `source_in`/`source_out` `coord` but left the sampling points behind, 5.86 mm
and 0.89 mm off-node. Both postprocessors are read **only by other postprocessors** — no
Function, BC, Material or Control — so the **mechanics of every SW-S4 run to date is unaffected**
and no re-run is needed. What was wrong:
- reported injection pressure 26.07 MPa at the peak against the prescribed 27.96, 1.50 MPa RMS low;
- `pp_outlet_pp` sampled *inside* the pressurised fracture and read ~7 MPa against its own 5 MPa
  Dirichlet.
The two errors **partly cancel** in `effective_normal_paper_frame_mpa_pp` (mean shift −0.005 MPa,
so SW-S4's sigma'_n overestimate is real model behaviour) but they **add** in `pp_drop_pp`: 3.9 MPa
of ~23 MPa, which is **27.5% of the peak `flow_rate_validation_ml_min_pp`**. That is most of the
"underestimates the peak flow rate". Corrected CSVs written alongside the originals as
`*_ppfix.csv`; both decks now use `AverageNodalVariableValue` on the nodeset, matching SW-T1/T2
(which score 1.2% on injection pressure against SW-S4's ~7%).

**Open and unresolved: SW-S3's Biot inversion.** `84_01` at `biot_coefficient = 1e-12` scores 4.0%
and beats itself at 0.6 (20.0%), while SW-T1/T2 both prefer 0.6. 1e-12 is physically
indefensible (#51), so the best SW-S3 score in the campaign rests on an unphysical parameter.
Not explained by the margin analysis. Do not quote `84_01` baseline as the reference case in the
manuscript until this is resolved.

**The 90-series** (8 decks, built and `--check-input` clean 2026-08-17) is the falsifiable test:
`90_01`/`90_02` and `90_03`/`90_04` bracket the SW-T1/SW-T2 **level** correction by raising peak
cohesion only (residual_cohesion untouched, since the parents' residuals are their strong suit);
`90_05` vs `90_06` separates **level from slope** on SW-S3 by pitting a 1.67 MPa cohesion against
JRC 5.69 at matched crossing strength; `90_07`/`90_08` bracket SW-S4's JRC at **fixed peak
envelope** (phi_r re-anchored each time) to test whether JRC owns the residual while phi_r owns
the onset. Each header carries its own derivation and a falsifiable prediction.

---

## 6. Hypothesis ledger — including the ones that failed

Recorded so they are not re-tried. Roughly half of what follows is my own reasoning
being wrong; that is the point of the section.

### 6.1 REJECTED — "Bakhtar's quadratic aperture law makes transmissivity go as E⁶"

Proposed as the cause of the Bakhtar SW-S4 instability. **Wrong.** The deck's calibrated
offset is 30.79 µm and SW-S4's mechanical aperture peaks at 1.16 µm (4.36 µm in the
Bakhtar runs), so the law is near-linear there: `dlnT/dlnE` tops out at **0.74, not 6**.
Transmissivity ratio between the two laws is only **1.00–1.45**.

Two follow-ups also rejected against real run data: clamp saturation (the 8 µm clamp is
never approached) and JRC mobilisation (`bb_jrc_mobilized` is pinned at 17.5 across all
three real Bakhtar runs in `orca_3.0_full`).

**Do not regularise the aperture law's stiffness** — the earlier notes proposed exactly
that, and it aims at the wrong target.

### 6.2 STILL OPEN — the Bakhtar instability is missing negative feedback

The live hypothesis after 6.1. The Bakhtar deck also disables the bounded power-law
normal closure, the damped dilation retention term, and the slip-damage/gouge
reduction — which the additive deck's own comments say were added to stop HM runaway.

### 6.3 REJECTED — three explanations for Mandel's 1.5% residual

Mesh (halves once from nx=10→20, then stops), timestep (1.506% → 1.250% → 1.250%), and
BC-table density (a 401-point table moved it 1.506% → 1.498%). All rejected.

Resolved differently: the residual is **shared with the reference implementation**.
Against the same analytic series, MOOSE's own `porous_flow mandel_constM` gold is
*further* from it than Orca at every matched time (+2.06% vs +1.40% at t = 0.116). The
verification claim is that Orca matches the reference and is marginally closer to the
closed form — **not** that the 1.5% is understood.

### 6.4 REJECTED — "SW-S3's fracture permeability is 3× too high"

**My own finding from earlier the same day, and it was wrong.** `SWS3/SWS3/` holds two
digitizations and the notebook plotted the stale one:

| file | sim/exp k |
|---|---|
| `permeability_m2_vs_time_sw3.csv` (stale) | **3.03** |
| `permeability_m2_vs_time_sw3_corrected.table2` | **1.02** |

The proof that the corrected file is right does **not** rest on the model agreeing with
it. Regressing the simulation's own output:

```
ln Q = 1.501 ln k + 1.441 ln P_inj + c
```

The 1.5 exponent on k is the cubic law, recovered to three digits. So a 3.0× error in k
implies a **5.2× error in flow rate** — and flow is matched at 1.04. The stale curve
contradicts the flow-rate curve *from the same experiment* by a factor of five in
transmissivity. The deck comments had already flagged it ("re-digitization pending");
the notebook was never repointed. Both notebook and scorecard now read the corrected
series.

### 6.5 REJECTED — cohesion explains the SW-T friction anomaly

The anomaly: the S-family draws 70–80% of its shear strength from the *stress-dependent*
roughness term, the T-family ~90% from the *constant* φ_r. All four decks set
`use_mobilized_jrc = false`, `use_scale_correction = false`,
`pore_pressure_strength_coefficient = 0`, so they evaluate the identical law
`phi_peak = phi_r + JRC·log10(JCS/sigma'_n)`. Both reproduce their own peak τ (0.989 and
0.999), so peaks cannot distinguish them.

**It cannot be fixed by re-tuning JRC.** Holding φ_r = 30° (granite reference) and
solving for the JRC that reproduces each sample's own τ:

| | JCS = 150 MPa | JCS = 300 MPa | deck has | physical range |
|---|---|---|---|---|
| SW-S3 | 3.91 | 2.84 | 23.35 | 0–20 |
| SW-S4 | **−4.15** | **−3.01** | 17.50 | 0–20 |
| SW-T1 | **45.41** | 27.65 | 15.32 | 0–20 |
| SW-T2 | **49.40** | 30.08 | 14.63 | 0–20 |

**Ruled out — the stress resolution is correct.** Each deck states its coefficient
`0.5 sin(2θ)` explicitly: SW-S3 0.424024 → θ = 29.0°, SW-T1 0.449397 → θ = 32.0°.
SW-S3's 29° is the optimal plane for φ ≈ 31°, as it should be. The normal resolution
agrees: at SW-T1's peak, `sigma3 + q sin²θ = 71.99 MPa` total against a reported
effective 59.84, implying a mean fault pressure of 12.15 MPa — correctly between the
5 MPa production and 19.2 MPa injection pressures. The state is admissible too:
`sin(phi_max) = q/(s1'+s3') = 0.808`, μ_max = 1.371, and SW-T1 sits at 1.12.

**Ruled out — cohesion.** SW-S4 is a documented saw-cut; if SW-T is a tensile fracture,
cohesion is the physical way to carry high strength. Solving for the cohesion that
closes the gap at φ_r = 30°, restricted to actively-yielding rows
(`plastic_slip_increment > 0`):

| sample | rows | mobilised μ | cohesion at φ_r = 30° |
|---|---|---|---|
| SW-T1 | 2210 | 0.878 – 1.202 | **15.9 ± 9.9 MPa** |
| SW-S3 | 547 | 0.332 – 0.666 | **−20.2 ± 0.9 MPa** |

A working hypothesis gives a small spread — one cohesion valid at every stress level.
SW-T1's is ±62%. Rejected. *(My first run of this test was itself wrong: I fitted over
the whole pre-slip branch, where τ sits below the limit and the fault is not yielding,
so "required cohesion" had no meaning there.)*

The model cannot express cohesion anyway — `computeCohesionEffective()` returns a
hard-coded `0.0`, no input parameter, no subclass override. **That is why a fit needing
cohesion inflated φ_r instead.** A real structural limitation, worth recording on its
own.

**What survives.** The contrast in the *scatter*. SW-S3's yielding follows one friction
law to within 0.9 MPa; SW-T1's mobilised μ swings 0.88 → 1.20 across only 35–59 MPa of
normal stress — far wider than any Barton-Bandis curve produces. **SW-T1's τ/σ'ₙ is not
well described by the Barton-Bandis form at all.** The model reproduces SW-T1's τ to
0.999 because the loading frame drives it, not because the friction law is right.

**And it cannot be settled yet**, because SW-T1's digitized σ'ₙ is the degenerate
near-constant file in §7.2. #66 blocks this.

### 6.6 REJECTED — "the SW-T1 dilation/slip mismatch is a model error"

The simulation is self-consistent, on three independent checks: both dilation channels
(`czm_normal_dilation_paper_mm_pp`, `frac_normal_dilation_paper_mm`) agree to every
printed digit; reported dilation = `-mechanical_aperture * 1e3` **exactly**; and
dilation/slip = 0.293 = tan(16.3°) against the deck's `dilation_angle_peak_degrees =
16.442`. There is only ever *one* error possible there, not two. The problem is the
data — §7.2.

---

## 7. Validation-data defects

**Of the problems visible in the sample figures, two of the three were in the
validation data, not the model.** Check the digitized series before tuning a deck
against it.

> **2026-08-16 — SUPERSEDED BY RE-EXTRACTION.** Saeed re-extracted all four
> specimens into one folder each, named after the specimen
> (`SWS3/SWS3`, `SWS4/SWS4`, `SWT1/SWT1`, `SWT2/SWT2`; SW-S4's is the Fig. 7 set).
> **This is the reference from here on.** It repairs every defect below. The
> sections are kept because the *reasoning* was load-bearing — §7.2 made a
> numerical prediction that the new data then confirmed to three digits.
>
> **The validation data is now tracked in git** (commit `81bce79`). It never had
> been: `.gitignore` line 23 is a blanket `*.csv` written for solver output, and it
> had been silently swallowing all four folders. The repo held decks tuned against
> data it did not store. That is precisely how §6.4's superseded permeability file
> was able to masquerade as a 3× model error — there was nothing to diff against.
> Negation rules now exempt the four folders; 37 files, ~416 KB.

### 7.1 SW-S3 fracture permeability — superseded file

See §6.4. Fixed: notebook and scorecard repointed to
`permeability_m2_vs_time_sw3_corrected.table2`, with the reasoning recorded inline in
the notebook so the next reader does not undo it.

**Retired 2026-08-16.** The re-extracted `permeability_m2_vs_time_sw3.csv` now agrees
with the hand-corrected `.table2` to the digit (both 1.21e-13 … 3.66e-13 over 11
points). The override is no longer needed and the scorecard points at the plain
`.csv`. Keep the `.table2` as the audit trail.

### 7.2 SW-T1 — three broken channels

| file | first | last | span | defect |
|---|---|---|---|---|
| `SWT1_shear_slip_mm.csv` | −48.731 | −46.844 | 1.944 | **un-zeroed LVDT baseline of −48.7 mm** |
| `SWT1_piston_displacement_mm.csv` | −38.075 | −38.075 | **0.000** | **constant — holds no data** |
| `SWT1_effective_normal_stress.csv` | | | ~0 | near-constant at 67.2 MPa |
| `SWT1_normal_dilation.csv` | −0.008 | +0.521 | 0.546 | **sign opposite to SW-S3's** |
| SW-S3 equivalents | ~0 | | 0.074 / 0.048 / 0.046 | all fine |

Once zeroed, the two usable SW-T1 curves share the simulation's onset (~1750 s) and
plateau (~1850 s), and their ratio is 1.9349/0.5439 = 3.56 ≈ 1/tan(15.7°) — they *are*
a slip/dilation pair related by a plausible dilation angle.

**Under the reading that `SWT1_normal_dilation.csv` actually holds shear slip:**

| | simulated | digitized (zeroed) | ratio |
|---|---|---|---|
| shear slip | 0.5256 mm | 0.546 mm | 0.96 |
| normal dilation | 0.154 mm | 0.546·tan(16.44°) = 0.161 mm | 0.96 |

Both within 4% — far more coherent than the labels give. **But this cannot be settled
from the CSVs alone**; it needs the paper figure. Flagged, not assumed.

The scorecard now guards both failure modes: constant files are rejected rather than
scored, and displacement channels are zeroed with the removed offset printed.

**CONFIRMED 2026-08-16 — the reading was right, and it predicted the number.**
The re-extraction resolves it without the paper figure:

| channel | old file | re-extracted | prediction above |
|---|---|---|---|
| `SWT1_shear_slip_mm.csv` | −48.731 … −46.844 (un-zeroed) | −0.0019 … **+0.5425** | — |
| `SWT1_normal_dilation.csv` | −0.008 … **+0.521** (wrong sign, ≈ slip) | −0.1612 … +0.0017 | **0.161 mm** |

The old "dilation" file was carrying something that tracked slip (+0.521 against the
corrected slip's +0.5425), exactly as suspected. And the dilation predicted from the
slip/dilation-angle argument — 0.546·tan(16.44°) = 0.161 mm — is what the corrected
extraction measures, **0.1612 mm**. A hypothesis that survives a blind test at three
digits is worth more than one that merely fits.

Task #66 is closed by this. What remains genuinely constant, in all three files that
have it, is **piston displacement** — still not scored, still guarded.
`SWt1_produciton_pressure.csv` and `SWT2_production_pressure_MPa.csv` are also
constant at 5.000 MPa, but that one is *physics*: it is the outlet backpressure, and
both decks already set `production_pressure = 5e6`. That BC is confirmed, not suspect.
Do not "fix" those two files.

---

## 8. Verification suite

12 tests, passing serially **and on 2 MPI ranks** (`./run_tests -j 2 -p 2`). Worth
checking both — production runs on 8, and a serial-only test is half a test.

| area | n | what it pins |
|---|---|---|
| `materials/biot_modulus` | 4 | the M formula and both vanishing-term boundaries |
| `kernels/mass_storage` | 2 | `(1/M)dp/dt`, the M-vs-1/M convention, 12 sig figs |
| `kernels/thermal_storage` | 2 | `−α_T dT/dt` including sign, 11 sig figs |
| `verification/pressure_diffusion` | 1 | Darcy flux and `c = M k/µ` vs erfc; worst 0.66% of p0 |
| `verification/terzaghi` | 1 | 1D consolidation vs Verruijt |
| `verification/mandel` | 1 | multi-axial coupling + Mandel–Cryer overshoot |
| `kernels/simple_diffusion` | 1 | stock smoke test |

**Mandel is the one that matters most.** Terzaghi is 1D and its pressure only decays, so
a formulation can pass it while being wrong multi-axially. Mandel's rigid platens push
load inward and the centre pressure *rises* first: peak 0.504772 vs analytic 0.505571,
**within 0.16%**. The platen BC is verified rather than trusted — the analytic series
regenerates the imposed table to 9.1e-6.

---

## 9. Conventions and gotchas

### Branch and commit

- Source changes go on a **new sequential branch** (`orca_v1` … `orca_v4`), never `main`.
- **Commit messages are detailed**: what changed, why, what was measured, what was
  rejected. The history is meant to be readable as a lab notebook.
- **The MDs are updated as part of the work**, not afterwards. `doc/TODO.md` gains a new
  lettered section per unit of work (currently A–S).

### Environment

```bash
source /home/geomechanics/miniforge/etc/profile.d/conda.sh && conda activate moose
```

- `/home/geomechanics/miniforge/bin/python` has pandas/numpy; the `moose` env does not.
- Machine: 32 cores, 30 GB. Campaign scheduling: 4 concurrent decks × 8 MPI ranks.

### HPC (Alliance Canada, `def-biaoli66`) — checkpoints are not available

Saeed's cluster allocation caps **file count**, and a 32-rank MOOSE `Checkpoint`
writes a `<base>_cp/` tree with one `<step>-restart-<rank>.rd` per rank plus a mesh
blob, per retained checkpoint. Suppress it on the command line rather than forking
the decks:

```
Outputs/chk/enable=false
```

- **Why it works:** `OutputWarehouse::outputStep()` gates on `obj->enabled()` before
  dispatching, so a disabled `Checkpoint` is never reached — including on the
  interrupt-signal path inside `Output::outputStep()`, which sits behind the same
  gate. This MOOSE version's `CommonOutputAction` creates no automatic checkpoint,
  so the deck's explicit `[chk]` block is the only one to disable.
- **Verified, not assumed.** Two-arm test on `87_02`, 1 rank, `num_steps=2`,
  `time_step_interval=1`: checkpoint ON → 8 files / 6 dirs with
  `chk_cp/0002-restart-0.rd`; `enable=false` → 2 files / 1 dir, no `chk_cp` at all.
  CSV and Exodus unaffected.
- **Do not delete the `[chk]` block instead.** It forks every deck into a local and
  an HPC copy that then drift. The override keeps one deck, so a local and an HPC run
  of the same name are the same physics by construction.
- **Override deck variables, not `Outputs/*/file_base`.** The decks define
  `csv_file_base` / `exodus_file_base` / `checkpoint_file_base` at top level and the
  `[Outputs]` blocks consume them. Setting `Outputs/csv/file_base=…` directly leaves
  the deck variable unreferenced and MOOSE aborts with *"unused parameter"*. This
  killed the first verification attempt.
- **No checkpoint means no restart**, so a job killed at the wall clock is
  unrecoverable. Mitigation: CSV is written incrementally and the scorecard reads
  CSV, so a killed job still leaves a scoreable partial record. Exodus is
  `execute_on = FINAL` and is lost. Generated jobs use `--time=24:00:00`.
- HPC runs get an `_hpc` output basename suffix so they cannot overwrite a local run
  of the same deck. `scripts/make_hpc_nochk_jobs.py` generates the SLURM scripts;
  `scripts/sample_scorecard.py` already lists the `_hpc` arms and skips missing ones.

### Gotchas that each cost a debugging cycle

- **`mpiexec` must come from the conda `moose` env** (MPICH/Hydra). The system
  `/usr/bin/mpiexec` is OpenMPI and aborts every rank with *"Runtime environment uses
  unsupported PMI version PMIx"*.
- **The moose env's `activate.d` hook reads `$CONDA_BUILD` unguarded**, which trips
  `set -u` in any launcher script. Relax the flag just across the activation.
- **Count ranks with `pgrep -c -x orca-opt`**, not by matching the binary path — the
  latter also counts each job's `mpiexec` wrapper (38 against 32 real ranks) and will
  leave a capacity-waiting queue stuck forever.
- **`automatic_scaling` is not a "always on for poromechanics" setting.** In
  `mass_storage` it is **required** — storage is the only equation, the residual sits at
  1e-14, and PETSc cannot tell convergence from noise. In `thermal_storage` it must be
  **off** — the temperature equation contributes an O(1) row, and scaling amplifies the
  pressure row (whose two terms cancel to round-off *by construction*), pinning |R| at a
  6e-9 floor and reporting DIVERGED_LINE_SEARCH on an answer that is exact. Decide per
  problem: does anything in it set an O(1) scale on its own?
- **`ADRankTwoAux` is not registered in this app.** Use `ADMaterialRankTwoTensorAux`
  with `property` / `i` / `j`.
- **`l_max_its`, not `ksp_gmres_restart`, was the real DIVERGED_ITS cap** in the v4 HPC
  batch. Reference decks never used hypre; use LU/MUMPS.
- **Reading a CSV while it is being appended gives torn rows.** Use
  `tail -2 | head -1` for progress reads — a naive read once showed a 1000 s "regression"
  that never happened.
- **Re-pin the injection source node after any mesh rebuild.** Injection can snap to a
  bulk node with no error.
- **Error metrics that divide by a decaying analytic value are meaningless in the tail.**
  A 0.016 Pa discrepancy against a 1e6 Pa step once reported as "9584% error". Normalise
  by the step, and mark deep-tail entries as tail.

---

## 10. Update log

| date | entry |
|---|---|
| 2026-08-15 | v1–v3: source import, deck sets, SLURM, Table-2 gate, Biot α A/B campaign method and launch |
| 2026-08-16 | v4: verification suite 1 → 12 tests; four source defects found and fixed (§4.1–4.4); Bakhtar aperture-law hypothesis rejected (§6.1); Mandel added and its residual traced to the reference implementation (§6.3) |
| 2026-08-16 | Cross-sample parameter audit (§5.1); SW-S3 permeability false alarm corrected (§6.4); SW-T1 validation files found broken (§7.2); SW-T friction anomaly narrowed, cohesion rejected (§6.5); SW-S3 refit decks `86_01`/`86_02` built and launched (§5.4); this file created |
| 2026-08-16 | **Validation set re-extracted by Saeed and adopted as the reference** (§7). #66 closed; §7.2's prediction confirmed to three digits. **Validation data put under version control** — a blanket `*.csv` in `.gitignore` had hidden it since the start (§7). Injection schedule audited on all four samples: SW-T1/SW-T2 were late by up to +155 s, SW-S4 clean, SW-S3 acceptable (§5.5). Refit decks `87_01`/`87_02` built, validated and queued. Established by time-shift decomposition that SW-T1's flow-rate misfit is 100% phase (29.2% → 2.5%) and needs no permeability retuning, while the dilation and σ'ₙ rebound misfits are real. `sample_scorecard.py` extended to all four samples. Commit `81bce79` |
| 2026-08-16 | **Root-caused both SW-T1 rebound complaints to one number** (§5.6): the joint+frame unloads at 0.859 MPa/µm against a measured 0.135, 6.3× too stiff. The dilation rebound (0.35×), the σ'ₙ rebound (1.82×) and the under-decaying permeability on unload (1.15× vs 1.46×) are the same defect. Traced to the closure constants — the pre-seating offset is 96.6% of V_m, putting the joint 42–646× K_ni across the whole experiment. Proved algebraically that V_m alone cannot fix it (k_n = (K_ni/p)x^(1/p−1)(1+x)² has a floor of 0.271 MPa/µm at the current K_ni, above the 0.158 needed) and **retired `normal_unload_retention_fraction` as a lever** — at f = 0.94 it modulates a spring 12× stiffer than the one in series with it. Bracket `88_01`/`88_02`/`88_03` built and validated, each holding the pre-seated stress invariant at 31.00 MPa. **HPC checkpoint suppression verified empirically** and documented in §9 |
| 2026-08-16 | **First audit of the decks against the source paper rather than against each other** (§5.7). Six discrepancies: the saw cuts' JRC is 12–15× the measured value with JCS at 2× UCS and sub-8.5° φ_r compensating, which cancels at the calibration point but leaves dτ/dσ'ₙ 28% too flat on both; the T-family's 44–46° φ_r is the interlock of a mated Mode-I surface with nowhere to go because cohesion is hard-coded to zero; the SW-S4 mesh is cut at 28.990° and 2.85 mm off centre and SW-T2 at 31° where its own Table 2 says 30°, with corrected journals sitting unported in `orca_3.0_claude_edit`; `fluid_bulk_modulus` is 2.17× water; SW-S4 reports a different σ'ₙ operator from its siblings; SW-S3's mesh is 1 mm too long. **The manuscript claims a dilation dissipation bound the validated law does not implement** — `dissipation_margin` exists only in the CompressionTensile material, i.e. in the MC *baseline*. Kept the bound as a diagnostic instead: applied to Table 2 it shows both saw cuts' published dilation angle exceeds their own mobilised friction angle, which is the quantitative form of the §2.3.1 identifiability argument. New `scripts/paper_parameter_audit.py` (re-reads the decks so it cannot go stale) and `doc/paper_vs_model_audit_2026-08-16.md`; correction notes inserted in the manuscript draft and the theory manual; two dangling cross-references in the theory manual fixed. **No source file touched, no run affected.** Tasks #71–#74 opened |
