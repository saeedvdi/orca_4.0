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

### 1.6 Round-4 meshes — TRIED, MEASURED, REJECTED 2026-08-24

**The premise was wrong.** I claimed the meshes were over-refined in the *bulk* and that
~45,000 elements could be recovered from OG-SH without touching the fracture. Saeed built
the graded meshes. They were measured. **There is no over-refined bulk.**

Median node spacing [mm] against distance from the fracture plane, OG-SH:

| | 0–1 | 1–2 | 2–4 | 4–8 | 8–16 | 16–32 | 32–100 mm |
|---|---|---|---|---|---|---|---|
| `_size3.e` | 0.968 | 0.988 | 0.986 | 1.004 | 0.977 | 0.955 | 0.978 |
| graded | 0.918 | 0.906 | 0.931 | 0.926 | 0.872 | 0.846 | 0.877 |

**Both profiles are flat.** The mesh was already uniform at ~0.98 mm everywhere out to
100 mm from the fracture, and `volume all size 0.00180` had no effect at all — the 1.00 mm
*surface* size propagated through the whole volume and made everything finer. Same on the
other two. The cause is the element type: `scheme polyhedron` yields **HEX8** here, and a
hex mesher propagates surface intervals along the mapped directions through the entire
volume. It cannot grade away from an interior surface the way a tet mesher can.

**Measured outcome of the three graded meshes:**

| | elements | interface nodes | pitch | source pinning | re-pinned W/L shift |
|---|---|---|---|---|---|
| OG-SH | 100,048 → **108,240 (+8.2 %)** | 1,977 → 2,521 | 1.035 → 0.942 mm | ❌ **BULK node**, 707.6 µm | **+1.82 %** |
| OG-T | 53,760 → 51,600 (−4.0 %) | 2,297 → 2,641 | 0.980 → 0.916 mm | ✅ OK, and **improves** 792.9 → 362.8 µm | +2.74 % |
| OG-SC | 68,096 → 65,744 (−3.5 %) | 2,185 → 2,407 | 1.004 → 0.941 mm | ❌ **BULK node**, 742.7 µm | −0.87 % |

Geometry is exact on all six meshes — L, D, θ, plane-fit residual 0.00 µm, fracture area to
6 digits. That part is clean.

**Verdict: not adopted. All three journals reverted to `auto factor 3` and `_size3.e`**, with
the measurement recorded in each header so it is not retried. OG-SH would have been **8 %
slower** and needed a borehole 732 µm off design, moving a scored channel by 1.8 %.

**Where the error came from, so it is not repeated.** I inferred an "implied bulk edge" as
`(volume / n_elements)^(1/3)` = 1.33 mm and compared it against the interface pitch of
1.035 mm, reading the 1.29 ratio as weak grading. Those two numbers are not commensurable —
one is a 3D element-volume scale, the other a 2D in-plane node spacing — so the ratio was an
artefact of the comparison, not a property of the mesh. **The spacing-versus-distance
profile is the direct measurement, it costs one command, and it should have been run first.**

**Worth keeping:** on **OG-T alone** the graded mesh is better on every axis — fewer
elements, +15 % interface nodes, finer pitch, and source pinning that *improves* to 362.8 µm
(from 792.9) with a flow path closer to the paper's (−0.85 % against +1.86 %). Not adopted
now, because OG-T's open problem is the preload defect and changing its mesh underneath an
unresolved model defect makes the diagnosis unattributable. Revisit after the probe closes;
the commented sizing pair is in its journal.

> **Amended 2026-08-24, later the same day — see §1.7.** The *pinning* column of the table
> above has nothing to do with grading. Every one of those six distances is fixed by a single
> integer, and §1.7 replaces the whole approach. The element-count and profile conclusions
> above still stand; the pinning conclusions were reading luck as quality, including OG-T's
> "improvement".

**The speed lever is not the mesh.** With a uniform hex mesh you can only coarsen globally,
and factor 4 already fails source pinning outright. What remains:

1. **128 ranks** — proven config in this repo (mesh-3 jobs), ~1.4–1.7× expected, no
   scientific risk. Use it on the next submission.
