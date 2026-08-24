# orca_4.0 — TODO

**Last updated:** 2026-08-24 · **Branch:** `orca_v8` · **Repo:** `/media/geomechanics/Data4TB/projects/orca_4.0`

This is the **active** action list: what was done, why it did not work, and what to do
next. Two things it is not:

* `doc/TODO.md` is the **Ye2018 campaign's** long-form task record (task IDs #2–#113) and
  stays the authority for that manuscript. Only its still-open items are carried forward
  here, in §3.
* `Examples/Kalantar2025/MEMORY.md` is the **full narrative** of the Kalantar validation —
  the paper audit, every constant and its source, every defect and its evidence. This file
  points at it rather than repeating it.

---

## 1. Kalantar 2025 validation — the active thread

### 1.1 What was done

**Round 1** (commit `5123326`, branch `orca_v7`). Three BBFast decks built from the paper
and Table 2, meshed, `--check-input` clean, submitted at 64 ranks.

**Round 2** (commit `353faf3`, branch `orca_v8`). Six defect classes found and fixed:

| | defect | fix |
|---|---|---|
| a | `PointValue` bulk gauges at the **Ye2018 parent's** half-height | repointed to `core_height/2 ± 45 mm` |
| b | OG-SC's borehole readouts at **SW-S3's** coordinates | repointed to its own `source_in`/`source_out` |
| c | the whole paper-frame reporting chain was Ye2018's — σ₃ = 30 not 33, parent's sin²θ and sinθcosθ, and **no τ reporter at all on two decks** | σ₃ substituted, angles computed per specimen, reporter inserted |
| d | `axial_pres_final` never gated — delivered σ₁ = 69.4 against a 94.65 MPa target | series-spring solve, `C_ax = 0.8987·L/E` |
| e | aperture law entirely SW-T2's, sitting 7 % above a hard `min_hydraulic_aperture` floor all run | anchored on Table 2 stage 1 |
| f | envelope 13.2 % too strong; slip-weakening residual **above** φ_r (the law strengthened with slip); OG-SC's `D_c` above its own burst cap; 26° dilation on a JRC-4.23 saw-cut | all four derived from Table 2 / Barton |

Plus two permanent pre-submission assertions in `scripts/build_110_kalantar_decks.py` —
every `PointValue` tested against its own mesh's bounding box, and the realised stick-slip
class `D_c < Δτ/k_eff` asserted against what the paper observed — and a validation notebook
that refuses to score a truncated run.

**Round 2 ran.** Results downloaded 2026-08-24 10:52 into `Examples/Kalantar2025/*/results_csv_hpc/`.

### 1.2 Why it did not work

**Two of the fixes provably worked.** The reporting frame is now exact — `θ_eff` recovers
**29.00° at every one of the nine hold stages** (it was 21.9°). The loading gate lands
stage 1 within **0.6 % on τ and 0.2 % on σ'ₙ**. Those two questions are closed.

**The run still fails, and the fixes are what let us see why: the fracture does not slip.**

| | measured | model |
|---|---|---|
| τ across the nine stages | falls 26.14 → 18.97 (**7.17 MPa**) | falls 25.98 → 25.23 (**0.75 MPa**) |
| slip at the end | 0.0480 mm | **0.0049 mm — 10× too little** |
| a_h loss | 1.15 µm | 0.15 µm |

The a_h and Q errors are *downstream* of this, not independent: `slip_damage_scale` is
driven by slip, and there is no slip.

**The mechanism, and it is a near miss.** `bb_jrc_mobilized_pp` is pinned at the full
**15.600 for the entire run** — the roughness never degrades, so the envelope never
weakens, so τ never falls. It never degrades because the joint never reaches its limit:
**τ/τ_limit peaks at 0.9900** at stage 5 and then unloads. It misses by one percent.

