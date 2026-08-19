# Branch `orca_v6` — what we are testing

The 93/94-series closed the Ye & Ghassemi (2018) validation at 2.4–4.6 % nRMSE with a
Barton–Bandis primary and a Coulomb baseline. This branch does **not** try to make that
number smaller by tuning. It tests two specific claims that came out of the 2026-08-18
audit, both of which are about *credibility* rather than accuracy:

1. the friction law's rate dependence is real, significant, and currently fitted on a knob
   labelled "numerics";
2. two parameters control pressure-driven de-stressing of the fracture, one of them sits
   outside its physical bound, and nobody has measured whether the fits care.

Nothing here is a recalibration. Every deck in both series is a 93-series final with one
or two named things moved, and the 93-series deck is its own control.

---

## 0. What the audit found (the short version)

**Rate dependence.** Every BBFast deck sets `tangential_viscosity` inside `[czm_contact]`.
The kernel forms a Perzyna overstress `eta * V` where `V = dgp/dt`
(`ADOrcaBartonBandisContactTractionFastAD.C`, the `visc_rate` term). At SW-S4's
`eta = 3.5e12 Pa.s/m` that is

| V (m/s) | `eta*V` |
|---|---|
| 1e-8 | 0.035 MPa |
| 1e-7 | 0.35 MPa |
| 1e-6 | 3.5 MPa |

against a shear strength of 15–25 MPa. This is not a regulariser; it is the model's rate
law. And the values are not uniform: SW-T1, SW-T2 and SW-S3 run at `4.0e11`, while **SW-S4
runs at 3.5e12 — nine times higher** — with the deck comment "66_03: lower the transient
shear pedestal". SW-S4 is precisely the specimen whose staircase burst timing never fitted
and whose `D_c` bracket failed in *both* directions. The specimen that needed extra
rate-strengthening got it through a parameter documented as numerical.

**Poroelastic constants.** All four decks use `E = 67 GPa`, `nu = 0.32`, giving a drained
bulk modulus `K = E/(3(1-2nu)) = 62.0 GPa`. Biot needs `alpha = 1 - K/K_s`, and granite's
mineral modulus `K_s` is 45–50 GPa. `K` already exceeds `K_s`, so `alpha` comes out
**negative**, not the 0.6 in the decks; reaching 0.6 would require `K_s = 155 GPa`, above any
silicate mineral. Separately, `fault_pressure_coefficient` — which scales the pressure fed
to the CZM fault-pressure kernels — is 1.0 on SW-T1/SW-T2 but **0.86–0.87 on the two saw
cuts**, one of them labelled "legacy fitted". A joint's effective-stress coefficient is
physically ~1. One knob above its bound and one below, both on the same lever.

---

## 1. Source change: `OrcaBartonBandisRateStateHardening`

New class, `ADOrcaBartonBandisRateStateHardening`, deriving from the existing
`...FastADHardening`. It adds a Dieterich–Ruina overstress and sets the Perzyna viscosity
aside:

```
tau_lim = c(W) + sigma'_n * mu(s^p)                          <-- parent, UNCHANGED
        + sigma'_n * [ a*ln(1 + V/V0) - b*ln(1 + V_theta/V0) ]   <-- new
```

with `V = dgp/dt`, `V_theta = D_rs/theta`, and `theta` obeying the aging law
`dtheta/dt = 1 - V*theta/D_rs`, integrated exactly over the step.

**Why an overstress and not the arcsinh flow form.** The parent is a return-map law with a
genuine elastic stick branch. The regularised flow form
`tau = sigma'_n a asinh[(V/2V0) exp(Psi/a)]` has no stick branch — it creeps at every
stress — so substituting it would destroy the active-set logic. Added as an overstress, RSF
occupies exactly the slot the viscosity occupies today: same residual term, same tangent.
The existing `ADOrcaBartonBandisFlowRSFContactTraction` *is* a flow-form RSF law, but it
bundles RSF with Barton's JRC-mobilization table and a different dilation law, so swapping to
it would confound three changes at once. That is why this needed code.

**The hooks already existed.** `computeAdditionalShearStrength[Real]`,
`carryAdditionalState` and `commitAdditionalState` are no-ops in the base class, and a
2026-07-11 comment there says theta must keep aging through stick because
"only RSF-enabled subclasses see the (correct) healing". The architecture anticipated this.