2. The dt schedule already bought **4.2–5.0×**. That was the real win and it is banked.
3. Beyond that would need a field-split preconditioner instead of LU/MUMPS — real work, and
   the DIVERGED_ITS history says do not reach for hypre casually.

**The durable fix, if mesh freedom is ever wanted:** imprint the two borehole vertices into
the geometry so a node exists at each source *by construction*. That is now §1.7.

### 1.7 Source pinning is one integer — imprint BUILT 2026-08-24, awaiting Cubit

**Every pinning distance ever measured on these meshes is `round(0.79992·N)/N`.**

Both boreholes sit at `y = 0` on the fracture plane. That is not the interior of a surface —
it is exactly where `webcut … yplane` cut the fracture ellipse, i.e. the ellipse's **major
axis**, and it is a *geometric curve*. Cubit divides that curve into `N` equal intervals
(verified: min spacing == max spacing to machine precision on all six meshes), so the only
node positions the source can reach are `k/N` along it. The design borehole sits at
`x/r = (24.99 − 5)/24.99 = 0.799920`, so the error is integer arithmetic:

| mesh | N | nearest fraction | pinning error | measured by `check_source_nodes.py` |
|---|---|---|---|---|
| `_size3` OG-SH | **25** | 20/25 = 0.800000 | 4.1 µm | 4.1 µm |
| `_size3` OG-T | 27 | 22/27 = 0.814815 | 792.9 µm | 792.9 µm |
| `_size3` OG-SC | 26 | 21/26 = 0.807692 | 388.5 µm | 388.5 µm |
| graded OG-SH | 28 | 22/28 = 0.785714 | 732.2 µm | 732.2 µm |
| graded OG-T | 29 | 23/29 = 0.793103 | 362.8 µm | 362.8 µm |
| graded OG-SC | 27 | 22/27 = 0.814815 | 744.4 µm | 744.4 µm |

All six agree to 0.1 µm. **OG-SH's much-quoted 4.1 µm pin was never mesh quality — it is 25
being divisible by 5**, because the design borehole sits two microns off exactly 4/5 of the
radius. The two graded "BULK node" failures and OG-T's graded "improvement" are the same
arithmetic. Nothing about grading, sizing, or element count enters it.

**Built (this repo, not yet run in Cubit):**

* `scripts/check_axis_intervals.py` — infers L, r, θ and the fracture plane *from the mesh*,
  reports `N`, the spacing uniformity, the nearest fraction, the pinning error and the
  implied borehole separation, and names the fix. Verified: it reproduces all six rows above.
* `Examples/Kalantar2025/mesh_probe_axis_curves.jou` — **probe only, exports nothing.** Builds
  all three geometries and lists the curves in surfaces `26 46 53 32`. The two wanted are the
  ones of length `r/sin θ` = 51.5460 / 53.2301 / 49.9800 mm, which is unique in each model.
* All three production journals — a `split curve … location position` at the design borehole
  after the webcuts and before `imprint all`, with the curve IDs left at `0` so an unfilled
  journal fails loudly. Each exports to a **new** name `…_size3_pin.e`; `_size3.e` is
  untouched because 110_02 and 110_06 are running on it.

**Why the split and not a webcut:** it adds one vertex and replaces one curve with two. No
new surfaces, no new volumes — the hardcoded block/nodeset surface IDs and the nodeset 5/6
vertex IDs survive. A webcut would renumber all of them.

**Fallback, in each journal, two commented lines:** `curve <ids> interval 25`. Forcing
`N ≡ 0 (mod 5)` puts a node at exactly `0.8 r = 0.019992` — 4.0–4.3 µm from design — at *any*
global coarseness, with no topology change at all. Strictly weaker than the imprint (4 µm vs
0) but zero risk, and it is already enough to decouple pinning from mesh size.

**Unverifiable here: there is no Cubit on this machine.** Two commands carry real risk and
neither could be tested — `split curve` on already-merged geometry, and whether `scheme
polyhedron` keeps good quality around the new vertex. That is what the new-export-name and
the two checker scripts are for.

**Sequence:**

