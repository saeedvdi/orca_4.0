# Kalantar 2025 — round-3 back-analysis

**Written 2026-08-24, from results downloaded 16:15 the same day.**
Method: `doc/back_analysis_method.md`, steps 1–10 in order.

> **These are mid-flight snapshots, not finished runs.** Nothing here is a score.
>
> | run | reached | of | complete |
> |---|---|---|---|
> | `110_02_og_sh_bbfast_r3` | t = 1800.5 s | 3600 | **50.0 %** |
> | `110_06_og_sc_bbfast_r3` | t = 4234.9 s | 9100 | **46.5 %** |
> | `110_04_og_t_bbfast_r3` | t = 34.2 s | 6800 | **0.5 %** |
>
> Only the **pressurization** branch exists. Nothing on depressurization has been reached by
> any run.

**Method trap, hit while writing this.** A stage matcher keyed on injection pressure matches
each depressurization stage against the *pressurization* time with the same `P_i`, and silently
returns a full-length table. That is the same phantom-match mechanism that gave
`kalantar_gate.py` its scores of 54 and 85 on truncated runs (§6.8). All such rows are
discarded below. **`kalantar_gate.py` still has no completeness guard and must not be run on
these files.**

---

## 1. OG-SH — the round-3 envelope fix worked. This fracture slips.

Round 2's defect was that `τ/τ_limit` peaked at **0.9900** and the joint never reached its
limit, so the envelope never weakened and `τ` never fell. Round 3 pinned the envelope through
stage 1 (`φ_peak` 32.70 → 30.12).

**It now reaches and rides the limit.** `τ/τ_limit` peaks at **1.0040** and sits at **1.000**
from stage 2 onward — the joint slides at its limit for the whole reached window.

| stage | P_i | τ meas | τ mod | err | σ'ₙ meas | σ'ₙ mod | err | dL_s meas | dL_s mod | τ/τ_lim |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 26.14 | 25.63 | −1.9 % | 42.99 | 42.70 | −0.7 % | 0.002 | 0.003 | 0.984 |
| 2 | 9 | 24.99 | 25.36 | +1.5 % | 40.85 | 41.05 | +0.5 % | 0.009 | 0.005 | 1.000 |
| 3 | 12 | 23.38 | 24.30 | +3.9 % | 38.46 | 38.96 | +1.3 % | 0.018 | 0.017 | 0.999 |
| 4 | 15 | 21.43 | 22.95 | +7.1 % | 35.88 | 36.71 | +2.3 % | 0.029 | 0.034 | 1.000 |
| 5 | 18 | 19.57 | 21.25 | +8.6 % | 33.35 | 34.28 | +2.8 % | 0.039 | 0.054 | 1.000 |

Against round 2, where slip at the **end** of the full run was 0.0049 mm: this run has
**0.054 mm at the halfway point**. The mechanism that was missing is present.

### 1.1 Three residual defects, and they are not the same defect

**(a) The weakening rate per unit slip is 2.07× too low.** This is the sharp one, because the
two channels move in *opposite* directions:

| | measured | model | ratio |
|---|---|---|---|
| slip, stages 1→5 | 0.039 mm | 0.054 mm | **+38 %** |
| τ drop, stages 1→5 | 6.57 MPa | 4.38 MPa | **−33 %** |
| weakening per unit slip | 168 MPa/mm | 81 MPa/mm | **0.48×** |

The model slips *more* and weakens *less*. So this is not "not enough slip" — the slip is
there and it is not being converted into strength loss. Either the characteristic slip distance
is roughly 2× too long, or the peak→residual drop is too small.

**(b) `bb_jrc_mobilized` is pinned at 15.600 for the entire run.** The JRC-mobilisation channel
contributes **nothing**. Every bit of the τ evolution above comes from `cohesion_effective`
(1.200 → 0.954 MPa) and from σ'ₙ falling under injection.

This is not a Kalantar problem. `bb_jrc_mobilized` is inert in **all four Ye2018 specimens and
all three Kalantar ones** — seven for seven, across two campaigns and two rock types. A channel
that never moves in any deck is a **code question, not a calibration one**, and it matches the
unseeded-stateful-property family already found twice in this codebase. **Highest-leverage open
item in the project**: both papers currently claim a mechanism that has never once activated.

**(c) The error is a slope, not a level.** τ error runs −1.9 → +1.5 → +3.9 → +7.1 → +8.6 %,
monotonic. Stage 1 is essentially exact. Whatever is wrong accumulates with injection, which is
consistent with (a) and inconsistent with a mis-set constant.

---

## 2. OG-SC — best result of the campaign, and the bracket narrows

**Stages 1–5 are the closest agreement anything in this campaign has produced.**

