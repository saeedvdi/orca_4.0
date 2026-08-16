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

---

## H. Mesh-size-3 deck set — 2026-08-15

Built the size-3 variant of all 18 `kernel_SV` decks. They are **HPC decks**; the reasoning
for that is H3 and it is not a preference, it is an arithmetic result.

### H1. What was generated
`<base>_kernel_SV*_mesh3.i` + matching `.sh` for every kernel_SV deck: SWS4 ×8, SWS3 ×4,
SWT1 ×3, SWT2 ×3. Each carries `mesh_file` repointed to the sample's size-3 mesh, output
file bases repointed to its own name, and a dated provenance header. The mesh-5 parents are
untouched. Generator: `scratchpad/mk_mesh3.py`.

Meshes copied into `orca_4.0` from `orca_3.0_full/Examples/YeGhasemmi2018/Final/mesh/`,
whose size-5 files were first confirmed **byte-identical** to the ones already in `orca_4.0`
(md5, all three samples) — so the size-3 siblings are the correct pairing, not a lookalike.

| sample | nodes 5 → 3 | elements 5 → 3 | ratio |
|---|---|---|---|
| SWS4 | 9,597 → 92,919 | 8,640 → 88,504 | 10.24× |
| SWS3 | 11,425 → 104,781 | 10,368 → 100,048 | 9.65× |
| SWT1 | 11,861 → 122,475 | 10,752 → 117,232 | 10.90× |
| SWT2 | 11,861 → 122,475 | 10,752 → 117,232 | 10.90× |

Size 3 is the **finer** mesh, ~10× the elements.

