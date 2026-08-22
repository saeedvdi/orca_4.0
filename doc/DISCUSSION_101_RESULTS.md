# 101-series results — cyclic stimulation, shut-in, and the frame-stiffness bracket

All 16 decks ran to their scheduled end time (`DISCUSSION_101_RUN_INDEX.csv`:
16 complete, 0 partial, 0 missing). This is the batch the 97/98 attempt was
supposed to be and was truncated out of; the resourcing root cause is recorded in
`DISCUSSION_DECKS_101.md`.

Metrics are the ones preregistered in `DISCUSSION_DECKS_101.md`, computed by
`scripts/analyze_101.py` into three CSVs under `doc/independent_analysis/`.

These decks replace the paper's monotonic schedule, so **they are not scoreable
against Table 2** and carry no nRMSE. They answer mechanism questions, not
accuracy questions.

---

## 1. Equal-peak cycling does not ratchet

Group A: three identical cycles between ambient and the specimen's peak
injection pressure. Cycle 3 versus cycle 1, at the *same* hold in each cycle:

| specimen | hold | aperture | Q | k | Δslip | W |
|---|---|---:|---:|---:|---:|---:|
| SW-T1 | peak | ×1.00000 | ×1.00001 | ×1.00002 | +0.007 µm | 0.0028 |
| SW-T1 | floor | ×1.00000 | ×0.99999 | ×1.00000 | +0.004 µm | 0.0028 |
| SW-T2 | peak | ×1.00000 | ×0.99999 | ×1.00000 | +0.001 µm | 0.0016 |
| SW-S3 | peak | ×1.00967 | ×1.02928 | ×1.02045 | −0.052 µm | 0.2684 |
| SW-S4 | peak | ×1.00165 | ×1.00497 | ×1.00327 | +0.550 µm | 0.2762 |

The joint shakes down inside cycle 1 and every later cycle retraces it. The
largest residual motion anywhere in the group is 0.55 µm of slip on SW-S4, and
the largest flow change is +2.9% on SW-S3 — and that one is spent entirely
between cycles 1 and 2, with cycle 3 adding +0.01%.

The weakening state explains why. SW-T1 and SW-T2 reach W = 0.003 and 0.002 in
the first cycle: they are already at residual strength, so there is nothing left
to weaken. SW-S3 and SW-S4 stop at W ≈ 0.27 and hold it unchanged across cycles
2 and 3.

**Cycling at or below a pressure the fracture has already seen does essentially
nothing.**

## 2. Escalating peaks do everything

Group B: same three cycles, but peaking at P_peak−4, P_peak−2, P_peak. Compared
at the **floor** hold, which is ambient (8.0 MPa) in every cycle and therefore
the only pressure-matched comparison in this group:

| specimen | aperture | Q | k | Δslip |
|---|---:|---:|---:|---:|
| SW-T1 | ×2.327 | ×12.61 | ×5.563 | +525.4 µm |
| SW-T2 | ×2.017 | ×8.21 | ×4.121 | +559.5 µm |
| SW-S3 | ×1.227 | ×1.85 | ×1.498 | +57.0 µm |
| SW-S4 | ×1.034 | ×1.10 | ×1.069 | +17.7 µm |

Same number of cycles, same fluid, same end pressure as group A. The only
difference is that each cycle in group B breaks new ground, and permeability at
matched ambient conditions rises by up to a factor of 5.6.

The peak-hold ratios in `DISCUSSION_101_CYCLIC_METRICS.csv` are larger still
(up to ×19.9 on Q) but those holds sit at different pressures by construction and
should not be quoted as irreversible change. The floor-hold numbers above are the
defensible ones.

**It is not the number of cycles that matters, it is whether a cycle exceeds the
previous maximum** — a Kaiser / preconsolidation statement for hydraulic
stimulation.

## 3. Path independence, and the one specimen that breaks it

Group B cycle 3 and group A cycle 1 end at the same injection pressure by
different routes — a staircase versus a single monotonic ramp. Do they arrive at
the same state?

| specimen | aperture | Q | slip | W | verdict |
|---|---:|---:|---:|---:|---|
| SW-T1 | −0.000% | −0.000% | −0.000% | +0.000% | identical |
| SW-T2 | −0.000% | −0.001% | −0.000% | +0.002% | identical |
| SW-S4 | +0.015% | +0.045% | +0.055% | −0.080% | identical |
| SW-S3 | −3.32% | **−9.64%** | **−19.0%** | **+41.2%** | path-dependent |

