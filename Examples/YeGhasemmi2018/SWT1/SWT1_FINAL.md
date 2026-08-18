# SW-T1 — final calibration and paper notes

**Final deck:** `93_01_swt1_final_c26p9_resc9p19_ppfix.i` — constitutively identical to
`91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6.i`, which is the run scored below; see §8.
**Mesh:** `mesh/ye2018_sw_T1_mesh_size_5.e` (convergence check at size 3: `93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3.i`)
**MC baseline:** `94_01_swt1_mc_final.i` / `94_02_swt1_mc_final_mesh3.i`
**Status:** FINAL. The last open bracket (`92_01`/`92_02`) was run and **failed**; see §4.
**Score against Ye & Ghassemi (2018) Table 2:** mean nRMSE **4.44 %** over eleven stages.

---

## 1. The specimen and what has to be reproduced

SW-T1 is one of the two **mated Mode-I tensile** fractures in the Ye & Ghassemi (2018) suite
(*JGR Solid Earth* **123**, 9009–9032). It was split in tension and reassembled, so the two
surfaces still interlock: the asperities on one face are the negatives of those on the other. That
is the single fact that organises everything below. A mated tensile fracture carries far more
cohesion than a saw cut, dilates strongly when it finally breaks, and — the part the model finds
hardest — **recovers most of that dilation when the injection pressure is taken back down.**

The paper's Table 2 gives eleven injection hold stages: six on the loading ramp at
`P_i` = 8, 12, 16, 20, 24, 28 MPa, then five unloading at 24, 20, 16, 12, 8 MPa. Eight quantities
are tabulated per stage but only **five are independent** and only those are scored:

| scored | why |
|---|---|
| `Q` (mL/min) | measured flow rate |
| `σ'ₙ` (MPa) | effective normal stress, from eq (3) |
| `τ` (MPa) | shear stress, from eq (4) |
| `d_n` (mm) | normal displacement |
| `d_s` (mm) | shear displacement |

`a_h` and `k` are **not** independent — the paper back-computes `a_h` from the measured `Q` through
the cubic law and then defines `k = a_h²/12`. They are reported as informational columns by
`scripts/table2_gate.py` and excluded from the score. `σ'ₙ` and `τ` are two projections of one
stress state through eqs (3)/(4); they agree by construction and count as **one** vote, not two.

There is a third dependency, measured on this run rather than assumed — see §5(a).

---

## 2. Calibrated joint parameters

| parameter | value | provenance |
|---|---|---|
| JRC | 15.32 | paper Table 1, measured |
| JCS | 150 MPa | paper §2.1 UCS |
| residual friction angle `φ_r` | 29.756° | granite basic friction, measured on this campaign's own saw cut (SW-S3) |
| peak cohesion `c` | 26.88 MPa | asperity interlock of the mated Mode-I fracture; pins the peak envelope through Table 2's last stick stage |
| **residual cohesion `c_res`** | **9.19 MPa** | interlock surviving the burst; **identified**, see §4 |
| characteristic slip distance `D_c` | 150 µm | |
| slip-weakening exponent `m` | 1.4 | |
| dilation angle | 16.442° | peak \|d_n\|/d_s from Table 2 |
| `normal_unload_retention_fraction` | 0.94 | **exhausted at its bound**, see §4 |
| `normal_unload_activation_slip` | 50 µm | |
| `normal_closure_offset` `c₀` | 44.33 µm | |
| Biot coefficient `α` | 0.6 | |
| Young's modulus `E` | 67 GPa | paper |
| Poisson's ratio `ν` | 0.32 | paper |
| `axial_bc_penalty` | 4.123e11 Pa/m | derived loading-frame stiffness |

---

## 3. Comparison against Table 2

Displacements are referred to the stage-1 datum, as the paper's are.

