# Does a stimulated fracture stay open? — the 108-series run list

**2026-08-28 · branch `orca_v11`.** Sixteen decks: three arms plus two controls,
answering one question — after stimulation, does the fracture return to its initial
state, and if so how long does it take?

---

## 0. Right now that question is answered by the input file, not by the physics

The aperture budget in `ADOrcaRoughnessDamageFracturePermeability::computeQpProperties` is

```
a_h = a_h0 + stress_aperture(N_eff) + aperture_scale * a_mech
            + dilation_term + self_prop(R) - gouge_fill(s)
```

Every term is a function of the **current** effective normal stress, the **current**
mechanical gap, or a history variable that is **monotone in slip**. No term contains
`t` or `dt`. The consequence is measurable in the finished runs — SW-T1 `100_01`, over
the last 300 s of its 8 MPa hold:

| | t = 3200 s | t = 3500 s | change |
|---|---:|---:|---:|
| cumulative plastic slip | 0.000533829 m | 0.000533829 m | 0 (10 s.f.) |
| hydraulic aperture | 3.54317 µm | 3.54316 µm | **−3 ppm** |
| Q | 0.542246 | 0.542244 mL/min | −4 ppm |
| roughness state | 0.125534 | 0.125534 | 0 |

It is not decaying; it has converged. Run it for a year and the number does not move.
A long-hold deck on the model as it stands returns a horizontal line, so "how long until
it returns to its initial state" is answered by construction. The 104-series already
showed this from the other side: a **ten-fold** change in shut-in decay time moved
retained permeability by at most 1.6 %.

The only two time-dependent objects anywhere in the constitutive path are the Perzyna
tangential viscosity — gated on being at yield, and the loading frame takes the joint
off yield — and `normal_unload_retention_time`, which is implemented and set to `0.0`
in **all 164 decks in the repository**. This series switches on the second, adds a
third, and supplies a stress-path arm that needs neither.

---

## 1. Read every result in this series against the frame caveat

`100_01` at its first 8 MPa hold and its last one — same injection pressure:

| | t = 200 s | t = 3500 s |
|---|---:|---:|
| axial command | −0.00073121 m | −0.00073121 m |
| differential stress | 150.19 MPa | 62.01 MPa |
| shear stress | 67.50 MPa | 27.87 MPa |
| sigma'_n | 65.68 MPa | 40.91 MPa |
| a_h | 1.630 µm | 3.543 µm |

**The piston never moved, and 88 MPa of axial load disappeared** — 0.54 mm of slip on
an inclined joint unloaded the machine spring. sigma'_n at the final 8 MPa hold is
24.8 MPa below its value at the first one, and that alone opens the joint.

So the raw ×2.17 in aperture and ×10.3 in Q between the two 8 MPa holds are **mostly
retained frame unloading, not retained propping.** The 101-series metric already knows
this and matches at equal sigma'_n, giving ×1.61 in k rather than ×4.7. Every number
quoted out of this series must be matched-sigma'_n. In the field there is no compliant
piston shedding 25 MPa of normal stress, so this is not a detail — it is the difference
between a laboratory artefact and a transferable result.

---

## 2. Arm A — reconfinement (108_03–06). No new physics, no rebuild

Kalantar et al. (2025) find that tensile and saw-cut granodiorite fractures *do*
self-prop but **lose the gain again on depressurisation**, because the post-slip
stress-sensitivity coefficient alpha in `k = k0 exp(-alpha sigma'_n)` roughly doubles:
k0 rises (propping is real) and alpha rises with it (the gain is not retained). That is
a **stress-path** mechanism, not a time one, and it is the one this model can be asked
about today.

After the calibrated protocol ends, the deck holds injection at its final pressure and
steps the confining pressure through ×1.5 / ×2.0 / ×2.5 / ×3.0 / ×3.5 in 350 s holds.
Written as a `CompositeFunction` over the parent's own `sigma3_x`/`sigma3_y`, so
SW-S4's existing side-unload relaxation survives untouched rather than being overwritten.

**What it delivers:** retained a_h against sigma'_n on the way back up, against the
virgin closure curve `a_h0 + stress_aperture(sigma'_n)`, which is analytic and needs no
second run. The crossing stress — if there is one — is the propping-resilience number,
directly comparable to the Pedrosa fit Kalantar report.