**Limits.** At steady state `theta = D_rs/V`, so `V_theta = V` and the overstress collapses
to the textbook `sigma'_n (a-b) ln(1 + V/V0)`. At `V = 0` held long enough, `theta -> inf`,
`V_theta -> 0`, and the overstress goes to zero: **the Barton–Bandis envelope is the
quasi-static, fully healed strength**, which is the frame it was calibrated in. Both branches
are logarithmic and therefore bounded on any velocity this problem can reach — no clamp is
applied and none is needed.

`use_rate_and_state = false` recovers the parent bit-for-bit.

---

## 2. The 95-series — rate-and-state (16 decks, mesh 5)

`D_rs = 5e-6 m` and `V0 = 5e-8 m/s` are **held fixed across all four specimens and all four
variants**. They are not fitted. 5 µm is a laboratory value for bare/saw-cut granite, and it
has to be well below the 30–80 µm of total slip in this test or `b` cannot express itself at
all. If the `b` bracket comes back flat, `D_rs` is the first suspect and the next thing to
bracket.

### The level-matched control

Equating the two rate laws' direct effects at `V = V0` (`eta*V0 = sigma'_n * a * ln 2`) turns
each deck's fitted viscosity into an implied `a`:

| specimen | `eta` (Pa·s/m) | `sigma'_n*` (MPa) | implied `a` | lab range |
|---|---|---|---|---|
| SW-T1 | 4.0e11 | 56.94 | 5.07e-4 | 0.008–0.015 |
| SW-T2 | 4.0e11 | 57.88 | 4.99e-4 | 0.008–0.015 |
| SW-S3 | 4.0e11 | 23.42 | 1.23e-3 | 0.008–0.015 |
| **SW-S4** | **3.5e12** | 26.51 | **9.52e-3** | **0.008–0.015** |

**SW-S4 is the only specimen whose fitted viscosity is already physical.** The other three sit
8–20× below the laboratory range. That is a result in itself, and it sets the expectation for
this series.

### Deck inventory

| deck | specimen | `a` | `b` | what it isolates |
|---|---|---|---|---|
| `95_01` | SW-T1 | 5.067e-4 | 0 | level-matched control: form only |
| `95_02` | SW-T1 | 0.010 | 0.005 | velocity strengthening, lab `a` |
| `95_03` | SW-T1 | 0.010 | 0.010 | velocity neutral |
| `95_04` | SW-T1 | 0.010 | 0.015 | velocity weakening |
| `95_05`–`95_08` | SW-T2 | 4.985e-4 / 0.010 | 0 / .005 / .010 / .015 | as above |
| `95_09`–`95_12` | SW-S3 | 1.232e-3 / 0.010 | 0 / .005 / .010 / .015 | as above |
| `95_13`–`95_16` | SW-S4 | 9.523e-3 / 0.010 | 0 / .005 / .010 / .015 | as above |

The `aeq_b0` deck is the controlled comparison: same rate-strengthening magnitude at `V0`,
`b = 0` so no state evolution, so **any move away from the 93-series is attributable to the
form of the rate law alone** (linear → logarithmic). The three `a = 0.010` decks then bracket
`b` in both directions around neutral.

### Falsifiable prediction

If the SW-S4 hold-stage deficit is a healing effect, `b > 0` supplies the slip during holds
that `93_07` misses and the staircase timing improves **without touching `D_c`**. If the
timing is set by the injection protocol instead, no value of `b` helps and the bracket comes
back flat — which closes the question rather than leaving it open.

### What would be a build error rather than a physics result

The `a = 0.010` decks give SW-T1/T2/S3 roughly an order of magnitude *more* rate strengthening
than they were calibrated with, so **those three are expected to move, possibly for the
worse**. That is a physics result about where the rate law was mis-set, not a bug.

A bug looks different: a large degradation on **all four including the `aeq_b0` controls**.
Before concluding anything in that case, check `rsf_overstress_mpa_pp` against `eta*V` from
the corresponding 93 run — they should agree closely at `V ~ V0` by construction.

### New diagnostics

`rsf_theta_pp` [s], `rsf_slip_velocity_pp` [m/s], `rsf_overstress_mpa_pp` [MPa]. The last is
the whole experiment in one channel: it is what `eta*V` used to be.

---

## 3. The 96-series — poroelastic consistency (8 decks, mesh 5)

One change per deck, nothing refitted.

