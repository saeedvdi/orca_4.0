# orca_4.0 — TODO

**Last updated:** 2026-08-15
**Repo:** `/media/geomechanics/Data4TB/projects/orca_4.0`, branch `orca_v2`

`orca_4.0` is the consolidation repo. It supersedes `orca_3.0` (R&D) and `orca_3.0_full`
(previous "final"/paper repo, branch `orca_edit_v27`).

**Deck set: 33 input files.** 15 original decks, left untouched as the reference
configuration, plus 18 generated `*_kernel_SV*` decks (15 one-per-original, 3 `_biot0p6`
variants). Per sample: SWS3 3+4, SWS4 10+8, SWT1 2+3, SWT2 2+3.

Status key: **OPEN** · **IN PROGRESS** · **BLOCKED** · **DONE** · **STALE**

**Agreed plan as of 2026-08-15:** hold everything until the three v27 SW-S4 runs in
`orca_3.0_full` finish (see H2), then test the three `_biot0p6` decks. See §F for what has
been done and §G for the standing caveats on that plan.

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

### N4. `SinglePhaseFluidProperties` removal — **CONFIRMED PERMANENT (2026-08-15)**
`orca_4.0`'s `OrcaTHMaterial` deletes external fluid-properties UserObject support;
`fluid_properties_model`, `fp` and `fluid_thermal_expansion_model` are deprecated params that
hard-error unless set to `user`. All 17 decks set `user`.

