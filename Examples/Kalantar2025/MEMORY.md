# Kalantar et al. (2025) validation — project memory

**What this file is.** The running memory of the second validation dataset. Everything
done from first reading of the paper to the round-2 rebuild: the paper audit, the mesh
work, the round-1 HPC batch and its back-analysis, every constant that changed and why,
what is still inherited, and the plan from here. It is the Kalantar counterpart of the
repo-root `MEMORY.md`, which stays with Ye2018.

**How to use it.** §0 is the state. §5 is what went wrong and §6 is what was done about
it — read both before touching a deck, because most of the round-1 defects were
*inherited* rather than chosen, and a "fix" applied without knowing that will be applied
backwards. §7 is the round-3 scope. §10 is the trap list.

**How to keep it.** Append to the section that fits. State what was measured, not just
what was concluded. When a claim here is shown wrong, correct it **in place and say so**
— §5 exists because the wrong round-1 assumptions were worth more than the right ones.
Add a line to §12.

**Last updated:** 2026-08-24 (round-3 results). **Branch:** `orca_v8`, commit `353faf3` +
round-2 and round-3 results.

> **State in one line, 2026-08-24 22:48.** Round 3 finished on OG-SH and OG-SC. **OG-SH mean
> nRMSE 62 → 67 → 17**, from acting on round 2's one preregistered null. OG-SC's force channel
> is exact for five stages then breaks on a single mis-derived constant. OG-T is unchanged and
> still blocked on its preload. TODO #121 (`bb_jrc_mobilized`) is **closed — it is a deck flag,
> not a bug**. Round-4 change list, with preregistered nulls:
> `doc/KALANTAR2025_ROUND3_BACKANALYSIS.md` **Part II §10**. Read Part II before Part I.

---

## 0. State

| item | path | status |
|---|---|---|
| Reading notes (69 kB) | `doc/reading_kalantar2025_self_propping_granodiorite.md` | done |
| Validation plan / method | `doc/KALANTAR2025_VALIDATION_PLAN.md` | done, 5 sections |
| Round-1 back-analysis | `doc/KALANTAR2025_ROUND2_BACKANALYSIS.md` | done, 8 sections |
| Digitized Table 2 (39 hold stages, 3 specimens) | `validation/kalantar2025_table2.csv` | done |
| Figure 8 Pedrosa fits, incl. their reanalysis of our four specimens | `validation/kalantar2025_figure8_pedrosa_fits.csv` | done |
| Parameter audit (runs before any deck) | `scripts/kalantar_parameter_audit.py` | done, 7 sections |
| Deck builder | `scripts/build_110_kalantar_decks.py` | done, round 2 |
| Gate | `scripts/kalantar_gate.py` | done, two scored channels |
| Notebook | `Kalantar2025_table2_validation.ipynb` | done, executed, 4 figures |
| Cubit journals ×4 (OG-SH 29°, OG-T 28° + 26° arm, OG-SC 30°) | `*/mesh/*.jou` | done |
| Meshes `.e` | `*/mesh/*.e` | built and verified 2026-08-23 |
| 110-series BBFast decks, **round 2** | `OGSH/110_01…`, `OGT/110_03…`, `OGSC/110_05…` | built, `Syntax OK`, **run** |
| SLURM jobs, 64 ranks / 64 GB | `*/110_0*_hpc.sh` | done — 2 d OG-SH, 3 d OG-T/OG-SC |
| **Round-2 results, downloaded 2026-08-24 10:52** | `*/results_csv_hpc/110_0{1,3,5}_*.csv` | **OG-SH complete and scored; OG-T 36 % and OG-SC 77 % — truncated, diagnosed but NOT scoreable** |
| **Round-3 results, downloaded 2026-08-24 22:48** | `*/results_csv_hpc/110_0{2,4,6}_*.csv` | **OG-SH 100 % (mean nRMSE 17) and OG-SC 100 % (77) — both scoreable; OG-T 0.5 %, dead** |
| Round-1 results | (superseded in place) | scored, see §5 |
| 111-series Mohr–Coulomb siblings | — | **unblocked** — round 3 landed clean on two of three |

**One line.** Round 1 went to HPC as three jobs; two died at the first timestep on a
reporting bug and the third ran 9.8 h and missed Table 2 on every channel. Six defect
classes were found and fixed, all six now guarded by an assertion in the builder. Round 2
ran; **its two big fixes both provably worked — the reporting frame is exact and the
loading gate lands stage 1 within 0.6 % — and the run still fails, for a reason those
fixes uncovered rather than caused: the fracture does not slip.** A seventh inherited
Ye2018 constant was found in the process (§6.7, §6.8). **Then the two truncated runs were
unhidden and the picture changed again (§6.9): the three specimens fail in three different
places, with OPPOSITE-signed envelope errors — OG-SH's too strong, OG-SC's too weak by a
two-sided measured bracket, and OG-T not loaded at all because its fracture unloads
normally during the preload ramp. Both truncations are `dtmax`, not the mesh (§6.10).**

---

## 1. The dataset, and why it is worth the effort

Kalantar et al. (2025), *JGR Solid Earth* **130**, e2025JB031938 — hydraulic behaviour of
self-propping fractures in Odenwald granodiorite, three specimens under triaxial
compression with fluid injection along the fracture.

| specimen | fracture | θ | core L × D | Table 2 stages | headline result |
|---|---|---|---|---|---|
| **OG-SH** | shear (natural) | 29° | 120 × 49.98 mm | 9 (5 load, 4 unload) | creeps through every hold, monotonic permeability **loss** |
| **OG-T** | tensile (mated) | 28° printed / 25.999° geometric | 100 × 49.98 mm | 9 (9/8) | progressive slip, 275 µm total |
| **OG-SC** | saw-cut | 30° | 100 × 49.98 mm | 7 (7/6) | one audible stick-slip burst at the 24 MPa step |

σ₃ = **33 MPa** (Table 2 back-calculates it; the prose says 30 — see §2). Pore pressure
`P_p = (P_i + 3)/2` MPa. UCS/JCS from Table 1.

Four reasons this is the right second dataset, beyond simply being a second dataset:

1. **It independently reanalyses our own four Ye2018 specimens** (Figure 8 Pedrosa fits).
   Somebody else's numbers for our samples.
2. **It measures the frame stiffness we had to infer.** `K_sys` is the single most
   leveraged derived constant in the Ye2018 campaign — a ×2 bracket moves Q by
   −93.9 %/+408 % — and this paper reports it.
3. **It confirms the gouge mechanism from the opposite direction**: their shear specimen
   loses permeability where ours gained it, and the difference is traceable to gouge
   production rather than to the constitutive law.
4. **It adds the rock-property axis our four specimens could not** — a different granitoid
   at a different JRC/JCS.

---

## 2. The paper audit — four internal inconsistencies, all checkable

The standing rule is *audit the plumbing before believing any physics*. Applied here it
found four things, in the order they were found:

1. **σ₃ = 33 MPa, not the prose's 30.** Recovered from Table 2's own stress columns
   through the angle identity below; consistent across all 39 stages.
2. **OG-T's angle.** The printed 28° and the printed core dimensions cannot both be true;
   the geometry gives 25.999°. Built 28° as primary and 26° as a sensitivity arm. Same
   class of error the Ye2018 audit found on SW-T2 — **twice, in two independent papers,
   by the same method.**
