# Biot coefficient A/B study — SW-S3, SW-T1, SW-T2 — 2026-08-15

Six full-length mesh-5 runs, local, four concurrent at 8 MPI ranks each. Three A/B pairs,
each pair identical except for `biot_coefficient`.

**Status: campaign in flight.** Method, deck integrity and the analytical part of the result
are settled and recorded below; the Table-2 scores are filled in as pairs complete.

---

## 1. What is being tested

`SWS3`, `SWT1` and `SWT2` all carry `biot_coefficient = 1e-12` against `initial_porosity =
0.001`. **SW-S4 already carries `biot_coefficient = 0.6`** — so this campaign is not
introducing a new value, it is asking whether the other three samples should be brought to
the one SW-S4 already uses and was validated with.

| pair | sample | baseline (A) | fixed (B) | law |
|---|---|---|---|---|
| 1 | SW-S3 | `84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV` | `…_biot0p6` | BBFast |
| 2 | SW-T1 | `Ye2018_SWT1_BBFast_sweep_19_…_Kinematic_IOsafe_kernel_SV` | `…_biot0p6` | BBFast |
| 3 | SW-T2 | `Ye2018_SWT2_BBFast_sweep_21_…_BBhyd_IOsafe_kernel_SV` | `…_biot0p6` | BBFast |

All six use the combined mass kernel
`OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel` (kernel_SV).

### Deck integrity

Verified by diff: each pair differs in **exactly three things** — the `biot_coefficient`
line, the provenance header, and the three `*_file_base` output paths. Nothing else. Any
difference in the results is attributable to α alone.

---

## 2. Why α = 1e-12 is wrong, quantitatively

Biot's coefficient cannot be smaller than porosity. Beyond that statement of principle, the
value has a concrete and measurable effect here, because `OrcaTHMaterial` builds the storage
term as

```
1/M = (1 - α)(α - φ)/K_d + φ/K_f
```

(`src/materials/THMaterial/OrcaTHMaterial.C`, `computeBiotModulus`), with `K_d = E/(3(1-2ν))`,
`φ = 0.001`, `K_f = 4.7836 GPa`, `ν = 0.32`.

| sample | E (GPa) | K_d (GPa) | 1/M at α=1e-12 | 1/M at α=0.6 | M falls by |
|---|---|---|---|---|---|
| SW-S3 | 75 | 69.44 | 1.946e-13 | 3.659e-12 | **18.8×** |
| SW-T1 | 67 | 62.04 | 1.929e-13 | 4.071e-12 | **21.1×** |
| SW-T2 | 67 | 62.04 | 1.929e-13 | 4.071e-12 | **21.1×** |

Two consequences, and the second is the sharper one:

1. **Storage compliance changes by a factor of ~20.** This is a recalibration, not a
   normalisation. Onset timing and the strength-envelope tuning were fitted at α=1e-12 and
   will not carry over unchanged. A shift in slip-event timing in arm B is therefore an
   expected consequence, not evidence of a bug.

2. **At α=1e-12 the grain-compressibility term carries the wrong sign.** Because α < φ, the
   factor `(α - φ)` is negative, so the term evaluates to −1.44e-14 (SW-S3) rather than a
   positive storage contribution — it *subtracts* 6.9 % of the fluid storage term instead of
   adding to it. The net 1/M stays positive only because the fluid term dominates. So α=1e-12
   is not merely "poroelastically decoupled" (the usual way of describing it); it is
   contributing spurious negative storage.

Also at α=1e-12 the pore pressure does not enter the bulk effective stress and bulk strain
does not drive fluid, so the matrix is poroelastically inert and all coupling is carried by
the fracture.

---

## 3. How the runs are scored

`scripts/table2_gate.py` (commit `0cbc441`, branch `orca_v3`) scores a run against
Ye & Ghassemi (2018) Table 2 for any of the four samples.

**Five observables, not eight.** Table 2 lists eight quantities per stage, but the paper
back-computes a_h from the measured Q through the cubic law and then defines k = a_h²/12, so
those two carry no information beyond Q. Scored: **Q, σ'_n, τ, d_n, d_s**. Reported but not
scored: a_h, k.

**Stage detection had to be rebuilt.** The pre-existing SW-S4 script detects hold stages as
plateaus in the deck's `[injection_pressure]` function. That does not generalise: SW-T1/SW-T2
use clean staircases whose plateaus sit exactly on the targets, but SW-S3 and SW-S4 use
digitized schedules, and SW-S3 has flat runs for only about six of the eleven stages. The
gate instead splits the schedule at its peak plateau and walks the eleven targets behind a
monotonic cursor. Verified on all four decks — eleven monotonic stages each:

| sample | schedule | peak | stage-6 time |
|---|---|---|---|
| SW-S3 | digitized | 28.57 MPa | 2699.0 s |
| SW-S4 | digitized | 27.96 MPa | 1788.0 s |
| SW-T1 | staircase | 28.00 MPa | 1955.0 s |
| SW-T2 | staircase | 28.00 MPa | 2541.0 s |

Two bugs were found and fixed while building it, both landing on stage 6 — the slip event,
the stage that matters most:

- `np.argmax` returns the **first** index attaining the maximum, so a tolerance search
  bounded above by it can only ever return the **start** of the 28 MPa hold on a staircase.
  SW-T1 stage 6 resolved to t=1824 (hold start) instead of t=1955 (hold end) — sampling the
  slip event before it happened.
- Sharing one tolerance between target-matching (0.35 MPa) and plateau membership let the
  wide value swallow the ramp points either side of the peak, putting SW-S4 stage 6 at
  t=1821.7 — 67 s past the hold, at 27.79 MPa on the way back down. Plateau membership now
  uses a 1 kPa flatness tolerance.

**Displacement datum.** Table 2 reports d_n = d_s = 0.000 at stage 1 for all four samples, so
the model is zeroed at stage 1 rather than at a preload timestamp — each deck's preload end
differs, and SW-T1's notebook `PRELOAD_END_S = 55.0` disagrees with its own deck's first
plateau ending at 75.0. Cost: stage 1 is zero by construction and so is **excluded** from the
d_n/d_s summary rather than left in to flatter the mean.

### Gate validated on a known result

Run against the three completed v27 SW-S4 runs: 11/11 stages resolved, reading the same
`czm_*` channels the notebook promotion gate uses. The MC vs BBFast comparison independently
reproduces the v27 finding — the two laws are identical through stage 4 and diverge only from
stage 5 (24 MPa loading) onward.

| observable | MC MAE | BBFast MAE | closer |
|---|---|---|---|
| Q (mL/min) | 0.00323 | 0.00255 | BBFast |
| σ'_n (MPa) | 0.340 | 0.393 | MC |
| τ (MPa) | 0.614 | 0.496 | BBFast |
| d_n (mm) | 0.00319 | 0.00144 | BBFast |
| d_s (mm) | 0.00138 | 0.00345 | MC |

---

## 4. Results

### 4.1 SW-S3 — both arms past the slip event (2026-08-16 05:2x)

Both arms have cleared stage 6, so the decisive comparison is available. Aggregated over the
six stages common to both, `α=1e-12` is closer on **every** observable:

| observable | α=1e-12 MAE | α=0.6 MAE | |
|---|---|---|---|
| Q (mL/min) | 0.0120 | 0.0761 | α=1e-12 closer (84.2 % lower) |
| σ'_n (MPa) | 0.166 | 1.082 | α=1e-12 closer (84.7 % lower) |
| τ (MPa) | 0.342 | 1.975 | α=1e-12 closer (82.7 % lower) |
| d_n (mm) | 0.00102 | 0.01049 | α=1e-12 closer (90.3 % lower) |
| d_s (mm) | 0.00070 | 0.01867 | α=1e-12 closer (96.3 % lower) |

**That aggregate is misleading on its own, and the per-stage breakdown is the real result.**
Essentially the entire difference comes from one stage:

| stage 5 (24 MPa) | α=1e-12 | α=0.6 | paper |
|---|---|---|---|
| d_s (mm) | 0.00057 | **0.0725** | 0.001 |
| d_n (mm) | −0.0020 | **−0.0401** | 0.000 |
| τ (MPa) | 14.67 | **5.86** | 14.26 |
| σ'_n (MPa) | 23.64 | 18.75 | 23.42 |
| Q (mL/min) | 0.190 | 0.471 | 0.150 |

**At α=0.6 the fault slips one full stage early — at 24 MPa instead of 28.** By stage 5 the
α=0.6 arm has already slipped ~0.072 mm, dilated ~0.040 mm and dropped its shear stress from
~15 to 5.9 MPa, while the paper (and the baseline) still have it locked. At stage 6 the α=0.6
arm is actually *closer* than baseline on σ'_n (−0.47) and τ (−0.98), because by then both
have slipped.

**The stresses re-converge; the kinematics do not.** With stage 7 (first unloading, 24 MPa)
now available on both arms, the two error signatures separate cleanly:

| B − A at stage | σ'_n (MPa) | τ (MPa) | d_s (mm) | d_n (mm) |
|---|---|---|---|---|
| 5 (premature slip) | +4.46 | +7.99 | +0.0711 | +0.0381 |
| 6 (both slipped) | −0.47 | −0.98 | **+0.01878** | +0.0095 |
| 7 (unloading, 24) | +0.33 | +0.68 | **+0.01875** | +0.0089 |
| 8 (unloading, 20) | +0.69 | +1.24 | **+0.01873** | +0.0068 |