Three of four are path-independent to five decimal places. SW-S3 is not: reached
by the staircase it ends *less* slipped, *less* weakened and *less* permeable
than the same specimen taken there in one ramp.

The discriminator is in the data. Strength margin at the peak hold — zero means
sitting on the yield surface:

```
group A   SW-T1  -0.00002   SW-T2  +0.00002   SW-S4  -0.00009   SW-S3  +0.67792
group B   SW-T1  -0.00002   SW-T2  +0.00002   SW-S4  -0.03334   SW-S3  -0.00088
```

SW-S3 is the only specimen that arrests *below* yield, and only on the monotonic
path. A joint that ends on the yield surface is at an attractor fixed by pressure
alone, so its history cannot be read off its final state. A joint that arrests
strictly below yield stopped where its own slip put it, and remembers the route.

The mechanism is loading-frame compliance: slip relieves the driving shear
stress. The monotonic ramp overshoots, slips 74 µm, sheds enough shear stress to
lock up 0.68 MPa below yield. The staircase creeps up in three steps, slips only
60 µm, sheds less, and finishes exactly on yield. This is the same lever that
group E measures directly.

**Staged pressurisation suppressed induced slip by 19% relative to a single ramp
to the same pressure — but only in the one specimen that arrests below yield.**
That is a narrower claim than the cyclic-soft-stimulation literature usually
makes, and it comes with a stated precondition that can be checked.

## 4. Shut-in: no delayed slip, but the permeability is kept

Groups C and D. Post-shut-in slip growth, over 2 400–6 000 s of observation:

| specimen | design | slip at shut-in | max growth after | net to end |
|---|---|---:|---:|---:|
| SW-T1 | τ=150 s | 0.532146 mm | +0.084 µm | −0.134 µm |
| SW-T2 | τ=150 s | 0.569388 mm | +0.002 µm | −0.150 µm |
| SW-S3 | τ=150 s | 0.074182 mm | +0.000 µm | −0.351 µm |
| SW-S4 | τ=150 s | 0.090705 mm | +0.212 µm | +0.005 µm |
| SW-T1 | τ=1500 s | 0.533931 mm | +0.000 µm | −0.222 µm |
| SW-S4 | τ=1500 s | 0.094088 mm | +0.002 µm | −0.223 µm |

Nothing. The largest post-shut-in advance anywhere is 0.21 µm, and the net motion
is *negative* on five of six — elastic recovery, not creep. The global maximum
slip rate always precedes shut-in (lag −62 to −617 s).

**This model produces no trailing seismicity.** That is a real limitation to
state rather than a result to celebrate: the mechanisms usually invoked for
post-shut-in events — pressure diffusion to a distant asperity, rate-and-state
healing, poroelastic stress transfer beyond the sample — are either absent at
sample scale or, in the case of rate-and-state, were built and tested in this
campaign and found not to heal the holds.