3. **Equation (7) does not reproduce the paper's own Table 2.** Table 2 prints `Q` and
   `a_h` for the same 39 stages, so the reduction is checkable against itself. Eq (7)
   misses by a constant factor **2.17 in a_h, 10.3 in a_h³**, with 0.12 % scatter across
   OG-SH's nine stages. The constancy is the argument: the functional form is right and a
   numerical factor is wrong. It cannot be rescued through the aspect ratio `n` — matching
   would need `B = 0.0807` and `B = 2/(π·tan⁻¹ 2n)` has a floor of 0.5750 at `n = 1`.
   What *does* reproduce Table 2 is the plain plane cubic law this project already uses,
   `a_h³ = (Qη/ΔP)·12·L/W`, with no fitted constant: **0.9946 ± 0.0012** on OG-SH.
   *So the Ye2018 flow operator transfers unchanged.*
4. **The `k` column disagrees with the `a_h` column on OG-T and OG-SC.** Found while
   deciding which flow channel to score:

   | | a_h / √(12k) | a_h / cubic-law(Q) | scatter |
   |---|---|---|---|
   | OG-SH | 0.990 | 1.005 | 0.12 % |
   | OG-T | **0.867** | 1.023 | 3.20 % |
   | OG-SC | **0.875** | 0.962 | 6.08 % |

   The cubic law reproduces printed `a_h` from printed `Q` within 4 % on all three, but
   `√(12k)` is 13 % off on two. **`k` is the inconsistent column there, not `a_h`** —
   which is independent justification for the gate's channel choice (§4).

The angle identity that does most of this work:

```
tan θ = (σ'ₙ − σ₃ + P_p) / τ ,      P_p = (P_i + 3)/2
```

---

## 3. Geometry and meshes

Four journals, built in Cubit by Saeed, verified with `scripts/check_mesh_geometry.py`
and `scripts/check_source_nodes.py` under the `moose` conda env.

| mesh | elements | ifc nodes | ifc pitch | L / D / θ | area vs derived | source pinning |
|---|---:|---:|---:|---|---|---|
| `og_sc_theta30_size3` | 68,096 | 2185 | 1.004 mm | 100.00 / 49.98 / 30.000 | exact | OK, 388.5 µm |
| `og_sh_theta29_size3` | 100,048 | 1977 | 1.035 mm | 120.00 / 49.98 / 29.000 | exact | OK, 4.1 µm |
| `og_sh_theta29_size4` | 30,600 | 937 | 1.504 mm | 120.00 / 49.98 / 29.000 | exact | **FAILS — bulk node** |
| `og_t_theta28_size3` | 53,760 | 2297 | 0.980 mm | 100.00 / 49.98 / 28.000 | exact | OK, 792.9 µm |
| `og_t_theta26_size3` | 35,840 | 2297 | 0.992 mm | 104.48 / 49.98 / 26.000 | exact | OK, 849.1 µm |

Plane-fit residual 0.00 µm on all five; `fracture_interface` area matches the closed-form
`πr²/sin θ` to six significant figures; all six nodesets present and populated.

**`og_sh_theta29_size4` is the one failure and it is the dangerous kind.** At 1.504 mm
interface pitch both borehole coordinates find a *bulk* node 951 µm away while the nearest
node actually on the fracture is 1217 µm away. `use_closest_node = true` would take the
bulk node, inject into the matrix, complete the run, and be wrong. Factor 3 is the OG-SH
production mesh and the journal's size/export lines were switched so regenerating cannot
reproduce the bad one.

**Snapped borehole coordinates are in each journal header and are what the decks use.**
The snap lengthens the borehole separation `L`; under the cubic law `Q ∝ W/L` so the bias
is just the length change: OG-SC −0.96 %, OG-SH −0.01 %, OG-T −1.83 %. Every deck carries
both `paper_flow_width_over_length_*` and `mesh_flow_width_over_length_*`, exactly as the
93-series does. All are smaller than the paper's own hole-centre/hole-edge ambiguity
(1.000 mm), which remains the dominant flow-path uncertainty.

**Stale duplicate:** `OGSC/mesh/og_sc_theta30_size5.e` has the same node count, element
count and interface pitch as `size3.e` — it is a pre-rename export, not a factor-5 mesh.
Scoring the two against each other would return perfect "mesh convergence" from a no-op.
**Rebuild or delete before any convergence claim.**

---

## 4. What is identifiable: Table 2 holds two channels, not five

Constant-piston-displacement control makes eq (6) with `ΔL = 0` an algebraic identity:

```
ΔL_s = − A·Δτ / (K_sys · sinθ · cosθ)
```

Verified against Table 2, fitted/predicted slope: OG-T **0.9999** at r = −1.0000, OG-SC
**0.9962**, OG-SH **1.0416** (inside its own 1 µm print resolution). And σ'ₙ and τ are
both affine in σ₁. **So σ'ₙ, τ and ΔL_s are three readouts of one force measurement.**

The same control law hands you a stick-slip criterion for free:

```
D_c < Δτ / k_eff ,     k_eff = K_sys · cos²θ · sinθ / A
```

`kalantar_gate.py` therefore scores **one force channel (τ) and one flow channel** — `Q`
on OG-SH, `a_h` on OG-T and OG-SC per §2 item 4 — and prints σ'ₙ, the unscored flow
channel and ΔL_s as diagnostics. It also carries its own stage walker: `table2_gate`'s
hard-codes Ye2018's eleven targets and went looking for a 24 MPa loading stage that does
not exist on a Kalantar schedule.

---

## 5. Round 1 — what was built, what came back, and the six defect classes

Built at commit `5123326` on branch `orca_v7`; three jobs submitted to HPC.

| deck | job | outcome |
|---|---|---|
| OG-SH `110_01` | 19443808, 19443844, 19444590 | cancelled by SIGTERM (user), not failures |
| OG-SH `110_01` | **19444645** | **completed** — 4800 steps to t = 3600, 35 250 s wall, 6.5 GB Exodus |
| OG-T `110_03` | 19443842 | **crashed at t = 0.75 s** |
| OG-SC `110_05` | 19444648 | **crashed at t = 0.75 s** |

Both crashes are *after* `Solve Converged!` on step 1. The solver was fine; the
postprocessors killed the run.

The completed run, scored at the nine hold plateaus (stage-mean error):

| σ'ₙ | τ | a_h | Q |
|---|---|---|---|
| **−13.2 %** (−17.8…−9.7) | **−19.3 %** (−34.8…−11.3) | **−48.2 %** (−56.1…−42.5) | **−80.7 %** (−88.4…−74.1) |

Every channel biased low and the bias shrinking monotonically along the stage sequence.
That pattern is the signature of a *loading* deficit, not a constitutive one — and so it
proved.

### 5.1 The root cause behind all of it

`build_110_kalantar_decks.py` said *"NOTHING IN THIS DECK IS CALIBRATED. Every constant
is DERIVED."* That was **true of the ~20 constants it substitutes and false of everything
else.** The `[czm_contact]` and `ADOrcaRoughnessDamageFracturePermeability` blocks came
over wholesale from whichever Ye2018 parent matched the fracture type (OG-SH ← SW-T2,
OG-T ← SW-T1, OG-SC ← SW-S3). Six defect classes follow.

### 5.2 (a) `PointValue` outside its own mesh — killed two of three runs

```
ERROR  No element located at (0.02499, 0, 0.1144)      PointValue 'bulk_disp_x_upper_pp'   [OG-T]
ERROR  No element located at (0.0231596, 0, 0.103481)  PointValue 'pp_outlet_pp'           [OG-SC]
```

