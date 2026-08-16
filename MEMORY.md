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
| **#67 / #60** | **Refit SW-S3 slip onset at α = 0.6.** The only remaining SW-S3 problem. Decks `86_01` (φ_r 8.45) and `86_02` (φ_r 9.00) bracket it. | 86_01 running; 86_02 queued |
| **#66** | **Replace the broken SW-T1 digitized files** (§7.2). Blocks the SW-T friction question *and* any scoring of SW-T1 kinematics. Needs the paper figure. | needs the paper |
| **#59** | **Rebuild `orca-opt`** and runtime-verify the three compile-checked-only fixes (§4.2, §4.3, §4.4). Register the `alpha_eff_lagged` test case and generate its gold. | blocked on the campaign draining |
| **#55 / #52** | Finish scoring the Biot A/B pairs; SW-T2 both arms still running. | running |

### Open, not blocking

| # | item |
|---|---|
| #65 | Unify the rock parameters (§5.1). E is settled; **do not unify φ_r until #66 is done.** |
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

### 5.1 Rock parameters are not shared across the four decks

| parameter | SW-S3 | SW-S4 | SW-T1 | SW-T2 | verdict |
|---|---|---|---|---|---|
| `youngs_modulus` | **75e9** | 67e9 | 67e9 | 67e9 | **drift — settled, use 67e9** |
| `poissons_ratio` | 0.32 | 0.32 | 0.32 | 0.32 | consistent |
| `biot_coefficient` | **1e-12** | **0.6** | **1e-12** | **1e-12** | must be shared → 0.6 |
| `initial_porosity` | 0.001 | 0.001 | 0.001 | 0.001 | consistent |
| `matrix_permeability` | 5e-19 | 5e-19 | 5e-19 | 5e-19 | consistent |
| fluid ρ / μ / Kf | identical everywhere | | | | consistent |
| `jcs` | **3.0e8** | **3.0e8** | **1.5e8** | **1.5e8** | unresolved — §6.5 |
| `residual_friction_angle_degrees` | **7.5** | **7.5** | **44.1** | **46.3** | unresolved — §6.5 |
| `jrc` | 23.35 | 17.5 | 15.32 | 14.63 | per specimen — legitimate |
| `dilation_angle_peak_degrees` | 26.0 | 24.0 | 16.44 | 13.97 | per specimen — legitimate |
| `normal_unload_retention_fraction` | 0.06 | 0.04 | **0.94** | **0.84** | see §4.7 |
| Kni / Vm / exponent / offset | identical across all four | | | | consistent |

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

### 7.1 SW-S3 fracture permeability — superseded file

See §6.4. Fixed: notebook and scorecard repointed to
`permeability_m2_vs_time_sw3_corrected.table2`, with the reasoning recorded inline in
the notebook so the next reader does not undo it.

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
