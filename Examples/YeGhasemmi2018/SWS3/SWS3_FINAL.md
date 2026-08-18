# SW-S3 — final calibration and paper notes

**Final deck:** `93_05_sw3_final_resc1p40_ppfix.i` — constitutively identical to
`92_03_sw3_final_paperjrc_resc1p40.i`, which is the run scored below, **except that the two
output-only `d_n` reporting knobs are back at their library defaults**; see §9.
**Mesh:** `mesh/sw3_mesh_L123p4_size5.e` (convergence check at size 3: `93_06_sw3_final_resc1p40_ppfix_mesh3.i`)
**MC baseline:** `94_05_sw3_mc_final.i` / `94_06_sw3_mc_final_mesh3.i`
**Status:** FINAL. The `92_03`/`92_04` bracket **succeeded** and closed the parameter; see §4.
**Score against Ye & Ghassemi (2018) Table 2:** mean nRMSE **3.59 %** over eleven stages
(down from 4.95 % at `91_05`). **On the honest `d_n` channel the headline is 4.58 % — read §9
before quoting either number.**

---

## 1. The specimen and what has to be reproduced

SW-S3 is the **rough saw cut** of the Ye & Ghassemi (2018) suite (*JGR Solid Earth* **123**,
9009–9032) — a sawn surface deliberately roughened, so it has real asperities but no interlock,
unlike the mated tensile pair (SW-T1, SW-T2). It sits between them and the polished SW-S4.

Two geometry facts matter and both were re-derived from the paper's own data rather than taken on
trust:

- **Specimen length is 123.40 mm**, not the 124.40 mm carried in every repository's mesh for most
  of this campaign. The corrected mesh (`sw3_mesh_L123p4_size*.e`) is the one used here.
- **Fracture angle θ = 29.000°**, recovered from Table 2 through `tan θ = (σ'ₙ − σ₃ + P_p)/τ`.

The paper's Table 2 gives eleven injection hold stages: six loading at `P_i` = 8, 12, 16, 20, 24,
28 MPa, then five unloading at 24, 20, 16, 12, 8 MPa. Eight quantities are tabulated but only
**five are independent** and only those are scored — `Q`, `σ'ₙ`, `τ`, `d_n`, `d_s`. `a_h` and `k`
are back-computed by the paper from `Q` through the cubic law (`k = a_h²/12`) and carry no
information beyond it. `σ'ₙ` and `τ` are two projections of one stress state via eqs (3)/(4) and
count as one vote. See §5(a) for a third dependency, measured on this run.

**SW-S3's schedule is digitized, not a clean staircase** — its plateaus do not sit exactly on the
target pressures, so `scripts/table2_gate.py` walks the eleven targets behind a monotonic time
cursor rather than detecting plateaus.

---

## 2. Calibrated joint parameters

| parameter | value | provenance |
|---|---|---|
| JRC | 1.96 | **paper Table 1, measured.** The deck previously ran 23.35 — 11.9× the measured value and outside Barton's 0–20 scale |
| JCS | 150 MPa | paper §2.1 UCS (was 300 MPa) |
| residual friction angle `φ_r` | 29.756° | pins the envelope through Table 2's last stick stage (23.42 MPa, 14.26 MPa) at the measured JRC/JCS |
| peak cohesion `c` | 1.67 MPa | level-only correction, `90_05` |
| **residual cohesion `c_res`** | **1.40 MPa** | **the 92-series result**; see §4 |
| slip-weakening residual `φ` | 8.45° | |
| characteristic slip distance `D_c` | 60 µm | |
| slip-weakening exponent `m` | 1.4 | |
| roughness | 0.64 → 0.10 | rough saw cut (SW-S4 runs 0.45) |
| `normal_unload_retention_fraction` | 0.06 | a saw cut recovers almost nothing — contrast SW-T1's 0.94 |
| `normal_closure_offset` `c₀` | 44.33 µm | |
| Biot coefficient `α` | 0.6 | |
| Young's modulus `E` | 67 GPa | paper |
| Poisson's ratio `ν` | 0.32 | paper |
| `axial_bc_penalty` | 1.0e13 Pa/m | measured from the v6/v7 pair; the stiffest of the four specimens — see §5(b) |

---

## 3. Comparison against Table 2