The bulk gauges sit at `mid ± 50 mm` where `mid` is the **Ye2018 parent's** half-height:

| | gauge centre | true core mid | upper point | mesh top | |
|---|---|---|---|---|---|
| OG-SH ← SW-T2 | 66.35 mm | 60.0 | 0.11635 | 0.120 | inside — survived by luck |
| OG-T ← SW-T1 | 64.40 mm | 50.0 | 0.11440 | 0.100 | **14.4 mm outside** |
| OG-SC ← SW-S3 | 61.70 mm | 50.0 | 0.11170 | 0.100 | **11.7 mm outside** |

### 5.3 (b) OG-SC's borehole readouts were at SW-S3's coordinates

`injection_pressure_pp` and `pp_outlet_pp` were `PointValue`s at SW-S3's borehole
coordinates, not matching OG-SC's own `source_in`/`source_out` 1150 lines above — despite
the deck comment saying *"must track the source_in coord above"*. `pp_outlet_pp` was
outside the mesh; `pp_inlet_pp` was inside but 0.862 mm off-node out near the cylinder
surface. Had it not crashed, OG-SC's injection-pressure channel would have been noise —
and `effective_normal_paper_frame_mpa_pp` consumes it.

**The source nodes themselves are exactly on-node in all three meshes.** The
source-pinning rule held. This whole class is reporting-only.

### 5.4 (c) The entire paper-frame reporting chain was Ye2018's — the worst one

Invisible in the physics, and it would have corrupted every future score:

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
σ₁−σ₃ at the fault was 35.56 — an 11 % inflation — and both paper-frame channels inherited
it. τ and σ'ₙ together implied `tan θ_eff = 0.4013`, i.e. **21.9° instead of 29°**.
**A physically perfect run would still have scored wrong.**

Third occurrence of this family, after the SW-S4 stale-PointValue trap and the
skeleton-vs-total stress frame mismatch.

### 5.5 (d) The loading was never gated

Line 253 of the round-1 deck said so: `axial_pres_final = -2.332804e-04 # FIRST ESTIMATE
… MUST BE GATED`. It delivered σ₁ = **69.36 MPa** against the **94.65 MPa** Table 2 stage
1 requires — differential 31.3 vs 61.65 MPa, short by a factor 1.7.

The estimate was `−σ₁/penalty`, which ignores that the penalty BC is a **series spring**:

```
σ₁ = penalty·(u_cmd − u_sample)   ⇒   u_cmd = σ₁/penalty + C_ax·(σ₁ − σ₃)
```

`C_ax` calibrated once on the completed OG-SH run: commanded 2.3328e-4 m, realised
σ₁ = 69.3554 MPa, machine-spring gap 1.71048e-4 m ⇒ u_sample = 6.2232e-5 m over a
36.36 MPa deviator ⇒ **C_ax = 1.71177e-12 m/Pa = 0.8987·L/E**. The shortfall from 1.0 is
the joint's own normal compliance plus the non-uniform `stress_zz` near the platens. It
reproduces the realised σ₁ to 0.02 %.

### 5.6 (e) The aperture law was SW-T2's