### H2. Two defects the mesh change exposed — both fixed
**Source nodes.** Deck source coordinates are pinned to *mesh-5* nodes and are not
transferable. Re-pinned against each size-3 mesh with `scratchpad/repin_source_coords.py`
(same method as the standing `snap_source_coords.py`: keep the deck's x/y, recompute z from
the mesh's own least-squares fracture plane, snap to the nearest `fracture_interface` node).
It acts only on `*_mesh3.i`, so no running deck was touched.

Result: SWS3, SWS4, SWT1 were "pin only" — same node either way, no physics change. **All
three SWT2 decks were selecting a BULK node** and would have injected into the matrix with
no error raised, fluid reaching the fracture only through the 5e-19 m² matrix permeability.
Moved 0.988 mm onto the fracture. This is the failure mode the standing rule exists for, and
it reproduced on the first mesh change since.

**Nodeset naming.** The SWS4 size-5 mesh is the only one of the set naming its nodesets
`top`/`bottom`/`sides`; every other mesh, including SWS4 size-3, uses `*_nodeset`. All eight
SWS4 mesh-3 decks aborted in `SideSetsFromNodeSetsGenerator`. Fixed by renaming
`nodesets_to_convert` and the 64 dependent `boundary =` references (72 lines across 8 decks)
to match SWS3's convention.

### H3. These cannot run locally — the solver is direct
`[Preconditioning]` is `-pc_type lu` with MUMPS. For a 3D problem a ~10× DOF increase raises
direct-factor memory by roughly 10^(4/3) ≈ 20×, far faster than the element count.

- Measured mesh-5 footprint: ~0.37 GB/rank, ~3.3 GB per 8-rank job.
- Projected mesh-3: ~70 GB per 8-rank job.
- **This machine has 30 GB of RAM total.**

Independent corroboration from the project's own history: the existing mesh-3 SLURM scripts
request **64 GB** against 32 GB for mesh 5, and task #21 exists *because a mesh-3 LU run ran
out of memory even at that*. So one mesh-3 deck needs more than twice this machine's entire
RAM, at any concurrency. Wall clock is the lesser problem and still severe: the mesh-5 SWS3
baseline is running at ~10 s simulated per wall minute, so 4802 s takes ~8 h; ~10× the work
per step puts a single mesh-3 deck in the multi-day range.

Generated `.sh` therefore request `--mem=180G`, `--time=48:00:00`, 32 ranks.

### H4. Validation
`--check-input`: **18/18 pass**. `--mesh-only` generation: 4/4 samples. Source-node audit on
the generated meshes: `source_in` and `source_out` each resolve to exactly **2 nodes** (the
two faces of the split), **all** in `fracture_interface`, for all four samples — the
authoritative check.

Not yet done: no mesh-3 deck has been *run*. H3 is why.

---

## I. v27 SW-S4 validation closed — 2026-08-15

All three local v27 SW-S4 runs reached t=3500 with **zero nonlinear exceptions** (2335 steps
each). Full write-up: `orca_3.0_full/doc/v27_validation_SWS4_2026-08-15.md` (commit `f388f77`
on `orca_edit_v27`).

Two headline points that bear on work here:

1. **Two of the three runs were the same deck** — `68_02_..._m0.i` and `68_02_..._m0_kernel_SV.i`
   differ by six lines, all output paths; both already carry the combined kernel. Verified
   numerically (median relative difference 1.7e-13 across 86 columns × 2335 rows). So that
   batch contains no split-vs-combined comparison, and A1 is closed for SW-S4 by the exception
   count, not by a kernel comparison.

2. **Scope is SW-S4 only.** SW-S3/SWT1/SWT2 are untouched by this result — which is exactly
   what the section D campaign is for. See G2.

Naming lesson for future batches: a `_kernel_SV` suffix on a deck whose parent is already
kernel_SV conveys nothing and cost ~5 h on 8 cores here. Check the parent before suffixing.

## J. Biot coefficient A/B campaign — 2026-08-15

Six full-length mesh-5 runs, local, 4 concurrent at 8 ranks. Three A/B pairs testing
`biot_coefficient` 1e-12 (baseline) vs 0.6 (fixed) on SW-S3, SW-T1 and SW-T2. This is
task N3 / #51 being answered with runs rather than argument.

Full write-up: `doc/biot_alpha_study_2026-08-15.md`.

**J1. The value is not new.** SW-S4 already carries `biot_coefficient = 0.6`; only the other
three carry 1e-12. The campaign asks whether to bring them to the value SW-S4 was validated
with, not whether to invent one.

**J2. Deck integrity verified.** Each pair differs in exactly three things — the
`biot_coefficient` line, the header, and the three `*_file_base` paths. Nothing else.

**J3. The unphysicality is measurable, and worse than "decoupled".** `OrcaTHMaterial` builds
`1/M = (1-α)(α-φ)/K_d + φ/K_f`. Going 1e-12 -> 0.6 raises the storage compliance by 18.8x
(SW-S3) / 21.1x (SW-T1, SW-T2). And because α < φ, the grain-compressibility term at 1e-12
is **negative** — it subtracts 6.9 % of the fluid storage rather than adding to it. Net 1/M
stays positive only because the fluid term dominates.

Consequence for reading the results: this is a **recalibration**. Onset timing and the
strength envelopes were fitted at α=1e-12, so a timing shift in arm B is expected, not a bug.

**J4. New tool — `scripts/table2_gate.py`** (commit `0cbc441`). Scores any run against
Ye & Ghassemi Table 2 for all four samples, replacing four disagreeing per-sample fragments
(one script + three notebook TABLE2 blocks). Scores the five independent observables only
(Q, σ'_n, τ, d_n, d_s); a_h and k are derived from Q and excluded.

Two stage-detection bugs found and fixed, both landing on stage 6 — the slip event:
`np.argmax` returns the first peak index, so the staircase decks were sampling the 28 MPa
hold at its **start** (SW-T1: t=1824 not 1955); and sharing one tolerance between target
matching and plateau membership put SW-S4 stage 6 67 s past the hold. Plateau membership now
uses a separate 1 kPa flatness tolerance. Verified: 11 monotonic stages on all four decks,
stage 6 exactly on the peak plateau in each.

Validated against the three completed v27 SW-S4 runs — 11/11 stages, and it independently
reproduces the v27 result that MC and BBFast are identical through stage 4 and diverge only
from stage 5 onward.

**J5. Mesh 5 only.** The mesh-3 set (§H) is not run here; the user is running it separately.

---

## K. First regression test suite — 2026-08-16

Branch `orca_v4`, commit `ba43f88`. Answers the "is the source validated?" question with
something other than "the physics runs looked right": before this the app had **no test
coverage at all** — `test/tests/` held only MOOSE's stock `simple_diffusion`, and nothing
referenced any Orca kernel or material. The combined mass kernel that all 32 production
mesh-5 decks depend on was guarded by nothing.

**K1. A real defect was found, in the comments rather than the arithmetic.**
`OrcaTHMaterial::computeBiotModulus` stores **M**, not `1/M` (`OrcaTHMaterial.C:638`,
`M_new = 1.0/denom`). Two comments in the consuming kernel asserted the opposite — line 41
*"interpret biot_modulus_qp as (1/M)"* and line 91 *"if it stores (1/M), use
multiplication"* — while the code read `dpdt * 1/_biot_modulus[_qp]`, which is
`(dpdt*1)/M` by left-associativity, i.e. a division, i.e. correct.

So the physics was right and the documentation was wrong in the exact direction that
invites a destructive fix: converting it to a true multiplication is wrong by a factor of
`M^2` ≈ 6e22. Comments corrected; the expression rewritten as an explicit `dpdt / M`, which
is bit-identical (multiplying by 1.0 is exact in IEEE-754) and changes no result.

**K2. `test/tests/materials/biot_modulus` — pins the storage formula.** Four cases, checked
against values derived by hand from the SW-T1 constants rather than against whatever the
code printed:

| case | α | M | note |
|---|---|---|---|
| `physical_alpha` | 0.6 | 2.4562999362e11 | agrees to 8 sig figs |
| `alpha_unphysical` | 1e-12 | 5.1832204827e12 | 21x larger |
| `alpha_eq_porosity` | φ = 0.001 | 4.7835616438e12 | grain term vanishes, `(α−φ)=0` |
| `alpha_unity` | 1.0 | 4.7835616438e12 | grain term vanishes, `(1−α)=0` |

The two boundary cases reach `M = K_f/φ` from opposite factors, so they pin both halves of
the product independently.

**K3. `test/tests/kernels/mass_storage` — pins the kernel against a closed form.** One
element, no Darcy kernel, no BCs, so the discrete problem collapses to the scalar ODE
`(1/M) dp/dt = q` with solution `p(t) = M q t`. Measured `p(10) = 2456299.9362447` Pa
against the exact `2.4562999362e6` — **12 significant figures**. This is what makes K1
uncatchable-by-accident from now on: a flipped operator moves the answer by `M^2`, not by a
few percent.

**K4. One non-obvious setup detail, worth remembering for any future minimal deck.** With
storage as the *only* term in the equation, the Jacobian diagonal is `(1/M)/dt · V ≈ 2e-14`,
and PETSc reported a **false** non-convergence at `dt ≥ 0.25` — even though a single Newton
step had already driven `|R|` from 3.5e-12 to 6.1e-28. `automatic_scaling = true` fixes it.
A production deck's Darcy term dominates this and hides the problem entirely, so it only
shows up in isolation tests.

**K5. Result.** `./run_tests` → **7 passed, 0 skipped, 0 failed** (was 1).

**K6. Deliberately deferred: the full rebuild.** The modified translation unit was compiled
in isolation (`make build/unity_src/kernels_Unity...opt.lo`) instead of a full `make`,
because the six-deck A/B campaign is mid-flight against the current `orca-opt` and
relinking would have left the queued SW-T2 pair running a different build from its partner.
`orca-opt` is byte-unchanged. **A full rebuild and re-run of the suite is due once the
campaign drains** — the change is comments plus a bit-identical expression, so no result
should move, but that is an expectation until it is checked.

**K7. What this still does not cover.** These are unit-level tests of the storage term.
There is no coverage of the Darcy kernels, the CZM/Barton-Bandis path, or any coupled
poroelastic response — a 1D Terzaghi consolidation case against the analytical solution is
the obvious next step and would be the first genuinely *coupled* verification in the repo.

---

## L. Terzaghi consolidation — first coupled verification — 2026-08-16

Branch `orca_v4`, commit `7596413`. Extends §K from unit-level tests of the storage term to
a verification of the **whole HM path** — `OrcaPoroMechKernel` + Darcy + the combined mass
kernel in `HydroMechanical` mode — against a closed-form solution.

**L1. Setup.** Terzaghi 1D consolidation, Verruijt *Theory and Problems of Poroelasticity*
(TU Delft 2013) §2.2. Parameters deliberately identical to MOOSE's own `porous_flow`
`terzaghi.i`, so any discrepancy is Orca's and not the problem's.

**L2. An algebraic confirmation, free of any numerics.** Verruijt's storativity
`S = φ/K_f + (α−φ)(1−α)/K` is *identical* to Orca's `1/M` in `computeBiotModulus`. Orca's
Biot modulus **is** the Verruijt storativity. That independently confirms the formula §K2
pins numerically.

**L3. Result.** Against the analytic series (`scripts/terzaghi_analytic.py`, committed so
the check is repeatable):

| probe | z | max rel. error |
|---|---|---|
| p0 | 0 | 0.20 % |
| p2 | 2 | 0.19 % |
| p5 | 5 | 0.34 % |
| p8 | 8 | 1.63 % ← adjacent to the drained face |
| degree of consolidation U | — | 0.25 % |
| final settlement | — | 1.236270 vs 1.236439 exact (**0.014 %**) |

**L4. A trap worth remembering — apparent non-convergence that was pure time-stepping.**
The first runs showed **5.1 % error that did not improve under 8× mesh refinement**, which
reads exactly like a physics defect. It was not. Refining the mesh also refined the
*initial* dt, but with `growth_factor = 1.4` and no cap, dt still grew to ~2.5 by t=10 in
every run. Backward Euler decays too *slowly* at large `λ·dt` — amplification `1/(1+λdt)`
against `exp(−λdt)`.

The diagnostic that settled it: the numeric/analytic ratio was **the same at z=0 and z=5**
(1.860 at t=10). A uniform multiplicative offset across depths means the spatial mode shape
is right and only the decay rate is wrong — which points at the integrator, not the
operator. With dt capped, convergence is clean and first-order:

| nz | dtmax | worst error |
|---|---|---|
| 20 | 0.0125 | 1.02 % |
| 40 | 0.00625 | 0.53 % |
| 80 | 0.003125 | 0.28 % |

`dtmax` is now set in the deck with a comment saying why it is not optional.

**L5. A silent-coupling bug, found because the analytic solution existed.**
`computeVolumetricStrain()` was called **only** from `computeIncrementalStrain()`. On the
`strain_model = total` path it was never called, so `vol_strain_rate` kept the 0.0 from
`initQpStatefulProperties`, and any `HydroMechanical` mass kernel lost its `α·div(du/dt)`
term entirely.

It fails silently: the first Terzaghi run completed happily with **zero pore pressure
everywhere** and settlement jumping straight to the fully-*drained* 1.25 — a self-consistent,
plausible, wrong answer. With no analytic reference there is no signal at all. This is the
clearest argument in the repo for why verification tests are worth the effort.

**Scope: no production result is affected.** All 33 mesh-5 decks use
`strain_model = incremental`, as does the in-flight campaign. This is a trap for future
work, not a correction to past results.

**L6. Honest status of the fix.** `./run_tests` → **8 passed, 0 failed** (1 → 7 → 8). The
Terzaghi test is fully verified. The `OrcaMechMaterial` fix is **compile-checked only**, not
runtime-verified: `orca-opt` was deliberately not relinked (see §K6 — the campaign is
mid-flight against it). So the passing suite exercises the *old* binary, in which the
total-strain path is still broken — it simply is not reached, since everything uses
incremental. **Due once the campaign drains:** rebuild, re-run the suite, and add a
`total_strain` case asserting the two strain models agree. Until then the fix is plausible,
not proven.

---

## M. Guard against α < φ — 2026-08-16

Branch `orca_v4`, commit `e4230e5`. Closes the loop on **why** N3/#51 survived: nothing told
anyone. `OrcaBiotCoefficientMaterial` range-checks only `0 < α ≤ 1`, which 1e-12 passes
comfortably; `OrcaTHMaterial` then accepted it silently. `computeBiotModulus` now emits a
one-time warning naming both values and the sign consequence.

**Warning, not error, on purpose.** The value is a legitimate thing to explore deliberately —
the A/B campaign is doing exactly that — and erroring would break decks mid-study. Loud
enough to prevent accidental adoption, quiet enough not to obstruct deliberate use.

The two tests that drive α below φ on purpose now set `allow_warnings = true` (testroot sets
it false globally); emitting the warning there is correct behaviour.

**Status: compile-checked only**, same caveat as §L6 — `orca-opt` is still not relinked while
the campaign is in flight, so the passing suite did not exercise this path. Verification is
folded into the same post-campaign rebuild as the total-strain fix (task #59).

## N. Thermal storage term — the kernel's last untested term — 2026-08-16

Branch `orca_v4`. `test/tests/kernels/thermal_storage`, 2 cases, both passing. Suite is now
**10 tests**.

The combined mass kernel assembles three terms. §K pinned `(1/M) dp/dt`, §L pinned
`α·div(du/dt)` through Terzaghi. `−α_T dT/dt` was the one nobody had ever exercised — no test
touched it, and **no production deck touches it either**: nothing in `Examples/` couples
`temperature` to `OrcaTHMaterial`, so the entire thermal path has been shipping unexecuted.

### N1. The closed form

One element, ThermoHydro, no Darcy kernel, no BCs, no mechanics. Temperature is a nonlinear
variable driven by `ADTimeDerivative` + `BodyForce`, so the uniform field `T = T0 + r·t` solves
the FE system exactly and `dT/dt = r` to machine precision. Pressure then obeys

```
(1/M) dp/dt − α_T r = 0     ⟹     p(t) = M α_T r t
```

With the SW-T1 constants at α = 0.6 and the `computed` model,
α_T = (0.6 − 0.001)·2.4e-5 + 0.001·2.1e-4 = **1.4586e-5** 1/K, M = 2.4562999362e11 Pa,
r = 1 K/s. Measured p(10) = 35827590.870065 Pa against 35827590.869413 — **11 significant
figures**, the residual difference being the truncation in the hand-supplied M, not the solve.

The **sign** is asserted, not just the magnitude: the term enters as −α_T dT/dt, so heating
pressurises. A flipped sign produces an equally smooth run that cools and depressurises.

The `alpha_eff_user` case sets `effective_thermal_expansion_coeff = 2.0e-5`, deliberately
different from the computed 1.4586e-5, so it fails if the user model ever falls through to the
mixture formula.

### N2. Defect: the lagged α_T is never seeded — thermal coupling silently vanishes

`effective_thermal_expansion_model = constant` read

```cpp
_alpha_eff_T[_qp] = _alpha_eff_T_old[_qp];
```

unconditionally. `initQpStatefulProperties()` routes through `computeQpProperties()` and hence
through this same function, so at t = 0 it returns the **zero-initialised** old property. That
zero becomes the old value for step 1, and so on. α_T is pinned at 0 for the entire run.

Confirmed against the shipped binary, not inferred:

| model | α_T | p, every step | closed form |
|---|---|---|---|
| `constant` | **0.0** | **0.0** | 3.582759e6 Pa/step |
| `user` | 1.4586e-5 | matches | matches |
| `computed` | 1.4586e-5 | matches | matches |

The run **converges cleanly the whole way**. No error, no warning, no stall — the thermal
coupling term is simply deleted, and the answer looks like a legitimate isothermal simulation.

This is the same failure family as §L's `vol_strain_rate` bug and the same reason it survived:
a stateful property whose "hold the previous value" path is also the path taken on the very
first call, so it holds a value that was never computed.

**Fix**: compute the mixture formula into a local unconditionally, then seed from it at
`_t_step == 0` and lag thereafter. The three models keep their documented meanings.

**No production deck affected** — the default is `computed`, and no deck sets the parameter or
couples temperature at all.

### N3. Conditioning note, recorded because it points the opposite way from §K

`mass_storage` **needs** `automatic_scaling`; this test **must not have it**. There, storage was
the only equation and the whole residual sat at 1e-14. Here the temperature equation contributes
an O(1) row, so |R| starts at 0.35 and one Newton step reaches 5e-17. Turning scaling on
amplifies the pressure row — whose two terms cancel to round-off *by construction* — and pins
|R| at a 6e-9 floor no tolerance can reach; the solve then reports DIVERGED_LINE_SEARCH on an
answer that is exact. Both settings are commented in place with the reasoning, because the
naive rule "always enable automatic_scaling for poromechanics" is wrong in one of these two
neighbouring tests.

### N4. Status

Test cases N1 pass against the current binary. The **N2 fix is compile-checked only** —
`orca-opt` is still not relinked while the campaign runs, so the third case, `alpha_eff_lagged`,
is written out in `tests` as a comment rather than registered, to avoid committing a red suite.
It lands with the same post-campaign rebuild as §L6 and §M (task #59). Tasks #61, #62.

## O. Darcy flux verified against erfc — 2026-08-16

Branch `orca_v4`. `test/tests/verification/pressure_diffusion`, 1 case, plus
`scripts/pressure_diffusion_analytic.py`. Suite is now **11 tests**.

`OrcaFullySaturatedSinglePhaseDarcySUPGKernel` had no test of any kind. It is the kernel
every production deck routes its flow through, and the one whose convention — `K/mu` with
density as a separate switch — is easiest to get wrong in a way that still looks right.

### O1. The closed form

Rigid skeleton (`coupling_type = Hydro`, no mechanics), so the storage + Darcy pair reduces to
linear diffusion with

```
c = M k / mu = 1.2256985710e-4 m²/s
```

Step inlet on a 4 m bar, 1000 s: `p(x,t) = p0 erfc(x / 2√(ct))`. Diffusion length reaches
0.70 m, so erfc at the far end is 6.5e-16 and the half-space solution applies to well past the
precision of the comparison. A `p_far_end` probe asserts that directly — if it ever lifts off
round-off, every other number in the file is suspect.

Four probes at x = 0.10/0.25/0.50/1.00 m put η = x/(2√(ct)) at 0.14/0.36/0.71/1.43, so erfc
runs 0.84 → 0.04 and the comparison exercises the whole curve rather than one convenient point.

**Worst error 0.66% of p0** across four probes and four report times; **0.06% at the final
time**. The 0.66% is at t = 100 s next to the inlet, where the step is still sharp.

### O2. Convergence — halving h and dt together, error at t = 1000 s as % of p0

| probe | nx=200 dt=5 | nx=400 dt=2.5 | nx=800 dt=1.25 | ratio |
|---|---|---|---|---|
| x=0.10 | −0.0282 | −0.0144 | −0.0072 | 1.97, 1.98 |
| x=0.25 | −0.0519 | −0.0300 | −0.0151 | 1.73, 1.99 |
| x=0.50 | −0.0599 | −0.0299 | −0.0150 | 2.00, 2.00 |
| x=1.00 | +0.0097 | +0.0060 | +0.0033 | 1.63, 1.83 |

Clean first order — implicit Euler in dt dominating O(h²) in space. Run because §L's
convergence study caught a spurious "physics defect" that was an uncapped `growth_factor`; the
same check here says the residual error is discretisation and nothing else.

The load-bearing point is that it converges **to** the erfc curve built with c = M k/mu. A
mobility with mu on the wrong side converges just as smoothly to a *different* curve.

### O3. Error normalisation — a reporting trap worth recording

The first version of the script divided by the local analytic value and reported **9584%** error
at x = 1.00, t = 100 s. That is an absolute discrepancy of 0.016 Pa against a 1e6 Pa step: deep
in the erfc tail the analytic value falls below a Pascal while the FE solution keeps a small
non-zero foot. The script now normalises by p0 and prints the local ratio only above 0.1% of p0,
marking the rest `tail`. Same trap set for `CSVDiff`, handled with `abs_zero = 1e-6`.

### O4. Remaining kernel coverage

`use_supg` is **still untested** — every production deck leaves it at the default `false`, and
the base kernel deliberately does not call `supgStabilization` (see the comment at
`computeQpResidual`). The stabilisation path is reachable only from derived advection kernels.
Worth a test if anything ever turns it on; not worth one now.
