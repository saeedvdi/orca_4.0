# Source comparison: `HPC_backup/orca_3.0_claude_edits` vs `orca_4.0`

**Date:** 2026-08-15
**Scope:** every file under `src/` and `include/` in both trees — all materials, interface
materials, kernels, interface kernels, auxkernels, BCs, mesh generators and utils.

| | `orca_3.0_claude_edits` | `orca_4.0` |
|---|---|---|
| path | `/media/geomechanics/Data4TB/projects/HPC_backup/orca_3.0_claude_edits` | `/media/geomechanics/Data4TB/projects/orca_4.0` |
| git HEAD | `aaa4d26` (2026-08-12, "up") | `orca_v1` |
| active branch | `feature/state-dependent-fault-pressure-coefficient` | `orca_v1` |
| `src/*.C` | 31 | 51 |
| `include/*.h` | 31 | 51 |

Method: exhaustive `find` over both trees, set difference on the relative paths, then `cmp`
on every shared path and a full `diff -u` on every mismatch. The only non-`.C`/`.h` files under
`src/`/`include/` in either tree are libtool build artifacts (`main.*.lo`, `.libs/*.o`), which
are ignored.

---

## 1. Headline result

**The backup is a strict subset of orca_4.0 in file coverage.** No file exists in
`orca_3.0_claude_edits` that is missing from `orca_4.0`.

| relation | count |
|---|---|
| shared paths | 62 (31 `.C` + 31 `.h`) |
| shared and **byte-identical** | **53** |
| shared and **differing** | **9** |
| present only in `orca_4.0` | **40** (20 `.C` + 20 `.h`) |
| present only in the backup | **0** |

The 9 differences fall into four functional groups, only one of which is a live physics
concern. They are covered in §3–§6 below.

---

## 2. The 40 files orca_4.0 adds

These are pure additions — capability the backup snapshot predates. Nothing here is a
regression; it is the reason `orca_4.0` is the more complete tree.

**Interface materials (8)**
- `ADOrcaBartonBandisBakhtarFracturePermeability` — literal Bakhtar `e_h = E_m²/JRC^2.5` law
- `ADOrcaCohesionlessDamageMohrCoulombContactTraction`
- `ADOrcaCohesionlessDamageRSFBBContactTraction`
- `ADOrcaDecoupledDilationRoughnessContactTraction`
- `ADOrcaHystereticFracturePermeability`
- `OrcaCZMCubicLawAperture`
- `OrcaCZMMohrCoulombFriction`
- `OrcaCZMStressDependentAperture`

**Energy-balance kernels (6)** — the entire thermal branch is absent from the backup:
`OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel`,
`…HeatAdvectionKernel`, `…HeatAdvectionSUPGKernel`,
`…HeatVolumetricExpansionKernel`, `OrcaHeatConductionKernel`,
`OrcaHeatConductionTimeDerivativeKernel`.

**Mass-balance kernels (2)**
- `OrcaFullySaturatedSinglePhaseDarcyKernel`
- `OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel` — the combined **kernel_SV**, see §3

**Interface kernels (2)** — `OrcaFaultFlowInterfaceKernel`, `OrcaFaultPressureInterfaceKernel`

**Auxkernels (1)** — `OrcaADRankTwoAux`

**BCs (1)** — `OrcaNormalPressureBC`

---

## 3. Group A — Biot storage formulation (4 files) — **the one that matters**

Files: `OrcaSinglePhaseMassTimeDerivativeKernel.{C,h}`,
`OrcaSinglePhaseMassVolumetricExpansionKernel.{C,h}`.

`orca_4.0` carries the **original 25 Jun 2026 versions**. The backup carries a corrected
rewrite. This is the only place where the backup is ahead of orca_4.0 on physics.

### Storage term

| | residual |
|---|---|
| `orca_4.0` (old) | `test · (1 + tr εₒₗd) · (φρ − φₒₗdρₒₗd)/Δt` |
| backup (fixed) | `test · γ · (1/M) · dp/dt`,  `1/M = (α − φ)/K_s + φ/K_f` |

With the constant porosity these decks use, the old form collapses to `(φ/K_f) dp/dt` and
therefore **drops the grain-compressibility storage `(α − φ)/K_s` entirely**.

### Poromechanical coupling term

| | coefficient |
|---|---|
| `orca_4.0` (old) | **porosity φ** |
| backup (fixed) | **Biot coefficient α** |

The in-source note on the fix records the consequence: the two errors together make the
consolidation coefficient wrong by `α/φ`, *"verified against the Terzaghi benchmark: 3.33x too
fast at alpha = 1, phi = 0.3"*.