| stage | branch | P_i | Q meas | Q mod | σ'ₙ meas | σ'ₙ mod | τ meas | τ mod | d_n meas | d_n mod | d_s meas | d_s mod |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | loading | 8 | 0.053 | 0.053 | 65.47 | 65.73 | 67.16 | 67.58 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2 | loading | 12 | 0.114 | 0.123 | 63.35 | 63.76 | 66.96 | 67.64 | 0.000 | -0.000 | 0.000 | 0.000 |
| 3 | loading | 16 | 0.190 | 0.194 | 61.27 | 61.82 | 66.82 | 67.72 | 0.000 | -0.000 | 0.001 | 0.000 |
| 4 | loading | 20 | 0.280 | 0.264 | 59.14 | 59.88 | 66.63 | 67.82 | -0.001 | -0.000 | 0.002 | 0.000 |
| 5 | loading | 24 | 0.389 | 0.335 | 56.94 | 57.87 | 66.32 | 67.80 | -0.003 | -0.001 | 0.008 | 0.002 |
| 6 | loading | 28 | 6.220 | 6.671 | 31.79 | 32.66 | 29.35 | 30.67 | -0.157 | -0.159 | 0.532 | 0.527 |
| 7 | unloading | 24 | 4.270 | 5.029 | 33.45 | 34.33 | 28.72 | 30.13 | -0.139 | -0.151 | 0.539 | 0.527 |
| 8 | unloading | 20 | 2.870 | 3.723 | 35.35 | 36.08 | 28.57 | 29.74 | -0.130 | -0.147 | 0.534 | 0.527 |
| 9 | unloading | 16 | 1.900 | 2.604 | 37.29 | 37.90 | 28.48 | 29.44 | -0.123 | -0.143 | 0.529 | 0.527 |
| 10 | unloading | 12 | 1.120 | 1.599 | 39.22 | 39.75 | 28.36 | 29.21 | -0.118 | -0.141 | 0.525 | 0.527 |
| 11 | unloading | 8 | 0.462 | 0.666 | 41.14 | 41.64 | 28.23 | 29.02 | -0.113 | -0.139 | 0.521 | 0.527 |

### Error summary

nRMSE is the RMS error normalised by the **measured range** of that column, so the five
observables — which span four orders of magnitude in absolute units — can share one table.

Table 2 reports `d_n = d_s = 0.000` at stage 1 for every specimen and the gate zeroes the model
there, so stage 1 is **zero by construction** and is not an independent test of either
displacement. It is excluded from the `d_n`/`d_s` statistics below (n = 10 against n = 11 for the
other three). An earlier revision of this file included it, which diluted both displacement RMSEs
by exactly `sqrt(10/11)` and put the headline at 4.34 %.

| observable | RMSE (abs) | mean abs err | max abs err | n | **nRMSE %** |
|---|---|---|---|---|---|
| `Q` (mL/min) | 0.455 | 0.321 | 0.853 | 11 | **7.38** |
| `σ'ₙ` (MPa) | 0.668 | 0.637 | 0.927 | 11 | **1.98** |
| `τ` (MPa) | 1.063 | 1.016 | 1.481 | 11 | **2.73** |
| `d_n` (mm) | 0.0142 | 0.0103 | 0.0257 | 10 | **9.06** |
| `d_s` (mm) | 0.0055 | 0.0043 | 0.0119 | 10 | **1.02** |
| | | | | **mean** | **4.44** |

The stress state is reproduced to about 2 %, the shear displacement to 1 %, and the whole
pre-burst loading branch (stages 1–5) is essentially exact. The residual is concentrated in the
**unloading branch of `d_n`, and in `Q` as its consequence** — §5.

---

## 4. Why this is final: the bracket was run and it failed

`c_res` was settled first. Applying the bracket-closure interpolation test to the
`91_01`→`91_02` pair (`c_res` 7.21 → 9.19 MPa) — interpolate each observable between the arms and
solve for the value that lands it on the paper —

    tau 8.48   sigma'n 8.47   d_s 9.05   |   d_n 12.5   Q 11.7

The three stress-and-slip observables agree at 8.5–9.1 MPa. `c_res` = 9.19 sits on them, so that
parameter is **identified**. But `d_n` and `Q` wanted 11.7–12.5. A split like this does not mean
"sweep further" — it means one knob is being asked to do two jobs, and the second job belongs to
something else.

The something else was `normal_unload_retention_fraction`. SW-T1 ran 0.94, the highest of the four
specimens (SW-T2 0.84, SW-S3 0.06, SW-S4 0.04) and it had **never been varied**. Decks `92_01`
and `92_02` bracketed it at 0.60 and 0.30.

**The result was unambiguous, and it was the opposite of the prediction.**

| deck | retention | Q | σ'ₙ | τ | d_n | d_s | mean |
|---|---|---|---|---|---|---|---|
| **91_02** | **0.94** | **7.38** | **1.98** | **2.73** | **9.06** | **1.02** | **4.44** |
| 92_01 | 0.60 | 11.45 | 2.64 | 3.65 | 14.55 | 1.02 | 6.66 |
| 92_02 | 0.30 | 11.89 | 2.72 | 3.75 | 15.10 | 1.02 | 6.90 |