| deck | specimen | moves |
|---|---|---|
| `96_01` | SW-T1 | `biot_coefficient` 0.6 → 0.2 |
| `96_02` | SW-T2 | `biot_coefficient` 0.6 → 0.2 |
| `96_03` | SW-S3 | `biot_coefficient` 0.6 → 0.2 |
| `96_04` | SW-S3 | `fault_pressure_coefficient` 0.87 → 1.0 |
| `96_05` | SW-S3 | both |
| `96_06` | SW-S4 | `biot_coefficient` 0.6 → 0.2 |
| `96_07` | SW-S4 | `fault_pressure_coefficient` 0.86 → 1.0 |
| `96_08` | SW-S4 | both |

SW-T1 and SW-T2 get only the alpha probe — their `fault_pressure_coefficient` is already 1.0,
so an "fpc1p0" deck would be a byte-for-byte rerun of the 93 deck. **That asymmetry is itself
the finding**: only the saw cuts are attenuated.

**How to read the result.** This is a sensitivity probe, not a recalibration. If the Table-2
scores barely move, the inconsistency is cosmetic, `alpha` can be corrected by fiat, and a
fitted parameter is deleted for free — worth more to the paper than another 0.5 % of nRMSE.
If they move a lot, `nu` has to be revisited before anything else, because `alpha` is not
independently adjustable at `nu = 0.32`.

**Deliberately not in this series:** `nu` 0.32 → 0.22. It changes the elastic response and so
requires re-gating `axial_pres_final`, which makes it not a one-change deck. It is the
follow-up if this probe comes back sensitive.

---

## 4. What is deliberately NOT here

The audit swept for missing physics. Most candidates are already present or negligible, and
they are recorded here so the sweep is not repeated:

- **Dilatancy hardening** (Segall & Rice 1995) — already in the model.
  `OrcaFractureFlowInterfaceKernel` carries exact `d(rho*a_h)/dt` storage, so a dilating patch
  does draw fluid and drop local pressure. If it is not acting, the reason is the Dirichlet
  pressure BC pinning `source_in`/`source_out`; measure it before adding anything.
- **Loading-frame compliance** — already modelled as a series penalty spring.
- **Shear-induced aperture / channelisation** — the literal Barton law was tried; the
  transmissibility ratio was only 1.00–1.45, so it is not the mechanism.
- **Non-Darcy flow, thermal, pressure solution, subcritical crack growth** — negligible at
  ml/min through micron apertures, isothermal, over hours.

Two real weak spots need no code and are **not** addressed by this branch:

1. **`Q` is partly circular.** The cubic-law `W/L` is inverted from Table 2 via eq (10), so
   scoring `Q` against Table 2 partly scores the inversion. All 93/94/95/96 decks carry
   `flow_rate_mesh_geometry_ml_min_pp`; score from that instead (task #13). Highest
   value-per-effort item in the campaign.
2. **Report the identifiable combination.** The loading path constrains `(mu_eff, c_eff)` at
   the operating `sigma'_n`; it does not separately constrain JRC, JCS and `c`. Quoting the
   tangent and stating the degeneracy turns `JRC = 5` from a fudge into a measurement.

---

## 5. Running

24 decks, all mesh 5, all with their own `file_base` (the inherited-`file_base` trap was
caught and fixed during the build — every deck initially pointed at its 93 parent's outputs).

```bash
cd Examples/YeGhasemmi2018
for d in SWT1 SWT2 SWS3 SWS4; do
  for s in $d/9[56]_*_hpc_nochk.sh; do sbatch "$s"; done
done
```

Local (mesh 5 only, 24-rank ceiling — three jobs at 8 ranks):

```bash
mpiexec -n 8 ../../../orca-opt -i 95_13_sw4_rsf_aeq_b0.i Outputs/chk/enable=false csv_file_base=results_csv_local/95_13_sw4_rsf_aeq_b0 exodus_file_base=results_exodus_local/95_13_sw4_rsf_aeq_b0
```

Use `/home/geomechanics/miniforge/envs/moose/bin/mpiexec` — `/usr/bin/mpiexec` is OpenMPI and
`orca-opt` is MPICH, so it aborts in `MPI_Init_thread`.

**Validation done:** all 24 pass `--check-input`; the 96 decks differ from their 93 parents by
exactly the 1–2 named constants and nothing else; the 95 decks by exactly the material type,
`tangential_viscosity → 0`, five RSF parameters and four postprocessors; every deck's
postprocessor set equals its parent's (plus the four new ones on the 95s) with no duplicates.

---

# 6. RESULT — the SW-S4 rate-law experiment (2026-08-18)

Four decks ran locally on mesh 5, 8 ranks each. **The pre-registered hypothesis of §2.4 is
falsified.** The section below is written against the prediction as it was recorded *before*
the runs, not reverse-engineered from the answer.

| run | `a` | `b` | reached | wall | outcome |
|---|---|---|---|---|---|
| `93_07` control | — (`eta = 3.5e12`) | — | t = 3500 | 3.6 h | complete |
| `95_13` | 9.523e-3 | 0 | t = 3500 | 5.2 h | complete |
| `95_14` | 0.010 | 0.005 | t = 3500 | 5.5 h | complete |
| `95_16` | 0.010 | 0.015 | **t = 1554.9** | 9.6 h | **stalled, killed** |

`93_07` had never actually been run. It was queued behind the 95s specifically for this
comparison, because the previously scored SW-S4 final (`90_08`) predates the 92-series channel
fixes and carries neither `reported_czm_shear_slip_mm_pp` nor
`flow_rate_mesh_geometry_ml_min_pp` — scoring the 95s against it would have confounded the rate
law with a change in what the postprocessors *mean*.

## 6.1 Build validation — clean

`95_13` and `93_07` produced an **identical time grid**: 2335 rows, `max|Δt| = 0.0`, the same
2334 steps, the same final `dt`. They agree on Table-2 stages 1–4 to four decimals, with slip
onset differing by 3 s (1254.0 vs 1257.0). The level-matched control is indistinguishable from
the Perzyna viscosity right up to first slip — which is exactly what `eta*V0 = sigma'_n*a*ln 2`
was constructed to guarantee, and it rules out the "build error" branch of §2.5.

`rsf_overstress_mpa_pp` matches `sigma'_n * a * ln(1 + V/V0)` to `2.9e-2 MPa` on a `0.53 MPa`
peak. The residual is not a defect: the check uses `effective_normal_paper_frame_mpa_pp` while
the class uses the internal `_bb_effective_normal_stress`, and side-averaging a nonlinear
function of `V` carries a Jensen gap.

## 6.2 Result 1 — `b` does not heal the hold stages (hypothesis falsified)

Stage-4 `d_s` [mm] is where SW-S4's deficit lives. Paper target **0.0170**:

| `93_07` | `95_13` (b=0) | `95_14` (b=.005) | `95_16` (b=.015) |
|---|---|---|---|
| 0.0038 | 0.0037 | 0.0039 | 0.0043 |

The **entire** `b` bracket buys 0.0005 mm of a 0.013 mm deficit — 4 % — while stage 5
degrades monotonically in the same direction (0.0476 → 0.0634 → 0.0659 → 0.0664 against a
paper value of 0.0410). `b` is flat where the hypothesis needs it to move and harmful where it
need not move at all.

Per §2.4 this closes the question: **the SW-S4 staircase timing is set by the injection
protocol, not by a hold-stage healing deficit.** That is consistent with the earlier campaign
finding that this specimen slips on ramps rather than holds, and it means `D_rs` is *not* the
next thing to bracket — the mechanism is absent, not mis-scaled.

Onset (first `d_s > 5 µm`) does respond to `b`, monotonically: 1254.0 / 1257.0 / 1233.6 /
1164.1 s. But onset was never the failing observable, and note that `b > 0` **advances** slip
rather than delaying it — the opposite of what was expected when the bracket was designed.
Recorded here because it was predicted wrong.

## 6.3 Result 2 — velocity weakening destabilises the solver, as predicted

`95_16` (`a-b = -0.005`) is the only run that produced discrete slip events: 7.2 µm over
t = 1347.1 → 1350.8 and 2.3 µm over t = 1353.9 → 1354.1. At the first event `d_s` went
11.18 → 41.24 µm, `theta` collapsed 376 → 1.21 s, the overstress reached **−1.51 MPa**, `tau`
dropped 11.53 → 8.14 MPa and `dt` fell 1.5 → 2.36e-4 s. It recovered (`dt` back to 1.5 by
t = 1468, `theta` re-healed to 144 s), then stalled permanently at t = 1554.86 with `V = 0`,
`d_s` frozen at 67.93 µm, overstress −0.146 MPa and the nonlinear residual oscillating in
`[0.98, 1.94]e-2` with no descent — **0.85 s of simulation in 264 steps**, at which rate
reaching t = 3500 needs ~600 000 more. Killed at 09:52 elapsed.

This is a quasi-static solver meeting a genuine dynamic instability, not a code fault: on the
stick branch the state term leaves a negative overstress that lowers strength and promotes
slip, while slipping consumes `theta` and raises strength back, so Newton flip-flops across the
active-set boundary. It is the same failure family as the long-standing SW-S3/SW-S4 slip-arrest
non-convergence, and `95_16` is now a **cheap deterministic reproducer** for it — far more
useful than waiting for a spontaneous stall.

## 6.4 Result 3 — the fitted viscosity was inflating `tau` (the keeper)

This is the one transferable finding, and it survives the falsified hypothesis.

Over slipping steps the Perzyna term supplies a mean **0.3138 MPa** (peak 0.8713, n = 615)
while the level-matched RSF supplies **0.1405 MPa** (peak 0.5346, n = 594). The reason is
structural: `ln` saturates and `eta*V` does not. Matched at `V0` by construction, they diverge
above it, and this problem runs above it — peak `V` was 2.489e-7 m/s (control) and 6.353e-7 m/s
(RSF), 5–13× `V0`.

Table-2 MAE, SW-S4, all 11 stages:

| observable | n | ctrl `93_07` (η) | `95_13` (b=0) | `95_14` (b=.005) |
|---|---|---|---|---|
| Q_ml_min | 11 | 0.0025268 | **0.0021171** | 0.0020857 |
| sigma_n_MPa | 11 | 0.43615 | **0.38502** | 0.38627 |
| tau_MPa | 11 | 0.72571 | **0.62359** | 0.62462 |
| dn_mm | 10 | **0.0012594** | 0.0022237 | 0.0024404 |
| ds_mm | 10 | **0.0042428** | 0.0066070 | 0.0071509 |

RSF improves Q, `sigma'_n` and `tau` by ~14 % each and degrades `d_n` by 76 % and `d_s` by
56 %. The `tau` gain localises cleanly: stages 1–4 are identical; at stage 5 the control reads
`tau = 7.514` against a paper value of 6.48 (+1.03) while `95_13` reads 5.847 (−0.63), a
control-minus-RSF difference of **1.667 MPa** of which `eta*V` contributes 0.58; stages 6–11
carry a flat ~0.13 MPa residual where `eta*V` is already zero, i.e. a slip-history offset
rather than a rate effect.

**For the manuscript:** the rate term is not a regulariser, and at SW-S4's fitted `eta` it is
worth over 1 MPa of shear strength at the decisive stage — enough to be visible in Table 2.
Stating that, and stating that a laboratory-valued `a` reduces it, is a credibility result
independent of whether RSF is adopted.

## 6.5 Verdict

**RSF at a physical `a` is not a net improvement for SW-S4.** It trades displacement accuracy
for stress and flow accuracy at roughly equal magnitude, so adopting it would be a lateral
move dressed as a physical upgrade.

The deeper read is that neither law addresses the actual defect. SW-S4's slip is too
**concentrated**: too little by stage 4, too much by stage 5, with the total roughly right.
Both `eta*V` and the RSF overstress act on *velocity*, so they can only rescale how fast slip
proceeds once it starts — neither changes *when the envelope yields*. That points back at the
onset envelope, not at the rate law.

## 6.6 Consequences for the queued HPC batch

- **Keep** the three remaining level-matched `b = 0` controls (`95_01` SW-T1, `95_05` SW-T2,
  `95_09` SW-S3). Those three have fitted viscosities 8–20× *below* the laboratory range, so
  the `tau`-inflation result may be SW-S4-specific and is worth one deck each to establish.
- **Drop or defer** the nine `b > 0` decks for SW-T1/T2/S3, and `95_15`. The `b` bracket has
  been run to exhaustion on the specimen where it had the best case and returned flat;
  spending 9 HPC jobs to re-establish that is not justified.
- **`95_15`** (`a = b = 0.010`, velocity neutral) is not worth running: it is bracketed on both
  sides by `95_14` and `95_16`, and both bounds are already known.
- **Keep all eight 96-series decks unchanged.** They probe the poroelastic constants and are
  entirely independent of the rate law; nothing here touches them.

## 6.7 A note on the negative result

The `b` bracket was designed to be falsifiable and it falsified. That is worth recording as
plainly as a success would be: the hold-stage healing hypothesis for SW-S4 is now closed, the
`D_rs` follow-up it would have spawned is cancelled, and the campaign is one live hypothesis
lighter. The two things that came out of it — a measured `tau` inflation and a deterministic
reproducer for the slip-arrest stall — were both by-products.