Displacements are referred to the stage-1 datum, as the paper's are.

| stage | branch | P_i | Q meas | Q mod | σ'ₙ meas | σ'ₙ mod | τ meas | τ mod | d_n meas | d_n mod | d_s meas | d_s mod |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | loading | 8 | 0.022 | 0.022 | 31.65 | 31.14 | 14.70 | 13.73 | 0.000 | 0.000 | 0.000 | 0.000 |
| 2 | loading | 12 | 0.050 | 0.054 | 29.58 | 29.22 | 14.57 | 13.94 | 0.000 | -0.000 | 0.000 | 0.000 |
| 3 | loading | 16 | 0.078 | 0.089 | 27.53 | 27.28 | 14.48 | 14.18 | 0.000 | -0.001 | 0.000 | 0.000 |
| 4 | loading | 20 | 0.121 | 0.129 | 25.48 | 25.49 | 14.38 | 14.44 | 0.000 | -0.001 | 0.001 | 0.000 |
| 5 | loading | 24 | 0.150 | 0.190 | 23.42 | 23.66 | 14.26 | 14.72 | 0.000 | -0.002 | 0.001 | 0.001 |
| 6 | loading | 28 | 0.860 | 0.828 | 15.25 | 16.43 | 3.55 | 5.79 | -0.044 | -0.045 | 0.071 | 0.073 |
| 7 | unloading | 24 | 0.460 | 0.518 | 17.27 | 18.03 | 3.19 | 4.51 | -0.044 | -0.043 | 0.072 | 0.073 |
| 8 | unloading | 20 | 0.310 | 0.332 | 19.14 | 19.69 | 2.95 | 3.93 | -0.044 | -0.042 | 0.072 | 0.073 |
| 9 | unloading | 16 | 0.210 | 0.204 | 21.01 | 21.50 | 2.68 | 3.48 | -0.043 | -0.042 | 0.073 | 0.073 |
| 10 | unloading | 12 | 0.130 | 0.118 | 22.86 | 23.27 | 2.44 | 3.15 | -0.042 | -0.041 | 0.073 | 0.073 |
| 11 | unloading | 8 | 0.054 | 0.046 | 24.79 | 25.15 | 2.31 | 2.87 | -0.041 | -0.041 | 0.073 | 0.073 |

### Error summary

nRMSE is the RMS error normalised by the **measured range** of that column.

Table 2 reports `d_n = d_s = 0.000` at stage 1 and the gate zeroes the model there, so stage 1 is
**zero by construction** and is excluded from the two displacement statistics (n = 10 against
n = 11 for the other three). An earlier revision of this file included it, diluting both
displacement RMSEs by `sqrt(10/11)` and putting the headline at 3.55 %.

| observable | RMSE (abs) | mean abs err | max abs err | n | **nRMSE %** |
|---|---|---|---|---|---|
| `Q` (mL/min) | 0.0252 | 0.0183 | 0.0581 | 11 | **3.00** |
| `σ'ₙ` (MPa) | 0.549 | 0.465 | 1.178 | 11 | **3.35** |
| `τ` (MPa) | 0.992 | 0.820 | 2.242 | 11 | **8.01** |
| `d_n` (mm) | 0.00108 | 0.00091 | 0.00208 | 10 | **2.46** |
| `d_s` (mm) | 0.00081 | 0.00057 | 0.00201 | 10 | **1.11** |
| | | | | **mean** | **3.59** |

**The `d_n` row above is not comparable with the other three specimens' — see §9.** It is read
through two output-only reporting knobs that only this deck sets. On the raw kinematic jump the
same run scores `d_n` **7.42 %** and the mean **4.58 %**.

Displacements are inside the ±3 µm acceptance gate at **10 of 10** stages for `d_n` and 9 of 10
for `d_s`. The final unloading state is hit almost exactly: `d_n` −0.0411 against a measured
−0.041, `d_s` 0.0727 against 0.073. The residual is almost entirely in **`τ`** — §5.

---

## 4. Why this is final: the bracket closed

The 91-series left `c_res` open. Applying the bracket-closure interpolation test to
`91_05`→`92_03`→`92_04` (`c_res` 1.65 → 1.40 → 1.20 MPa) — interpolate each observable between two
arms and solve for the value that lands it on the paper — gives, for **all three** pairings:

