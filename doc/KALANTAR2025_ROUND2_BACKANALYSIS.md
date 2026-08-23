# Kalantar 2025 round-1 back-analysis, and the round-2 rebuild

**2026-08-23, branch `orca_v8`.** Follows `doc/back_analysis_method.md`.

Round 1 (the 110-series, built at commit `5123326`) went to HPC as three jobs. Two died
at the first timestep and the third ran 9.8 h and missed Table 2 on every channel. This
is what was wrong and what was changed.

---

## 1. What came back

| deck | job | outcome |
|---|---|---|
| OG-SH `110_01` | 19443808, 19443844, 19444590 | cancelled by SIGTERM (user), not failures |
| OG-SH `110_01` | **19444645** | **completed** — 4800 steps to t = 3600, 35 250 s wall, 6.5 GB Exodus |
| OG-T `110_03` | 19443842 | **crashed at t = 0.75 s** |
| OG-SC `110_05` | 19444648 | **crashed at t = 0.75 s** |

Both crashes are *after* `Solve Converged!` on step 1. The solver was fine; the
postprocessors killed the run.

---

## 2. The crashes: one root cause, and it is a reporting bug

```
ERROR  No element located at (x,y,z)=(0.02499, 0, 0.1144)      PointValue 'bulk_disp_x_upper_pp'   [OG-T]
ERROR  No element located at (x,y,z)=(0.0231596, 0, 0.103481)  PointValue 'pp_outlet_pp'           [OG-SC]
```

The bulk gauge points sit at `mid ± 50 mm` where `mid` is the **Ye2018 parent's**
half-height, byte-identical to the parent decks:

| | gauge centre in deck | true core mid | upper point | mesh top | |
|---|---|---|---|---|---|
| OG-SH ← SW-T2 | 66.35 mm | 60.0 | 0.11635 | 0.120 | inside — survived by luck |
| OG-T ← SW-T1 | 64.40 mm | 50.0 | 0.11440 | 0.100 | **14.4 mm outside** |
| OG-SC ← SW-S3 | 61.70 mm | 50.0 | 0.11170 | 0.100 | **11.7 mm outside** |

OG-SC carries a second instance: `injection_pressure_pp` and `pp_outlet_pp` are
`PointValue`s at **SW-S3's** borehole coordinates, which do not match OG-SC's own
`source_in`/`source_out` 1150 lines above — though the deck comment says *"must track the
source_in coord above"*. `pp_outlet_pp` is outside the mesh; `pp_inlet_pp` is inside but
0.862 mm off-node at x = −0.024021, out near the cylinder surface rather than at the
borehole. Had it not crashed, OG-SC's injection-pressure channel would have been noise —
and `effective_normal_paper_frame_mpa_pp` consumes it.

**The source nodes themselves are exactly on-node in all three Kalantar meshes.** The
source-pinning rule holds. This is purely a reporting-point defect, the same family as
the SW-S4 stale-PointValue trap.

`scripts/build_110_kalantar_decks.py` now has `check_points_in_mesh()`, which reads the
deck's own `mesh_file` and asserts every `PointValue` is inside its bounding box. It runs
on every build and would have caught this before submission.

---

## 3. The one run that finished did not reproduce Table 2

Scored at the nine hold plateaus:

| | mean error | range |
|---|---|---|
| σ'ₙ | **−13.2 %** | −17.8 … −9.7 |
| τ | **−19.3 %** | −34.8 … −11.3 |
| a_h | **−48.2 %** | −56.1 … −42.5 |
| Q | **−80.7 %** | −88.4 … −74.1 |

Every channel biased low, and the bias *shrinks* monotonically along the stage sequence.
Four separate causes.

### 3.1 The reporting frame was Ye2018's — three hard-coded constants

This one is the most dangerous because it is invisible in the physics and would have
corrupted every future score:

```
differential_stress_reaction_mpa_pp = 'sigma1_reaction_mpa_pp - 30.0'
effective_normal_paper_frame_mpa_pp = '30.0 - 0.5*(P_in + P_out)*1e-6 + 0.25*D'
shear_stress_paper_frame_mpa_pp     = '0.433012701892219*D'
```

`30.0` is Ye2018's σ₃ (Kalantar's is 33.0). `0.25` is sin²(30°) and `0.4330…` is
sin30·cos30 — SW-T2's angle, not OG-SH's 29°. On OG-SC the coefficient was sin²(29°),
SW-S3's. And OG-T and OG-SC had **no τ reporter at all**: only the SW-T2 parent carries
that postprocessor, so the gate's primary channel did not exist on two of three decks.

