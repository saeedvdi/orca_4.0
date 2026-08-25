# Final deck selection, and the mesh-3 convergence batch

**2026-08-22.** Branch `orca_v6`. This closes the question the ranking CSV was built
to answer: for each of the four Ye & Ghassemi (2018) specimens, which single deck is
*the* Barton–Bandis result and which is *the* Mohr–Coulomb result, so that the mesh
convergence study runs on the decks the manuscript actually reports.

Source of every number here:
`doc/independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv`, rebuilt by
`scripts/update_table2_ranking.py --write`, which rescores every listed run from its
result CSV through `scripts/table2_gate.py`. Nothing in this document was computed by
hand — that is deliberate, and the reason is in
`doc/DISCUSSION_104_RESULTS.md` §0.

---

## 1. The ranking is now complete

Two series of finished monotonic runs were missing from it. Both are now in, at 86
rows, 71 ranked and 15 partial:

- **102-series (4 runs), `best_case_constitutive_baseline`.** The Mohr–Coulomb
  baseline rebuilt on the *best* Barton–Bandis calibration of each specimen instead
  of the nominal one.
- **103-series (3 runs), `mechanism_control`.** Barton–Bandis with the slip-weakening
  exponent dropped 1.4 → 1.0, the value Mohr–Coulomb uses, and nothing else changed.

The 103 decks carry their own `model_family` (`BBFast linear-weakening control`) so
they cannot compete with the calibration decks for a family rank. Reading them as
"bad BBFast runs" inverts their meaning: on the tensile pair the whole MC/BBFast gap
is *supposed* to open up when the exponent is changed, and it does.

The 97/98/101/104 runs are not in the ranking and should not be: they are cyclic and
shut-in schedules, not the monotonic eleven-stage Table-2 protocol this metric scores.

---

## 2. Mohr–Coulomb: the 94-series, on all four. No contest.

The 102-series asked whether the MC/BBFast accuracy gap is *calibration* or
*constitutive form*. Each 102 deck transplants onto the matched MC envelope whatever
scalar refinement won the BBFast ranking for that specimen. If the gap were
calibration, the MC score should have moved.

| specimen | **final** | mean nRMSE % | best-case MC | mean nRMSE % | change |
|---|---|---|---|---|---|
| SW-T1 | **`94_01_swt1_mc_final`** | 25.313363 | `102_01` (V_m 55 µm) | 25.444760 | +0.131 |
| SW-T2 | **`94_03_swt2_mc_final`** | 23.182517 | `102_02` (aperture scale 0.0177) | 23.402790 | +0.220 |
| SW-S3 | **`94_05_sw3_mc_final`** | 18.227743 | `102_03` (c_res 1.30 MPa) | 18.506613 | +0.279 |
| SW-S4 | **`94_07_sw4_mc_final`** | 7.067297 | `102_04` (93_07 calibration) | 7.062957 | −0.004 |

Three moved the wrong way and the fourth did not move at all: 0.004 points is a
twentieth of the 0.1-point cross-machine reproducibility floor, so `102_04` and
`94_07` are the same run. **The gap is not closed by Barton–Bandis-derived
refinements, and the 94-series stands as the matched baseline.**

