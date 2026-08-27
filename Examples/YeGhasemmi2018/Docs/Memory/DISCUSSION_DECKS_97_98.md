# The 97 (cyclic) and 98 (shut-in) discussion decks

> **SUPERSEDED 2026-08-22 by the 101-series** (`DISCUSSION_101_RESULTS.md`), and
> then extended by the 104-series (`DISCUSSION_104_RESULTS.md`). Two independent
> problems retire this batch's numbers; the deck design and the reasoning below
> are still the right ones and were inherited by the 101 build.
>
> **1. Truncation.** Three of the four 97-series runs were killed by their
> wall-clock allocation — SW-T1 at 9088 s of 10 375, SW-T2 at 10 960 of 13 882,
> SW-S3 at 6214 of 15 793 — so SW-S3 contributed one cycle and could not test
> outcome 3 at all. Root cause: `scripts/make_hpc_nochk_jobs.py` rewrites only
> `--time` when it regenerates a job script, leaving `--ntasks` and the
> `srun -n` line at whatever the template carried. **That script is still
> unfixed and will silently under-resource any future batch generated through
> it.** The 101 and 104 SLURM scripts bypass it (`build_101_decks.py` emits 32
> ranks directly), which is why that batch completed 16 of 16.
>
> **2. A metric bug in the retained-permeability column.** The "retained $k$ at
> matched $\sigma'_n$" values reported for the 98-series — and carried into
> Table 12 of the manuscript as 5.52 / 4.03 / 1.50 / 0.91 — are wrong on both
> tensile specimens. Recomputing the same four runs with the corrected reader
> gives **1.605 / 1.450 / 1.497 / 0.893**. The matched state was found by
> nearest-neighbour search over a window in which $\sigma'_n$ is *not monotonic*
> (the confining preload ramps it up before injection brings it back down), so
> the reference could be drawn from the preload ramp instead of the injection
> branch. No committed script produced those numbers — they were computed ad
> hoc, which is why the error survived review. See `DISCUSSION_104_RESULTS.md`
> §0. The fix is in `scripts/analyze_101.py::interpolate_at_sigma`.

2026-08-18. Branch `orca_v6`, repo `orca_4.0`. Built by
`scripts/build_cyclic_shutin_decks.py`. Companion to `MC_BASELINE_94_SERIES.md`
and `HPC_90_91_92_TABLE2_ERROR_ANALYSIS.md`.

These are the paper's **discussion-section** runs. The 93-series remains the
validation set and the 94-series the constitutive baseline.

---

## 1. Scope, and the one thing that must not be done with them

**Neither series is scoreable against Table 2.** Table 2 is stage-wise data
recorded under Ye & Ghassemi's own monotonic injection history. Both series
deliberately replace that history, so `scripts/table2_gate.py` does not apply and
must not be run on them. Their observables are defined in §4.

| series | decks | question |
|---|---|---|
| 97 | 4 (one per specimen) | How much permeability enhancement is retained after the **first** cycle, and does it keep accumulating on cycles 2 and 3 or saturate? |
| 98 | 4 (one per specimen) | Once the injection pressure is back near ambient, does slip keep growing (delayed reactivation) or arrest promptly? |

---

## 2. What changes from the 93-series parent

Exactly three things: the `[injection_pressure]` function, `end_time`, and the
three output file bases. Every constitutive parameter, the mesh, the source
nodesets and their coordinates, the boundary conditions, the paper-frame trig
constants, the flow constants and the solver are byte-identical to the validated
parent. A 93/97 or 93/98 pair therefore isolates the **loading history** and
nothing else.

This is the same minimal-diff recipe the 68-series prototypes used
(`68_02_..._cyclic` / `_shutin`), which are the design reference. Those two decks
could not be reused: they sit on the 68 deck generation, which predates the θ30
mesh, the `ppfix` reporting frame and `JRC = 5`.

| specimen | parent (validated) | 97 cyclic | 98 shut-in |
|---|---|---|---|
| SW-T1 | `93_01_swt1_final_c26p9_resc9p19_ppfix` | `97_01_swt1_cyclic3` | `98_01_swt1_shutin` |
| SW-T2 | `93_03_swt2_final_theta30_resc9p71_ppfix` | `97_02_swt2_cyclic3` | `98_02_swt2_shutin` |
| SW-S3 | `93_05_sw3_final_resc1p40_ppfix` | `97_03_sw3_cyclic3` | `98_03_sw3_shutin` |
| SW-S4 | `93_07_sw4_final_theta30_jrc5_ppfix` | `97_04_sw4_cyclic3` | `98_04_sw4_shutin` |

All eight pass `orca-opt --check-input` (`rc = 0`, `Syntax OK`, zero error lines).

---

## 3. Schedule design

### 3.1 Constants measured from the parents, not chosen

`P_ambient`, `P_peak` and `t_peak` are read off each parent's own digitized
`[injection_pressure]` schedule:

| specimen | P_amb (MPa) | P_peak (MPa) | t_peak (s) | ramp rate R (kPa/s) |
|---|---|---|---|---|
| SW-T1 | 5.00 | 28.00 | 1640.0 | 14.04 |
| SW-T2 | 5.00 | 28.00 | 2280.0 | 10.10 |
| SW-S3 | 5.75 | 28.57 | 2569.2 | 8.89 |
| SW-S4 | 5.00 | 27.96 | 1720.7 | 13.36 |

`P_floor = 8.0 MPa` is likewise the paper's own value: all four digitized
schedules bleed back to 7.88–8.00 MPa after their peak.

### 3.2 Cyclic (97): three **equal-peak** cycles

Each cycle ramps to the specimen's own `P_peak`, holds 200 s, bleeds to the
8 MPa floor at the same rate, holds 200 s. After cycle 3 a final bleed to
ambient. Sixteen knots, `PiecewiseLinear`.