The backup also renames the now-unused `base_name` to a retained-but-ignored parameter so old
decks still parse, and reads `one_over_biot_modulus_qp` instead of reconstructing storage from
porosity and strain.

### Blast radius — small, but not zero

`orca_4.0` does not depend on these kernels for most work, because the **combined kernel_SV**
(`OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel`, orca_4.0-only) assembles the correct
`(1/M) dp/dt + α ε̇_v` in one object. Active (uncommented) usage across the 17 decks:

| kernel form | decks |
|---|---|
| combined `kernel_SV` — correct | **16 of 17** |
| old split pair — stale physics | **1**: `SWS4/67_11_sw4_mc_dS0p15_s28_w12_m0.i` |

So exactly one deck — the MC baseline that exists specifically as the split-pair control
against `67_11_…_kernel_SV.i` — is running the uncorrected consolidation coefficient. That
weakens it as a control: the two decks differ not only in kernel packaging but in physics.

> **Note on a misleading comment, not a bug.** Line 41 of the combined kernel says
> *"interpret biot_modulus_qp as (1/M)"*, but `OrcaTHMaterial` stores **M**. The code is
> right — it computes `dpdt * 1/_biot_modulus[_qp]` — so the residual is `(1/M) dp/dt` as
> intended. Only the comment is wrong, and it contradicts the correct comment 50 lines below it.

### Porting is not a one-file change

The backup's fixed kernel reads `one_over_biot_modulus_qp`, **a property `orca_4.0` never
declares** (it exists nowhere in `orca_4.0/src` or `orca_4.0/include`). Porting Group A
therefore requires the `OrcaTHMaterial` change in §4 as well.

---

## 4. Group B — `OrcaTHMaterial` (2 files, 171 changed lines)

Three independent divergences bundled in one file.

### B1. External fluid-properties support — orca_4.0 removed it *(deliberate, permanent)*

The backup can query a `SinglePhaseFluidProperties` UserObject for ρ, μ, c_p, c_v, e, h, s, k
and β. `orca_4.0` deletes that path: `fluid_properties_model`, `fp` and
`fluid_thermal_expansion_model` became `addDeprecatedParam` and **hard-error unless set to
`user`**.

Compatibility: all 17 orca_4.0 decks set `= user`, so nothing breaks today. It is a genuine
capability reduction, and it is the change that makes the two `OrcaTHMaterial` files
irreconcilable by simple merge.

### B2. `one_over_biot_modulus_qp` — only in the backup

The backup declares the storativity `1/M` explicitly rather than reciprocating `M`, so that the
`M → ∞` (incompressible) limit is representable and no kernel divides by `M`. Required by the
Group A kernels. Absent from orca_4.0.

### B3. Two robustness guards on `biot_modulus_qp` — only in the backup

**Guard 1 — degenerate bulk modulus.** When `K_d ≤ 0` or no stiffness source is available:

| | behaviour |
|---|---|
| `orca_4.0` | `biot_modulus = 0`, `biot_modulus_available = 0`, return → downstream `mooseError` |
| backup | falls back to the incompressible-grain limit (`1/K_s = 0`), keeping the always-present `φ/K_f` fluid compressibility |

orca_4.0 fails loudly rather than silently producing a wrong answer, so this is a
graceful-degradation difference, not a correctness one.

**Guard 2 — negative storativity clamp.** The backup clamps the grain term at zero:

```
grain_term = (1 − α)(α − φ) / K_d          // negative when α < φ, or α > 1
denom      = max(0, grain_term) + φ/K_f    // backup
denom      =         grain_term  + φ/K_f   // orca_4.0
```

The comment names the exact situation: *legacy decks that set `biot_coefficient ≈ 0` with a
nonzero porosity*, where a negative storativity would make the flow problem ill-posed.

**This condition is live in the current deck set.** `SWS3`, `SWT1` and `SWT2` all set
`biot_coefficient = 1e-12` with `initial_porosity = 0.001`, so `α ≪ φ` and the grain term is
negative. It does **not** go ill-posed, because `φ/K_f` dominates — but the two trees compute
measurably different storage:

| family | E [GPa] | α | φ | K_d [GPa] | M, orca_4.0 | M, clamped | Δ |
|---|---|---|---|---|---|---|---|
| SWS4 | 67 | 0.6 | 0.001 | 62.0 | 2.4562e11 | 2.4562e11 | 0.00 % |
| SWS3 | 75 | 1e-12 | 0.001 | 69.4 | 5.1374e12 | 4.7836e12 | **+7.40 %** |
| SWT1 / SWT2 | 67 | 1e-12 | 0.001 | 62.0 | 5.1832e12 | 4.7836e12 | **+8.36 %** |