Three distinct behaviours, and they separate cleanly:

- **Slip offset is frozen.** d_s holds at +0.01878 → +0.01875 → +0.01873 mm across three
  stages — constant to 0.3 %. Slip is irreversible, so the displacement banked during the
  premature event at 24 MPa is never given back. This is why d_s stays the worst-scoring
  observable (96 % higher MAE) even where the stresses agree.
- **Dilation partially recovers.** d_n decays +0.0095 → +0.0089 → +0.0068 mm as normal stress
  rises through unloading and closes the aperture elastically — the reversible part of the
  offset.
- **Stresses re-converge, then drift again.** The σ'_n and τ gaps collapse from 4.5/8.0 MPa at
  stage 5 to a few tenths at stage 6–7, then widen modestly by stage 8 (+0.69/+1.24).

**Not a reporting artifact.** The paper-frame postprocessors are pure geometry on
`differential_stress_reaction_mpa_pp` — `σ'_n = 30 − 0.5(p_inj+p_out)·1e-6 + 0.235·Δσ` and
`τ = 0.424·Δσ` — with no `biot_coefficient` anywhere in them, and they use the correct
load-cell channel rather than the σ₃-hardcoded trap. The shift is physical.

### 4.2 What this does and does not establish

**It does not establish that α=1e-12 is right.** It remains unphysical — below porosity, with
the negative grain-storage term of §2. What the campaign establishes is narrower and more
useful:

> The deck's slip-onset calibration is **entangled with α**. Swapping α from 1e-12 to 0.6
> while holding everything else fixed moves the slip event one stage earlier, so α cannot be
> corrected on its own.

This is the outcome §2 anticipated ("a shift in slip-event timing in arm B is an expected
consequence, not evidence of a bug") — now measured rather than predicted. Two mechanisms act
together, and this campaign does not separate them:

1. **Storage compliance rises 18.8×**, changing how fast pressure builds at the fault.
2. **Pore pressure enters the bulk effective stress at all.** At α=1e-12 the matrix is
   poroelastically inert; at α=0.6 the effective-stress path itself changes. The systematic
   pre-slip drift in stages 1–4 — σ'_n error growing +0.22 → +0.73 MPa and τ +0.35 → +1.36 MPa
   — is that coupling switching on, visible well before any slip.

**Consequence for the paper:** fixing α to a physical value requires **re-fitting the
slip-onset envelope at that α**. It is not a parameter that can be corrected in isolation.
That is a new task, not a result of this one.

### 4.3 The shear-traction overshoot is independent of α

At stage 6 both samples under-predict the co-seismic stress drop by about the same amount,
*at different α*:

| stage 6 | model τ | paper τ | overshoot |
|---|---|---|---|
| SW-S3 (α=1e-12) | 4.585 | 3.55 | +29.2 % |
| SW-S4 v27 (α=0.6) | 4.104 | 3.12 | +31.5 % |

Since SW-S4 already runs at α=0.6 and shows the same ~30 % overshoot, **α is not the cause**
and the A/B cannot fix it. This belongs to the strength envelope (task #15). SW-S4's unloading
branch shows the model relaxing back toward the paper (+23.6 % at stage 7 → +8 % at stage 11),
so it is specifically the *drop* that is under-predicted, not the residual level.

### 4.4 Baseline SW-S3 quality through stage 6

For the record, the α=1e-12 arm against Table 2 at the slip event: Q +1.3 %, σ'_n +3.3 %,
d_n +3.1 %, d_s +2.9 %, τ +29.2 %. Against the promotion gates, dilation is **5/5 in gate**
(±0.003 mm) and slip **4/5**, the single miss being stage 6 at 0.00206 mm against a ±0.002 mm
gate — over by 60 nm.

### 4.5 Still outstanding

- **SW-T1** — both arms still inside the hand-placed `event_dt_cap` bracket (dt = 0.05 over
  t ∈ [1740, 1825]), running ~0.2 s of simulated time per wall minute. Stage 6 not reached.
- **SW-T2** — never started; it waits on SW-T1's ranks. Six full-length decks at 8 MPI ranks
  do not fit concurrently in 32 cores.
- **SW-S3 unloading branch** (stages 7–11) — baseline is past the event and accelerating
  (~8.5 s/min); the α=0.6 arm trails.

Nothing failed: **zero non-convergence and zero exceptions on all four arms** for the whole
campaign, including through the slip event.

---

## 5. Scope

Mesh 5 only. The mesh-3 deck set exists and is committed (§H of `TODO.md`) but is not run
here — it needs more memory than this machine has, and the user is running it separately.
