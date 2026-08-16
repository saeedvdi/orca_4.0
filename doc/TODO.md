# orca_4.0 — TODO

**Last updated:** 2026-08-15
**Repo:** `/media/geomechanics/Data4TB/projects/orca_4.0`, branch `orca_v2`

`orca_4.0` is the consolidation repo. It supersedes `orca_3.0` (R&D) and `orca_3.0_full`
(previous "final"/paper repo, branch `orca_edit_v27`). Deck set: **17 decks** across
SWS3 (3), SWS4 (10), SWT1 (2), SWT2 (2).

Status key: **OPEN** · **IN PROGRESS** · **BLOCKED** · **DONE** · **STALE**

---

## A. Blocking the paper

### A1. SW-S3 / SW-S4 non-convergence at the slip / arrest event — **IN PROGRESS**
The long-running thread. SW-S4 is resolved by the v27 dilation cure in
`ADOrcaBartonBandisContactTractionFastAD.C` (damped 50-iteration closure solve with
residual-halving acceptance); that file is identical in `orca_4.0`, `orca_3.0_full` and the
HPC backup, so the fix is in place everywhere.

**SW-S3 is not resolved and fails differently** — see A2. Everything in §D is queued behind
this item.

*Verification in flight:* three v27 SW-S4 runs in `orca_3.0_full` toward `end_time = 3500`
(`68_02` bbfast, `68_02` kernelSV, `67_11` mc). Zero convergence exceptions so far. Report due
when all three finish.

### A2. Diagnose SW-S3's distinct failure mode — **OPEN**
SW-S3 does not fail the way SW-S4 did, so the v27 dilation cure does not transfer. Needs its
own root-cause pass before A1 can close.

### A3. Correct the slip-onset strength envelopes — **OPEN**
Onset timing still misses the digitised targets. Related lever: `fault_pressure_coefficient`
(see the 2026-07 SW-S3 verification notes).

### A4. Make the flow measurement mesh-independent — **OPEN**
Flow-rate postprocessing still carries mesh dependence. The 132× measurement bug was fixed on
2026-08-06; the residual mesh sensitivity is a separate, still-open problem.

---

## B. Arising from the source comparison (2026-08-15)

Full analysis in [`SOURCE_COMPARISON.md`](SOURCE_COMPARISON.md). Comparison target:
`/media/geomechanics/Data4TB/projects/HPC_backup/orca_3.0_claude_edits`.

### N1. Decide the fate of the stale split mass-balance pair — **OPEN, high**
`OrcaSinglePhaseMassTimeDerivativeKernel` and
`OrcaSinglePhaseMassVolumetricExpansionKernel` in `orca_4.0` are the original 25 Jun 2026
versions. They drop the grain-compressibility storage `(α − φ)/K_s` and use porosity φ where
the Biot coefficient α belongs — together making the consolidation coefficient wrong by `α/φ`
(3.33× too fast at α = 1, φ = 0.3 on Terzaghi).

16 of 17 decks are on the correct combined `kernel_SV` and are unaffected. **One deck is not:**
`SWS4/67_11_sw4_mc_dS0p15_s28_w12_m0.i`, which exists as the split-pair control against
`67_11_…_kernel_SV.i`. As it stands that control differs from its counterpart in *physics*,
not just kernel packaging, which is not what a control is for.

Three ways out:
1. **Port the fix** from the backup. Requires the `one_over_biot_modulus_qp` property, which
   `orca_4.0` does not declare — so `OrcaTHMaterial` must change too (couples to N4).
2. **Delete both kernels** and move `67_11` base onto `kernel_SV`. Loses the split/combined
   comparison entirely.
3. **Keep as-is** and document `67_11` base as a legacy-physics reference, not a control.

Recommendation: (1) if the split/combined comparison still has to appear in the paper,
otherwise (2).

### N2. Fix the contradictory comment in the combined kernel — **OPEN, trivial**
`src/kernels/MassBalanceKernel/OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel.C:41`
says *"interpret biot_modulus_qp as (1/M)"*. `OrcaTHMaterial` stores **M**. The arithmetic is
correct (`dpdt * 1/_biot_modulus[_qp]`) and the comment 50 lines below is correct — only line
41 is wrong. Delete it before anyone "fixes" the working code to match it.