**The one number behind it.** At stage 1 the model's τ_limit is **28.48 MPa** at
σ'ₙ = 42.33. But the specimen is *already creeping* at stage 1, so the measurement says its
limit is **26.14 MPa** at σ'ₙ = 42.99. **The envelope is still 9.0 % too strong**, even
after round 2's 0.92·τ_p correction.

**A note on the score, because it is misleading.** OG-SH's mean nRMSE went 62.19 → **67**,
i.e. *worse*. That is an artefact: round 1's τ was flat at 17.0 MPa (too low), round 2's is
flat at ~25.5 MPa (too high), and a flat curve at the top of the measured range scores
worse than one at the bottom. **The score got worse and the model got better.** Rank on the
per-stage table, not the scalar. The invariant across both rounds — and the real defect —
is that **τ does not evolve**.

### 1.3 Two further findings from scoring

**A seventh inherited Ye2018 constant.** `paper_flow_width_over_length` and
`mesh_flow_width_over_length` are byte-identical to the 93-series values on **OG-SH
(0.813242611781) and OG-T (0.814323680496)**. Only OG-SC got the derived per-specimen
value, because SW-S3's parent uses a suffixed key name the builder happened to match. The
derived values are 0.60607 / 0.58690 / 0.62506 (paper frame). Measured consequence: OG-SH's
`Q/(a_h³·ΔP)` is a constant 1.342× above Table 2's across all nine stages — **exactly
0.813242611781 / 0.60607.** Q is a scored channel on OG-SH, so much of its `Q 66` is this
one number. It does not touch a_h, so OG-T's and OG-SC's scored flow channels are clean.

**`kalantar_gate.py` has no completeness guard.** It returned confident scores for OG-T
(54) and OG-SC (85) by matching 17 and 13 hold stages inside runs that only reached **36 %
and 77 %** of their schedules. Those numbers are ghost matches and mean nothing. The
notebook already guards this (`MIN_COMPLETE_PCT = 99.9`); the gate must too, or a truncated
run will be ranked against a complete one.

### 1.4 What the two truncated runs say — read before planning round 3

*(2026-08-24, later. The notebook hid OG-T and OG-SC because they were incomplete. It now
shows them without scoring them — see §1.4.4. They are the most informative runs in the
batch and they change the plan.)*

**The three specimens fail in three different places, and only one of them is the
"envelope 9 % too strong" story above.**