1. Run `mesh_probe_axis_curves.jou`, paste the six curve IDs into the three journals.
2. Mesh and export the three `_pin.e`.
3. `check_axis_intervals.py` → expect **0.0 µm**; `check_source_nodes.py` → sources **on the
   interface**. If either fails, switch to the commented interval fallback and re-run.
4. Only then re-point the decks, and **re-derive `mesh_flow_width_over_length_*` from the
   design separations** — 82.4654 / 85.1596 / 79.9600 mm. This removes a scored-channel bias
   of +0.010 % / **+1.862 %** / **+0.972 %**, and OG-T's design separation *is* the paper's.

**This is what makes coarsening possible at all** — pinning stops depending on mesh size, so
factor 4 and 5 become testable instead of automatically disqualified. It does not by itself
make anything faster; **128 ranks is still the immediate lever** (§1.6).

### 1.8 Round-3 results — mid-flight back-analysis 2026-08-24

**Full write-up: [`doc/KALANTAR2025_ROUND3_BACKANALYSIS.md`](doc/KALANTAR2025_ROUND3_BACKANALYSIS.md).**
Snapshots downloaded 16:15: OG-SH **50.0 %**, OG-SC **46.5 %**, OG-T **0.5 %**. Pressurization
branch only — nothing is scoreable, and `kalantar_gate.py` must not be run on these files (still
no completeness guard; it phantom-matches depressurization stages to pressurization times).

* **OG-SH — the envelope fix worked.** `τ/τ_limit` reaches **1.0040** and holds 1.000 from stage 2;
  round 2 peaked at 0.9900 and never reached the limit. Slip 0.054 mm at halfway against round 2's
  0.0049 mm at the end. τ errors by stage: −1.9 / +1.5 / +3.9 / +7.1 / +8.6 %.
  **Residual defect:** slips **+38 %** too much while weakening **−33 %** too little — 81 MPa/mm
  against a measured 168. Attack the conversion, never the slip.
* **OG-SC — best agreement in the campaign.** Stages 1–5 within 1.4 % on τ, 0.3 % on σ'ₙ. Burst
  moved stage 4 → **stage 6**; measured is 7. **Bracket narrows to 22.660° < φ_r < 24.05°.** It
  also over-weakens (post-burst τ 5.95 vs 9.73) — a *second* knob.
* **OG-T — the defect is not constitutive.** `dσ'ₙ/dσ₁` is **−0.090** against a required
  `+sin²28 = +0.220`, at 2.9 µm of slip: the fracture **opens under rising axial compression**
  while OG-SH (+0.228/0.235) and OG-SC (+0.183/0.250) both close. Area-averaged channel, so not a
  reporting artefact. σ₁ = 193.43 MPa is verified correct. Prime suspect is the 3.00 mm tip
  clearance against the platen BC — warned about in the mesh journal on 2026-08-23, never checked.

