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

*Pending — filled in as pairs complete. SW-S3 is the long pole (4802 s of simulated time);
SW-T1 and SW-T2 run to 3500 s and 2852 s.*

---

## 5. Scope

Mesh 5 only. The mesh-3 deck set exists and is committed (§H of `TODO.md`) but is not run
here — it needs more memory than this machine has, and the user is running it separately.