| stage | P_i | τ meas | τ mod | err | σ'ₙ meas | σ'ₙ mod | err | τ/τ_lim |
|---|---|---|---|---|---|---|---|---|
| 1 | 6 | 13.16 | 13.14 | −0.1 % | 36.10 | 36.08 | −0.1 % | 0.781 |
| 2 | 9 | 13.14 | 13.10 | −0.3 % | 34.59 | 34.56 | −0.1 % | 0.805 |
| 3 | 12 | 13.12 | 13.10 | −0.1 % | 33.07 | 33.06 | −0.0 % | 0.839 |
| 4 | 15 | 13.08 | 13.14 | +0.5 % | 31.55 | 31.58 | +0.1 % | 0.884 |
| 5 | 18 | 13.02 | 13.20 | +1.4 % | 30.02 | 30.11 | +0.3 % | 0.937 |
| 6 | 21 | 12.95 | **5.95** | −54 % | 28.48 | 24.43 | −14 % | **1.001** |

### 2.1 The burst moved from stage 4 to stage 6. Measured is stage 7.

Round 3 raised `φ_r` from 19.148° to **22.660°**, inside the round-2 measured bracket
[21.36°, 24.05°]. That bought **two stages**. The model now bursts at t ≈ 3676 s, in stage 6,
with a slip jump of 0.0046 mm/step and `τ/τ_limit` reaching 1.3032.