> **CORRECTION, 2026-08-31, after wave 1.** This design overshoots a model-form limit it
> did not account for. computeStressAperture clamps the closure term to zero above
> reference_effective_normal_stress, so the aperture cannot close further beyond it. The
> reference stresses are 65.47 / 66.74 / 32.1 / 31.0 MPa, so only rungs 1-2 are usable on
> the tensile pair and **the entire ladder is in the dead zone for SW-S3 and SW-S4**,
> which returned nothing (SW-S4 pinned at its aperture floor). The usable result is real
> -- retained a_h is x2.03-2.09 the virgin value at matched sigma'_n, stable all the way
> back to the datum stress -- but the saw-cut arms must be redesigned to sweep *below*
> their reference stress. See SELF_PROPPING_AND_CYCLIC_CAMPAIGN.md section 4.3.

**Stated limitation:** the ladder reaches 105 MPa of confinement, beyond what a triaxial
cell would apply. The independent variable is sigma'_n and the deck's job is to sweep
it; whether a real cell could reach the crossing is a separate question and must be
reported as one. Raising sigma_3 *reduces* the deviator, so this arm cannot re-trigger
slip and measures closure alone — which is the point.

---

## 3. Arm B — retention lag (108_07–10). No rebuild

`normal_unload_retention_time` exists in
`ADOrcaBartonBandisContactTractionFastAD::updateNormalUnloadState` and has never been
used. Three values on SW-T1 (retention fraction 0.94) and one on SW-T2 (0.84), held for
6e4 s.

**Read the source before interpreting the result.** The update is

```cpp
const Real target = std::min(raw, _normal_unload_retention_fraction * recovered_closure);
const Real alpha  = 1.0 - std::exp(-_dt / _normal_unload_retention_time);
retained = retained_old + alpha * (target - retained_old);
```

`target` is set by the **current** stress. So a positive time constant is a **lag toward**
the propped state, never a decay away from it. At constant stress the aperture still
ends exactly where `tau = 0` puts it; it just takes about 3 tau to get there. This arm
therefore answers "how fast does propping establish", the mirror of the question asked,
and **cannot** produce a closing fracture at any value of tau. It is included because
tau = 15 000 s against SW-T1's ~1470 s unloading limb separates *the lag is irrelevant*
from *the unloading limb was too fast to prop fully* — and the second would change how
the retention fraction should be calibrated.

> **CORRECTION, 2026-08-31, after wave 1.** "Cannot produce a closing fracture at any
> value of tau" is wrong. Arm B *does* produce one: SW-T1 at tau = 15 000 s goes
> 4.114 -> 3.962 um over 6e4 s and is still falling. What survives is the claim about the
> *destination* -- all three tau converge back to the tau = 0 state, so it is a delayed
> approach, not a healing mechanism, and it cannot close below the propped equilibrium.
> What was wrong is the *rate*: measured effective relaxation times are 3.0e3 / 2.0e4 /
> 1.8e5 s for tau = 150 / 1500 / 15000, i.e. **12-21x the input parameter**. The source
> reading above is correct about updateNormalUnloadState in isolation but missed the
> feedback: the retained opening holds the joint more open, which raises sigma'_n against
> the frame (46.2383 / 46.2389 / 46.2608 / 46.3431 MPa at t = 6e4), which raises its own
> target. Consequence for anyone calibrating this parameter:
> **normal_unload_retention_time is not the observed decay time, it is ~1/15th of it.**
> Numbers in SELF_PROPPING_AND_CYCLIC_CAMPAIGN.md section 4.2.

---

## 4. Arm C — closure creep (108_11–16). Needs `orca_v11` built on the cluster

The 2026-08-25 cyclic-realism back-analysis identified normal/closure creep as the one
mechanism **genuinely absent** from this model (shear creep is present through the
Perzyna term; rate-and-state healing was built, run, and bounded at <= 1.05 MPa of the
wrong sign). Pressure solution and asperity indentation close a loaded joint at constant
stress over 1e5–1e7 s. That is the missing time scale.

New opt-in term in `ADOrcaRoughnessDamageFracturePermeability`:

```
da_c/dt = (1/closure_creep_time) * (<N_eff>_+ / closure_creep_reference_stress)^q
          * (closure_creep_max_aperture - a_c),        a_c(0) = 0
```

integrated **implicitly**, `a_c = (a_c_old + r dt a_max)/(1 + r dt)`, because these decks
span dt from 0.05 s inside the slip event to 2000 s during the hold and the explicit
update is unstable once `r dt > 2`. The rate vanishes for an open joint, so creep
**freezes rather than reverses** when the fracture is pressurised back open — pressure
solution does not undo.

