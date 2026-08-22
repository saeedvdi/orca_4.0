# 104-series results — why SW-S4 closes, and whether retention is rate-independent

All five decks reached their scheduled end times on the cluster. Read with
`scripts/analyze_104.py`, which recomputes each 101 mirror through the same code
path so a deck and its mirror are compared by identical arithmetic rather than
against a quoted number. Metrics land in
`doc/independent_analysis/DISCUSSION_104_METRICS.csv`.

Like the 101 decks these replace the paper's monotonic schedule and **are not
scoreable against Table 2**. `104_01`–`104_03` additionally change a calibrated
parameter on purpose, so they are not valid hydraulic calibrations of their
specimens either — they are single-knob controls.

---

## 0. A metric bug found while reading arm 2, and what it invalidates

`104_04` first reported a retained-permeability ratio of **×4.030** against its
mirror's ×1.459 — a +176% swing from a run in which *no parameter was changed*.
Its end state, however, was indistinguishable from the mirror's: hydraulic
aperture 4.2441 against 4.2395 µm (+0.11%) at effective normal stress 48.13
against 48.41 MPa. The end states agreed; only the metric moved.

The metric is "end state compared against the loading path at the same σ'ₙ",
which differences out reversible closure. It was implemented as a
nearest-neighbour search over `[T_SETTLE, t_shut]`. **σ'ₙ is not monotonic over
that window.** The confining preload ramps it from 25 to 67.7 MPa over the first
≈55 s, and injection then brings it back down, so every target below the peak is
attained *twice* inside the window. Which of the two the search returns is
decided by output sampling density, not by physics: `104_04` matched a preload
row at t = 21 s where its mirror matched an injection row at t = 2073 s.

Fixed in `scripts/analyze_101.py` (shared by both readers): the window now starts
at the time of peak σ'ₙ, so only the injection branch is searched, and the
reference state is linearly interpolated to the target stress instead of snapped
to the nearest stored row.

**Effect on the 101 numbers already published.** Ten of the eleven shut-in cases
are bit-identical before and after. One changes: SW-T2's ×1.459 becomes
**×1.451**, from interpolation alone — its nearest row sat 0.10 MPa off target,
the largest residual in the set. No 101 conclusion changes.

**Effect on the manuscript.** Table 12 (the 98-series shut-in table) quotes
retained $k$ of 5.52 / 4.03 / 1.50 / 0.91. Recomputing the four 98 runs with the
corrected metric gives **1.605 / 1.450 / 1.497 / 0.893**. The two saw cuts
reproduce; both tensile entries are wrong by a factor of ≈3, and 4.03 is
precisely the artifact value reproduced above. No committed script generates
Table 12 — those numbers were computed ad hoc — which is why the error survived.
The 101-series supersedes that table and has a committed reader.

---

## 1. Arm 1 — SW-S4's closure is the gouge-fill term

Prediction registered before the runs: turning gouge-fill off flips SW-S4's
ratio across 1.0; the same knob on SW-S3 raises it but cannot flip it.

| deck | specimen | change from mirror | k ratio | mirror | Δ |
|---|---|---|---:|---:|---:|
| `104_01` | SW-S4 | `use_slip_damage` → false | **×1.531** | ×0.859 | +78.3% |
| `104_02` | SW-S4 | `dilation_scale` 0.0117 → 0.038 | **×1.916** | ×0.859 | +123.1% |
| `104_03` | SW-S3 | `use_slip_damage` → false | ×2.126 | ×1.497 | +42.0% |

**The sign flips on both SW-S4 arms and does not flip on the control.** That is
the full pattern the hypothesis required: the same knob moves both saw cuts in
the same direction, but only SW-S4 crosses 1.0, so gouge-fill is the channel the
two specimens differ *by* rather than a knob that happens to move SW-S4.

The aperture budget says why, and it is not a difference in the gouge term
itself — it is a difference in what the term is subtracted from:

| specimen | $a_{h0}$ | fill at end | fill / $a_{h0}$ | $a_h$ end, gouge on → off |
|---|---:|---:|---:|---|
| SW-S3 | 1.22 µm | 0.3056 µm | 25% | 1.5589 → 1.8511 µm |
| SW-S4 | **0.74 µm** | 0.2533 µm | **34%** | 0.7531 → 0.9997 µm |

Both specimens lose ≈0.25–0.31 µm of aperture to wear products, and the absolute
losses are within 20% of each other. SW-S4 starts from a baseline aperture 40%
smaller, so the same absolute subtraction is decisive on the polished saw cut and
merely a tax on the rough one. `104_02` shows the other side of the same balance:
leaving gouge on but giving SW-S4 SW-S3's dilation gain also clears 1.0, and by
more (×1.916), because the added dilation outruns a fill term that is unchanged
at 0.2507 µm.

So the sign of SW-S4's shut-in permeability change is set by the ratio of a
subtraction fixed by slip to a baseline aperture fixed by the specimen — and
both of those are **calibrated quantities, not predictions of the constitutive
law**. This must be reported that way. What the law predicts is that a joint with
a small initial aperture and an active wear term can close under net slip; that
SW-S4 in particular does so is a consequence of its fit.

## 2. Arm 2 — retention is rate-independent on all four specimens

`104_04` and `104_05` change no parameter at all: they are ordinary group-D
decks at τ = 1500 s for the two specimens group D skipped. With the corrected
metric:

| specimen | τ = 150 s | τ = 1500 s | change |
|---|---:|---:|---:|
| SW-T1 | ×1.609 | ×1.584 | −1.6% |
| SW-T2 | ×1.451 | ×1.436 | −1.1% |
| SW-S3 | ×1.497 | ×1.494 | −0.2% |
| SW-S4 | ×0.859 | ×0.855 | −0.5% |

A ten-fold change in shut-in decay time moves retained permeability by at most
1.6%, and in the same direction on every specimen. **The finding that rested on
two specimens now rests on four**, and the sign of SW-S4's exception is
rate-independent too.

Post-shut-in slip growth remains nil on both new decks (0.000 µm on each), so the
no-delayed-slip result also now covers all four specimens at both bleed-off
rates.

---

## What goes in the manuscript

1. SW-S4's closure is gouge-fill acting on a small baseline aperture, confirmed
   by a two-arm test with a sign control (§1) — reported as calibration-driven.
2. Retained permeability is rate-independent across a ten-fold range of shut-in
   decay time, on all four specimens (§2).
3. Table 12's two tensile retained-$k$ values are wrong and must be replaced by
   the 101-series numbers (§0).