Consequence on the OG-SH run: `differential_stress_reaction_mpa_pp` read 39.36 MPa when
σ₁−σ₃ at the fault was 35.56, an 11 % inflation, and the two paper-frame channels
inherited it. τ and σ'ₙ implied `tan θ_eff = 0.4013`, i.e. **21.9° instead of 29°**.

Fixed: σ₃ substituted, sin²θ and sinθcosθ computed per specimen, and the τ reporter
inserted into the two decks that lacked it.

### 3.2 The loading was never gated

Line 253 of the round-1 deck says so: `axial_pres_final = -2.332804e-04 # FIRST ESTIMATE
… MUST BE GATED`. It delivers σ₁ = 69.36 MPa against the 94.65 MPa Table 2 stage 1
requires — differential 31.3 vs 61.65 MPa.

The estimate was `−σ₁/penalty`, which ignores that the penalty BC is a *series spring*:

```
sigma_1 = penalty * (u_cmd - u_sample)      ->   u_cmd = sigma_1/penalty + C_ax*(sigma_1 - sigma_3)
```

`C_ax` is now calibrated once on the completed OG-SH run: commanded 2.3328e-4 m, realised
σ₁ = 69.3554 MPa, machine-spring gap 1.71048e-4 m ⇒ u_sample = 6.2232e-5 m over a 36.36 MPa
deviator ⇒ **C_ax = 1.71177e-12 m/Pa = 0.8987·L/E**. The shortfall from 1.0 is the joint's
own normal compliance plus the non-uniform `stress_zz` near the platens.

| | σ₁ target | round 1 | round 2 |
|---|---|---|---|
| OG-SH | 94.65 MPa | −2.332804e-04 | **−3.388091e-04** |
| OG-T | 193.43 MPa | −4.780340e-04 | **−7.056216e-04** |
| OG-SC | 63.39 MPa | −1.562470e-04 | **−1.995975e-04** |

Still worth a 200 s preload check per specimen — the relation stops being linear once
the joint slips — but it is no longer a factor-1.7 guess.

### 3.3 The aperture law was SW-T2's