Four design decisions that must be reported as decisions:

1. **It is hydraulic only.** It subtracts from `a_h` and does not feed back on the
   traction — exactly the treatment the existing gouge-fill gets, read explicitly from
   the raw stress with no Jacobian term. It models loss of connected void space, not
   mechanical convergence of the two surfaces.

   > **CORRECTION, 2026-08-31, after wave 2.** True of the *direct* path, false of the
   > coupled solution. Closing `a_h` lowers transmissivity, which raises the pressure the
   > fracture holds against the shared field (+0.161 MPa on SW-T1 at 1e6 s), which lowers
   > sigma'_n (-0.192 MPa), which opens the joint back (+0.006 um). The loop is weak but
   > real. The claim that survives is "no direct Jacobian coupling"; "hydraulic only" does
   > not. See SELF_PROPPING_AND_CYCLIC_CAMPAIGN.md section 9.4.
2. **`a_c_max` is imposed, not predicted.** It is set to each run's own retained gain
   `a_h(T_p) - a_h0`, so the asymptote is exactly the pre-stimulation aperture and the
   deck answers a pure timing question. Calibrating it would need a long-duration
   experiment; Ye & Ghassemi's protocol is 3500 s and cannot supply one.

   > **CORRECTION, 2026-08-31, after wave 2.** The asymptote is NOT the pre-stimulation
   > aperture on any of the four specimens. `min_hydraulic_aperture` binds pointwise while
   > the reported aperture is a side average, so a_h converges 0.010-0.219 um ABOVE a_h0
   > with a_c fully spent, and the crossing time section 8 asks for does not exist at any
   > run length. On SW-S3 and SW-S4 `a_min` was set equal to `a_h0`, so those two cannot
   > reach it by construction. Section 9.3.
3. **Creep runs during the protocol too.** It does not switch on at `T_p`, which
   perturbs the calibrated match slightly — a further reason these are not scoreable.

   > **CORRECTION, 2026-08-31, after wave 2.** This cuts the other way. Because creep runs
   > during the protocol it leaves a signature in the unloading-branch flow rate, and the
   > protocol window CAN be scored — on the parent's stage clock, since these decks extend
   > `injection_pressure` to 1e6 s. SW-T1's Q channel brackets an optimum at tau_c = 1e5 s
   > (4.51 -> 3.37 %) and rejects tau_c = 1e4 (5.52 %). `a_cmax` remains uncalibratable;
   > tau_c is not. Section 9.5.
4. **SW-S4's arm is near-degenerate by construction** — its retained gain is 0.0207 µm
   against SW-T1's 1.913 µm, so there is almost nothing for creep to take away. That is
   not a defect in the arm; it is the 104-series result (SW-S4 *closes*, k ratio ×0.86)
   showing up again, and it should be reported as the same finding.

### Verification, both directions

**Flag off is bit-compatible.** `100_01` on `orca_v11` at 10 ranks against the 32-rank
HPC baseline, t = 3.75 s:

| | orca_v11 local | HPC baseline |
|---|---:|---:|
| `hydraulic_aperture_um_pp` | 1.659597423 | 1.659597423 |
| `differential_stress_reaction_mpa_pp` | 6.142971516 | 6.142971516 |
| `bb_effective_normal_stress_pp` | 2.682589e7 | 2.682396e7 |

The first two are identical to every printed digit. sigma'_n differs in the fifth — MPI
partition noise at 10 vs 32 ranks, the same magnitude the `orca_v9` change showed.

**Flag on integrates its own ODE.** `108_11` run locally to t = 26 s, with
`closure_creep_aperture_pp` compared against the same ODE reintegrated offline from the
run's own exported `effective_normal_compression_pp` trace:

| t (s) | N_eff (MPa) | a_c model (nm) | a_c offline ODE (nm) | rel. diff |
|---:|---:|---:|---:|---:|
| 0.75 | 26.658 | 0.0058055 | 0.0058425 | 6.3e-3 |
| 9.00 | 30.130 | 0.0730571 | 0.0730789 | 3.0e-4 |
| 18.00 | 36.677 | 0.1620579 | 0.1615416 | 3.2e-3 |
| 26.25 | 42.938 | 0.2594066 | 0.2581560 | 4.8e-3 |

