# The 94-series Mohr-Coulomb baseline — construction and parameter transfer

2026-08-18. Branch `orca_v5`, repo `orca_4.0`. Companion to `SWT1_FINAL.md`, `SWT2_FINAL.md`,
`SWS3_FINAL.md`, `SWS4_FINAL.md` and to `HPC_90_91_92_TABLE2_ERROR_ANALYSIS.md`.

The paper's framing is **BBFast primary, Mohr-Coulomb baseline**. For that comparison to say
anything, the two runs of a pair have to differ in the constitutive law and in nothing else. This
document records how the eight 94-series decks were built and where their parameters come from.

---

## 1. Why none of the four existing MC decks could be reused

| specimen | old deck | blocking defects |
|---|---|---|
| SW-S3 | `83_11_sw3_mc_opening_gate5d30_m0_kernel_SV.i` (+ `_mesh3`) | mesh `sw3_mesh_size5.e` = **124.40 mm**, superseded by the corrected `L123p4` (123.40 mm); `biot_coefficient = 1e-12` |
| SW-S4 | `67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV.i` (+ `_mesh3`) | mesh `ye2018_sw_s4_size5_mesh.e` = **θ 28.9904°, fracture plane 2.85 mm off-centre**; **no paper-frame `σ'ₙ` or `τ` postprocessor at all**, so the gate silently fell through to the local Barton-Bandis frame |
| SW-T1 | `orca_3.0 .../SWT1_MC_casevalidation_01_mesh5.i` | `biot = 1e-12`; split mass kernel; no mesh-3 sibling; **swapped paper-frame θ** |
| SW-T2 | `orca_3.0 .../SWT2_MC_casevalidation_01_mesh5.i` | as above, plus it sits on the 31° mesh while the BBFast final uses the θ30 mesh |

**The decisive defect is the swapped angle on the tensile pair.** Each deck carries the *other*
specimen's fracture angle in its paper-frame constants:

```
SWT1_MC : mesh 32.0 deg, but sin^2 = 0.265264, sin*cos = 0.441474  ->  assumes 31 deg
SWT2_MC : mesh 31.0 deg, but sin^2 = 0.280814, sin*cos = 0.449397  ->  assumes 32 deg
```

At this campaign's differential stress (~150 MPa) that is about **2.3 MPa on `σ'ₙ` and 1.2 MPa on
`τ`** — roughly **three times SW-T1's entire `σ'ₙ` RMSE of 0.67 MPa**. The MC cohesions fitted in
those decks (14.54 and 15.41 MPa) were therefore fitted against mis-resolved stresses and cannot
be ported.

One thing those decks did have right: all four carry the same digitized injection schedule as
their BBFast counterparts (25 / 25 / 57 / 119 knots, identical `t_end` and `P_i,max`). That is
also what the 93-series carries, so `scripts/table2_gate.py` scores the 94-series unchanged.

---

## 2. How the 94-series decks were built