| | loading frame | slip onset | weakening |
|---|---|---|---|
| **OG-SH** | ✅ stage 1 exact (−0.6 % τ, −0.2 % σ'ₙ) | never slips, τ/τ_lim peaks **0.9900** | absent |
| **OG-T** | ❌ broken before injection | slips **at t ≈ 31 s, during preload** | runs away to residual |
| **OG-SC** | ✅ stages 1–3 exact (τ −0.13/−0.32/−0.79 %, σ'ₙ −0.03/−0.07/−0.18 %) | bursts at **stage 4**, measured burst is **stage 7** | sheds 9.1 MPa, measured 3.4 |

**1.4.1 OG-SC is the best result in the campaign so far, and it gives a two-sided bracket.**
Its first three stages match on every channel. Then τ/τ_lim crosses 1.0 at stage 4 and it
bursts three stages early. Table 2 says it must **hold** at stage 6 (σ'ₙ 28.48, τ 12.95) and
**fail** by stage 7 (σ'ₙ 25.12, τ 13.0 → 9.73). At the deck's own JRC 4.23 / JCS 153 MPa
that brackets

> **21.36° < φ_r(OG-SC) < 24.05°**,  current value **19.148° — below the bracket by 2.2°.**

Both ends are measurements, neither is a fit. This is the closure test of
`bracket-closure-test-table2` and it closes. **Note the sign: OG-SC's envelope is too WEAK
while OG-SH's is too STRONG.** A single global envelope correction would have been wrong.

**1.4.2 OG-T never gets loaded, so none of its constants can be judged yet.** During the
preload ramp — before injection, at a pore pressure identical to the other two decks — the
fracture's own normal traction **falls** while the reported paper-frame σ'ₙ **rises**:

| t [s] | σ'ₙ seen by the law | σ'ₙ reported | ratio |
|---|---|---|---|
| 3.75 | 30.34 | 31.19 | 0.97 |
| 26.25 | 24.76 | 45.92 | **0.54** |

OG-SH and OG-SC show **no such divergence** over the same ramp (both track to ~1 %, and on
OG-SH the ratio stays 0.987–1.011 at *every* hold stage). So this is not the reporting chain
and not a poroelastic effect — `pp_outlet_pp` is pinned at 3 MPa and `injection_pressure_pp`
ramps identically on all three. It is specific to OG-T. The consequence: τ reaches the
envelope at **t ≈ 31 s**, the joint sheds **0.53 mm**, slip-weakens to residual, and all
6800 s that follow are a joint already lying on its residual envelope at τ/τ_lim ≈ 1.04.
**Do not touch OG-T's φ_r, JRC or cohesion until this is found.** Two candidates, in order:
the axial gate (`axial_pres_final = −7.056e−4` is a **0.71 % axial strain, 2.5–3.5× the
other two decks**, because OG-T's σ₁ target is 193.43 MPa against 94.65 and 63.39), and the
θ = 28° geometry, where two meshes exist on disk (`_theta26_`, `_theta28_`) and the deck
loads `theta28` with `bulk_sin_theta = sin 28°`.

**1.4.3 Both truncations are wall-clock, not solver failures — and the fix is the time
stepper, not the mesh.** Every deck carries `dtmax = 0.75` with `end_time` 3600 / 6800 /
9100, so the step count is fixed at 4800 / 9067 / 12133 before the solver is consulted. From
OG-SH's own log (`Finished Executing 35249.66 s` = **9.79 h** for 4800 steps at 64 ranks):

* **1206 steps actually solve**, ~24.3 s each = **83 % of the wall time**. These are the
  100 s pressure ramps.
* **3594 steps converge at nonlinear iteration 0** (residual 4.3e−9), ~1.65 s each. These
  are the 300 s holds.

Measured directly: across every OG-SH hold, `a_h` moves ≤ 0.09 %, Q ≤ 0.32 %, slip ≤ 1.7 %.
**Three of the nine holds move nothing at all, to seven digits.** The holds are dead time —
75 % of OG-SH's schedule and **86 % of OG-SC's**. OG-T is different again: 3351 of its 6194
steps (54 %) went into the single stick-slip event at t = 1300–1700 s, at dt down to 0.0166.
That cost is real physics and must not be optimised away.

Projected at 64 ranks, holding the mesh fixed:

| | now | ramp dt 1.5 / hold dt 5 | ramp dt 2.5 / hold dt 10 |
|---|---|---|---|
| OG-SH | 9.75 h | 4.30 h (2.3×) | 2.55 h (3.8×) |
| OG-SC | 16.45 h | 6.56 h (2.5×) | 3.87 h (4.3×) |

**1.4.4 The notebook now shows truncated runs without scoring them.** `SHOWN` (everything
with a CSV) drives the stage tables and figures; `LOADED` (complete only) drives the
scorecard. Stage tables are clipped to the last time the run reached, and the unreached span
is greyed on every panel. Before this, `stage_table` re-read the final row once per
unreached stage — the same mechanism that produced the phantom gate scores of 54 and 85.

### 1.5 Round 3 — BUILT 2026-08-24, ready to submit

Rebuild with `python scripts/build_110_kalantar_decks.py` then
`cd scripts && python make_kalantar_jobs.py`. New deck numbers, so round 2's CSVs and
Exodus files are not overwritten — they are the evidence for these changes.

| deck | specimen | wall | state |
|---|---|---|---|
| [`OGSH/110_02_og_sh_bbfast_r3.i`](Examples/Kalantar2025/OGSH/110_02_og_sh_bbfast_r3.i) | OG-SH | 24 h | ✅ `Syntax OK`, **submit** |
| [`OGSC/110_06_og_sc_bbfast_r3.i`](Examples/Kalantar2025/OGSC/110_06_og_sc_bbfast_r3.i) | OG-SC | 24 h | ✅ `Syntax OK`, **submit** |
| [`OGT/110_04_og_t_bbfast_r3.i`](Examples/Kalantar2025/OGT/110_04_og_t_bbfast_r3.i) | OG-T | 3 d | ⚠️ built and valid, **do not submit yet** |
| [`OGT/110_04_og_t_preload_probe.i`](Examples/Kalantar2025/OGT/110_04_og_t_preload_probe.i) | OG-T | — | 🔬 **local**, 60 s / ~120 steps, run this first |

**What changed, and what it is derived from:**

| # | change | evidence | assertion that now guards it |
|---|---|---|---|
| **1** | `dtmax = 0.75` → per-segment `time_t`/`time_dt`: **1.5 s on ramps, 5 s in holds**, snapped onto every injection breakpoint via `timestep_limiting_function` + `force_step_every_function_point`. Steps **4800/9067/12133 → 1140/2153/2427**, a 4.2–5.0× cut. `dtmin = 1e-6` and the cutback untouched | §1.4.3 — 83 % of OG-SH's wall time is ramp steps, and its holds move a_h ≤ 0.09 % / Q ≤ 0.32 % | `dt_schedule()` asserts increasing times and `max(dt) ≤ DT_HOLD` |
| **2** | OG-SC `φ_r` **19.148 → 22.660°**, the midpoint of the bracket Table 2's own `dL_s` column sets | §1.4.1 — hold at stage 6, fail at stage 7 → 21.365 < φ_r < 23.955 | `phi_r` must lie **inside** the bracket, and the `dL_s` jump and the largest `τ` drop must be the **same stage** |
| **3** | OG-SH's envelope **pinned through Table 2 stage 1** instead of read off Figure 3: φ_peak 32.70 → **30.12°**, φ_r 24.099 → **21.519°** | §1.2 — the joint creeps at stage 1 (§4.1), so its (σ'ₙ, τ) pair *is* on the envelope | `τ_limit(42.99)` must equal Table 2's 26.14 MPa to 1e-6 relative |
| **4** | `flow_width_over_length` really substituted now — **0.606072/0.606012** (OG-SH) and **0.586898/0.576170** (OG-T). Round 2's regex required a suffix only the SW-S3 parent had | §1.3 | build **fails** if `paper_` == `mesh_`, if either matches ≠ 1 key, or if a Ye2018 value survives |
| **5** | OG-T's `event_dt_cap` flattened — an **eighth** inherited Ye2018 constant, capping dt to 0.05 s over t ∈ [1530, 1680], which is **SW-T1's** burst window. 3000 forced full-cost steps in a place chosen for a different specimen | found while doing #1; round 2 showed the cutback reaching 0.0166 s unaided | — |
| **6** | OG-T's **envelope deliberately unchanged**, with a warning block at the top of its deck | §1.4.2 | — |

**Correction to §1.4/§1.2 as first written:** OG-SH's pin gives φ_peak **30.12°**, not the
31.3° quoted earlier. 31.3 is `atan(26.14/42.99)`, which ignores the 1.2 MPa Barton–Bandis
cohesion the deck also carries; with it, `42.99·tan φ + 1.2 = 26.14` → 30.11°. The builder
now computes this rather than taking a literal, and asserts the result.

**Still to do, after these run:**

| # | do | why then |
|---|---|---|
| **7** | Run the OG-T preload probe locally (≤ 24 ranks) and read its four checks | every OG-T constant is unjudgeable until this closes |
| **8** | Add a completeness guard to `kalantar_gate.py`, mirroring the notebook's | stops a truncated run being ranked; the notebook guards, the gate still does not |
| **9** | Only then touch `roughness_characteristic_slip` (§7 of the Kalantar memory) | it is a free knob with no measurement behind it; **do not tune it to compensate for changes 2 or 3**, which do |

**Do not coarsen the mesh to buy speed.** It is the wrong lever twice over: the cost is the
LU/MUMPS factorisation on ramp steps, which step 1 cuts 2.3× for free; and OG-SH's factor-4
mesh moves both injection nodes off the fracture onto **bulk** nodes 0.59 / 1.06 mm away
(`OGSH/mesh/kalantar2025_og_sh_theta29.jou` lines 55–81 — the source-pinning test that
already failed once), lengthening the flow path **2.94 %** on the one channel that already
carries a 1.342× bug. Changing discretisation in the same round as the physics fixes makes
the result unattributable. Coarsen later, deliberately, as a convergence check.

**Prediction for round 3**, written now, one number per specimen:

* **OG-SC** — `τ_limit(σ'ₙ = 31.55) > 13.08 MPa`, i.e. it holds through stage 6 and bursts
  at stage 7. This is the whole claim; if it bursts early *or* never, step 2 is wrong.
* **OG-SH** — `τ_limit` at stage 1 equals the measured **26.14 MPa**. If JRC still does not
  mobilise once that passes, the cause is `roughness_characteristic_slip`, not the envelope.
* **OG-T** — no prediction is legitimate until §1.4.2 is closed. Writing one would be
  preregistering a proxy for a confound, the mistake logged in the round-2 write-up.

*(Round 2's own prediction is scored in `Examples/Kalantar2025/MEMORY.md` §9.1 — it was
half right, and its falsifier was mis-specified in a way worth reading before writing
another one.)*

### 1.6 Kalantar items not on the critical path

* **111-series Mohr–Coulomb siblings** — after round 3 lands.
* **Step G mechanism decks**, the gouge arm on OG-SH first.
* **Rebuild or delete `OGSC/mesh/og_sc_theta30_size5.e`** — it is a pre-rename copy of
  `size3.e`, identical node and element counts. Scoring the two would return perfect "mesh
  convergence" from a no-op. Must not survive into any convergence claim.
* **#113 — fold the four Kalantar cross-checks into the Ye2018 manuscript** (§6.7, the
  §5/§6 frame-stiffness caveat, §6.9, the cyclic paragraph).
* Housekeeping: ~30 stale `tmp_jit_*` directories under `Examples/Kalantar2025/OGSH/` and a
  few under the other two. Stale comments in the decks: OG-SC's `end_time = 9100` still
  carries the SW-S3 comment *"FULL SW-S3 cycle (11 stages)"*, and the
  `residual_friction_angle_degrees` comments still argue the Ye2018 case.

### 1.7 Decisions that are Saeed's

1. **OG-T's angle** — 28° built as primary, 26° as a ready sensitivity arm. Recommendation
   is 28° with the published stress columns re-reduced; 26° cannot be realised without
   contradicting a measured dimension, and needs a 4.5 % longer core, which changes the
   axial compliance of a system whose frame stiffness dominates.
2. **Whether the 5 mm borehole inset is to the hole centre or its edge** — ~5 % on flow path
   length, resolvable from the GFZ release. Also OG-SC's core length.
3. **Whether to publish the three checkable defects in the paper** — the OG-T angle, eq (7)
   being out by a constant 10.3× in `a_h³`, and the `k` column disagreeing with `a_h` by
   13 % on two specimens. All are checkable against the paper's own Table 2. Reporting them
   makes the audit method itself a contribution: the same class of error caught twice, in
   two independent datasets.

---

## 2. Standing rules

* **Never exceed 24 MPI ranks on the local workstation** — past that wall time doubles.
* **Saeed submits the HPC jobs and builds the meshes in Cubit.** This repo produces `.jou`
  and `.sh` files, not submissions.
* Source changes go on a new `orca_vN` branch, with detailed commit messages; the MDs are
  updated as part of the work, not after it.
* **Do not sync `.jitcache/` back from HPC.** Those `.so` files were compiled by a different
  build and crash the local `orca-opt` with a bare `MPI_Abort` inside `vtkMPICommunicator`
  and no MOOSE message. `rm -rf */.jitcache` restores `Syntax OK`. Note that a CLI override
  of a key absent from the parent deck aborts *identically*, which is what made this take an
  hour to find.
* Reading Exodus needs `/home/geomechanics/miniforge/envs/moose/bin/python` (netCDF4 1.7.4).
  Running the notebook needs the **base** interpreter (jupyter/nbconvert). No single env has
  both; the notebook only needs the latter.
* `.gitignore` carries `*.jou`, `*.csv`, `*.e` — result assets are force-added past it.
  Exodus files are correctly left out.

---

## 3. Ye2018 — still open

Full detail and history in `doc/TODO.md`; these are the items that are actually live.

| # | item | state |
|---|---|---|
| **#81** | Score the mesh-3 convergence runs against their mesh-5 finals | 8 twins verified and re-resourced to 128 ranks / 128 G / 2 d; **Saeed submits** |
| **#105** | Rewrite §5.5/§6.3 and fold in the five 08-17/18 findings | in progress |
| **#113** | Fold the Kalantar cross-checks into the manuscript | pending — see §1.5 |
| **#59** | Rebuild `orca-opt`; runtime-verify the three compile-checked-only fixes; register the `alpha_eff_lagged` test and gold it | blocked on the campaign draining |
| **#91** | Bracket SW-S4's unused cohesion-weakening channel (the stage-4 defect) | pending |
| **#106** | Write a real README for the repository | pending |
| **#13** | Make the flow measurement mesh-independent | pending |
| **#65** | Unify rock-characteristic parameters across the four sample decks | pending |
| **#50 / #51** | Stale split mass-balance kernel pair; `biot_coefficient = 1e-12` in SWS3/SWT1/SWT2 | pending |
| **#76 / #78** | Why the SW-T1 87/88 lineage barely opens; SW-S3's Biot inversion before quoting `84_01` | pending |
| **#19 / #20 / #21** | SW-S3's distinct failure mode; SWT2_BBFast's 800 s LU regression; SWS4_MC mesh-3 LU retry with more memory | pending |
| **#14 / #15 / #31 / #42 / #52 / #55 / #60 / #67 / #92** | older threads, several superseded by the 93/94-series finals — **triage against `doc/TODO.md` before reopening any of them** | stale |

**Editorial, unassigned:** the 99/100 refinement probes are not in the manuscript. They
localise SW-T1's residual to joint normal compliance and put a price on that knob — better
content than the 1.7-point score gain they were rejected for. Wants a sensitivity paragraph
in §5 or §6.

---

## 4. Loose end from an earlier session, never answered

~1 GB of truncated output left by killed local SW-T1/SW-S3 runs. **Complete HPC versions of
all four exist in `results_csv_hpc_rorqual/`,** so nothing is lost by deleting these — but
they are currently indistinguishable from complete runs by filename, which is the actual
risk.

```
Examples/YeGhasemmi2018/.../SWT1/results_csv_local/103_01_swt1_weakexp1p0_ppfix_local.csv     4.9 MB
Examples/YeGhasemmi2018/.../SWT1/results_exodus_local/…e                                      539 MB
Examples/YeGhasemmi2018/.../SWS3/results_csv_local/103_03_sw3_weakexp1p0_ppfix_local.csv      4.7 MB
Examples/YeGhasemmi2018/.../SWS3/results_exodus_local/…e                                      482 MB
```

Delete, or rename with a `_PARTIAL` suffix. Saeed's call.