Retained permeability at **matched effective normal stress** (end state compared
against the loading path at the same σ'ₙ, so elastic closure is differenced out):

| specimen | σ'ₙ matched | aperture ratio | **k ratio** |
|---|---:|---:|---:|
| SW-T1 | 43.14 MPa | ×1.250 | **×1.609** |
| SW-T2 | 40.90 MPa | ×1.195 | **×1.459** |
| SW-S3 | 26.16 MPa | ×1.227 | **×1.497** |
| SW-S4 | 25.73 MPa | ×0.932 | **×0.859** |
| SW-T1 τ=1500 s | 42.86 MPa | ×1.240 | **×1.584** |
| SW-S4 τ=1500 s | 25.32 MPa | ×0.929 | **×0.855** |

Three specimens self-prop: after the pressure is removed they are 46–61% more
permeable than they were passing through the same stress on the way up. A ten-fold
change in shut-in decay time moves this by less than 2% (1.609 → 1.584;
0.859 → 0.855), so the retention is rate-independent over the range tested.

**SW-S4 does the opposite — it grinds shut, ×0.86.**

### Why SW-S4 loses what the others keep

My first explanation was roughness destruction, and the data falsify it. All four
degrade, and SW-S3 degrades *most* while still gaining permeability:

```
SW-T1  roughness_state 0.2246 -> 0.1264  (-43.7%)   slip 532 um   k x1.609
SW-T2                  0.1882 -> 0.1206  (-35.9%)   slip 569 um   k x1.459
SW-S3                  0.6400 -> 0.1862  (-70.9%)   slip  74 um   k x1.497
SW-S4                  0.4478 -> 0.2128  (-52.5%)   slip  91 um   k x0.859
```

The sign is set by the *balance* between the aperture that shear dilation adds
and the aperture that roughness loss takes away — not by either alone. SW-S4 is
the specimen whose dilation contribution was cut by a factor of 17 during
calibration, so it is the only one where the loss term wins.

That makes the closure result **calibration-driven, not a prediction of the
constitutive law**, and it should be reported that way. It is also consistent
with the independently established fact that SW-S4's Q is a stress readout rather
than an aperture readout (r = 0.562 against d_n, where SW-T1/T2 give r = 1.000).

## 5. The frame-stiffness bracket, and what it costs the paper

Group E re-runs SW-T1's equal-peak cycling at ×2 and ×0.5 the loading-frame
stiffness. That constant is *derived* from the paper's Table 2, not measured, so
this is the honest uncertainty on it.

| frame | aperture (peak) | Q (peak) | slip | ΔQ |
|---|---:|---:|---:|---:|
| ×2.0 | 1.630 µm | 0.405 mL/min | 0.0048 mm | **−93.9%** |
| ×1.0 | 4.148 µm | 6.671 mL/min | 0.5339 mm | — |
| ×0.5 | 7.131 µm | 33.892 mL/min | 1.1592 mm | **+408%** |

A factor of two in a derived constant moves flow by an order of magnitude, and at
×2 the specimen barely slips at all (4.8 µm against 534 µm). **No absolute flow
or slip magnitude from this model should be quoted without this bracket beside
it.**

The qualitative conclusions survive it. The group-A null holds at both ends of
the bracket — cycle 2 versus cycle 1 gives ×1.000000 at ×2.0 and ×1.00077 at
×0.5. So "equal-peak cycling does not ratchet" is robust to the frame stiffness
even though every number in §1 is not.

---

## Status of the SW-S4 preregistered falsifier

`DISCUSSION_DECKS_101.md` required SW-S4 to show < 0.1 µm of slip at t = 800 s,
before injection starts, so that the confinement bleed seen in 97_04 could not
contaminate the cyclic signal. **All four SW-S4 decks fail it at 1.186 µm**, and
they are flagged `qualified_failed_pre_injection_falsifier` in the run index.

The threshold was mis-specified. The confound is *drift*, and I wrote the test on
the *absolute* value:

| | 97_04 (original) | 101_04 (retimed) |
|---|---|---|
| σ'ₙ, t = 100 → 800 s | 31.52 → 26.84 MPa | 32.13 → 31.4984 MPa |
| σ'ₙ drift, final 100 s | 0.66 MPa, still running | 0.0002 MPa |
| slip drift, final 100 s | 0.0014 µm | 0.0001 µm |
| slip rate at injection | non-zero | exactly 0.000 |

The retiming removed 4.7 MPa of confinement still bleeding down while injection
ran; σ'ₙ now reads 31.4984 MPa at t = 750, 789 and 799.5 s, identical to four
decimals. What remains is a one-time elastic settling that peaks at 1.25 µm by
t ≈ 99 s and relaxes to a dead stop. It costs 1.05% of the weakening budget
(γ/D_c = 0.016, W = 0.990) and is present identically in the 93-series decks
already in the paper.

The flag stays. Rewriting a preregistered threshold after seeing the result is
exactly what preregistration is for preventing; the correct record is that the
test failed, the quantity it was protecting is demonstrably fixed, and the test
was the wrong test.

---

## What goes in the manuscript

1. Equal-peak cycling is a null (§1) — robust to the frame bracket.
2. Escalating peaks give up to ×5.6 permeability at matched conditions (§2).
3. The end state is path-independent iff the joint ends on the yield surface (§3).
4. Shut-in produces no delayed slip (§4) — stated as a limitation.
5. Self-propping ×1.46–1.61, rate-independent, three of four specimens (§4).
6. The frame bracket (§5) belongs in the limitations, attached to every absolute
   number quoted from these runs.

## Open

- The §4 closure sign for SW-S4 rests on a calibration choice (the 17× dilation
  cut). Worth a deck that restores the dilation scale and re-runs the shut-in, to
  confirm the sign flips back.
- SW-T2 and SW-S3 have no slow-τ shut-in; group D covers only SW-T1 and SW-S4.
  The rate independence is therefore established on two specimens, not four.