**Why equal peaks and not an increasing staircase.** The 68-series prototype
ramped to 15/20/24/28 MPa on successive cycles. That confounds two effects —
enhancement from *cycling*, and enhancement from simply reaching a higher
pressure than before. Holding the peak fixed isolates the first, which is the
question being asked.

**Why the holds matter.** The permeability probe has to be taken at the *same*
pressure in every cycle or the comparison is confounded by the elastic part of
the closure law. Each cycle therefore holds at both the peak and the floor, and
the enhancement is read there. The holds are also where slip velocity relaxes to
zero, so the reading is insensitive to the Perzyna `tangential_viscosity`
overstress `eta*V` — a first-order term on the ramps (0.31 MPa mean, 0.87 MPa
peak on SW-S4; see the memory note *tangential-viscosity-is-the-hidden-rate-law*).

### 3.3 Shut-in (98): ramp, hold, exponential fall-off

`ParsedFunction`: ambient to `t = 2`; ramp to `P_peak` over `t = 2 .. t_peak` at
the parent's rate; hold 200 s (past onset); then relax exponentially toward
ambient with `tau = 150 s`, a standard proxy for wellbore pressure fall-off.
`end_time` gives 3000 s of post-shut-in observation.

### 3.4 Why the calibrated ramp rate is preserved

Each specimen ramps at its **own** `R`, not at a common convenient rate. The
model has a genuine rate dependence, so a cyclic run at a different loading rate
than the validation run would not be comparable to it. The cost is wall time and
it is affordable — see §5.

### 3.5 Cost

| deck | end_time (s) | est. wall (h) |
|---|---|---|
| `97_01_swt1_cyclic3` | 10375 | 5.3 |
| `97_02_swt2_cyclic3` | 13882 | 7.1 |
| `97_03_sw3_cyclic3` | 15793 | 8.1 |
| `97_04_sw4_cyclic3` | 10816 | 5.6 |
| `98_01_swt1_shutin` | 4840 | 2.5 |
| `98_02_swt2_shutin` | 5480 | 2.8 |
| `98_03_sw3_shutin` | 5769 | 3.0 |
| `98_04_sw4_shutin` | 4921 | 2.5 |

Estimated from the measured rate of `93_05` (SW-S3, mesh 5): **8877 s of wall
time for 4802 s of simulated time on 32 ranks**, i.e. ~1.85 s wall per simulated
second. The longest deck is ~8 h, so the standard 24 h / 32 rank / 32 G job is
right with better than 2× margin.

---

## 4. What to measure (these replace the Table-2 gate)

### Cyclic — permeability enhancement

Read at the **hold** instants, where pressure is identical cycle to cycle:

1. `hydraulic_aperture_pp` and `flow_rate_validation_ml_min_pp` at each peak hold
   and each floor hold. The headline number is the **floor-to-floor ratio**,
   cycle 1 → cycle 3: enhancement retained at the *same low pressure* is
   irreversible enhancement, which is the quantity of interest.
2. Whether the increment saturates. Equal peaks mean cycle 2 and cycle 3 add
   nothing unless a genuinely path-dependent mechanism is active. A saturating
   series and a linearly accumulating series are different physical claims.
3. `czm_normal_dilation_paper_mm_pp` retained at each floor — the mechanical
   counterpart, and the channel that distinguishes dilation-driven enhancement
   from roughness-damage-driven enhancement.
4. `bb_roughness_state_pp` and `bb_dilation_angle_pp` per cycle, to attribute (3).

**Expect the specimens to disagree, and expect SW-S4 to disagree most.** Its
`dilation_scale` was cut ~17× to hold the hydraulic aperture at an earlier fit,
which decoupled `a_h` from the mechanical opening: `r(a_h, d_n)` is 1.000 / 0.999
/ 0.946 / **0.562** across T1 / T2 / S3 / S4. On SW-S4 the flow channel reports a
stress state, not an opening. Read items 1 and 3 as **separate** results there
rather than as one story — see the memory note
*ye2018-q-is-a-stress-readout-not-an-aperture-one*.

### Shut-in — delayed reactivation

1. Does `reported_czm_shear_slip_mm_pp` keep rising after `injection_pressure_pp`
   has returned to near ambient? That is the headline yes/no.
2. Lag between the shut-in instant and the peak slip rate.
3. Residual `hydraulic_aperture_pp` at `end_time` versus its pre-injection value.

---

## 5. Caveats to carry into the write-up

**SW-S4 inherits fitted, time-anchored loading-frame terms.** Its parent carries
an axial piston relaxation from `relax_t0 = 1000 s` over 800 s and a confinement
bleed from `side_unload_t0 = 1900 s` over 1400 s. Both are `min(...,1)`-bounded,
so they saturate and then hold — nothing runs away on a longer run. But they were
fitted to the paper's schedule, and on a ~10.8 ks cyclic history they sit at
their saturated values for two thirds of the run. This is a property of the
inherited deck, not of the cyclic schedule, and it should be stated rather than
silently inherited. The other three specimens have no such terms.

**Cycles 2 and 3 start from the 8 MPa floor, not from ambient.** So cycle 1's
up-leg is longer than cycles 2 and 3's. This is deliberate — it matches the
paper's own post-peak floor and avoids a full depressurisation that would
re-seat the joint — but it means cycle 1 is not exactly the same excursion as
cycles 2 and 3 in *pressure range*, only in peak. Compare floor-to-floor.

---

## 6. Submission

```bash
bash Examples/YeGhasemmi2018/submit_discussion_97_98.sh
```

Eight jobs, 32 ranks / 32 G / 24 h each. They are independent of the 94-series
MC baseline and of each other, so submission order does not matter.