Agreement is better than 0.65 % throughout and the residual has the expected source:
the material integrates the creep **pointwise** at each qp using the local N_eff, while
the offline check can only use the **side-averaged** postprocessor, and the rate law is
nonlinear in N_eff. The rate law and the implicit integration are both confirmed.

---

## 5. The controls (108_01–02) are not optional

`108_01` (SW-T1) and `108_02` (SW-S4) are their parents, unchanged, run for the same
1e6 s as arm C. If they do not hold `a_h` flat to a few ppm over that window then the
arm-B and arm-C signals are numerical rather than physical, and nothing else in the
series can be believed. The 3 ppm/300 s figure in §0 is measured over 130 s of hold at
dt <= 0.75 s; these extend it by four orders of magnitude in time and three in step size,
so they test the time integration as much as the constitutive law.

---

## 6. The list

| # | deck | specimen | parent | change from parent | end time (s) |
|---|---|---|---|---|---:|
| 1 | `108_01_swt1_ctrl_hold1e6` | SW-T1 | 100_01 | none (long hold only) | 1.0035e6 |
| 2 | `108_02_sw4_ctrl_hold1e6` | SW-S4 | 93_07 | none (long hold only) | 1.0035e6 |
| 3 | `108_03_swt1_reconf3p5x` | SW-T1 | 100_01 | sigma_3 ladder to ×3.5 | 6 200 |
| 4 | `108_04_swt2_reconf3p5x` | SW-T2 | 100_04 | sigma_3 ladder to ×3.5 | 5 552.53 |
| 5 | `108_05_sw3_reconf3p5x` | SW-S3 | 100_06 | sigma_3 ladder to ×3.5 | 7 502 |
| 6 | `108_06_sw4_reconf3p5x` | SW-S4 | 93_07 | sigma_3 ladder to ×3.5 | 6 200 |
| 7 | `108_07_swt1_unldtau150` | SW-T1 | 100_01 | retention tau = 150 s | 63 500 |
| 8 | `108_08_swt1_unldtau1500` | SW-T1 | 100_01 | retention tau = 1 500 s | 63 500 |
| 9 | `108_09_swt1_unldtau15000` | SW-T1 | 100_01 | retention tau = 15 000 s | 63 500 |
| 10 | `108_10_swt2_unldtau1500` | SW-T2 | 100_04 | retention tau = 1 500 s | 62 852.5 |
| 11 | `108_11_swt1_creeptc1e5` | SW-T1 | 100_01 | creep, tau_c = 1e5 s | 1.0035e6 |
| 12 | `108_12_swt2_creeptc1e5` | SW-T2 | 100_04 | creep, tau_c = 1e5 s | 1.00285e6 |
| 13 | `108_13_sw3_creeptc1e5` | SW-S3 | 100_06 | creep, tau_c = 1e5 s | 1.0048e6 |
| 14 | `108_14_sw4_creeptc1e5` | SW-S4 | 93_07 | creep, tau_c = 1e5 s | 1.0035e6 |
| 15 | `108_15_swt1_creeptc1e4` | SW-T1 | 100_01 | creep, tau_c = 1e4 s | 1.0035e6 |
| 16 | `108_16_swt1_creeptc1e6` | SW-T1 | 100_01 | creep, tau_c = 1e6 s | 1.0035e6 |

Parents are the **best-on-disk** decks adopted in the 2026-08-26 superseding notes, not
the published finals — these are the runs whose stationarity was measured in §0, which
is what makes the controls meaningful. They are deliberately *not* the 106-series decks:
those carry an aperture-law refit that has not yet been run, and forking an experiment
off an unvalidated parent would confound the two.

`scripts/make_108_series.py` derives every deck mechanically from its parent — no deck
was hand-edited — so each is auditable as a diff against a run already in the ranking.
Re-running the generator is idempotent. All sixteen pass MOOSE's own input checker,
which validates every parameter name, type, range check and material dependency against
the compiled app.

The paper protocol itself is untouched in every deck: `injection_pressure` is extended
by one point at its own final value, which is what `PiecewiseLinear` already clamps to,
and the time-step cap is raised **only after** the protocol ends, through a `FunctionDT`
that returns the parent's own cap up to `T_p`. The calibrated window is stepped exactly
as the parent stepped it.

**Like the 101 and 104 decks, these extend or alter the paper protocol, so they carry no
nRMSE and must not be scored against Table 2.**

---