> **SCOPE CORRECTION, 2026-08-25.** This section previously read "**The gap is
> constitutive**". That is more than the 102-series can support, and it has been
> narrowed. The 102-series transplants *BBFast-derived* refinements onto the MC
> envelope; those act on a roughness description MC does not carry, so their failure
> to help is expected and says nothing about calibrating MC in its own right. It can
> be calibrated: 52 completed, independently fitted MC runs in `orca_3.0_full` reach
> **4.40 %** on SW-S4 (better than our BBFast final's 6.139 %) and **6.07 %** on
> SW-S3 — using roughly eight fitted parameters per specimen against the 94-series'
> zero. Full record, scores and caveats:
> `doc/independent_analysis/MC_ARCHIVE_RECOVERY_2026-08-25.md`.
>
> The numbers in the table above also moved, because `scripts/table2_gate.py` now
> scores `d_n` on the global kinematic jump rather than each material's own
> `normal_opening_total` decomposition — the MC material's omits the elastic term, so
> the baseline had been charged for a missing reporting term. No BBFast score
> changed. SW-S4's MC baseline improved 8.97 → 7.07, taking that specimen's BB/MC
> ratio from 1.46× to **1.15×**.

This is still a real result, not a null. It is the other half of the 103-series
argument in manuscript §6.3.1: the exponent change alone reproduces the gap on the
tensile pair, and no BBFast-derived refinement closes it anywhere.

---

## 3. Barton–Bandis: the 93-series, on all four — but this one needed an argument

Unlike MC, three of the four specimens have a *better-scoring* run in the repository
than the deck the manuscript reports. The 99- and 100-series are single-axis
refinement probes cut from the 93-series parents, and they are legitimate descendants
— `ppfix` postprocessors, every correction retained, one or two scalars moved.

| specimen | **final** | mean nRMSE % | best probe | mean nRMSE % | probe better by |
|---|---|---|---|---|---|
| SW-T1 | **`93_01_swt1_final_c26p9_resc9p19_ppfix`** | 4.435159 | `100_01` (V_m 45.91 → 55 µm) | 2.688632 | 1.747 |
| SW-T2 | **`93_03_swt2_final_theta30_resc9p71_ppfix`** | 2.427821 | `100_04` (aperture scale 0.0165 → 0.0177) | 2.131869 | 0.296 |
| SW-S3 | **`93_05_sw3_final_resc1p40_ppfix`** | 4.574322 | `100_06` (c_res 1.30 MPa, retention 0.00) | 4.353781 | 0.220 |
| SW-S4 | **`93_07_sw4_final_theta30_jrc5_ppfix`** | 6.139187 | `99_07` (weakening exponent 1.05) | 6.244586 | — none |

Two of those margins are above the 0.1-point floor and one is large. The 93-series is
still the answer, for three reasons that are worth separating because only the first
is about the score.

### 3(a) SW-T1's winning knob is not closed, and cannot close

`100_01` is not a converged calibration; it is one point on a sweep that is still
falling:

| `maximum_closure` V_m | mean nRMSE % |
|---|---|
| 45.91 µm (`93_01`) | 4.435159 |
| 50.00 µm (`99_01`) | 3.678819 |
| 55.00 µm (`100_01`) | 2.688632 |

The second step is *larger* than the first per micron (0.198 vs 0.185 points/µm), so
the bracket has not turned. Under the campaign's own closure rule that means the
sweep is unfinished, and adopting its last point is arbitrary.

It is worth knowing where the sweep would end. The Barton–Bandis closure law
`σ_n = (K_ni·V_m)·[c/(V_m − c)]^(1/p)` has tangent stiffness

    k_n = (K_ni/p)·u^(1−p)·(1 + u^p)²,     u = σ_n /(K_ni·V_m)

which is **non-monotonic in V_m**: raising V_m softens the joint until the scale
stress `K_ni·V_m` overtakes the operating stress, after which it stiffens again. At
`K_ni` = 2.443e11 Pa/m and p = 3.28 the minimum is `k_n` = 0.271 MPa/µm — the same
value at every stress, only the V_m that attains it moves (174 µm at σ'_n = 35 MPa,
332 µm at 67 MPa). In series with the inferred frame at 0.94 MPa/µm that is a best
achievable system unloading tangent of **0.210 MPa/µm against 0.135 measured**.

So V_m is a genuine knob — it can absorb roughly three quarters of SW-T1's 6.3×
unloading-stiffness excess, which is why the score keeps improving — but it **cannot
reach the measurement at any value**, and the value that gets closest is 4–7× the
deck's. `SWT1_FINAL.md` concluded that SW-T1's residual is model form; this prices
that conclusion instead of overturning it. 55 µm is neither the fitted value nor the
knob's optimum, so it is the one number on that sweep with no argument behind it.

*(Caveat: the 0.94 MPa/µm frame stiffness is inferred, not measured, and
`ye2018-frame-stiffness-dominates-magnitudes` warns how much leverage it carries. The
0.271 MPa/µm joint bound does not depend on it; the 0.210 system figure does.)*

### 3(b) SW-T2 and SW-S3 are closed, and their margins are small

Unlike SW-T1 these two really are converged — and they still do not justify the
switch on their own.

- **SW-T2**: 0.0165 → 0.0170 → 0.0175 → 0.0177 gives 2.428 → 2.237 → 2.136 → 2.132.
  The last step is 0.004 points, below the floor, so the optimum is ≈ 0.0176 and
  `100_03`/`100_04` are tied. Closed, worth 0.296 points.
- **SW-S3**: c_res 1.40 → 1.30 → 1.25 gives 4.574 → 4.451 → 4.436, the last step
  0.015 points and below the floor; retention 0.06 → 0.03 → 0.00 ends at the physical
  lower bound. Both axes exhausted, worth 0.220 points combined.

### 3(c) Switching would decouple the finals from everything built on them

The decisive cost is not the manuscript's scorecard — that is a table edit. It is
that **the 101, 103 and 104 discussion decks were all cut from the 93-series
parents**, as were the MC pairings and the eight mesh-3 twins. Promoting the 100-series
would leave every mechanism result in §6.6, §6.7 and §6.3.1 reported on a parent that
is no longer the final, for a mean gain of 0.57 points across four specimens, one of
which rests on an open sweep.

**The 99/100 probes are better as reported content than as a substitute.** They
localise SW-T1's residual to joint normal compliance, and §3(a) shows that compliance
cannot be fitted away — a stronger statement than a 1.7-point score improvement.
This is not currently in the manuscript; it belongs in §5 or §6 as a sensitivity
paragraph, and is flagged as an open editorial item, not silently dropped.

---

## 4. The eight decks, and what is being run

| specimen | law | reported (mesh 5) | convergence twin (mesh 3) |
|---|---|---|---|
| SW-T1 | BBFast | `93_01_..._ppfix` | `93_02_..._ppfix_mesh3` |
| SW-T1 | MC | `94_01_swt1_mc_final` | `94_02_swt1_mc_final_mesh3` |
| SW-T2 | BBFast | `93_03_..._ppfix` | `93_04_..._ppfix_mesh3` |
| SW-T2 | MC | `94_03_swt2_mc_final` | `94_04_swt2_mc_final_mesh3` |
| SW-S3 | BBFast | `93_05_..._ppfix` | `93_06_..._ppfix_mesh3` |
| SW-S3 | MC | `94_05_sw3_mc_final` | `94_06_sw3_mc_final_mesh3` |
| SW-S4 | BBFast | `93_07_..._ppfix` | `93_08_..._ppfix_mesh3` |
| SW-S4 | MC | `94_07_sw4_mc_final` | `94_08_sw4_mc_final_mesh3` |

Note the direction: **mesh 3 is the FINE mesh** — roughly ten times the element
count; mesh 5 is what the paper reports. "3" and "5" are the **Cubit auto-size
factor** in the journals (`vol all size auto factor N`), a coarseness index, not
an element length in millimetres. Measured instead: at factor 5 the SW-S3
fracture carries 457 interface nodes over 4.0e-3 m² (areal spacing near 3 mm) and
the SW-T1 fracture-line node pitch is 4.33 mm, so factor-5 edges are 3–4 mm and
factor-3 edges are about half that.

All eight mesh-3 decks already existed. Each was diffed against its mesh-5 parent
with comments stripped, and the only surviving differences are the mesh file, the
source-node coordinates (mesh-resolution dependent by construction) and the output
basenames — plus one benign extra noted in §5. So any difference in the results is
discretisation and nothing else, which is the entire point.

**Resourcing**, `scripts/make_mesh3_convergence_jobs.py`: 128 ranks, 128 G, 2 days,
one node. The previous attempt ran 64/64 G/48 h and three of four specimens died —
SW-T2 at stage 4 of 11, SW-S3 at stage 6, and SW-T1 at t = 70.5 s of 3500, still
inside the confining preload. Wall time was already at its ceiling, so the lever is
width and memory.

---

## 5. Two defects found while verifying the twins, and one difference left alone

**Fixed — four decks wrote to another deck's `file_base`.** `93_02` and `94_02` both
named `91_02_swt1_bbfast_..._hpc`; `93_06` and `94_06` both named
`92_03_sw3_final_paperjrc_resc1p40_hpc`. Two errors on the same three lines: the
mesh-5 grandparent's name, inherited when each deck was cut, and then in the MC decks
a *Barton–Bandis* name on a *Mohr–Coulomb* run. Within each specimen the BBFast and
MC mesh-3 decks pointed at the same three files and would have overwritten each other.

No result on disk is affected: the SLURM scripts override `csv_file_base` and
`exodus_file_base` on the command line, and that is what every completed run used. But
`checkpoint_file_base` was never overridden, and any local run would have collided
outright. All four now name themselves; all four re-pass `--check-input`.

**Fixed — the generator that caused the 97/98 truncation.**
`scripts/make_hpc_nochk_jobs.py` rewrote `--time` and nothing else, so jobs silently
inherited the template's `--ntasks` and `srun -n`. Rank count appears twice in every
script and a file where the two disagree is not mis-resourced but wrong: SLURM
allocates one number and MPI launches the other. Both generators now go through
`scripts/set_hpc_resources.retarget`, which rewrites `--ntasks`, `--mem`, `--time` and
`srun -n` together and reads its own output back to prove the two rank counts agree.

**Left alone — SW-S3's `end_time` is 4802 on mesh 5 and 4803 on mesh 3.** Stage 11
sits at t = 4802.4 s, so the mesh-3 deck covers it outright while the mesh-5 deck
needs `table2_gate`'s two-interval grace window. The difference is one second at the
very end of unloading and it favours the finer mesh; changing the mesh-5 value would
invalidate a completed reported run for nothing.

**Carried forward — SW-T1's convergence pair is not purely a mesh comparison.** Its
mesh-5 source separation is 69.335 mm against 72.690 intended, and mesh 3 reaches
71.501 mm, so the pair carries a 3.1 % source-separation difference that is not
discretisation. `Q` enters through `pp_drop_pp`, so expect a first-order `Q` effect of
that size and do not read it as mesh error.

---

## 6. What to do when the runs land

`scripts/update_table2_ranking.py --write` rescores everything and will pick the
mesh-3 rows up automatically. Then, per specimen and law, compare mean nRMSE against
the mesh-5 parent.

> **RESOLVED 2026-08-25.** All four BBFast pairs have now completed eleven stages:
> SW-T1 4.44 → 5.53, SW-T2 2.43 → 2.26, SW-S3 4.58 → 4.76, SW-S4 6.14 → 6.29. The MC
> siblings are complete only on SW-S4 (7.07 → 6.85); SW-S3's reaches stage 6, SW-T2's
> stage 4, SW-T1's the preload only. The changes are not one-signed and individual
> channels move in opposite directions within a specimen, so the manuscript reports a
> bound rather than a convergence order (§5.1).
>
> **The SW-S3 `tau` watch fired.** It improves 8.01 → 5.69 at mesh 3 — about 29 % of
> that residual is discretisation compliance, not the loading frame. `SWS3_FINAL.md`
> §5(b) has been revised accordingly: the stiffness-deficit diagnosis stands, the
> "non-tunable" qualifier does not.