| pairing | `Q` | `σ'ₙ` | `τ` | `d_n` | `d_s` |
|---|---|---|---|---|---|
| 91_05 → 92_03 | 1.47 | 0.73 | 0.75 | 1.33 | 1.44 |
| 91_05 → 92_04 | 1.47 | 0.72 | 0.73 | 1.32 | 1.44 |
| 92_03 → 92_04 | 1.47 | 0.71 | 0.72 | 1.32 | 1.44 |

Two things follow. First, the three pairings agree to **±0.03 MPa**, so the response is linear in
`c_res` across this range and the estimates are trustworthy rather than an artefact of where the
arms were placed. Second, the estimates **split cleanly into two groups**: the stress state wants
`c_res` ≈ 0.72 MPa, while the aperture and displacements want 1.32–1.47 MPa.

Scores across the bracket:

| deck | `c_res` | Q | σ'ₙ | τ | d_n | d_s | mean |
|---|---|---|---|---|---|---|---|
| 91_05 | 1.65 | 3.10 | 4.24 | 10.11 | 4.65 | 3.01 | 5.02 |
| **92_03** | **1.40** | **3.00** | **3.35** | **8.01** | **2.46** | **1.11** | **3.59** |
| 92_04 | 1.20 | 3.27 | 2.72 | 6.56 | 2.72 | 3.26 | 3.71 |

A quadratic through the three means puts the aggregate optimum at `c_res` = **1.32 MPa**, worth
3.50 % — **0.09 points better than the run we already have.** That is far inside stage-detection
and run-to-run noise, and chasing it would cost an HPC job for nothing. `c_res` = 1.40 MPa also
sits directly on the displacement cluster (1.32/1.44/1.47, mean 1.41). **No further sweep.**

### The split is real, and its cause was measured independently

A split means one knob is doing two jobs, so the question is what the second job belongs to. It
was measured, with a control: the **secant τ–slip stiffness** `Δτ/Δd_s` across the slip event,
model ÷ measured, computed identically for all four specimens:

| specimen | SW-T1 | SW-T2 | SW-S4 | **SW-S3** |
|---|---|---|---|---|
| model / measured | 1.00 | 0.98 | 0.93 | **0.81** |

Three specimens agree with the measurement to within 7 %; SW-S3 alone is **19 % too compliant**.
That is a genuine second defect, and it is the one loading `τ`. The obvious remedy — stiffen the
loading frame — is unavailable: `axial_bc_penalty` is already 1.0e13 Pa/m, effectively rigid and
the stiffest of the four specimens.

So **no value of `c_res` can satisfy both `τ` and the displacements**, and the bracket does not
choose a best value — it chooses which side of the split to sit on. `92_03` sits on the
displacement side, at the value the displacements identify. That is the defensible choice: the
displacements are the primary calibration target, they are the quantities the paper's Figure 7
panels display, and they are measured directly rather than inferred through eqs (3)/(4).

---

## 5. The error, and how to justify it

**(a) `Q` is not an independent error — it is the aperture, through the cubic law.** Tested
directly. Comparing the model's flow ratio against the cube of its aperture ratio:

| stage | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| `(a_h,mod/a_h,meas)³` | 1.004 | 1.061 | 1.142 | 1.057 | 1.264 | 0.935 | 1.137 | 1.073 | 0.979 | 0.916 |
| `Q_mod/Q_meas` | 0.991 | 1.070 | 1.145 | 1.065 | 1.267 | 0.962 | 1.126 | 1.071 | 0.973 | 0.907 |
| ratio | 0.987 | 1.008 | 1.002 | 1.008 | 1.003 | 1.029 | 0.990 | 0.997 | 0.993 | 0.990 |

Agreement is 1.00 ± 0.03 throughout. The flow solution follows the aperture exactly; the 3.00 %
`Q` error is the aperture error restated, not a separate failure of the hydraulic model. The
honest count of independent constraints is three — a stress state, an aperture, and a slip.

**(b) The residual is `τ`, and its cause is measured, not fitted.** `τ` carries 8.01 % against
2.35 % for `d_n` and 1.06 % for `d_s`. Its error is one-signed on the post-slip branch — the model
reads 0.7–2.2 MPa high at every stage from 6 on — which is the signature of a stiffness deficit,
not a strength offset. §4 gives the number: 19 % too compliant in secant τ–slip, against three
sibling specimens that agree with the measurement. Because the frame is already rigid, this is
reported as a **known, quantified, non-tunable residual**, and the paper should quote it that way
rather than as unexplained scatter.