Confirmed by the author as a permanent design decision, not a temporary regression.
`OrcaTHMaterial` is self-contained by intent: fluid properties come from its own input
parameters and nowhere else. **Consequence:** the `orca_4.0` and
`HPC_backup/orca_3.0_claude_edits` versions of `OrcaTHMaterial` are permanently unmergeable —
any future port from that backup (e.g. N1's `one_over_biot_modulus_qp`) must be applied as a
hand-picked hunk, never a file copy or a merge.

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

---

## F. Work log — 2026-08-15

Three commits on `orca_v2`. Everything below is verified, not assumed.

### F1. `7fe8589` — audit, deck completion, normalisation

**Source audit of the new repo.** `src/` (51 `.C`) and `include/` (51 `.h`) confirmed
byte-identical to `orca_3.0_full` on `orca_edit_v27` except `OrcaTHMaterial.{C,h}`. The v27
dilation cure is present in `ADOrcaBartonBandisContactTractionFastAD.C` (damped 50-iteration
loop, residual-halving acceptance). Binary `orca-opt` confirmed current — `make -n` queued
only MOOSE framework unity files.

**Deck set 9 → 17.** Added SWS3 (3), SWT1 (2), SWT2 (2) and `SWS4/68_01`, each a
self-contained sample directory with its own `mesh/`, `logs/` and `results_*/`.

**Two defects fixed.**
- Four SWS4 decks pointed at `../mesh/ye2018_sw_s4_low_mesh.e` — wrong directory *and* wrong
  filename. Repointed to `mesh/ye2018_sw_s4_size5_mesh.e`, verified byte-identical to the
  reference mesh (md5 `88b7a31eef6985d0408dc265bad433d4`).
- All 9 original decks failed `--check-input`. Root cause isolated to an uncommitted
  +515-line working-tree edit that had merged AuxVariables from the `orca_3.0` v4 family
  without the mesh generator they depend on; the committed HEAD version passed.

**The `fracture_surface` block and its five consequences.** Added a
`LowerDBlockFromSidesetGenerator` producing block 900 from the `fracture_interface` sideset.
That block silently widens every previously unrestricted object from
`{top_block, bottom_block}` to the whole mesh, which forced:

| change | why |
|---|---|
| `[Variables]` pinned to `'top_block bottom_block'` | otherwise `disp_*` / `pore_pressure` gain spurious DOFs on the lower-D block; affected element postprocessors pinned back to the bulk for the same reason |
| `kernel_coverage_check = false`, `boundary_restricted_elem_integrity_check = false` | block 900 is output-only; the split-interface lower-D map is orientation-sensitive |
| `extra_tag_vectors = 'mech_reaction mass_reaction'` + `extra_vector_tags` on 4 kernels | `react_pore_pressure_aux` consumes a tag no deck declared |
| 11 CZM output materials appended per deck | `jump_x/y/z`, `traction_x/y/z`, normal/tangent traction and jump are declared by no other material |
| AuxKernel AD-ness resolved **per deck** | 7 properties are `declareADProperty` in the MC interface material and `declareProperty` in the BBFast one, so the same name needs `ADMaterialRealAux` in MC decks and `MaterialRealAux` in BBFast |

The two Bakhtar decks additionally drop `cumulative_dilation`,
`roughness_retention_factor` and `self_propping_aperture` (3 AuxVariables + 3 AuxKernels):
`ADOrcaBartonBandisBakhtarFracturePermeability` declares none of them, verified in source.

**Other.** `68_02` and `68_03` restored to the combined mass kernel. 17 SLURM scripts
generated on the standard template. `.gitignore` extended to whitelist the SWS3/SWT1/SWT2
mesh directories on the same terms as SWS4 (+2.4 MB) — without it those eight decks are
unrunnable from a clone.

**Validation.** `--check-input` 17/17. Runtime smoke at 4 ranks, `end_time = 6`, one deck per
family (SWS4 BBFast kernel_SV, SWS4 MC, SWS3, SWT2): 4/4 reached t=6 and finished. Confirmed
9 representative new aux variables reach the Exodus output.

### F2. `a82a09f` — `SinglePhaseFluidProperties` removal confirmed permanent

Recorded as a design decision, not a regression. Consequence for N1: the two
`OrcaTHMaterial` versions are permanently unmergeable, so any future port from the backup
must be a hand-picked hunk, never a file copy or merge.

### F3. `889aaef` — the kernel_SV deck set

Generated 18 decks (15 one-per-original + 3 `_biot0p6`), 18 SLURM scripts and 4
`run_all.sh`. Originals left byte-identical; the two pre-existing `*_kernel_SV.i` decks were
regenerated in place, since they were generated variants rather than originals.

- **Storage kernel** — all 18 on the combined kernel. Only `67_11` still carried the split
  pair, so this mainly makes the naming honest about what the decks solve.
- **`confining_pressure = 30e6`** on all 18. Affects the 10 SWS4-derived decks; SWS3/SWT1/SWT2
  were already there. See §G1 — this is applied under an explicit caveat.
- **`_biot0p6` variants** for the three samples still at `biot_coefficient = 1e-12`. SWS4 gets
  none: already 0.6.
- **`run_all.sh`** per sample directory, executable, `--dry` supported, skips missing decks.
- **Dated provenance header** in every generated deck naming its parent and enumerating what
  changed, so each deck explains itself without the commit log.

**Validation.** `--check-input` 18/18. Runtime smoke at 4 ranks, `end_time = 6`:
`SWS3/84_01_..._kernel_SV` 9 steps to t=6, and `SWS3/84_01_..._kernel_SV_biot0p6` also 9
steps to t=6 with **zero convergence exceptions** — but at 97.8 s wall against ~20 s, i.e.
roughly **5× the cost per unit simulated time** once the effective-stress coupling is live.
That clears the deck for submission; it says nothing about the slip event, which is far
beyond t=6.

### F4. Source comparison against `HPC_backup/orca_3.0_claude_edits`

Full write-up in [`SOURCE_COMPARISON.md`](SOURCE_COMPARISON.md). Exhaustive `find` + `cmp` +
`diff -u` over every file in `src/` and `include/`. Result: the backup is a strict subset in
file coverage — 62 shared paths (53 byte-identical, 9 differing), 40 files only in
`orca_4.0`, **0 only in the backup**. The 9 differences became N1–N5 in §B.

---

## G. Standing caveats on the current plan

### G1. `confining_pressure = 30e6` was measured worse, and is applied anyway
`confining_pressure` is a **live BC magnitude** — it feeds the `czm_pressure_x` /
`czm_pressure_y` BC function expressions — not just a diagnostic label. The 29.4 → 30.0 MPa
change was tested on `68_02` on 2026-08-14 and moved every Table-2 metric further from target:

| metric | Table 2 | 29.4e6 | 30e6 |
|---|---|---|---|
| slip | 0.0794 mm | 0.0814 (+2.5 %) | 0.0752 (**−5.3 %**) |
| dilation end | −0.0314 mm | −0.0314 (~0 %) | −0.0291 (**−7.3 %**) |
| differential stress | 5.14 MPa | 5.78 (+12.4 %) | 7.12 (**+38.5 %**) |
| shear traction | 2.20 MPa | 2.48 (+12.9 %) | 3.20 (**+45.6 %**) |

Applied on request, with the caveat recorded in every generated header. The calibrated
29.4e6 configuration survives in the untouched parent decks, so nothing is lost — but the
decision should be deliberate rather than by default.

### G2. The v27 runs answer SW-S4, not SW-S3
The three runs in flight are all SW-S4. They close A1 for that sample and settle whether the
v27 dilation cure holds through the full cycle. They carry **no information** about SW-S3,
SW-T1 or SW-T2, which have a different parameterisation (`biot_coefficient = 1e-12` vs 0.6)
and, per A2, a different failure mode. The `_biot0p6` question is untouched by them.

### G3. The `_biot0p6` decks need their α = 1e-12 twins run alongside
No full-length `biot_coefficient = 1e-12` baseline exists for SWS3 — a search of `orca_3.0`
and `orca_3.0_full` found none. Running only the `_biot0p6` version therefore shows that it
ran, not whether it is better. Run the **pairs**, not the three.

### G4. Cost of the local `_biot0p6` test
End times: SWS3 4802, SWT1 3500, SWT2 2852.53 — SWS3 is 37 % longer than SW-S4's 3500. With
the ~5× per-step cost measured in F3, six full-length decks sharing 32 local cores is a
multi-day proposition.

Cheaper split, since the diagnostic and the physics are different questions:
- **Local, truncated** — the convergence question ("does α = 0.6 change behaviour at the slip
  event?") is answered the moment the first exception does or does not appear. Run the pairs
  and stop at the answer; no need for full length.
- **HPC, full length** — the physics comparison against Table 2 needs the complete cycle, and
  32 ranks per deck running in parallel is exactly what the allocation is for.