**Next, in order:** let 110_02/110_06 finish → cancel 110_04 → run the OG-T preload probe with a
written falsifiable prediction (#120) → the tip test → **#121, why `bb_jrc_mobilized` has never
moved in seven decks across both campaigns** → OG-SC's last φ_r step → OG-SH's weakening
conversion.

> **§1.8 is superseded by §1.8b. Three of its five conclusions did not survive completion**
> — the `bb_jrc_mobilized` item, OG-SC's bracket, and the prime suspect on OG-T.

### 1.8b Round-3 results — COMPLETE, 2026-08-24 22:48

**Full write-up: [`doc/KALANTAR2025_ROUND3_BACKANALYSIS.md`](doc/KALANTAR2025_ROUND3_BACKANALYSIS.md)
Part II.** `110_02` and `110_06` both reached `end_time`; `110_04` is unchanged at 0.5 %. Both
completed runs are legitimately scoreable.

| | round 1 | round 2 | **round 3** |
|---|---|---|---|
| OG-SH mean nRMSE | 62 | 67 | **17** (τ 21, Q 13) |
| OG-SC mean nRMSE | — | — | 77 (τ 120, a_h 39) |

**The headline is not the number, it is that a preregistered null paid off.** Round 2 closed by
naming one — *"τ_limit at stage 1 equals the measured τ"* — after the falsifier before it had
been mis-specified. Round 3 acted on that single number (φ_peak 32.70° → 30.12°) and the score
fell 3.7×. First time in either campaign. **Keep closing rounds this way.**

* **#121 CLOSED — not a bug, a deck flag.** `use_mobilized_jrc = false` in every deck of both
  campaigns; `ADOrcaBartonBandisContactTractionFastAD.C:782-787` pins the property when it is
  off. **And turning it on is not the fix** — `jrc = JRC·sbar^n` ramps roughness *up* with slip,
  the opposite of both datasets. The live weakening channel is `roughness_state` (OG-SH
  1.000 → 0.732, OG-SC 0.640 → 0.141). **Both manuscripts must be reworded — #127.**
  *I had called this the project's highest-leverage item and blamed the unseeded-property
  family. A constant that is constant in every deck is first evidence about the decks.*
* **OG-SC's φ_r bracket closes on the deck's own 22.660°** — on the *undegraded* envelope it
  holds stage 6 by +6.1 % and fails stage 7 by −5.8 %, exactly Table 2. §1.8's "bracket narrows"
  is **withdrawn**: it read the early burst as a weak envelope when the weakening law had
  already cut the limit 13 %. **Do not spend another φ_r step.**
* **OG-SC's one wrong constant:** `slip_weakening_residual` 15.354° was derived from Table 2's
  *last* stage, where slip has been frozen since stage 10 — a **locked** joint, so a lower bound
  not a measurement. Correct value **21.17°**, from stage 7 where it has just slid. The model
  collapses to μ = 0.2746 and gives τ 4.85 vs 9.73 measured.
* **OG-SH's `characteristic_slip_distance` 150 → 26.5 µm.** The residual (25.930°) is right and
  never reached: 48 µm of slip is `s/D = 0.32`, worth 18 % of the drop. The assertion that
  blocked this is **1.36× too strict** (linear-drop assumption on an `exp(−(s/D)^1.4)` law) and
  also charged σ'ₙ's fall to the friction term; corrected cap 23.2 µm, so 26.5 µm is stable by
  1.14× — matching "creeps, no burst".
* **OG-SC's aperture law is saturated.** σ₀ = V_m·K_ni = 15 MPa sits *below* the 28.5–36.1 MPa
  operating range, so the closure term delivers 0.051 µm against a measured 0.570 — 11–24×
  short. Refit on six pre-burst stages: **V_m 1.20 → 2.651 µm, σ₀ → 36.29 MPa**, K_ni unchanged.
  RMS 25 nm. Closes OG-SC's half of the still-inherited list.
* **OG-T: geometry promoted over the axial gate.** The measured/predicted `Δσ'ₙ` ratio orders
  monotonically with **fracture-tip clearance** — 14.92 / 6.72 / 3.00 mm → **1.012 / 0.830 /
  −0.382** — and does *not* order with Δσ₁ (OG-SH carries twice OG-SC's and scores better). The
  **26° arm is 1.0 mm clearance**: a falsifier, never a rescue. Probe prediction sharpened in
  #120.

**Next, in order:** #126 round-4 decks (four constants + two builder assertions, four
preregistered nulls) → #120 OG-T preload probe with both predictions written first → #127
manuscript wording → 111-series MC siblings, now unblocked.

### 1.9 Kalantar items not on the critical path

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

### 1.10 Decisions that are Saeed's

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

### 3.0 Back-analysis of the completed campaign — 2026-08-24

Full write-up: **`doc/YE2018_FINAL_BACKANALYSIS_2026-08-24.md`**. Arithmetic:
`scripts/mesh3_convergence.py` (new), `scripts/check_axis_intervals.py`.
**Nothing here changes Table 5.** Three findings, in order of what they cost:

1. **The completeness belief was wrong.** It is not only SW-T1's mesh-3 run that is
   outstanding — **seven of ten** mesh-3 runs are truncated, plus `96_04/05/07/08` at
   48–52 % and the `97`-series (superseded by the complete `101`s, so harmless).
   Wall-clock percentage misleads in both directions: measure the cut against **peak
   injection**, not `end_time`.
2. **SW-S3's refined pair is usable and the draft threw it away.** Its stage 6 *is* peak
   injection, so it covers every loading stage and the slip event with them. Matched
   six-stage means: BB 4.36 → 5.26 (+0.90), MC 24.39 → 24.89 (+0.50). SW-S3 is a **burst**
   specimen, which fills the draft's own stated gap. §5.1 rewritten — task **#124**.
3. **The 2026-08-06 flow fix was never ported to the finals** — *now fixed, task #123.* All
   16 decks were still `NodalSum`-ing `inj_flux_aux` while `react_pore_pressure`, built with
   `remove_variable_scaling = true` in every deck, was never summed. §5.4's "solved injection
   flux 0.0277" read **0.000191** in `93_01`, and in *every* SW-T1 run back to `87_01`.
   Repointed everywhere and re-measured: injection **0.0272**, production **0.0293**, balance
   **7.6 %** (was 16.8 %), correction factor **142×**. Scores were never affected — the scored
   $Q$ is the cubic-law channel — and the re-run proves it: $a_h$ and $Q$ bit-identical.
   **§5.4's argument survives unchanged**: the solved flux is 0.52× the reported $Q$, which is
   the "about half" the subsection already claimed.

Also established, and it is the reason the mesh comparison survives at all: **$Q$ is an
exact algebraic function of the aperture** — $C\,a_h^3\Delta p$ with $C$ fitted and
$\Delta p$ prescribed by two Dirichlet BCs, $r = 1.00000000$ and max departure 0.0000 % on
all four specimens. So the borehole-separation defect (which the Kalantar tooling found on
**all four** Ye2018 specimens: every mesh-5 run is 2.0–3.9 % long, pair differences 2.2–4.4 %)
cannot reach $Q$ directly. Empirically the largest separation change produces *zero*
aperture response. **Do not rebuild the Ye2018 meshes** — the null prices the fix at nothing.

**On the SW-T1 mesh-3 run in flight:** its predecessor reached 2.0 % of the schedule, and
SW-T1's flow response is 99.7 % concentrated after that point. If it does not reach stage 6,
it adds no evidence — write §5.1 on SW-S4 + SW-S3 regardless rather than waiting on it.

| # | item | state |
|---|---|---|
| **#123** | Port the flow-measurement fix into the 93/94 finals; re-run SW-T1 | **DONE 2026-08-24.** All 16 decks repointed at `react_pore_pressure`; legacy `save_in` sums kept as `*_saveiin_sum_legacy_pp`. Verified **output-only**: $a_h$ and $Q$ bit-identical, $\sigma'_n$/$\tau$ to $10^{-8}$ %, $d_n$ inside the cross-machine floor. Re-run `126_01` (SW-T1, $t\le320$ s, 16 ranks, 427 steps, all converged). Corrected: injection **0.0272**, production **0.0293**, balance **7.6 %**, correction factor **142×**, ratio to reported $Q$ **0.52**. §5.1 + §5.4 + Appendix B updated |
| **#124** | Rewrite §5.1's mesh paragraph + footnote 14 with SW-S3 promoted | **applied 2026-08-24**, verify on read-through |
| **#125** | Correct the separation claim to all four specimens; add the $Q\equiv a_h^3$ null | **applied 2026-08-24**, verify on read-through |
| **#81** | Score the mesh-3 convergence runs against their mesh-5 finals | **done** — `scripts/mesh3_convergence.py`; reproduces the manuscript's SW-S4 numbers exactly |
| **#105** | Rewrite §5.5/§6.3 and fold in the five 08-17/18 findings | in progress |
| **#113** | Fold the Kalantar cross-checks into the manuscript | pending — see §1.5 |
| **#59** | Rebuild `orca-opt`; runtime-verify the three compile-checked-only fixes; register the `alpha_eff_lagged` test and gold it | blocked on the campaign draining |
| **#91** | Bracket SW-S4's unused cohesion-weakening channel (the stage-4 defect) | pending |
| **#106** | Write a real README for the repository | pending |
| **#13** | Make the flow measurement mesh-independent | pending — and note `flow_rate_mesh_geometry_ml_min_pp` is currently **identical** to the fitted channel on SW-S4/T1/T2 (the same $W/L$ copied), so the "independent" diagnostic only computes anything on SW-S3 |
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