**(c) The largest single error is stage 6, the burst itself** (τ 5.79 vs 3.55 MPa). The measured
specimen drops its shear stress further and faster than the slip-weakening law can. This is the
same class of limitation documented on SW-S4 — a slip-weakening law has no rate or normal-stress-rate
dependence — and it is worth reporting as a transferable limit of Barton–Bandis slip weakening on
staged injection, not as a defect of this calibration.

**(d) Scale.** The `d_n` errors are 0.9 µm mean and 2.1 µm maximum on a joint that opens 44 µm;
`d_s` is 0.6 µm mean on 73 µm of slip. In hydraulic terms `a_h` runs 1.20–2.10 µm and the model
tracks it to a few hundredths of a micron on the unloading branch.

**(e) What is right.** The entire pre-burst branch on all five observables; the burst magnitude on
both displacements (`d_n` −0.045 vs −0.044, `d_s` 0.073 vs 0.071); the whole unloading branch on
displacement, including the final state to 0.2 %; and the effective stress path to 3.35 %. The
calibration is not compensating: `c_res` was placed by three observables that agree to ±0.03 MPa.

---

## 6. A plumbing defect found while scoring this specimen

**Every SW-S3 score in this campaign had been computed on ten stages, not eleven** — silently.

The injection schedule's last knot is at t = 4802.4 s and the deck's `end_time` was 4802. The run
was complete in every physical sense (`P_i` = 7.883 MPa at the last row, well within the gate's
0.35 MPa tolerance of the 8 MPa target), but the final CSV row predated the schedule's last point,
so the gate sampled past the end of the data and dropped the stage. The stage lost was **the end
of unloading — the single stage the unloading-branch argument rests on.**

Two fixes, both applied:

- `scripts/table2_gate.py` now allows a grace window of two output intervals, sampling the run's
  last row and printing a `NOTE` naming the stages where it did so. A genuinely truncated run
  misses by hundreds of seconds and still scores `None`. **This recovered stage 11 from the runs
  already in hand — no re-run was needed**, and all SW-S3 numbers in this document are eleven-stage.
- The mesh-3 deck sets `end_time = 4803`, so the grace window is not needed at all.

The general lesson is in [`doc/back_analysis_method.md`](../../../doc/back_analysis_method.md):
a data-reduction step that drops a stage is indistinguishable from a model that never reached it,
unless the tool says which it was.

---

## 7. Mesh convergence

`92_08_sw3_final_resc1p40_mesh3.i` repeats the final deck at element size 3, changing the mesh
file, the source coordinates, and `end_time` (§6) — no calibration parameter.

**The source coordinates must move with the mesh.** `ExtraNodesetGenerator` with
`use_closest_node = true` never errors, searches the whole mesh, and runs *before* the fault split,
so a coordinate near the fracture can snap to a **bulk** node and inject into the matrix silently.
SW-T2 was caught by exactly this on its own size-3 mesh. SW-S3 is **not** trapped — the nearest
size-3 node is on the interface at 173.7 µm — but the deck is pinned to it exactly:

```
source_in    -0.023159583 0.0 0.019919005  ->  -0.023243800 0.0 0.019767074
source_out    0.023159583 0.0 0.103480995  ->   0.023243800 0.0 0.103632926
```

The two `PointValue` postprocessors that duplicate these coordinates were moved with them. Leaving
one behind is its own silent failure: it keeps reporting, just from the wrong place, and the
resulting "model error" is a plotting artefact.

```bash
python3 scripts/check_source_nodes.py Examples/YeGhasemmi2018/SWS3/mesh/sw3_mesh_L123p4_size3.e -0.023243800 0.0 0.019767074 0.023243800 0.0 0.103632926
```