## 7. Submitting

Two waves, because arm C needs a new executable:

**Wave 1 — no rebuild required (10 decks).** Arms A and B plus both controls,
`108_01` through `108_10`. Every parameter they use exists in the current build.

**Wave 2 — requires `orca_v11` built on the cluster (6 decks).** `108_11` through
`108_16`.

Per-deck scripts are `<spec>/Sweeps/<stem>_hpc_nochk.sh`, 32 ranks / 32 GB / 24 h.

**Do not run these locally.** The workstation has 16 physical cores and 30 GB, and the
OOM killer has already taken a 16-rank job on this campaign.

**Wall-clock risk, stated.** The arm-C and control decks add roughly 550 steps at a
2000 s cap on top of a parent that already uses most of its 24 h. If they truncate, the
truncation lands in the flat part of the hold and the result is still readable — but
checkpoints are disabled in these scripts (`_nochk`), so a truncated run cannot be
restarted.

---

## 8. What to look at when they land

- **108_01/02 first.** Everything else is conditional on these being flat. Plot
  `hydraulic_aperture_um_pp` over the whole 1e6 s window; anything beyond a few ppm of
  drift is a time-stepping artefact and invalidates arms B and C.
- **108_03–06** — plot `hydraulic_aperture_um_pp` against
  `effective_normal_compression_mpa_pp` on the reconfinement limb, over the analytic
  virgin curve. Report the crossing sigma'_n, or report that there is none in range. Do
  **not** quote an 8 MPa-to-8 MPa ratio (§1).
- **108_07–10** — the diagnostic is whether the *end* state differs from the parent's at
  all. Per §3 it should not, at any tau. If it does, the retention update is
  path-dependent in a way the source reading did not predict, and that needs explaining
  before the arm is used for anything.
- **108_11–16** — read `closure_creep_aperture_um_pp` against the analytic
  `a_c_max (1 - exp(-t/tau_eff))`, tau_eff = tau_c (sigma_ref/N_eff). Deviation means the
  implicit update is being driven at dt where the linearisation matters. The headline
  number is the time at which `a_h` re-crosses `a_h0` — which, because `a_c_max` was
  *chosen* to make that crossing exist, is a statement about rate only. Say so in the
  caption.

  > **RESULT, 2026-08-31.** tau_eff is confirmed to 2-14 % (arm B's was wrong by 12-21x),
  > and the deviation from the reintegrated ODE peaks mid-transient at 0.8-7.9 % and
  > vanishes at saturation — pointwise-vs-averaged N_eff, not the implicit update. **There
  > is no crossing**, for the clamp reason above. `scripts/ye_series108_wave2.py`
  > regenerates all of it.

---

## 9. Two repository defects found while building this series

1. **`submit_106.sh` would have failed on all fifteen decks.** It `cd`s to
   `<spec>/Sweeps` and runs `-i <stem>.i`, but MOOSE resolves relative paths against the
   *input file's* directory, so `mesh_file = mesh/...` resolved to `Sweeps/mesh/`, which
   does not exist. Reproduced locally with `--check-input`. Fixed: the fifteen 106 decks
   now use `../mesh/...`, and their per-deck `_hpc_nochk.sh` scripts — which chdir'd to
   the specimen directory, where the decks are not — now chdir to `Sweeps`, as the array
   script does. All fifteen re-checked clean. The 108 decks carry the fix from birth.
2. **A diagnostic postprocessor that silently reports zero.**
   `effective_normal_compression` is written only when `_effective_normal_traction` is
   non-null, which needs one of `normal_stress_aperture_compliance > 0`,
   `use_nonlinear_normal_closure`, `compute_effective_normal_compression` or
   `use_closure_creep`. The source comment claims the diagnostic is unconditional; it is
   not. The five SW-T1 wave-1 decks (`108_01`, `108_03`, `108_07`, `108_08`, `108_09`)
   therefore export a column of exact zeros. No recorded result was corrupted — section
   4.3's numbers reproduce exactly from `bb_effective_normal_stress_pp` — but
   `scripts/ye_series108_checks.py` reads the zeroed column at three places and should
   refuse an all-zero column rather than return zeros. Section 9.6.
3. The same latent mismatch exists for every archived deck under `Sweeps/` that still
   carries `mesh_file = mesh/...`. Those were run historically from the specimen
   directory and are not being resubmitted, so they are left alone; anything revived
   from the archive needs the one-line path change first.
