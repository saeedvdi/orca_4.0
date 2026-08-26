# SW-T2 — final validation case and paper notes

## SUPERSEDING NOTE (2026-08-26) — the deck of record is now `100_04`

**Deck of record:** `100_04_swt2_apscale0p0177_ppfix.i` — **mean nRMSE 2.132 %**, against the
2.428 % of `93_03` recorded below. Rank 1 of 18 ranked SW-T2 runs.

It differs by **one line**: `aperture_scale` 0.0165 -> 0.0177 (via 99_04's 0.0170). The gain is
entirely in Q, 5.873 -> 4.336; the other four channels are unchanged to three digits, which is
itself the cleanest orthogonality demonstration in the campaign.

**This specimen was never bracketed on the axis that matters.** Its 99/100-series arms moved only
`residual_cohesion` and `aperture_scale`. Its mechanical closure quadruple
(K_ni 2.443e11, V_m 4.591e-5, p 3.28, offset 4.433e-5) is shared verbatim with all three other
specimens across JRC 1.19-15.32, and SW-T1 — the only specimen where it *was* bracketed — found it
**20 % off**.

**Known open defect in this deck.** The hydraulic closure is saturated:
sigma_0 = V_h*K_h = 1.2e-6 * 1.25e13 = **15.0 MPa** against a **58-67 MPa** pre-event operating
range, so the stress-aperture term delivers 0.0023 um where Table 2 opens 0.58. Stage-5 flow is
0.730 against 1.505 ml/min, **-51.5 %**, this deck's single worst point. Addressed by `106_05`.

**And one thing no aperture law can fix.** Table 2 has SW-T2 creeping 0.015 mm in shear by stage 5
where this model has 0.003, and its aperture kinks 2.31 -> 2.69 um between stages 4 and 5 while
sigma'_n falls only 2.1 MPa. That is pre-peak creep, not closure. See `106_14`/`106_15` and the
opt-in stress-dependent tangential stiffness added on branch `orca_v9`.

> This block was added on 2026-08-26 after the 105-series post-mortem. It **supersedes the
> "Final deck" line below it**; everything after it is left exactly as written so the earlier
> selection stays auditable. The authoritative ranking is
> `doc/independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv`, regenerated the same day and now
> complete through series 105. The next campaign is
> `doc/independent_analysis/RUN_LIST_106_SERIES.md`.

---

**Status: FINAL. No further sweep.**
Deck of record (mesh 5): `93_03_swt2_final_theta30_resc9p71_ppfix.i` — constitutively identical to
`91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6.i`, which is the run scored below; see §8.
Mesh-convergence run: `93_04_swt2_final_theta30_resc9p71_ppfix_mesh3.i`
MC baseline: `94_03_swt2_mc_final.i` / `94_04_swt2_mc_final_mesh3.i`
Date: 2026-08-17. Branch `orca_v5`, repo `orca_4.0`.

---

## 1. Specimen and what the model has to reproduce

SW-T2 is a **mated Mode-I (tensile) fracture** in Sierra White granite, created by Brazilian
splitting and then reassembled, so the two surfaces are geometrically matched and interlock
strongly. Ye & Ghassemi (2018) hold the specimen at 30 MPa confining pressure and a fixed axial
piston position, then raise borehole pressure in six 4-MPa steps to 28 MPa and unload in five.
Table 2 records five independent measurements at each of the eleven holds.

**Fracture angle.** Table 1 prints 31°. The paper's own Table 2 says otherwise. Dividing eq (3)
by eq (4) removes the differential stress and leaves `tan θ = (σ'ₙ − σ₃ + P_p)/τ`, which can be
evaluated at all eleven stages from tabulated quantities alone; it returns **30.001°** for SW-T2
and reproduces the printed angle to within 0.03° for the other three specimens. The mesh is
therefore cut at 30.000°, not 31°. This matters: at 30° instead of 31° the ratio τ/σ'ₙ rises 2.5%
at the same (σ_d, P_p), which is a whole injection step of strength — earlier deck generations
absorbed the 1° error into their friction calibration.

## 2. Calibrated joint parameters

| parameter | value | source |
|---|---|---|
| θ (fracture angle) | 30.000° | recovered from Table 2, not Table 1 |
| L × D | 132.70 × 50.52 mm | Table 1 |
| JRC | 14.63 | rough mated tensile fracture |
| JCS | 150 MPa | paper §2.1, intact UCS |
| φ_r | 29.756° | joint-constant refit |
| peak cohesion `c` | 33.20 MPa | asperity interlock; pins the envelope through the last stick stage |
| residual cohesion `c_res` | **9.71 MPa** | the one parameter this campaign fitted |
| D_c | 150 µm | slip-weakening length |
| slip-weakening exponent `m` | 1.4 | |
| dilation angle | 13.965° (peak = residual) | |
| Biot coefficient α | 0.6 | |
| E, ν | 67 GPa, 0.32 | shared by all four specimens |
| axial frame penalty | 5.121 × 10¹¹ Pa/m | per-specimen loading-frame compliance |

Strength law: `τ_lim = c(s) + σ'ₙ·tan[φ_r + JRC·log₁₀(JCS/σ'ₙ)]`, with
`c(s) = c_res + (c − c_res)·exp[−(sᵖ/D_c)^m]`.


## 3. Comparison against Ye & Ghassemi (2018) Table 2

Scored with `scripts/table2_gate.py`. Stage times come from the deck's own injection schedule
(the last schedule point inside 0.35 MPa of each target; stage 6 is anchored to the end of the peak
plateau); the model is sampled at the last output row at or before that time. Displacements are
zeroed at stage 1, as Table 2 is, so stage 1 is excluded from the d_n and d_s statistics.
The informational columns a_h and k are NOT scored — the paper back-computes a_h from the measured
Q through the cubic law and defines k = a_h²/12, so neither carries information beyond Q.


| stage | branch | P_i (MPa) | Q (mL/min) paper \| model \| err | sigma'_n (MPa) paper \| model \| err | tau (MPa) paper \| model \| err | d_n (mm) paper \| model \| err | d_s (mm) paper \| model \| err |
|---|---|---|---|---|---|---|---|
| 1 | loading | 8 | 0.1150 \| 0.1144 \| -0.0006 | 66.74 \| 66.14 \| -0.60 | 74.87 \| 73.86 \| -1.01 | 0.0000 \| 0.0000 \| +0.0000 | 0.0000 \| 0.0000 \| +0.0000 |
| 2 | loading | 12 | 0.2760 \| 0.2670 \| -0.0090 | 64.53 \| 64.19 \| -0.34 | 74.54 \| 73.95 \| -0.59 | -0.0010 \| -0.0000 \| +0.0010 | 0.0010 \| 0.0000 \| -0.0010 |
| 3 | loading | 16 | 0.4500 \| 0.4199 \| -0.0301 | 62.37 \| 62.25 \| -0.12 | 74.25 \| 74.04 \| -0.21 | -0.0020 \| -0.0000 \| +0.0020 | 0.0030 \| 0.0000 \| -0.0030 |
| 4 | loading | 20 | 0.7500 \| 0.5731 \| -0.1769 | 60.19 \| 60.31 \| +0.12 | 73.94 \| 74.14 \| +0.20 | -0.0030 \| -0.0001 \| +0.0029 | 0.0070 \| 0.0000 \| -0.0070 |
| 5 | loading | 24 | 1.5050 \| 0.7294 \| -0.7756 | 57.88 \| 58.23 \| +0.35 | 73.40 \| 74.01 \| +0.61 | -0.0050 \| -0.0008 \| +0.0042 | 0.0150 \| 0.0031 \| -0.0119 |
| 6 | loading | 28 | 11.1000 \| 9.1363 \| -1.9637 | 29.36 \| 30.19 \| +0.83 | 27.48 \| 28.91 \| +1.43 | -0.1420 \| -0.1431 \| -0.0011 | 0.5710 \| 0.5627 \| -0.0083 |
| 7 | unloading | 24 | 7.2000 \| 6.9345 \| -0.2655 | 31.26 \| 31.94 \| +0.68 | 27.29 \| 28.48 \| +1.19 | -0.1420 \| -0.1384 \| +0.0036 | 0.5720 \| 0.5627 \| -0.0093 |
| 8 | unloading | 20 | 5.1500 \| 5.1663 \| +0.0163 | 33.23 \| 33.77 \| +0.54 | 27.24 \| 28.18 \| +0.94 | -0.1390 \| -0.1357 \| +0.0033 | 0.5660 \| 0.5626 \| -0.0034 |
| 9 | unloading | 16 | 3.5400 \| 3.6368 \| +0.0968 | 35.23 \| 35.63 \| +0.40 | 27.25 \| 27.94 \| +0.69 | -0.1390 \| -0.1341 \| +0.0049 | 0.5650 \| 0.5626 \| -0.0024 |
| 10 | unloading | 12 | 2.1600 \| 2.2464 \| +0.0864 | 37.18 \| 37.52 \| +0.34 | 27.15 \| 27.74 \| +0.59 | -0.1330 \| -0.1331 \| -0.0001 | 0.5570 \| 0.5626 \| +0.0056 |
| 11 | unloading | 8 | 0.9100 \| 0.9415 \| +0.0315 | 39.14 \| 39.42 \| +0.28 | 27.09 \| 27.58 \| +0.49 | -0.1300 \| -0.1325 \| -0.0025 | 0.5520 \| 0.5626 \| +0.0106 |

| observable | n | MAE | RMSE | max abs err | mean abs % | nRMSE (% of measured range) |
|---|---|---|---|---|---|---|
| Q (mL/min) | 11 | 0.3139 | 0.6452 | 1.964 | 10.7% | **5.87%** |
| sigma'_n (MPa) | 11 | 0.42 | 0.47 | 0.83 | 1.1% | **1.26%** |
| tau (MPa) | 11 | 0.72 | 0.81 | 1.4 | 2.1% | **1.70%** |
| d_n (mm) | 10 | 0.002546 | 0.002923 | 0.004888 | 38.9% | **2.06%** |
| d_s (mm) | 10 | 0.006237 | 0.007178 | 0.01188 | 38.4% | **1.25%** |
| **mean** |  |  |  |  |  | **2.43%** |

**Mean normalised RMSE 2.43%** — the best of the four specimens by a factor of two.
For reference, the two bracket arms and the parent:

| case | residual cohesion | Q | σ'ₙ | τ | d_n | d_s | **mean nRMSE** |
|---|---|---|---|---|---|---|---|
| `90_03` | 10.695 MPa | 7.59 | 2.87 | 3.88 | 3.46 | 2.95 | 4.15% |
| `91_03` | 8.74 MPa | 4.46 | 1.06 | 1.43 | 2.36 | 2.63 | **2.39%** |
| `91_04` | **9.71 MPa** | 5.87 | 1.26 | 1.70 | 2.06 | 1.25 | **2.43%** |

## 4. Why this is final, and why 91_04 rather than 91_03

`91_03` and `91_04` are a statistical dead heat (2.39 vs 2.43%), and that is the point: the
bracket has **closed**. Interpolating each observable between the two arms and asking what
residual cohesion would put it exactly on the paper gives

| from | τ | σ'ₙ | d_s | d_n | Q |
|---|---|---|---|---|---|
| implied `c_res` (MPa) | 9.15 | 9.15 | 9.65 | 9.36 | 8.51 |

All five independent measurements agree to ±0.6 MPa. The parameter is identified, both arms
straddle it, and neither is more than 0.6 MPa away. There is nothing left for another sweep to
find — a third deck at 9.15 MPa would change the mean score by a few hundredths of a percent.

`91_04` is preferred on two grounds. It is better on both displacements (d_s 1.25 vs 2.63%,
d_n 2.06 vs 2.36%), which are what the joint model actually predicts, and its 9.71 MPa sits in
the same 9–10 MPa band that SW-T1 converged on independently (`91_02`, 9.19 MPa). Two mated
Mode-I fractures in the same granite, tested under the same confining pressure, ought to retain
similar interlock, and they do. `91_03` is retained as the second arm of the bracket, not
discarded.

## 5. The remaining error, and how to justify it in the paper

Five residuals survive. Three of them are one physical effect, and none is a mis-set parameter.

**(a) Pre-peak aseismic slip — the largest error, at stage 5.** Q reads 0.73 mL/min against
1.505 measured, −52%, and it is the only relative error above 20% anywhere in the table. Look at
the same stage in d_s: the experiment has already accumulated **15 µm of shear displacement**
before the main event, the model 3 µm. The measured joint is creeping and dilating for two full
injection stages before it fails; the modelled joint is still locked. This propagates: stage 4 Q
is −24%, stage 6 (peak) is −18%, and the loading-branch d_n error of +0.002 to +0.004 mm is the
same 5 µm of pre-peak closure the model does not have. A Barton–Bandis envelope with slip
weakening is a **threshold** law: nothing weakens until τ reaches τ_lim. Reproducing progressive
sub-critical asperity failure needs a time- or rate-dependent term (creep, or rate-and-state),
which is a constitutive addition, not a calibration. This is the honest statement for the paper:
*the model reproduces the failure event and everything after it, and under-predicts the
precursory hydraulic response by roughly a factor of two.*

**(b) The unloading branch cannot back-slip.** The measurement's shear displacement **decreases**
from 0.571 mm at stage 6 to 0.552 mm at stage 11 — 19 µm of recovery as σ'ₙ is restored. The
model's plastic slip is irreversible by construction and holds at 0.5626 mm, so its error walks
from −0.0083 mm at stage 6 to +0.0106 mm at stage 11. Both bracket arms do this identically, so
it is not a parameter. It is worth one sentence in the paper: the measured reversal is elastic
recovery of the loading frame plus the joint's own shear compliance, and an irreversible slip
variable does not carry it.

**(c) Residual shear traction runs 0.5–1.4 MPa strong.** Stages 6–11 are all positive, decaying
monotonically from +1.43 to +0.49 MPa. This is the 0.56 MPa by which 9.71 MPa exceeds the 9.15
MPa optimum, and it is the price paid for the better displacement match. On a 27 MPa residual
traction it is a 2–5% error.

**(d) σ'ₙ mirrors τ.** The σ'ₙ errors (+0.28 to +0.83 on the same stages) are the same defect
seen through eq (3): σ'ₙ and τ are two projections of one stress state, so they cannot disagree.
They should not be quoted as independent confirmations of anything.

**(e) The loading branch is 0.1–1.0 MPa soft in τ at stages 1–3 and 0.1–0.6 MPa stiff at
stages 4–5.** The crossover is a ±0.8% deviation on a 74 MPa traction and is within the
digitisation width of Table 2.

## 6. Mesh convergence

`92_05_swt2_final_theta30_resc9p71_mesh3.i` is the identical physics on the size-3 mesh
(121 745 nodes, 1873 on the interface, against 11 861 / 409 at size 5). **Not one constitutive
parameter differs.** Two things had to change and both are mesh-resolution artefacts:

* **The source node.** `ExtraNodesetGenerator ... use_closest_node = true` never errors. On the
  size-3 mesh the size-5 borehole coordinate snaps to a **bulk node 584.9 µm away**, beating the
  nearest interface node at 956.8 µm — the run would have driven the matrix instead of the joint,
  silently. The mesh-3 deck therefore carries the exact size-3 interface-node coordinates
  (`∓0.017892500, 0, 0.035359281 / 0.097340719`). The borehole moves 28 µm relative to size 5,
  well inside one element. `scripts/check_source_nodes.py` must be re-run after any mesh change.
* Output `file_base` names.

`injection_pressure_pp` and `pp_outlet_pp` are `AverageNodalVariableValue` over the nodesets, so
they follow the source automatically — SW-T2 was never exposed to the stale-`PointValue` failure
that hit SW-S4.

**What to expect.** `flow_rate_validation_ml_min_pp` (the paper's eq (9) cubic-law value, and the
only flow channel used anywhere in this document) is built from boundary averages and should be
mesh-insensitive. `flow_rate_pp` — a `NodalSum` of the injection flux over a one-node set — and
`flow_rate_mesh_geometry_ml_min_pp` are **not** mesh-independent by construction; they are
diagnostics, and a change in them between the two meshes is expected.

## 7. Reproduce

```bash
sbatch SWT2/92_05_swt2_final_theta30_resc9p71_mesh3_hpc_nochk.sh
python3 scripts/table2_gate.py --tag hpc \
  SWT2/results_csv_hpc_rorqual/91_04_swt2_bbfast_theta30_resc9p71_kernel_SV_biot0p6_hpc.csv \
  SWT2/results_csv_hpc_rorqual/92_05_swt2_final_theta30_resc9p71_mesh3_hpc.csv
```


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

**1. Twenty diagnostic postprocessors added.** SW-S4 carried 87 channels and this deck 70; the
eight `bb_*` envelope channels, the five loading-frame channels and the seven `bulk_*` kinematic
channels existed only there (open task #82). All eight 93-series decks now emit the same 91.
`bulk_sin_theta` / `bulk_cos_theta` are set from this specimen's own 30 deg, and the bulk probes
sit on one rule across all four specimens: cylinder surface, `z = L/2 +- 50 mm`. None of these
feeds the Table-2 gate.

**2. Nothing else.** Both SW-T2 source coordinates are exact `fracture_interface` nodes to 0.00 um
on both meshes, the theta30 mesh is the one in use, and the paper-frame constants match it.

### The 94-series MC baseline

`94_03_swt2_mc_final.i` / `94_04_swt2_mc_final_mesh3.i` are the 93-series decks with **one block replaced**: `[czm_contact]` becomes
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