**Acceptance:** mean nRMSE within ±0.5 points of 3.59 %, no single observable moving more than 1.5
points, and stage 11 landing without the grace window. `τ` is the one to watch: it carries the
whole residual and it is what the 19 % stiffness deficit acts on. **If `τ` improves markedly at
mesh 3, part of what §4 attributes to the loading frame was discretisation compliance instead, and
§5(b) needs rewriting.** `flow_rate_validation_ml_min_pp` is the mesh-independent flow channel and
the one quoted here; `flow_rate_pp` and `flow_rate_mesh_geometry_ml_min_pp` are not mesh-independent
by construction (open task #13) and are expected to shift.

---

## 8. Reproducing

```bash
cd Examples/YeGhasemmi2018/SWS3 && sbatch 92_08_sw3_final_resc1p40_mesh3_hpc_nochk.sh
```

Score any run against Table 2:

```bash
python3 scripts/table2_gate.py --tag hpc --sample SWS3 Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/92_03_sw3_final_paperjrc_resc1p40_hpc.csv
```

Related: [`SWT1_FINAL.md`](../SWT1/SWT1_FINAL.md), [`SWT2_FINAL.md`](../SWT2/SWT2_FINAL.md),
[`SWS4_FINAL.md`](../SWS4/SWS4_FINAL.md), and the reasoning procedure in
[`doc/back_analysis_method.md`](../../../doc/back_analysis_method.md).


---

## 9. The 93/94 series — audit fixes and the Mohr-Coulomb baseline

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

**1. The two output-only `d_n` reporting knobs were removed. This one changes a headline number.**
SW-S3 was the only specimen of the four setting

```
reported_reversible_normal_opening_scale              = 0.758   # library default 1.0
reported_reversible_normal_opening_retention_fraction = 0.552   # library default 0.0
```

The source labels both **OUTPUT ONLY**: they touch neither contact, nor aperture, nor
permeability, nor flow. They reshape only the reconstruction of `normal_opening_total` — which is
precisely the channel the Table-2 gate scores for `d_n`.

| specimen | `d_n` via `normal_opening_total` | `d_n` via the raw kinematic jump | delta |
|---|---|---|---|
| SW-T1 `91_02` | 9.06 | 9.06 | 0.00 |
| SW-T2 `91_04` | 2.06 | 2.06 | 0.00 |
| **SW-S3 `92_03`** | **2.46** | **7.42** | **+4.96** |

SW-T1 and SW-T2 agree exactly *because* their knobs are at defaults, which is how we know the
knobs and not the channel choice are the effect. **SW-S3's headline mean moves 3.59 % -> 4.58 %.**

This is a disclosure and consistency problem, not a physics bug: a two-parameter fit sitting on
the reporting path is invisible in the scorecard and makes one specimen look better than its
mechanics. `93_05` and `93_06` run at the library defaults. Either quote 4.58 % from the 93-series
run, or quote 3.55/3.59 % from `92_03` **with the knobs stated**; do not quote 3.59 % beside the
other three specimens' numbers as though they were computed the same way.

**2. Twenty diagnostic postprocessors added** (task #82), as on SW-T1 and SW-T2, with
`bulk_sin_theta` / `bulk_cos_theta` from this specimen's own 29 deg and the bulk probes at
`z = L/2 +- 50 mm`. None feeds the gate.

**3. Nothing else.** Both SW-S3 source coordinates are exact interface nodes on both meshes, the
mesh is the corrected `L123p4` (123.40 mm), and the paper-frame constants match its 29.0000 deg.

### The 94-series MC baseline

`94_05_sw3_mc_final.i` / `94_06_sw3_mc_final_mesh3.i` are the 93-series decks with **one block replaced**: `[czm_contact]` becomes
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

Agreement between the two envelopes is within 0.03 MPa at every stick stage and the MC strength
margin over the measured `tau` is identical to BB's, so **slip onset is inherited, not refitted**.
Rate-and-state is off: the baseline is a plain Coulomb model.

None of the four pre-existing MC decks was reusable. SW-S3's `83_11` sits on the superseded
124.40 mm mesh at `biot = 1e-12`; SW-S4's `67_11` sits on the buggy 28.9904 deg / 2.85 mm
off-centre mesh and emits no paper-frame stress channel at all; and the SW-T1 and SW-T2 MC decks
**carry each other's fracture angle** in their paper-frame constants (32 deg mesh with 31 deg
constants and vice versa) — about 2.3 MPa on `sigma'_n` at this campaign's differential stress,
roughly 3x SW-T1's entire `sigma'_n` RMSE, which invalidates the cohesions fitted in them.