### N3. Resolve `biot_coefficient = 1e-12` in SWS3 / SWT1 / SWT2 — **OPEN, high**
Eight decks set `biot_coefficient = 1e-12` with `initial_porosity = 0.001`, i.e. **α ≪ φ**,
which is not physical: Biot's coefficient cannot be below porosity. Consequences:

- The grain term `(1 − α)(α − φ)/K_d` goes **negative**. It does not make the problem ill-posed
  here only because `φ/K_f` dominates.
- The backup clamps that term at zero; `orca_4.0` does not. The two therefore compute
  different storage: **M is 7.40 % higher in SWS3 and 8.36 % higher in SWT1/SWT2** than the
  clamped formulation gives. SWS4 (α = 0.6) is unaffected.

Fix the parameterisation first — the clamp only masks it. Then decide whether the clamp is
still worth porting as a guard against a recurrence.

### N4. Confirm the `SinglePhaseFluidProperties` removal is permanent — **OPEN, low**
`orca_4.0`'s `OrcaTHMaterial` deletes external fluid-properties UserObject support;
`fluid_properties_model`, `fp` and `fluid_thermal_expansion_model` are deprecated params that
hard-error unless set to `user`. All 17 decks set `user`, so nothing breaks — but this is a
real capability reduction versus `orca_3.0_full`, and it is what makes the two
`OrcaTHMaterial` versions unmergeable. Confirm it is intended before anyone tries to merge.

### N5. Groups C and D — **no action**
- *State-dependent α* in `OrcaCZMFluidPressureInterfaceKernel`: present in the backup (branch
  `feature/state-dependent-fault-pressure-coefficient`), absent from `orca_4.0`. This matches
  the deliberate 2026-08-14 revert. orca_4.0 is correct as-is.
- *`src/main.C`* instantiates `OrcaTestApp` (backup uses `OrcaApp`). `OrcaTestApp` is a
  superset; no physics implication.

---

## C. Housekeeping

### H1. Commit v26 and v27 work in `orca_3.0_full` — **OPEN**
That repo still has uncommitted v26/v27 changes on `orca_edit_v27`.

### H2. Report the v27 three-way comparison — **BLOCKED on the runs finishing**
Once the three SW-S4 runs reach `end_time = 3500`, report: per-deck run health (steps, t_end,
dt collapse, exception count); v27 vs v26-stalled vs pre-2.3 baseline; end-state slip and
dilation against the Table-2 targets (0.0794 mm slip, −0.0314 mm dilation).

### H3. Re-run SWS4_MC mesh3 LU retry with more memory — **OPEN**

### H4. Explain the SWT2_BBFast 800 s LU regression — **OPEN**

---

## D. Queued production runs

### D1. Launch the queued decks — **BLOCKED on A1/A2**
17 decks are validated (`--check-input` 17/17; runtime smoke 4/4 at 4 ranks) and each has a
SLURM script targeting
`/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/<SAMPLE>/`
with 32 ranks and a 12 h wall limit. Held until the SW-S3 convergence question is settled, so
the batch is not spent on decks that will stall at the slip event.

---

## E. Closed / superseded

| item | resolution |
|---|---|
| Extend state-dependent α to SW-S3/T1/T2 | **STALE** — the feature was reverted 2026-08-14; see N5 |
| Bring missing decks + meshes into orca_4.0 | DONE — 9 → 17 decks |
| Fix broken `mesh_file` paths in 4 decks | DONE — verified identical by md5 |
| Add `fracture_surface_output` mesh generator | DONE — all 17 |
| Apply the standard AuxVariables/AuxKernels block | DONE — all 17, minus 3 diagnostics on the Bakhtar pair |
| Restore combined mass kernel in 68_02 / 68_03 | DONE |
| Generate SLURM `.sh` for every deck | DONE — 17 |
| Validate all decks with `--check-input` | DONE — 17/17 |
| Port Bakhtar material and verify on SW-S4 | DONE |
| Barton-Bandis physics correctness audit | DONE |
| Refit SW-T1/SW-T2 normal-closure constants | DONE |
| Loading-frame stiffness, strength envelopes, preload gate, min-dt | DONE |