Table 2 requires stage 6 to **hold** (σ'ₙ 28.48, τ 12.95) and stage 7 to **fail**.

> **The bracket therefore narrows to 22.660° < φ_r(OG-SC) < 24.05°.**
>
> Both ends remain measurements, not fits: the lower end is now this run bursting one stage
> early, the upper end is the round-2 requirement that stage 7 must fail.

This is the bracket-closure test working as designed, for the second time on this specimen.

### 2.2 It also over-weakens

Post-burst the model sheds to τ = 5.95 MPa; measured stage 7 is 9.73 MPa. Consistent with
round 2's "sheds 9.1 MPa, measured 3.4". **This is a separate defect from the burst timing** —
raising `φ_r` fixes when it bursts, not how far it falls. Do not expect one knob to close both.

---

## 3. OG-T — the defect is localised, and it is not constitutive

`110_04` was submitted and reached **t = 34.2 s of 6800 (0.5 %)** with `dt` collapsed to ~0.2 s.

### 3.1 The decisive measurement: dσ'ₙ/dσ₁ during preload

For a fracture at θ from the loading axis, the normal stress must **rise** with axial load as
`Δσ'ₙ = Δσ₁ · sin²θ`. Measured over each specimen's preload ramp, from the interface's own
area-averaged normal traction:

| | Δσ₁ | Δσ'ₙ measured | predicted `Δσ₁ sin²θ` | slope meas | slope pred | slip |
|---|---|---|---|---|---|---|
| OG-SH | +56.40 | **+12.80** | +13.25 | +0.228 | 0.235 | 0.0027 mm |
| OG-SC | +27.12 | **+4.96** | +6.78 | +0.183 | 0.250 | 0.0013 mm |
| **OG-T** | +56.46 | **−5.69** | **+12.44** | **−0.090** | 0.220 | 0.0029 mm |

**OG-T's fracture unloads normally as the axial load rises — the wrong sign — and it does so at
3 µm of slip.** OG-SH matches its prediction to 3.4 %. OG-SC is 27 % low but the right sign.
OG-T is off by 18.1 MPa and inverted.

**This is not a reporting artefact.** `czm_sigma_n_pp` is
`ADSideAverageMaterialProperty` over the whole `fracture_interface` — an **area average**, not a
point sample — so method step 2 passes. It is what the constitutive law actually sees.

### 3.2 Causal order: the normal unloading comes first

| t [s] | σ₁ | σ'ₙ | τ/τ_lim | slip [mm] | d_n [µm] |
|---|---|---|---|---|---|
| 0.5 | 31.97 | 30.79 | 0.004 | 0.0000 | 0.03 |
| 8.55 | 48.11 | 29.14 | 0.227 | 0.0008 | 0.34 |
| 24.87 | 88.43 | 25.10 | 0.882 | 0.0029 | 1.48 |
| 28.12 | 96.04 | 24.27 | **1.026** | 0.0052 | 1.88 |
| 34.21 | 98.45 | 24.84 | 1.258 | 0.0688 | 4.04 |

σ'ₙ is already 4.2 MPa in deficit at t = 8.6 s and 15.6 MPa at t = 24.9 s — **all before
`τ/τ_limit` reaches 0.9 and at under 3 µm of slip.** The fracture is *opening* (`d_n` rising)
under increasing axial compression, while OG-SH and OG-SC both *close* (`d_n` → −1.02 and
−0.59 µm).

**The slip runaway is a consequence, not the cause.** Once the ratio crosses 1.0 at t ≈ 28 s the
feedback slip → dilation → normal unloading → lower limit → more slip has no arrest: τ_limit
falls 32.19 → 27.30 MPa while τ holds near 34.7, and σ₁ peaks at **99.63 MPa and turns over** —
the model specimen loses load capacity at **half** the σ₁ = 193.43 MPa the real one carried.

### 3.3 The axial target is correct — do not touch it

Checked against Table 2 stage 1 (26° frame, σ₃ = 33, P_p = 4.5):

```
σ_d = 63.21 / (sin26 cos26) = 63.21 / 0.393996 = 160.43 MPa
σ₁  = 33 + 160.43                              = 193.43 MPa   <- the deck's value
σ'ₙ = 28.5 + 160.43 sin²26                     =  59.33 MPa   <- Table 2 exactly
```

`σ_d` is frame-independent — it is what the machine applied — so 193.43 MPa is also correct for
the 28° mesh. **The axial gate is not the defect**, despite being flagged as suspect #1 in the
deck header for its 0.71 % axial strain.

### 3.4 Prime suspect — written down a day before round 1, never checked

`OGT/mesh/kalantar2025_og_t_theta28.jou`, dated 2026-08-23:

> "THE TIP CLEARANCE IS ONLY 3.00 mm. That is smaller than one factor-5 element, so the fracture
> tip will sit within a single element of the end face and the loading platen. **Check the meshed
> result at both tips** before trusting a stress concentration there."

A through-going 28° fracture spanning 94.00 mm of a 100.00 mm core puts **both tips inside the
platen boundary condition's zone of influence**. A fixed-displacement platen across the whole
end face is far stiffer than a real platen, and it can lever the two wedges apart as the axial
load rises. That is the only candidate so far that is consistent with **opening under
compression at negligible slip**.

**The angle does not rescue it.** 26° needs 102.47 mm of axial extent in a 100 mm core — it
overruns both end faces. OG-T's fracture is nearly through-going as a matter of specimen
geometry. The question is the *model's platen BC*, not the angle.

### 3.5 The preload probe never ran

`110_04_og_t_preload_probe.csv` contains **2 rows**, t = 0.5 s. It is the cheapest instrument
available for this specimen and it is the only thing standing between OG-T and a diagnosis.

---

## 4. How to move forward

Ordered. Each item says why it is where it is.

1. **Let `110_02` and `110_06` run to completion. Do not resubmit them.** Both are healthy,
   both are producing the best data in the campaign, and both conclusions above are provisional
   until the depressurization branch exists.

2. **Cancel `110_04`.** At 0.5 % with `dt` at 0.2 s it needs of order 34,000 steps to finish. It
   cannot complete and it cannot be scored. Every further hour is spent allocation.

3. **Run the OG-T preload probe locally — 60 s, no injection.** Write the falsifiable prediction
   into the deck header first:
   > *`dσ'ₙ/dσ₁` will come out ≈ −0.09 instead of +0.220, at slip < 5 µm and `τ/τ_limit` < 0.9.*

   If it reproduces, the defect is in the preload boundary condition or geometry and **nothing
   constitutive on OG-T can be judged until it is fixed** — which retires every envelope
   question on that specimen. If it does *not* reproduce, the probe differs from the full deck
   and the difference is itself the finding.

4. **Then the tip test.** From the probe's Exodus output, plot `czm_dn` along the fracture at
   t = 25 s. **Opening concentrated at the two tips and ≈ 0 mid-fracture confirms the platen
   interaction.** Uniform opening falsifies it, and the next suspect becomes the interface
   normal or the fracture-plane geometry. This is a *discriminating* test, which is why it comes
   before any fix.

5. **Investigate why `bb_jrc_mobilized` never moves.** Seven decks, two campaigns, two rock
   types, one value. This is a source-code question. It is listed fifth only because items 1–4
   are already in flight; **by leverage it is first**, because both planned papers currently
   claim a mechanism that has never activated.

6. **OG-SC: one more `φ_r` step into 22.660°–24.05°.** Only *after* `110_06` finishes and the
   burst stage is confirmed on a complete run. Price it before building: the bracket is now
   1.39° wide and the last 3.5° step moved the burst two stages, so expect roughly half a stage
   per degree — meaning the remaining window is worth about one stage, which is exactly the
   error. Also expect it **not** to fix the over-weakening (§2.2); that is a second knob.

7. **OG-SH: attack the weakening-per-unit-slip deficit, not the slip.** The model already slips
   38 % too much. Anything that increases slip makes the fit worse. The target is the 0.48×
   conversion ratio in §1.1 — and note item 5 may dissolve this entirely, since the channel that
   *should* be doing the weakening is the inert one.

### Do not do

* **Do not run `kalantar_gate.py` on these files.** No completeness guard; it will return
  confident numbers for stages no run reached.
* **Do not rank on the scalar mean nRMSE.** Round 2 established that the score got worse while
  the model got better. Rank on the per-stage tables above.
* **Do not touch OG-T's envelope, aperture law or `axial_pres_final`** until item 3 returns.
  Every one of those is unattributable while the preload is inverted.