So the eight SWS3/SWT1/SWT2 decks currently run a Biot modulus 7–8 % stiffer than the clamped
formulation would give. SWS4 (α = 0.6) is unaffected — its grain term is positive and the clamp
never engages.

The deeper issue is upstream of both trees: `biot_coefficient = 1e-12` with `φ = 0.001` is
not a physical parameterisation, and the clamp only masks it. See TODO item N3.

---

## 5. Group C — state-dependent α in the CZM pressure kernel (2 files) *(deliberate revert)*

Files: `OrcaCZMFluidPressureInterfaceKernel.{C,h}`.

The backup — snapshotted from the branch literally named
`feature/state-dependent-fault-pressure-coefficient` — adds an optional
`alpha_property_name` parameter pointing at an AD material property (e.g.
`fault_pressure_area_coefficient`), which multiplies `pressure_traction_coefficient`:

```
coefficient = _alpha ? _pressure_traction_coefficient * (*_alpha)[_qp]
                     : _pressure_traction_coefficient;
```

Left empty it is byte-identical to the constant-coefficient behaviour, so the feature is
opt-in and backward compatible.

`orca_4.0` does not have it. This matches the decision recorded on 2026-08-14 to revert
state-dependent α. **No action needed** — orca_4.0 is intentionally the reverted state.

---

## 6. Group D — `src/main.C` (1 file) — build target only

| | app instantiated |
|---|---|
| backup | `Moose::main<OrcaApp>` |
| `orca_4.0` | `Moose::main<OrcaTestApp>` |

Cross-repo: `orca_3.0` uses `OrcaApp`; `orca_3.0_full`, `HPC_backup/orca_3.0_claude` and
`orca_4.0` all use `OrcaTestApp`. The backup is the outlier, following the `orca_3.0` lineage.
`OrcaTestApp` registers the test objects on top of `OrcaApp`, so the binary is a superset. No
physics implication.

---

## 7. Appendix — the 53 byte-identical shared files

Every file below is `cmp`-identical between the two trees. Listed by `src/` path; the matching
`include/` header is identical too.

**InterfaceMaterial (13)** — `ADOrcaBartonBandisContactTractionFastAD`,
`ADOrcaBartonBandisContactTractionFastADHardening`, `ADOrcaBartonBandisFlowRSFContactTraction`,
`ADOrcaCZMComputeMechanicalAperture`,
`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`,
`ADOrcaPeakShelfTailFlowRSFContactTraction`, `ADOrcaRoughnessDamageFracturePermeability`,
`OrcaComputeGlobalTractionSmallStrain`, `OrcaCZMComputeDisplacementJump`,
`OrcaCZMComputeLocalTractionIncrementalBase`, `OrcaCZMInterfacePressure`,
`OrcaCZMRealVectorCartesianComponent`, `OrcaCZMRealVectorScalar`

**Auxkernels (2)** — `OrcaDarcyVelocityComponent`, `OrcaFractureDarcyVelocityComponent`

**Interface kernels (2)** — `OrcaFractureFlowInterfaceKernel`, `OrcaMechInterfaceKernel`

**Kernels (2)** — `OrcaFullySaturatedSinglePhaseDarcySUPGKernel`, `OrcaPoroMechKernel`

**Materials (4)** — `OrcaElasticMechMaterialBase`, `OrcaMechMaterial`,
`OrcaBiotCoefficientMaterial`, `OrcaGravityVectorMaterial`

**Base / mesh / utils (3)** — `OrcaApp`, `OrcaFaultInterface3DGenerator`, `OrcaCZMTools`

Notably `ADOrcaBartonBandisContactTractionFastAD.C` — carrying the v27 dilation-solver cure
(damped 50-iteration loop with residual-halving acceptance) — is **identical** in both trees.
The Barton-Bandis core is fully in sync.

---

## 8. What to do about it

| # | Item | Priority |
|---|---|---|
| 1 | Decide the fate of the stale split pair — port the Biot fix, or delete the kernels and move `67_11` base onto `kernel_SV` | high |
| 2 | Fix the contradictory `biot_modulus_qp` comment in the combined kernel | low, trivial |
| 3 | Resolve `biot_coefficient = 1e-12` in SWS3/SWT1/SWT2, then decide whether the clamp is still needed | high |
| 4 | Confirm the `SinglePhaseFluidProperties` removal is permanent | low |
| 5 | No action on Groups C and D | — |

Tracked as N1–N5 in [`TODO.md`](TODO.md).