Each `94_*` deck is its `93_*` sibling with **one block replaced**: `[czm_contact]` becomes
`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` ("roughness-dependent Coulomb
return map"). The rest of the `[Materials]` block — `czm_jump`, `czm_pressure`,
`czm_global_traction`, `aperture_mech`, `czm_aperture`, all the output-property materials — is
identical, as are the mesh file, the source nodesets and their coordinates, the boundary
conditions, the injection schedule, the paper-frame constants, the flow constants and the solver.

Three mechanical consequences of the swap had to be handled, none of them a modelling choice:

1. **Seven postprocessors change.** The `bb_*` envelope channels read Barton-Bandis material
   properties that the MC law does not declare. They are replaced one-for-one by seven `mc_*`
   analogues (`mc_roughness_state_pp`, `mc_mu_effective_pp`, `mc_cohesion_effective_pp`,
   `mc_dilation_angle_effective_pp`, `mc_limit_tau_pp`, `mc_normal_contact_pressure_pp`,
   `mc_cumulative_plastic_slip_pp`). Both series emit **91** postprocessors; 84 are shared.
2. **Twelve properties flip AD-ness.** The BBFast law declares `fracture_state`, `limit_tau`,
   `cumulative_plastic_slip`, `friction_coefficient_effective`, `cohesion_effective`,
   `normal_opening_total` and six others as non-AD; the MC law declares them AD. Every consumer
   in the deck is promoted to its AD flavour (`MaterialRealAux` → `ADMaterialRealAux`,
   `SideAverageMaterialProperty` → `ADSideAverageMaterialProperty`), and `[czm_aperture]`'s
   `cumulative_plastic_slip_is_ad` flips `false` → `true`.
3. **The MC return map rejects increment caps.** `max_plastic_slip_increment` and
   `max_dilation_increment` must be 0; SW-T1's BBFast deck ran 5.0e-6 and 1.5e-6. Substepping
   (`max_local_substeps = 48`) and `tangential_viscosity` do that job instead.

Barton-Bandis-only top-level constants (`bb_jrc`, `bb_jcs`, the `normal_unload_*` family,
`min_tau_limit`, …) are commented out in the 94 decks with a marker, because MOOSE treats an
unreferenced top-level assignment as an error.

All sixteen decks pass `orca-opt --check-input`.

---

## 3. The parameter transfer

The MC parameters are **not a fresh calibration**. They are a transfer of each specimen's
already-calibrated Barton-Bandis envelope, so that a 93/94 pair differs in constitutive *form*
rather than in fitted strength. The two laws:

```
BB peak      tau = c     + sigma'_n * tan(phi_r + JRC*log10(JCS/sigma'_n))
BB residual  tau = c_res + sigma'_n * tan(phi_r,sw)              <- already a Coulomb line
   weakened by  W = exp(-(s/Dc)^m),   c(W) = c_res + (c - c_res)*W

MC           tau = c(R)  + sigma'_n * mu(R)
   Rbar = (R - R_res)/(1 - R_res),  R = R_res + (R_0 - R_res)*exp(-gamma/D_R)
   mu(R) = mu_smooth + (mu_rough - mu_smooth) * Rbar^n_f          (n_f = n_c = 1)
```

Three rules:

* **Residual — exact.** `mu_smooth = tan(phi_r,sw)` and `c_smooth = c_res`. The BB residual
  envelope *is* a Coulomb line, so nothing is lost.
* **Peak — tangent match at onset.** `mu_rough` and `c_rough` match the value and the slope of the
  BB peak envelope at `sigma'_n*`, the last stick stage's normal stress from Table 2. They are
  then divided by `Rbar_0` so that MC's strength **at zero slip** equals the BB peak on decks that
  start at `R_0 < 1`.
* **Roughness — copied verbatim.** `initial_roughness`, `residual_roughness` and
  `roughness_decay_distance` are the BBFast `roughness_state_*` values, because `roughness_state`
  is consumed by `ADOrcaRoughnessDamageFracturePermeability` and therefore drives the hydraulic
  aperture and the scored `Q`. Both laws use the same exponential decay form, so this is exact.

### Transferred values

| specimen | σ'ₙ* (MPa) | Rbar₀ | `friction_coefficient_rough` | `cohesion_rough` (MPa) | `friction_coefficient_smooth` | `cohesion_smooth` (MPa) | R₀ | R_res | D_R (m) |
|---|---|---|---|---|---|---|---|---|---|
| SW-T1 | 56.94 | 1.0000 | 0.5536 | 37.034 | 0.5717 | 9.190 | 1.00 | 0.10 | 1.5e-4 |
| SW-T2 | 57.88 | 1.0000 | 0.5528 | 42.959 | 0.5717 | 9.710 | 1.00 | 0.10 | 1.5e-4 |
| SW-S3 | 23.42 | 0.6000 | 0.8818 | 2.645 | 0.1486 | 1.400 | 0.64 | 0.10 | 4.0e-5 |
| SW-S4 | 26.51 | 0.3889 | 0.9804 | 3.225 | 0.1139 | 0.000 | 0.45 | 0.10 | 8.0e-5 |

Dilation angles, dilation decay distance, the normal-closure law (`use_hyperbolic_normal_closure`
with the same `K_ni`, `V_m`, exponent and offset) and `tangential_viscosity` are copied verbatim
from the BBFast sibling.

### How good the transfer is

Checked against Table 2's own `σ'ₙ` values:

| specimen | stick stages | max \|MC − BB\| over the stick stages | max \|MC − BB\| over the full σ'ₙ range | strength margin over measured τ, BB / MC |
|---|---|---|---|---|
| SW-T1 | 1–5 | 0.090 MPa | 1.00 MPa | +2.23 / +2.23 MPa |
| SW-T2 | 1–5 | 0.091 MPa | 1.25 MPa | +1.55 / +1.55 MPa |
| SW-S3 | 1–5 | 0.026 MPa | 0.03 MPa | +1.67 / +1.67 MPa |
| SW-S4 | 1–3 | 0.015 MPa | 0.13 MPa | +1.07 / +1.07 MPa |

The margins are identical to two decimal places, so **slip onset is inherited rather than
refitted**. This matters: onset in this campaign is quantized by the injection step, and a
baseline that triggers one step early or late would produce a difference that has nothing to do
with the constitutive law being tested.

---

## 4. What the two laws are still allowed to disagree about

This is the point of running the pair, and it should be what the paper reports.

1. **Envelope curvature.** Barton-Bandis is log-curved in `σ'ₙ`; Mohr-Coulomb is a straight line
   through the onset tangent. They separate by up to 1.25 MPa (SW-T2) at the far end of the
   unloading branch, where `σ'ₙ` is furthest from the match point.
2. **The weakening path.** BB weakens on `W = exp(-(s/Dc)^m)` with `m` = 1.10–1.40; MC weakens
   linearly in `Rbar = exp(-gamma/D_R)`. Same endpoints, different route between them — which is
   exactly the burst-and-arrest behaviour SW-S4 and SW-S3 are sensitive to.
3. **One characteristic distance instead of two.** BB has a strength distance `Dc` and a roughness
   distance `D_R`; MC has only `D_R`, which drives both. `D_R` was set from the BBFast *roughness*
   distance so the aperture-permeability path — feeding the scored `Q` — stays identical. On
   SW-T1 and SW-T2 the two BB distances are equal and this is exact; on SW-S3 BB used
   `Dc = 6.0e-5` against `D_R = 4.0e-5` (1.5×) and on SW-S4 `7.45e-5` against `8.0e-5` (1.07×), so
   on those two the MC strength weakens over a slightly different distance than BB's did. This is
   a genuine expressive difference between the laws, not a fitting choice, and it should be stated
   that way.
4. **Rate-and-state is off.** The old MC decks ran it with constants fitted against the superseded
   meshes. The baseline here is a plain roughness-dependent Coulomb model, which is what a baseline
   should be.

---

## 5. Deck inventory

| specimen | BBFast mesh 5 | BBFast mesh 3 | MC mesh 5 | MC mesh 3 |
|---|---|---|---|---|
| SW-T1 | `93_01_swt1_final_c26p9_resc9p19_ppfix` | `93_02_..._mesh3` | `94_01_swt1_mc_final` | `94_02_swt1_mc_final_mesh3` |
| SW-T2 | `93_03_swt2_final_theta30_resc9p71_ppfix` | `93_04_..._mesh3` | `94_03_swt2_mc_final` | `94_04_swt2_mc_final_mesh3` |
| SW-S3 | `93_05_sw3_final_resc1p40_ppfix` | `93_06_..._mesh3` | `94_05_sw3_mc_final` | `94_06_sw3_mc_final_mesh3` |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix` | `93_08_..._mesh3` | `94_07_sw4_mc_final` | `94_08_sw4_mc_final_mesh3` |

Sixteen runs — the four specimens × two mesh sizes × two constitutive laws. Each has an
`*_hpc_nochk.sh` beside it (32 ranks / 32 G / 24 h at mesh 5, 64 ranks / 64 G / 48 h at mesh 3).

```bash
for d in SWT1 SWT2 SWS3 SWS4; do
  for s in $d/9[34]_*_hpc_nochk.sh; do sbatch "$s"; done
done
```

Scoring is unchanged:

```bash
python3 scripts/table2_gate.py --tag hpc --sample SWT1 \
  Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/93_01_swt1_final_c26p9_resc9p19_ppfix_hpc.csv \
  Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/94_01_swt1_mc_final_hpc.csv
```

---

## 6. What to expect, and what would be a red flag

The BBFast decks are calibrated and the MC decks inherit their envelope, so the MC runs are **not**
expected to match Table 2 as well — that is the finding the baseline exists to produce. What
*would* indicate a build error rather than a physics result:

* slip onset landing on a different injection stage than its BBFast sibling (the peak envelopes
  agree to 0.09 MPa, so onset should be the same stage);
* `Q` at stages 1–5, before any slip, differing by more than a percent (the aperture path is
  identical until `roughness_state` moves);
* `σ'ₙ` or `τ` differing at stage 1 (nothing has yielded yet, so both laws are on the same elastic
  normal closure).

Any of those three means the swap leaked something it should not have, and the pair should be
diffed before the numbers are believed.