`initial_hydraulic_aperture` = 2.11 µm against Table 2's stage-1 4.87, anchored at
`reference_effective_normal_stress` = 66.74 MPa (Ye2018's), with `min_hydraulic_aperture`
= 2.0045 µm — **a hard floor the model sat 7 % above for the entire run.** a_h moved only
2.139 → 2.181 µm across the whole 6→18→6 MPa cycle.

Since Q ∝ a_h³, (2.14/4.87)³ = 8.5 % accounts for essentially the whole Q deficit.
**Q was not an independent failure.** Also `slip_damage_scale = 0` on OG-SH — the only
mechanism that could produce loss, switched off, on the specimen whose headline result
*is* monotonic loss.

*Not* a defect: `dilation_scale = 0` with `aperture_scale ≈ 0.016` is dilation routed
through the mechanical aperture — the documented flag pairing. Do not set both.

### 5.7 (f) The traction law: three separate errors

* **OG-SH's envelope was 13.2 % too strong.** The builder used the Figure 3b criterion;
  §2.3 says that criterion overestimates and the test actually ran at ~0.92 τ_p, not 0.85.
  Backing τ_p out of the stated ratios and walking up the loading path (slope cot θ) gives
  φ_peak **32.70°** not 36.05 and φ_r **24.10°** not 27.451. The same check confirms OG-T
  (−1.4 %) and OG-SC (−3.3 %) need no override — OG-SH is the outlier, as the paper warned.
* **`slip_weakening_residual_friction_angle_degrees` unsubstituted in all three**, left at
  the parent's 29.756°, which on OG-SH exceeded φ_r 27.451 — **the law strengthened with
  slip.**
* **OG-SC could not have burst.** Its `D_c` cap is 25.4 µm and the deck carried 60 µm — on
  the specimen whose entire result is one audible slip.

And **the dilation angle was a Ye2018 fit**: 13.97 / 16.44 / **26.0°** — a 26° dilation
angle on a saw-cut with JRC 4.23.

### 5.8 Why the fracture never slipped

τ sat flat at 17.0 MPa across all nine stages while the paper's falls 26.14 → 18.97 and
stays down. That permanent drop *is* the slip (ΔL_s 0.002 → 0.042 mm, unrecovered).
τ/τ_limit only ever reached 0.67. Three compounding causes, all above: the loading was
49 % short (5.5), the envelope 13.2 % too strong (5.7), and the weakening law ran the
wrong direction (5.7).

---

## 6. Round 2 — what changed

### 6.1 Loading

| | σ₁ target | round 1 | round 2 |
|---|---|---|---|
| OG-SH | 94.65 MPa | −2.332804e-04 | **−3.388091e-04** |
| OG-T | 193.43 MPa | −4.780340e-04 | **−7.056216e-04** |
| OG-SC | 63.39 MPa | −1.562470e-04 | **−1.995975e-04** |

Still worth a 200 s preload check per specimen — the relation stops being linear once the
joint slips — but it is no longer a factor-1.7 guess.

### 6.2 Traction law

| | round 1 | round 2 | source |
|---|---|---|---|
| φ_peak (SH/T/SC) | 36.05 / 47.73 / 21.80 | **32.70** / 47.73 / 21.80 | §2.3's 0.92 τ_p correction, OG-SH only |
| φ_r | 27.451 / 43.135 / 19.148 | **24.099** / 43.135 / 19.148 | same |
| slip-weakening residual | 29.756 (all three) | **25.930 / 27.414 / 15.354** | `atan(τ_last/σ'ₙ_last)`, Table 2 last stage |
| dilation angle | 13.97 / 16.44 / 26.0 | **4.300 / 2.296 / 1.327** | Barton peak dilation `½·JRC·log₁₀(JCS/σ'ₙ)` |
| `D_c` | 150 / 150 / 60 µm | 150 / 150 / **15.2 µm** | stability class, §4 |

The residual is checked against **φ_peak**, not φ_r, because the material weakens the
*mobilised* BB peak toward this value —
`ADOrcaBartonBandis…Hardening.C` line 109: `mu_p = friction_coefficient` is the BB peak
from the base class.

### 6.3 Aperture law

| | round 1 | round 2 | source |
|---|---|---|---|
| `initial_hydraulic_aperture` | 2.11 / 1.63 / 1.22 µm | **4.87 / 0.10 / 1.03 µm** | Table 2 stage 1 |
| `reference_effective_normal_stress` | 66.74 MPa (all) | **42.99 / 63.86 / 36.10 MPa** | Table 2 stage 1 σ'ₙ |
| `slip_damage_scale` | 0 / 0 / — | **1.15 / 0 / 0.45 µm** | Table 2's irreversible a_h loss |

Anchoring `(a_h0, σ'ₙ_ref)` on the same Table 2 stage makes the stress–aperture term vanish
exactly there; the bounds are bracketed around Table 2's own observed range rather than
Ye2018's.

### 6.4 The two assertions that would have caught round 1

Both run on every build of `scripts/build_110_kalantar_decks.py`:

1. `check_points_in_mesh()` reads the deck's own `mesh_file` and asserts every `PointValue`
   is inside its bounding box.
2. The realised stability class `D_c < Δτ/k_eff` is asserted against what the paper
   observed:

   | | D_c | cap | class | paper |
   |---|---|---|---|---|
   | OG-SH | 150.0 µm | 47.7 | stable | creeps through every hold ✓ |
   | OG-T | 150.0 µm | 310.4 | unstable | progressive, 275 µm ✓ |
   | OG-SC | **15.2 µm** | 25.4 | unstable | one burst ✓ |

Plus `φ_residual < φ_peak` on all three (the weakening direction), and the schedule stage
counts asserted against Table 2's (5/4, 9/8, 7/6). `main()` returns 1 on any problem.

Builder output as of `353faf3` — φ_peak, φ_r, slip-weakening residual, dilation, σ₁ target,
D_c/cap, a_h0, end_time, (load/unload stages):

```
OG-SH   32.70d 24.099d  25.930d  4.30d   94.65M  150.0/47.7     4.87u    3600   (5, 4)
OG-T    47.73d 43.135d  27.414d  2.30d  193.43M  150.0/310.4    0.10u    6800   (9, 8)
OG-SC   21.80d 19.148d  15.354d  1.33d   63.39M   15.2/25.4     1.03u    9100   (7, 6)
Every PointValue is inside its own mesh.
```

### 6.5 Resourcing

64 ranks / 64 GB throughout. Wall time **2 d** on OG-SH, **3 d** on OG-T and OG-SC (2.5×
OG-SH's schedule). Exodus `time_step_interval` scaled per deck — 10 / 18 / 24 — so each
writes ~500 frames; without it OG-SC would have produced ~16 GB.

### 6.6 The baseline to beat

Round-1 OG-SH through `kalantar_gate.py` (nRMSE %, `*` = scored):

```
*tau_MPa      9  0   70.95   ...  shear_stress_paper_frame_mpa_pp
*Q_ml_min     9  0   53.43   ...  flow_rate_validation_ml_min_pp
 sigma_n_MPa  9  0   54.23
 ah_um        9  0  179.79
 ds_mm        9  0   79.28
 MEAN (* only)        62.19
```

### 6.7 Round-2 results — what actually happened

Downloaded 2026-08-24 10:52. Logs were not synced, only the CSVs.

| specimen | t reached | of | complete | scored mean nRMSE |
|---|---:|---:|---:|---|
| **OG-SH** | 3600.0 | 3600 | **100 %** | **67** (τ 68, Q 66) |
| OG-T | 2449.7 | 6800 | 36 % | *(54 — invalid, see below)* |
| OG-SC | 7003.0 | 9100 | 77 % | *(85 — invalid)* |

**Only OG-SH is scoreable.** `kalantar_gate.py` happily returned numbers for the other two
— it matched 17 and 13 hold stages inside runs that never reached them, because unlike the
notebook it has **no completeness guard**. Those two scores are ghost matches on partial
data and mean nothing. That is a gate defect, not a result. (Round-3 item.)

#### The two headline fixes both worked

| check | round 1 | round 2 |
|---|---|---|
| frame: `θ_eff = atan[(σ'ₙ−σ₃+P_p)/τ]` | 21.9° | **29.00° at every one of the nine stages** |
| loading: stage-1 τ | — | **25.98 vs 26.14 measured, −0.6 %** |
| loading: stage-1 σ'ₙ | — | **42.90 vs 42.99 measured, −0.2 %** |

The series-spring gate (§5.5) is confirmed. σ₁ lands where Table 2 says it should.

#### And the run still fails — the fracture does not slip

| stage | P_i | τ meas | τ **model** | σ'ₙ meas | σ'ₙ model | a_h meas | a_h model | slip meas | slip model |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 6 | 26.14 | **25.98** | 42.99 | 42.90 | 4.87 | 4.871 | 0.0023 | 0.0026 |
| 2 | 9 | 24.99 | 25.84 | 40.85 | 41.32 | 4.56 | 4.873 | 0.0103 | 0.0026 |
| 3 | 12 | 23.38 | 25.77 | 38.46 | 39.79 | 4.31 | 4.877 | 0.0206 | 0.0026 |
| 4 | 15 | 21.43 | 25.68 | 35.88 | 38.23 | 4.27 | 4.853 | 0.0332 | 0.0029 |
| 5 | 18 | 19.57 | 25.48 | 33.35 | 36.63 | 4.33 | 4.736 | 0.0446 | 0.0049 |
| 6 | 15 | 19.18 | 25.43 | 34.63 | 38.10 | 3.98 | 4.731 | 0.0469 | 0.0049 |
| 7 | 12 | 19.11 | 25.37 | 36.09 | 39.56 | 3.88 | 4.727 | 0.0480 | 0.0049 |
| 8 | 9 | 19.03 | 25.30 | 37.55 | 41.03 | 3.78 | 4.724 | 0.0480 | 0.0049 |
| 9 | 6 | 18.97 | 25.23 | 39.02 | 42.48 | 3.72 | 4.721 | 0.0480 | 0.0049 |

(τ, σ'ₙ in MPa; a_h in µm; slip in mm.)

* Measured τ falls **7.17 MPa**; the model's falls **0.75 MPa**.
* Measured slip reaches **0.0480 mm**; the model reaches **0.0049 mm — 10× too little**.
* Measured a_h loses **1.15 µm**; the model loses **0.15 µm** — which follows directly,
  because `slip_damage_scale` is driven by slip and there is no slip.

**The invariant across both rounds is that τ does not evolve.** Round 1 was flat at
17.0 MPa (too low); round 2 is flat at ~25.5 MPa (too high). Round 2's mean nRMSE is
*worse* than round 1's 62.19 purely because a flat curve at the top of the measured range
scores worse than a flat curve at the bottom. **The score got worse and the model got
better** — the reproducibility floor and the score both being blind to that is exactly why
the per-stage table above, not the scalar, is the diagnosis.

#### Why it does not slip — and it is a near miss

| stage | τ/τ_limit | JRC mobilised |
|---:|---:|---:|
| 1 | 0.9122 | 15.600 |
| 4 | 0.9770 | 15.600 |
| **5** | **0.9900** | 15.600 |
| 9 | 0.8868 | 15.600 |

`bb_jrc_mobilized_pp` is **pinned at the full 15.600 for the entire run.** The roughness
never degrades, so the envelope never weakens, so τ never falls. And the reason it never
degrades is that the joint never reaches its limit: τ/τ_limit peaks at **0.9900** at
stage 5 and then unloads. **It misses by one percent.**

Two candidate causes, and they are separable:

1. **The envelope is still too strong.** At stage 1 the model's τ_limit is **28.48 MPa**
   at σ'ₙ = 42.33. But the specimen is *already creeping* at stage 1, so the measurement
   says its limit is **26.14 MPa** at σ'ₙ = 42.99. **The envelope is 9.0 % too strong even
   after the 0.92 τ_p correction.** Pinning τ_limit through the stage-1 measurement wants
   φ_peak ≈ **31.3°**, about 1.4° below the deck's 32.70.
2. **`roughness_characteristic_slip` is still Ye2018's** (§7). It sets the slip scale over
   which JRC mobilises; against the ~5 µm the model actually achieves it may simply be too
   long for any degradation to register. This is inseparable from (1) until (1) is fixed,
   because with no slip there is nothing for it to act on.

Fix (1) first — it is a derived quantity with a measurement behind it, whereas (2) is a
free knob. *Do not tune (2) to compensate for (1).*

### 6.8 Defect class (g), found while scoring: a seventh inherited constant

```
OG-SH  paper_flow_width_over_length = 0.813242611781   mesh_… = 0.813242611781
OG-T   paper_flow_width_over_length = 0.814323680496   mesh_… = 0.814323680496
OG-SC  paper_flow_width_over_length_og_sc = 0.625063   mesh_…_og_sc = 0.619048   ✓
```

The first two are **byte-identical to the Ye2018 93-series values.** The plan §3.1 derived
per-specimen numbers — 0.60607 / 0.58690 / 0.62506 paper-frame, 0.60602 / 0.57616 /
0.61905 mesh-frame — and only OG-SC got them, because SW-S3's parent happens to use the
suffixed key name `…_og_sc` that the builder matched. **OG-SH and OG-T kept the parent's.**
The `paper_` and `mesh_` values being *identical to each other* within a deck is the
second tell; they should differ in the third decimal.

Measured consequence: OG-SH's model Q obeys `Q/(a_h³·ΔP) = 4.066e-3` exactly constant
across all nine stages, against Table 2's `2.961e-3` — **a constant inflation of 1.342×,
which is precisely 0.813242611781 / 0.60607.** So a large part of OG-SH's Q error is this
one number and not physics. OG-T's factor is 1.387×.

It does **not** touch a_h, which the material computes, so OG-T's and OG-SC's scored flow
channels are unaffected — but OG-SH's scored flow channel is Q, so OG-SH's `Q 66` is
substantially an artefact.

Same lesson as round 1, one round later on a different key set: *a build script's "derived"
claim covers only the keys it actually matched.* The builder must print its inherited set,
or diff child against parent, before any deck is called calibrated.

---

### 6.9 OG-T and OG-SC, unhidden — three specimens, three different failures

*(2026-08-24, later the same day. §6.7 above was written from OG-SH alone, because the
notebook's completeness guard hid the other two. It now shows them without scoring them —
§6.11. They change the round-3 plan, and §6.7's conclusion turns out to be **OG-SH's alone**,
not the batch's.)*

| | loading frame | slip onset | weakening |
|---|---|---|---|
| **OG-SH** | ✅ stage 1 exact | never slips, τ/τ_lim peaks **0.9900** | absent |
| **OG-T** | ❌ broken before injection begins | slips at **t ≈ 31 s, during preload** | runs away to residual |
| **OG-SC** | ✅ stages 1–3 exact | bursts at **stage 4**; measured burst is **stage 7** | sheds 9.1 MPa; measured 3.4 |

**OG-SC is the best result of the campaign, and it yields a two-sided bracket.** Its first
three stages match on every channel — τ within 0.13/0.32/0.79 %, σ'ₙ within 0.03/0.07/0.18 %,
a_h within 0.2/12/17 %. Then τ/τ_lim crosses 1.0 at stage 4 (1.0160) and it bursts three
stages early, at P_i = 15 MPa instead of 24. Table 2 requires it to **hold** at stage 6
(σ'ₙ 28.48, τ 12.95; measured slip still 0.001 mm) and to **fail** by stage 7 (σ'ₙ 25.12,
τ 13.0 → 9.73; slip 0.001 → 0.023 mm). At the deck's own JRC 4.23 / JCS 153 MPa the two
conditions give

```
hold  at stage 6:  tan(phi_r + 4.23*log10(153/28.48)) > 12.95/28.48  ->  phi_r > 21.36 deg
fail  by stage 7:  tan(phi_r + 4.23*log10(153/25.12)) < 13.0 /25.12  ->  phi_r < 24.05 deg
```

> **21.36° < φ_r(OG-SC) < 24.05°.** The deck runs **19.148°** — 2.2° below the bracket.

Both ends are measurements; neither is a fit. This is the closure test of
`bracket-closure-test-table2` and it closes. **The sign matters: OG-SC's envelope is too
WEAK while OG-SH's (§6.7) is too STRONG.** Any single global envelope correction would have
been wrong, and would have been read as a partial success.

**OG-T never gets loaded, so none of its constants can be judged.** During the preload ramp —
before injection, with `pp_outlet_pp` pinned at 3 MPa and `injection_pressure_pp` ramping
identically on all three decks — the fracture's own normal traction **falls** while the
reported paper-frame σ'ₙ **rises**:

| t [s] | `bb_effective_normal_stress_pp` | `effective_normal_paper_frame_mpa_pp` | ratio |
|---|---|---|---|
| 3.75 | 30.34 | 31.19 | 0.97 |
| 15.00 | 27.53 | 38.55 | 0.71 |
| 26.25 | 24.76 | 45.92 | **0.54** |

OG-SH and OG-SC show **no such divergence** over the same ramp — both track to ~1 %, and on
OG-SH the ratio stays within 0.987–1.011 at *every one* of the nine hold stages. So this is
neither the paper-frame reporting chain (which §6.7 verified) nor a poroelastic effect
(identical pore boundary conditions on all three). It is specific to OG-T.

Consequence: τ reaches the peak envelope at **t ≈ 31 s**, the joint sheds **0.53 mm** in
about 25 s, `bb_jrc_mobilized_pp` degrades 12.10 → 12.10 (already at cap) while the envelope
falls to the slip-weakened residual, and all 6800 s that follow are a joint lying on that
residual at τ/τ_lim ≈ 1.03–1.05. Its stage-1 τ is 16.48 MPa against a measured 66.50.

**Do not touch OG-T's φ_r, JRC or cohesion until this is found.** Two candidates, in order:

1. **The axial gate.** `axial_pres_final = −7.056e−4` on a 100 mm core is **0.71 % axial
   strain, 2.5–3.5× the other two decks** (OG-SH −3.388e−4 / 120 mm = 0.28 %; OG-SC
   −1.996e−4 / 100 mm = 0.20 %), because OG-T's σ₁ target is 193.43 MPa against 94.65 and
   63.39. The divergence scales with σ₁ across the three decks, which fits.
2. **The θ = 28° geometry.** Two OG-T meshes are on disk (`_theta26_size3.e`,
   `_theta28_size3.e`); the deck loads `theta28` and sets `bulk_sin_theta = sin 28°`, which
   is self-consistent — but the paper's own Table 2 implies 25.999°, and this is the one
   specimen whose printed and geometric angles disagree.

For the record, OG-T's envelope is *not* obviously the problem: pinning it through Table 2's
stage 1 (σ'ₙ 63.86, τ 66.50) needs φ_r > 41.57° and the deck carries 43.135°. Stage 6 needs
φ_r > 44.31°, so it is ~1.2° short there — a second-order correction, invisible under a
defect that costs 0.53 mm before injection starts.

### 6.10 Why both runs stopped, and why the answer is the time stepper, not the mesh

Both truncations are wall-clock, not solver failures. OG-SC ran at a clean `dt = 0.75` for
99.9 % of its steps and stopped mid-stride at t = 7003.03 — no cutback, so no divergence.
OG-T's dt trace shows cutbacks confined to one window (below).

**Every deck carries `dtmax = 0.75`**, so with `end_time` 3600 / 6800 / 9100 the step count
is fixed at **4800 / 9067 / 12133** before the solver is ever consulted. From OG-SH's own
log (`Finished Executing 35249.66 s` = **9.79 h**, 4800 steps, 64 ranks, 101 972 elements,
427 032 nonlinear DOFs, LU/MUMPS):

* **1206 steps actually solve**, ~24.3 s each → **83 % of the wall time**. These are the
  nine 100 s pressure ramps.
* **3594 steps converge at nonlinear iteration 0** (`|R| = 4.3e−9`), ~1.65 s each. These are
  the nine 300 s holds.

The holds are measurably dead. Across every OG-SH hold, start → end:

| hold | Δa_h | ΔQ | Δslip |
|---|---|---|---|
| 100→400 | 0.000 % | 0.25 % | −0.01 % |
| 900→1200 | **0.000 %** | **0.000 %** | **0.000 %** |
| 1700→2000 | −0.091 % | −0.32 % | 1.74 % |
| 3300→3600 | **0.000 %** | **0.000 %** | **0.000 %** |

Three of the nine move *nothing*, to seven digits. Holds are **75 % of OG-SH's schedule and
86 % of OG-SC's**. OG-T is different: **3351 of its 6194 steps (54 %) went into the single
stick-slip event at t = 1300–1700 s**, at dt down to 0.0166 s, and dt returns cleanly to
0.75 afterwards. That cost is real physics and must be preserved.

Projected at 64 ranks with the mesh unchanged, using the measured 24.3 s / 1.65 s per step:

| | now | ramp dt 1.5 / hold dt 5 | ramp dt 2.5 / hold dt 10 |
|---|---|---|---|
| OG-SH | 9.75 h | 4.30 h (2.3×) | 2.55 h (3.8×) |
| OG-SC | 16.45 h | 6.56 h (2.5×) | 3.87 h (4.3×) |

**Why not coarsen the mesh.** Three reasons, in order of weight:

1. It is not where the time goes that can be safely recovered. The recoverable time is in
   step count, and step count is set by `dtmax`, not by the mesh.
2. OG-SH's factor-4 mesh **fails the source-pinning test**: both injection points snap to
   **bulk** nodes 950.7 / 933.5 µm off the fracture
   (`OGSH/mesh/kalantar2025_og_sh_theta29.jou` lines 55–81). Forcing them onto the nearest
   interface nodes instead moves them 0.59 / 1.06 mm from the design boreholes and lengthens
   the source-to-source path from 82.474 to 84.899 mm — **+2.94 %** — on the one channel that
   already carries the 1.342× bug of §6.8.
3. Changing discretisation in the same round as the physics fixes makes the round
   unattributable. We are chasing a 9 % envelope error and a 2.2° friction angle; a mesh
   change of comparable size destroys the inference.

Coarsen later, deliberately, as a convergence check — the standing purpose of the size-5
twins — never as a speed hack mid-calibration.

### 6.11 The notebook now shows truncated runs without scoring them

`Kalantar2025_table2_validation.ipynb` kept two dicts as of 2026-08-24:

* **`LOADED`** — runs that reached `end_time` (`MIN_COMPLETE_PCT = 99.9`). Drives **§6, the
  scorecard**, and nothing else.
* **`SHOWN`** — every run that produced a CSV. Drives **§7 stage tables, §8 channel figures,
  §9 stress path, §10 aperture**, each labelled with its completion percentage.

`stage_table` clips the stage list to `t ≤ t_end` and reports how many stages were never
reached; the channel figures grey out the unreached span on every panel. Before this,
`stage_table` re-read the run's final row once per unreached stage, so a truncated run
produced a full-length table that looked merely *wrong* rather than *absent* — the same
mechanism that produced `kalantar_gate.py`'s phantom scores of 54 and 85 (§6.8). The gate
still lacks the guard.

**The lesson is worth more than the fix.** Hiding the two incomplete runs cost a day: OG-SC's
two-sided friction bracket and OG-T's preload defect were both sitting in CSVs that had been
on disk since 10:52, behind a boolean. *A run that is unscoreable is not uninformative.*
Guard the **score**, never the **plot**.

### 6.12 Source pinning is one integer, and the boreholes can be imprinted

The pinning distance had been treated as an empirical property of each mesh — measured after
every rebuild with `check_source_nodes.py`, never explained, and the only known remedy was to
try another global size and re-measure. **It is closed-form.**

Both boreholes sit at `y = 0` on the fracture plane. That is not the interior of a surface:
it is exactly where `webcut … yplane` (§3) cut the fracture ellipse — the ellipse's **major
axis** — and it is a *geometric curve*. Cubit divides that curve into `N` **equal** intervals
(verified: min spacing == max spacing to machine precision on all six meshes), so the only
node positions the source can reach are `k/N` along it. The design borehole sits at
`x/r = (24.99 − 5)/24.99 = 0.799920`, so the error is `round(0.79992·N)/N − 0.79992`:

| mesh | N | nearest fraction | predicted | `check_source_nodes.py` |
|---|---|---|---|---|
| `_size3` OG-SH | **25** | 20/25 = 0.800000 | 4.1 µm | 4.1 µm |
| `_size3` OG-T | 27 | 22/27 = 0.814815 | 792.9 µm | 792.9 µm |
| `_size3` OG-SC | 26 | 21/26 = 0.807692 | 388.5 µm | 388.5 µm |
| graded OG-SH | 28 | 22/28 = 0.785714 | 732.2 µm | 732.2 µm |
| graded OG-T | 29 | 23/29 = 0.793103 | 362.8 µm | 362.8 µm |
| graded OG-SC | 27 | 22/27 = 0.814815 | 744.4 µm | 744.4 µm |

Six for six, to 0.1 µm. **OG-SH's 4.1 µm pin — quoted throughout §3 as the reason it is the
production mesh — was never quality. It is 25 being divisible by 5**, because the design
borehole sits two microns off exactly 4/5 of the radius. The graded experiment's two
"PASSES → FAILS" verdicts and OG-T's lone "pins better" are the same arithmetic, so **the
OG-T exception recorded in §6.10 is not evidence that its graded sizing was good.**

**Fix A, active in all three journals.** `split curve <id> location position <borehole>`
after the webcuts, before `imprint all`. A vertex forces a node, so the error goes to **0**
and stays there at any mesh size. It adds one vertex and replaces one curve with two — no new
surfaces, no new volumes, so the hardcoded block/nodeset surface IDs and the nodeset 5/6
vertex IDs survive. **A webcut would renumber all of them; do not use one.**

**Fix B, commented fallback.** `curve <ids> interval 25`, forcing `N ≡ 0 (mod 5)`: a node at
exactly `0.8 r = 0.019992`, 4.0–4.3 µm from design, at any coarseness, no topology change.

**Why it is worth doing at all** — it is not speed. It (i) removes a **scored-channel** bias,
since the re-pinned separations are +0.010 % / **+1.862 %** / **+0.972 %** off design and
OG-T's design separation *is* the paper's 85.1596 mm; and (ii) it decouples pinning from mesh
size, which is the only reason factor 4 was disqualified (§3). Coarser meshes become testable
rather than automatically wrong.

**Status: unrun — there is no Cubit on the workstation.** `split curve` on already-merged
geometry and the element quality around the new vertex are both untested. The journals
therefore export to a **new** `…_size3_pin.e`; `_size3.e` is untouched because 110_02 and
110_06 are running on it. New tooling: `scripts/check_axis_intervals.py` (infers L, r, θ and
the fracture plane from the mesh itself, reports `N` and names the fix) and
`Examples/Kalantar2025/mesh_probe_axis_curves.jou` (probe only, prints the curve IDs).
Sequence in `TODO.md` §1.7.

---

## 7. What is still inherited — the round-3 scope

Not derived, still Ye2018 fits:

`initial_normal_stiffness`, `maximum_closure`, `normal_closure_*`,
`normal_unload_retention_fraction`, `aperture_scale`, `tangential_viscosity`,
`roughness_characteristic_slip`, `dilation_decay_distance`.

At Kalantar's stress levels the closure term contributes ~0.03 µm
(σ₀ = V_m·K_ni = 15 MPa against σ'ₙ ≈ 43 MPa with p = 4), so it is nearly inert — **but
"inert" is not "derived".** Refit against the a_h(σ'ₙ) loop once the loading gate passes.

> **2026-08-24, round 3: the precondition is met on OG-SC and the refit is done.** "Nearly
> inert" turned out to be the whole aperture defect, not a footnote: OG-SC's measured `a_h`
> swings 0.570 µm over the pressurization branch and the saturated law can deliver 0.051 µm —
> **11–24× short, stage by stage.** Two-parameter refit on Table 2's own six pre-burst stages,
> `p` held at 4: **V_m 1.20 → 2.651 µm, σ₀ 15.0 → 36.29 MPa**, K_ni essentially unchanged at
> 1.369e13. RMS 25 nm on a 570 nm swing. `K_ni` was never wrong; `V_m` was, and with it the
> placement of σ₀ *below* the operating range instead of inside it. Details:
> `doc/KALANTAR2025_ROUND3_BACKANALYSIS.md` §7.4.

`tangential_viscosity` deserves separate attention: it is not a numerical regulariser, it
is the hidden rate law, worth 0.035–3.5 MPa in τ, and SW-S4 needed 9× the others.

---

## 8. Tooling

| script | what it does |
|---|---|
| `scripts/kalantar_parameter_audit.py` | 7-section audit of Table 1/2 against the prose; runs before any deck |
| `scripts/build_110_kalantar_decks.py` | derives every substituted constant from `validation/kalantar2025_table2.csv` and §2–3; `reduce_stages` re-projects σ₁−σ₃ from the **printed** τ at the **printed** θ; asserts stability class, weakening direction, stage counts, and every `PointValue` against its mesh |
| `scripts/kalantar_gate.py` | scores τ + one flow channel per specimen, prints the rest as diagnostics, own stage walker, frame check alongside |
| `Kalantar2025_table2_validation.ipynb` | 24 cells: Table-2 self-consistency, completeness-gated loading, scorecard, stage tables, channel figures, τ–σ'ₙ path against the deck's own BB envelope, a_h(σ'ₙ) hysteresis, error summary |

**The notebook refuses to *score* a truncated run but does *show* it** (`MIN_COMPLETE_PCT =
99.9`; `LOADED` drives the scorecard, `SHOWN` drives every diagnostic section — see §6.11).
It currently reports `scored (complete only): OG-SH` and `plotted (all with CSV): OG-SH,
OG-T, OG-SC`. It imports `kalantar_gate` rather than reimplementing the stage walk, so the
two cannot drift — except that **the gate still has no completeness guard of its own** and
must not be called directly on a truncated CSV.

Run it with the **base** python (the `moose` env has netCDF4 but no `jupyter_client`; base
has jupyter but no netCDF4 — the notebook needs only the former):

```bash
/home/geomechanics/miniforge/bin/python -m nbconvert --to notebook --execute --inplace Examples/Kalantar2025/Kalantar2025_table2_validation.ipynb
```

---

## 9. The plan

Series **110** for Kalantar BBFast, **111** for the Mohr–Coulomb siblings — nothing
collides with Ye2018's 93–104.

| step | what | state |
|---|---|---|
| **A** | Build 6 meshes in Cubit, 3 specimens × factors 5 and 3 | **done** (§3) |
| **B** | `check_source_nodes.py` on each; snapped coordinates into the journal headers | **done** |
| **C** | Derive the flow geometry factor for eq (7) | **done — and it inverted**: eq (7) as printed is wrong, the Ye2018 cubic form transfers unchanged (§2 item 3) |
| **D** | Port the injection schedule | **done**, generated and asserted against Table 2's stage counts |
| **E** | Build `kalantar_gate.py` | **done**, restructured to two scored channels in round 2 |
| **F** | 110-series BBFast decks, round 2 | **run — OG-SH complete, other two truncated; all three back-analysed (§6.7, §6.9, §6.10)** |
| **F3** | **Round 3 decks BUILT and `Syntax OK`, 2026-08-24** — `110_02` OG-SH, `110_06` OG-SC (both **ready to submit**, 24 h), `110_04` OG-T (**built, not to be submitted**), plus `110_04_og_t_preload_probe.i` (local, 60 s). Changes and their guards in `TODO.md` §1.5 | **built; submit OG-SH + OG-SC** |
| **F3b** | Run the OG-T preload probe locally, close §6.9, then submit OG-T | blocked on the probe |
| **G** | Mechanism decks, chosen after F3 lands — the obvious first is the gouge arm on OG-SH | blocked on F3 |
| **H** | 111-series MC siblings | after F3 lands |
| **I** | Refit the remaining inherited constants (§7) against the a_h(σ'ₙ) loop | blocked on F3 |

### 9.1 Prediction, written before the round-2 runs — and how it scored

> Fixing 5.4–5.7 should move OG-SH's τ from −19.3 % to within a few percent at stage 1 and
> let the joint reach its envelope. The remaining risk is that OG-SH's a_h *loss* is now
> carried entirely by `slip_damage_scale = 1.15 µm` with a 15 µm characteristic slip, and
> that rate is the one number in the aperture law taken from the *shape* of Table 2 rather
> than from a stated constant.
>
> **Falsifier:** if OG-SH's a_h now falls too fast early and flattens, the characteristic
> slip is too short and the *level* was right. If it falls uniformly too little, the
> loading gate has not delivered enough slip and 5.5 is not finished.

**Verdict: half right, and the falsifier fired in a third way that was not preregistered.**

* *"within a few percent at stage 1"* — **correct**: −0.6 %.
* *"let the joint reach its envelope"* — **wrong**: it reached 0.9900 and stopped.
* The falsifier offered two branches, a_h falling *too fast* or *too little*. It fell too
  little — which the preregistration reads as "the loading gate is not finished". **That
  reading is wrong**, and the stage-1 agreement is what proves it: the loading gate *is*
  finished, and a_h fell too little because the *envelope* is 9 % too strong, a cause the
  falsifier did not enumerate.

Recorded as written and marked wrong rather than rewritten. The lesson is the standing one
about mis-specified thresholds: a two-branch falsifier silently asserts the cause is one of
those two. Next time, name the null — *"τ_limit at stage 1 equals the measured τ"* — which
is a direct check on a single number and could not have been misread.

---

## 10. Traps

* **`.jitcache/*.so` downloaded with HPC results crash the local `orca-opt`** — a bare
  `MPI_Abort` inside `vtkMPICommunicator`, no MOOSE message, during setup. They were
  compiled by a different build. `rm -rf */.jitcache` restores `Syntax OK`. `.jitcache/`
  is gitignored; **do not sync it back from HPC.** Cost an hour of bisecting a "deck"
  failure that was not one.
* **CLI overrides of keys absent from the parent also abort with the same bare
  `MPI_Abort`** — which is why the first bisection of the above blamed the wrong keys.
* **Never exceed 24 MPI ranks on the local workstation.** Past that wall time doubles.
* `.gitignore` carries `*.jou`, `*.csv`, `*.e`; the Kalantar result assets are force-added
  past those rules. The 6.2 GB Exodus is correctly left out.
* Reading Exodus needs `/home/geomechanics/miniforge/envs/moose/bin/python` (netCDF4
  1.7.4). The base interpreter cannot.
* `czm_tau_1_pp` (≈ −2.5 kPa) is **not** the shear traction; `czm_tau_2_pp` is.
* **When a ported deck's *reporting* postprocessors contain literal numbers, treat every
  one as a suspected parent constant.** σ₃, sin²θ, sinθcosθ all look like innocent
  coefficients. Diff the child's `expression =` lines against the parent's before trusting
  any score.

---

## 11. Decisions that are Saeed's

1. **OG-T's angle.** 28° is built as primary with 26° as a sensitivity arm; the full
   argument is in the journal headers. Recommendation is 28° with the published stress
   columns re-reduced, because 26° cannot be realised without contradicting a measured
   dimension — and it needs a 4.5 % longer core, which changes the axial compliance of a
   system whose frame stiffness dominates.
2. **Whether the 5 mm borehole inset is to the hole centre or its edge.** ~5 % on the flow
   path length; resolvable from the GFZ data release.
3. **Whether to publish the three checkable defects** — the OG-T angle, the eq-(7) factor
   of 10.3, and the new a_h/k discrepancy. All are genuine and checkable in a 2025 JGR
   paper, found by the same method that found SW-T2's. Reporting them makes the audit
   method itself a contribution: the same class of error caught twice in two independent
   datasets.
4. **OG-SC's core length** from the GFZ release.

---

## 12. Change log

| date | branch / commit | what |
|---|---|---|
| 2026-08-22 | `orca_v7` | Reading notes; Table 2 and Figure 8 digitized; parameter audit; the σ₃ = 33 and OG-T angle defects found |
| 2026-08-23 | `orca_v7` `5123326` | Meshes built and verified; eq (7) shown wrong and the cubic law substituted; round-1 decks + SLURM + gate built; four round-1 defects found by algebra before any run |
| 2026-08-23 | `orca_v8` `353faf3` | Round 2: reporting frame fixed, loading gated, constitutive and aperture constants derived, gate restructured, notebook built, two pre-submission assertions added. 26 files, 77 548 insertions |
| 2026-08-24 | `orca_v8` (results only) | Round-2 batch run and downloaded. Frame and loading gate both confirmed correct; OG-SH complete, other two truncated. New finding: the fracture reaches τ/τ_limit 0.9900 and never weakens — the envelope is 9.0 % too strong. Defect class (g) found: `flow_width_over_length` still Ye2018's on OG-SH and OG-T. Round-2 prediction scored and marked wrong |
| 2026-08-24 (round 3 built) | `orca_v8` | Round-3 decks built: `110_02` OG-SH, `110_04` OG-T, `110_06` OG-SC, plus `110_04_og_t_preload_probe.i`. All four `Syntax OK`. Per-segment `time_t`/`time_dt` (4.2–5.0× fewer steps); OG-SC φ_r 19.148 → 22.660 (inside its measured bracket); OG-SH envelope pinned through stage 1, φ_peak 32.70 → **30.12** (the 31.3 quoted earlier ignored the 1.2 MPa cohesion); `flow_width_over_length` really substituted; OG-T's `event_dt_cap` found to be an **eighth** inherited Ye2018 constant and flattened. Four new build-time assertions. OG-T's envelope untouched by design |
| 2026-08-24 (later) | `orca_v8` | **Notebook rewritten to show truncated runs without scoring them** (`SHOWN` vs `LOADED`, stage tables clipped to `t_end`, unreached span greyed) — §6.11. Unhiding OG-T and OG-SC produced three findings: **§6.9** OG-SC matches stages 1–3 exactly and gives a two-sided measured bracket `21.36° < φ_r < 24.05°` against a deck value of 19.148° (envelope too WEAK — opposite sign to OG-SH's); OG-T's constitutive σ'ₙ **falls** while the reported one rises during the preload, ratio 0.54 by t = 26 s, so it sheds 0.53 mm before injection and none of its constants are judgeable. **§6.10** both truncations are `dtmax = 0.75` forcing 9067/12133 steps, not the mesh: 83 % of OG-SH's wall time is 1206 ramp steps, 3594 hold steps converge at NL iteration 0, and three of nine holds move nothing to 7 digits. Mesh coarsening rejected with reasons. §9 step F3 re-ordered |
| 2026-08-24 (round 3 results) | `orca_v8` | **Round 3 landed: OG-SH 100 %, OG-SC 100 %, OG-T dead at 0.5 %.** OG-SH **62 → 67 → 17** mean nRMSE — round 2's preregistered single-number null (`τ_limit` at stage 1 = measured τ) was acted on and paid off 3.7×; first such payoff in either campaign. **TODO #121 closed**: `bb_jrc_mobilized` is pinned by `use_mobilized_jrc = false` in every deck of both campaigns, and turning it on is *not* the fix because the law ramps roughness **up** with slip; the live weakening channel is `roughness_state` (OG-SH 1.000 → 0.732, OG-SC 0.640 → 0.141) and both manuscripts must name it instead. **OG-SC's φ_r bracket closes on the deck's own 22.660°** (holds stage 6 by +6.1 %, fails stage 7 by −5.8 % on the undegraded envelope) — the Part I "bracket narrows" inference withdrawn; the early burst is premature weakening (9.11 µm of model slip vs Table 2's 1.2). **OG-SC's `slip_weakening_residual` 15.354° was derived from a LOCKED stage** — a lower bound, not a measurement; correct value 21.17° from the one sliding stage. **OG-SH's `characteristic_slip_distance` 150 → 26.5 µm**, and the build assertion that blocked it is 1.36× too strict (linear-drop assumption on an `exp(−(s/D)^1.4)` law) plus charges σ'ₙ's fall to the friction term. **OG-T's preload defect orders with fracture-tip clearance (14.9/6.7/3.0 mm → 1.012/0.830/−0.382) and NOT with Δσ₁** — geometry promoted over the axial gate, and the 26° arm is 1.0 mm clearance, i.e. a falsifier not a rescue. §7's inherited-constant refit done for OG-SC. Round-4 list + 4 preregistered nulls in the back-analysis §10 |
| 2026-08-24 (mesh) | `orca_v8` | Graded meshing **tried, measured, rejected** — the spacing-vs-distance profile is flat at ~0.98 mm out to 100 mm, `scheme polyhedron` yields HEX8 and propagates surface intervals through the whole volume, OG-SH came out **+8.2 % larger**. Then the real mechanism: **§6.12, source pinning is `round(0.79992·N)/N`** for the interval count on the fracture's major-axis curve — all six meshes predicted to 0.1 µm, OG-SH's famous 4.1 µm pin is 25 being divisible by 5. Borehole **vertex imprint** written into all three journals (`split curve … location position`, exporting to a new `_size3_pin.e`), with `curve … interval 25` as the commented fallback; `scripts/check_axis_intervals.py` and `mesh_probe_axis_curves.jou` added. **Unrun — no Cubit on the workstation** |