`initial_hydraulic_aperture` = 2.11 µm against Table 2's stage-1 4.87, anchored at
`reference_effective_normal_stress` = 66.74 MPa (Ye2018's), and `min_hydraulic_aperture`
= 2.0045 µm — a hard floor the model sat 7 % above for the entire run. a_h moved only
2.139 → 2.181 µm across the whole 6→18→6 MPa cycle.

Since Q ∝ a_h³, (2.14/4.87)³ = 8.5 % accounts for essentially the whole Q deficit.
**Q was not an independent failure.**

Round 2 anchors `(a_h0, σ'ₙ_ref)` on Table 2 stage 1 — so the stress-aperture term
vanishes exactly there — and brackets the bounds around Table 2's own observed range.

### 3.4 The fracture never slipped

τ sat flat at 17.0 MPa across all nine stages while the paper's falls 26.14 → 18.97 and
stays down. That permanent drop *is* the slip (ΔL_s 0.002 → 0.042 mm, unrecovered).
τ/τ_limit only ever reached 0.67. Three compounding reasons:

* the loading was 49 % short (§3.2);
* the envelope was 13.2 % too strong — §2.3 says the Figure 3b criterion overestimates
  OG-SH specifically (the test ran at ~0.92 τ_p, not 0.85), giving φ_peak **32.70°** not
  36.05 and φ_r **24.10°** not 27.451. The same check on OG-T (−1.4 %) and OG-SC (−3.3 %)
  confirms they need no override;
* `slip_weakening_residual_friction_angle_degrees` was left at the parent's 29.756°,
  which on OG-SH exceeded φ_r 27.451 — **the law strengthened with slip.**

Round 2 takes the residual from Table 2's last stage, `atan(τ_last/σ'ₙ_last)`:
**25.930 / 27.414 / 15.354°**. Each is checked against φ_peak, not φ_r, because the
material weakens the *mobilised* BB peak toward this value (`ADOrcaBartonBandis…Hardening.C`
line 109: `mu_p = friction_coefficient` is the BB peak from the base class).

---

## 4. Two further round-1 defects, caught by algebra rather than by the run

**OG-SC could not have burst.** Stick-slip needs `D_c < Δτ/k_eff` with
`k_eff = K_sys cos²θ sinθ / A`. OG-SC's cap is 25.4 µm and the deck carried 60 µm — on the
specimen whose entire result is one audible slip at the 24 MPa step. Now 15.2 µm. The
builder asserts the realised stability class against the observed one for all three:

| | D_c | cap | class | paper |
|---|---|---|---|---|
| OG-SH | 150.0 µm | 47.7 | stable | creeps through every hold ✓ |
| OG-T | 150.0 µm | 310.4 | unstable | progressive, 275 µm ✓ |
| OG-SC | **15.2 µm** | 25.4 | unstable | one burst ✓ |

**The dilation angle was a Ye2018 fit.** 13.97 / 16.44 / **26.0°** — a 26° dilation angle
on a saw-cut with JRC 4.23. Barton's peak dilation is `½·JRC·log₁₀(JCS/σ'ₙ)` =
**4.30 / 2.30 / 1.33°**.

---

## 5. Scoring: Table 2 holds two channels, not five

Constant-piston-displacement control makes eq (6) with `ΔL = 0` an algebraic identity:

```
dL_s = -A dtau / (K_sys sin(theta) cos(theta))
```

Verified against Table 2 (fitted/predicted slope): OG-T 0.9999 at r = −1.0000, OG-SC
0.9962, OG-SH 1.0416 — the last inside its own 1 µm print resolution. And σ'ₙ and τ are
both affine in σ₁. So σ'ₙ, τ and ΔL_s are **three readouts of one force measurement**.

`scripts/kalantar_gate.py` now scores one force channel (τ) and one flow channel — Q on
OG-SH, a_h on the other two — and prints the rest as diagnostics. It also grew its own
stage walker: `table2_gate.stage_times` hard-codes Ye2018's eleven targets and went
looking for a 24 MPa loading stage that does not exist on a Kalantar schedule.

**Which flow channel to trust is now measured, not assumed.** The notebook's §3 checks
Table 2 against itself:

| | a_h / √(12k) | a_h / cubic-law(Q) | scatter |
|---|---|---|---|
| OG-SH | 0.990 | 1.005 | 0.12 % |
| OG-T | **0.867** | 1.023 | 3.20 % |
| OG-SC | **0.875** | 0.962 | 6.08 % |

The plane cubic law reproduces the printed `a_h` from the printed `Q` on all three within
4 %, but the `k` column disagrees with `a_h` by 13 % on OG-T and OG-SC. **`k` is the
inconsistent column there, not `a_h`** — which independently justifies scoring a_h on
those two.

---

## 6. What is still inherited

Not derived, and still Ye2018 fits: the Barton–Bandis normal-closure constants
(`initial_normal_stiffness`, `maximum_closure`, `normal_closure_*`),
`normal_unload_retention_fraction`, `aperture_scale`, `tangential_viscosity`,
`roughness_characteristic_slip`, `dilation_decay_distance`.

At Kalantar's stress levels the closure term contributes ~0.03 µm (σ₀ = V_m·K_ni = 15 MPa
against σ'ₙ ≈ 43 MPa with p = 4), so it is nearly inert — but "inert" is not "derived".
Refit against the a_h(σ'ₙ) loop once the loading gate passes. Round 3.

---

## 7. Round-2 deliverables

* `scripts/build_110_kalantar_decks.py` — derives every constant above from
  `validation/kalantar2025_table2.csv` and section 2–3, asserts the stability class and
  the weakening direction, and checks every `PointValue` against its own mesh.
* the three rebuilt decks, all `Syntax OK`.
* `scripts/kalantar_gate.py` — two scored channels, its own stage walker, the frame
  check printed alongside.
* `Examples/Kalantar2025/Kalantar2025_table2_validation.ipynb` — stage tables, channel
  figures, τ–σ'ₙ stress path against the deck's own envelope, a_h(σ'ₙ) hysteresis,
  and a completeness gate that **refuses to score a truncated run**.
* wall time 3 days on OG-T/OG-SC (2.5× OG-SH's schedule), and the Exodus
  `time_step_interval` scaled to hold every deck near 500 frames rather than letting
  OG-SC write ~16 GB.

### One local-toolchain note

The `.jitcache/*.so` files that came down with the HPC results **crash the local
`orca-opt`** — a bare `MPI_Abort` inside `vtkMPICommunicator` with no MOOSE message, during
setup. They were compiled by a different build. Deleting them restores `Syntax OK`.
`.jitcache/` is in `.gitignore`; do not sync it back from HPC.

---

## 8. Prediction, written before the round-2 runs

Fixing §3.1–3.4 should move OG-SH's τ from −19.3 % to within a few percent at stage 1 and
let the joint reach its envelope. The remaining risk is that OG-SH's a_h *loss* is now
carried entirely by `slip_damage_scale = 1.15 µm` with a 15 µm characteristic slip, and
that rate is the one number in the aperture law taken from the shape of Table 2 rather
than from a stated constant.

**Falsifier:** if OG-SH's a_h now falls too fast early and flattens, the characteristic
slip is too short and the *level* was right; if it falls uniformly too little, the loading
gate has not delivered enough slip and §3.2 is not finished.