Lowering the retention made **every** observable worse except `d_s`, which does not respond at all
(1.02 in all three runs — the retention branch touches only the normal closure, so this is exactly
right, and it means `d_s`'s interpolated estimate is a division by zero and must be discarded).
Reading the sign off the source settles why. In
[`ADOrcaBartonBandisContactTractionFastAD.C:1091`](../../../src/InterfaceMaterial/ADOrcaBartonBandisContactTractionFastAD.C)
the closure fed to the BB normal law is

    closure = raw_closure − retained,        retained = f · recovered_closure

so a **larger** `f` subtracts more, keeps the joint effectively more open on unloading, and yields
**more** apparent recovery. 0.94 was already the best available value, not an unexamined default.

### The knob is exhausted, and by a factor of two

Recovery of `d_n` from stage 6 to stage 11:

| retention `f` | model recovery | measured |
|---|---|---|
| 0.94 | 19.9 µm | 44.0 µm |
| 0.60 | 3.9 µm | 44.0 µm |
| 0.30 | 2.2 µm | 44.0 µm |

Local sensitivity between 0.60 and 0.94 is (19.9 − 3.9)/0.34 ≈ **47 µm per unit `f`**. Closing the
remaining 24 µm therefore needs `f` ≈ 0.94 + 24.1/47 ≈ **1.45**. The parameter is validated as
`>= 0.0 & < 1.0` — it is a fraction of *recovered* closure and cannot physically exceed one. Even
at the open bound, `f` → 1.0 buys about +2.8 µm, reaching ~23 µm of the 44 µm required.

**The required value is about 1.5× outside the parameter's admissible range.** This is not a
sweep that stopped early; it is a knob that cannot reach the target under any setting. No third
arm was built.

### What that leaves

The pre-planned fallback applies exactly as written: if `d_n` does not move toward the measurement,
the retention branch is not the carrier and the gap is in **shear-dilation recovery — model form,
not parameter value**. SW-T1 is final at `91_02`.

Note also that the closure law itself was ruled out earlier and independently: at this joint's
pre-seating (`c₀` = 44.33 µm against `V_m` = 45.91 µm) the BB power-law closure
`σ_n = (K_ni·V_m)·[c/(V_m − c)]^(1/p)` moves only **0.8 µm** across the entire unloading branch. It
cannot carry a 26 µm gap either. Two candidate mechanisms have now been priced and both are an
order of magnitude short.

---

## 5. The error, and how to justify it

**(a) `Q` is not an independent error — it is the aperture, through the cubic law.**
Tested directly rather than assumed. Comparing the model's flow ratio against the cube of its
aperture ratio, stage by stage:

| stage | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `(a_h,mod/a_h,meas)³` | 1.000 | 1.077 | 1.019 | 0.947 | 0.852 | 1.074 | 1.178 | 1.298 | 1.371 | 1.430 | 1.441 |
| `Q_mod/Q_meas` | 0.996 | 1.081 | 1.019 | 0.943 | 0.861 | 1.072 | 1.178 | 1.297 | 1.371 | 1.428 | 1.442 |
| ratio | 0.996 | 1.003 | 1.000 | 0.996 | 1.010 | 0.998 | 1.000 | 0.999 | 1.000 | 0.998 | 1.001 |

Agreement is 1.000 ± 0.01 at every stage. The flow solution is doing exactly what the aperture
tells it to; **the 7.38 % `Q` error and the 8.64 % `d_n` error are one defect counted twice**, not
two independent failures. The paper should say so rather than reporting them as separate
discrepancies. It also means the honest count of independent constraints on this specimen is
three, not five: a stress state, a normal aperture (with `Q` following), and a shear slip.

**(b) The defect is confined to the unloading branch and is one-signed.** Through stage 6 the
model is within 0.002 mm on `d_n`. From stage 7 the model over-predicts closure monotonically:
−12, −17, −20, −23, −26 µm. The measured joint recovers 44 µm of its 157 µm of opening as
pressure is withdrawn; the model recovers 20. A one-signed, monotonically growing error on the
return path is the signature of a **missing reversible mechanism**, not of a mis-set constant —
a mis-set constant would bias the loading branch too.

**(c) The mechanism is mated-fracture shear dilation recovery.** SW-T1's surfaces interlock. As
`σ'ₙ` is restored the asperities ride back down their mating ramps and give back most of the
dilation they created. The model's dilation is driven by an **irreversible** cumulative-slip
variable, so it can be held (via the retention branch) but never genuinely reversed. The
comparison across specimens supports this reading: recovery is worst on the most strongly mated
surface. SW-T2, also mated but less so, recovers 10.6 µm of a measured 12 and scores 2.06 % on
`d_n`; the two saw cuts, which barely dilate at all, are unaffected.

**(d) Scale.** The largest `d_n` error is 25.7 µm on a specimen whose fracture opens 157 µm and
whose surface roughness (JRC 15.32) implies asperity heights of the same order. The error is
comparable to one asperity. In flow terms, `a_h` is 3.36–4.05 µm and the excess is 0.21–0.43 µm —
under half a micron of aperture, amplified into an apparent 44 % flow error purely by the cube.
Reporting the aperture excess alongside the flow excess is the fair way to present this.

**(e) What is right.** The whole pre-burst branch, the burst itself (stage 6: `d_n` −0.159 vs
−0.157, `d_s` 0.527 vs 0.532, `Q` 6.67 vs 6.22), the effective stress path to 2 %, and the total
shear displacement to 1 %. The calibration is not compensating for the unloading defect elsewhere:
`c_res` was identified independently by three observables that agree to ±0.6 MPa.

---

## 6. Mesh convergence

`92_07_swt1_final_c26p9_resc9p19_mesh3.i` repeats the final deck at element size 3. Two things
change and neither is a calibration parameter: the mesh file, and the source coordinates.

**The source coordinates must move with the mesh.** `ExtraNodesetGenerator` with
`use_closest_node = true` never errors, searches the whole mesh, and runs *before* the fault split
— so a coordinate that merely lies near the fracture can snap to a **bulk** node and the run then
injects into the matrix with no warning at all. Source coordinates are mesh-**resolution**
specific, not merely geometry specific. SW-T2 was actually caught by this on its own size-3 mesh.

SW-T1 was **not** trapped: on the size-3 mesh the nearest node to the mesh-5 coordinate is on the
interface, 594.4 µm away. The deck is pinned to that node exactly anyway, so it states the point
it uses:

```
source_in    -0.019260000 0.0 0.033577557  ->  -0.018945000 0.0 0.034081662
source_out    0.019260000 0.0 0.095222443  ->   0.018945000 0.0 0.094718338
```

Verify after any mesh rebuild:

```bash
python3 scripts/check_source_nodes.py Examples/YeGhasemmi2018/SWT1/mesh/ye2018_sw_T1_mesh_size_3.e -0.018945000 0.0 0.034081662 0.018945000 0.0 0.094718338
```

**Acceptance:** Table-2 mean nRMSE within ±0.5 points of 4.44 %, no single observable moving more
than 1.5 points. `flow_rate_validation_ml_min_pp` is the mesh-independent flow channel and is the
one quoted here. `flow_rate_pp` and `flow_rate_mesh_geometry_ml_min_pp` are **not** mesh-independent
by construction (open task #13) and are expected to shift; that is a known property of those two
channels, not a convergence failure.

---

## 7. Reproducing

```bash
cd Examples/YeGhasemmi2018/SWT1 && sbatch 92_07_swt1_final_c26p9_resc9p19_mesh3_hpc_nochk.sh
```

Score any run against Table 2:

```bash
python3 scripts/table2_gate.py --tag hpc --sample SWT1 Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/91_02_swt1_bbfast_c26p9_resc9p19_kernel_SV_biot0p6_hpc.csv
```

Related: [`SWT2_FINAL.md`](../SWT2/SWT2_FINAL.md), [`SWS3_FINAL.md`](../SWS3/SWS3_FINAL.md),
[`SWS4_FINAL.md`](../SWS4/SWS4_FINAL.md), and the reasoning procedure in
[`doc/back_analysis_method.md`](../../../doc/back_analysis_method.md).


---

## 8. The 93/94 series — audit fixes and the Mohr-Coulomb baseline

Everything above was scored on the deck named in the "Final deck" line's parenthetical. A
mesh-and-postprocessor audit of all eight BBFast decks (four specimens x two mesh sizes) then
found the items below. **No constitutive parameter moved.** The corrected decks are the
**93-series**; each has a **94-series** Mohr-Coulomb sibling that differs from it in one block.

### What the audit confirmed

All eight meshes are correct and current: L and D match Table 1, the fracture angle is exact to
four decimals (SW-T1 32.0000, SW-T2 30.0000, SW-S3 29.0000, SW-S4 30.0000 deg), the fracture plane
is centred to 0.0000 mm on every one, and the mesh-3 meshes are about 2.2x finer in edge length and
10x in element count. Critically, **each deck's paper-frame trig constants match its own mesh's
angle**, checked by an SVD plane fit on the `fracture_interface` nodeset — there is no frame/mesh
mismatch anywhere in the BBFast set.

### What the audit fixed

**1. The source coordinate was 1.678 mm off-node — the only such case in the eight.** The mesh-5
deck asked for `+-0.019260000 / z 0.033577557 & 0.095222443`, which is not a
`fracture_interface` node. `ExtraNodesetGenerator` with `use_closest_node = true` never errors, so
it silently snapped to `+-0.018370909 / z 0.035000400 & 0.093799600` and the run used that. The
93-series deck names the node it was always using; **no number changes**, and `91_02` remains a
valid run.

What does not go away is the consequence. The intended injection-production separation is
72.690 mm; the pair actually used is **69.335 mm, 4.62 % short**. The mesh-5 node pitch along the
fracture is 4.333 mm, so the two reachable symmetric separations are 69.335 and 78.002 mm — the
snapped one is the closer, and mesh 5 cannot do better without remeshing. The mesh-3 deck reaches
71.501 mm exactly.

**This is a caveat on the mesh-convergence test (§6), not only on the deck.** The two runs differ
by 3.1 % in source separation, which is not discretisation. `Q` is computed as
`(W/L)/(12*mu) * a_h^3 * Delta p` with `W/L` a fixed constant inverted from Table 2, so the path
length enters through `pp_drop_pp` and a first-order `Q` shift of that size is expected between
the two meshes independently of mesh refinement.

**2. Twenty diagnostic postprocessors added.** SW-S4 carried 87 channels and this deck 70; the
eight `bb_*` envelope channels, the five loading-frame channels and the seven `bulk_*` kinematic
channels existed only there (open task #82). All eight 93-series decks now emit the same 91.
`bulk_sin_theta` / `bulk_cos_theta` are set from this specimen's own 32 deg, and the bulk probes
sit on one rule across all four specimens: cylinder surface, `z = L/2 +- 50 mm`. None of these
feeds the Table-2 gate.

### The 94-series MC baseline

`94_01_swt1_mc_final.i` / `94_02_swt1_mc_final_mesh3.i` are the 93-series decks with **one block replaced**: `[czm_contact]` becomes
`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`. Mesh, source nodesets and
their coordinates, boundary conditions, injection schedule, paper-frame constants, flow constants,
solver, and 84 of the 91 postprocessors are byte-identical to the BBFast sibling. The seven `bb_*`
envelope channels become seven `mc_*` analogues because the Barton-Bandis properties they read do
not exist under the other law.

The MC parameters are a **transfer of this specimen's already-calibrated Barton-Bandis envelope**,
not a fresh fit, so the pair differs in constitutive form rather than in fitted strength:

* `mu_smooth` / `c_smooth` are an **exact** transfer — the BB slip-weakened envelope
  `tau = c_res + sigma'_n*tan(phi_r,sw)` is already a Coulomb line.
* `mu_rough` / `c_rough` **tangent-match** the BB peak envelope at the onset normal stress, then
  are divided by `Rbar_0` so MC's strength at zero slip equals the BB peak on a deck that starts
  at `R_0 < 1`.
* `initial_roughness`, `residual_roughness` and `roughness_decay_distance` are copied verbatim,
  because `roughness_state` drives the aperture material and therefore the scored `Q`.

Agreement between the two envelopes is within 0.09 MPa at every stick stage and the MC strength
margin over the measured `tau` is identical to BB's, so **slip onset is inherited, not refitted**.
Rate-and-state is off: the baseline is a plain Coulomb model.

None of the four pre-existing MC decks was reusable. SW-S3's `83_11` sits on the superseded
124.40 mm mesh at `biot = 1e-12`; SW-S4's `67_11` sits on the buggy 28.9904 deg / 2.85 mm
off-centre mesh and emits no paper-frame stress channel at all; and the SW-T1 and SW-T2 MC decks
**carry each other's fracture angle** in their paper-frame constants (32 deg mesh with 31 deg
constants and vice versa) — about 2.3 MPa on `sigma'_n` at this campaign's differential stress,
roughly 3x SW-T1's entire `sigma'_n` RMSE, which invalidates the cohesions fitted in them.
