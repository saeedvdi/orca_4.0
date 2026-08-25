# Kalantar 2025 — round-3 back-analysis

**Part I written 2026-08-24 16:15 from mid-flight snapshots. Part II (§5 onward) written
2026-08-24 22:48 from the completed runs.**
Method: `doc/back_analysis_method.md`, steps 1–10 in order.

> **Read Part II first.** `110_02` and `110_06` both finished. Part I was written at 50 % and
> 46.5 % and three of its conclusions do not survive the depressurization branch — each is
> marked **[SUPERSEDED]** in place below, with the replacement named. Part I is kept because
> the wrong inferences are the instructive part.
>
> | run | reached | of | complete |
> |---|---|---|---|
> | `110_02_og_sh_bbfast_r3` | t = 3600 | 3600 | **100 %** |
> | `110_06_og_sc_bbfast_r3` | t = 9100 | 9100 | **100 %** |
> | `110_04_og_t_bbfast_r3` | t = 34.2 s | 6800 | **0.5 %** — dead, unchanged |

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

**(b) `bb_jrc_mobilized` is pinned at 15.600 for the entire run.** **[SUPERSEDED — §6.]** The
inference drawn here, that a channel inert in seven decks across two campaigns must be a code
defect of the unseeded-stateful-property family, was wrong. It is a deck flag,
`use_mobilized_jrc = false`, set in all thirty-odd decks of both campaigns. The observation was
right and the diagnosis was not; §6 has the source lines and the correct weakening channel.

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

**[SUPERSEDED — §7.]** The lower end is not a measurement. It reads the early burst as evidence
that the *peak envelope* is too weak, when the envelope had already been degraded 13 % by the
weakening law before the crossing happened. Evaluated on the undegraded envelope, φ_r = 22.660°
**satisfies both Table-2 conditions** — holds stage 6 by +6.1 %, fails stage 7 by −5.8 %. The
bracket does not narrow; it closes on the value already in the deck. Do not spend another φ_r
step.

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

---
---

# Part II — the completed runs

**2026-08-24 22:48.** `110_02` and `110_06` both reached `end_time`. Both branches exist, so
`kalantar_gate.py` is now legitimate on them (the prohibition above was about truncation, and
the truncation is gone). `110_04` is unchanged at 0.5 % and is still unscoreable.

## 5. The scorecard, and the first unambiguous win of the campaign

```
OG-SH  110_02   9 stages          OG-SC  110_06  13 stages
 *tau_MPa       21                 *tau_MPa       120
 *Q_ml_min      13                 *ah_um          39
  sigma_n_MPa  8.7                  sigma_n_MPa    24
  ah_um         19                  Q_ml_min       34
  ds_mm         14                  ds_mm         250
  MEAN (*)      17                  MEAN (*)       77
```

| | round 1 | round 2 | **round 3** |
|---|---|---|---|
| OG-SH mean nRMSE | 62 | 67 | **17** |

**The round-2 preregistration was right and acting on it worked.** Round 2 closed with a named
null — *"τ_limit at stage 1 equals the measured τ"* — written precisely because the two-branch
falsifier before it had been mis-specified. Round 3 acted on that one number (`φ_peak`
32.70° → 30.12°, the envelope pinned through Table 2 stage 1) and the score fell by a factor
3.7. This is the first time in either campaign that a preregistered single-number null has been
stated, acted on, and paid off. It is worth more than the score.

OG-SH per stage — compare against the round-2 column, which was flat at ~25.5 MPa throughout:

| stage | τ meas | τ mod | err | σ'ₙ err | a_h err | slip meas | slip mod | τ/τ_lim |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 26.14 | 25.63 | −1.9 % | −0.7 % | −0.2 % | 0.0023 | 0.0028 | 0.984 |
| 2 | 24.99 | 25.36 | +1.5 % | +0.5 % | +3.2 % | 0.0103 | 0.0052 | 1.000 |
| 3 | 23.38 | 24.30 | +3.9 % | +1.3 % | −2.9 % | 0.0206 | 0.0170 | 0.999 |
| 4 | 21.43 | 22.95 | +7.1 % | +2.3 % | −8.3 % | 0.0332 | 0.0335 | 1.000 |
| 5 | 19.57 | 21.22 | +8.4 % | +2.7 % | −11.2 % | 0.0446 | 0.0553 | 1.000 |
| 6 | 19.18 | 21.14 | +10.2 % | +3.1 % | −4.1 % | 0.0469 | 0.0552 | 0.960 |
| 7 | 19.11 | 21.04 | +10.1 % | +3.0 % | −2.1 % | 0.0480 | 0.0552 | 0.924 |
| 8 | 19.03 | 20.93 | +10.0 % | +2.8 % | +0.2 % | 0.0480 | 0.0552 | 0.892 |
| 9 | 18.97 | 20.81 | +9.7 % | +2.6 % | +1.6 % | 0.0480 | 0.0552 | 0.861 |

(slip in mm, in-plane; Table 2's axial `dL_s` divided by cos θ.)

The joint reaches its limit at stage 2, rides it to stage 5, then locks and unloads — which is
the measured behaviour. **Slip is now essentially right**: exact at stage 4 (0.0335 vs 0.0332)
and +15 % at the end. τ falls 4.82 MPa against a measured 7.17.

---

## 6. `bb_jrc_mobilized` is not a bug. The flag is off. — closes TODO #121

Part I §1.1(b) called this the highest-leverage open item in the project and attributed it to
the unseeded-stateful-property family. That was wrong, and the check that settles it costs one
grep:

```
$ grep -rn "use_mobilized_jrc" Examples/ --include=*.i
   ... = false        # in every deck, both campaigns, no exceptions
```

`ADOrcaBartonBandisContactTractionFastAD.C:782-787`:

```cpp
jrc_mobilized = ADReal(_jrc_scaled_const);
if (_use_mobilized_jrc)
{
  ...
  jrc_mobilized *= pow(sbar, Real(_mobilized_jrc_exponent));
}
```

With the flag off the property is assigned the constant and nothing else touches it. **It is
pinned by construction, in exactly the decks that were built to pin it.**

**And turning it on is not the fix, because the law runs the wrong way for this purpose.**
`sbar` is normalised accumulated slip, so `jrc_mobilized = JRC · sbar^n` ramps roughness **up**
from zero as slip accumulates. It is Barton's *mobilisation* limb — a joint that has not yet
slipped carries no roughness strength — not a degradation limb. Switching it on would make the
peak envelope weakest at the start and strongest after sliding, which is the opposite of every
observation in both datasets.

**The weakening the two papers actually claim runs through a different channel, and that channel
works.** `roughness_state` is live in both completed runs:

| | start | end |
|---|---|---|
| OG-SH `roughness_state_pp` | 1.000 | **0.732** |
| OG-SC `roughness_state_pp` | 0.640 | **0.141** |
| OG-SH `friction_coefficient_effective_pp` | 0.6378 | 0.5677 |
| OG-SC `friction_coefficient_effective_pp` | 0.4790 | 0.2746 |

> **Consequence for both manuscripts: nothing to fix, but the wording must name
> `use_roughness_degradation` + slip weakening, never JRC mobilisation.** Any sentence that
> attributes weakening to a mobilised JRC describes a switch that was off in every run reported.

*Method note.* The Part I inference generalised from a pattern — seven decks, two campaigns,
two rock types, one value — straight to a source-code cause, without checking whether the decks
had asked for the behaviour. **A constant that is constant in every deck is first evidence about
the decks.** Read the input before reading the source.

---

## 7. OG-SC: the envelope was already right. One constant is not.

### 7.1 The φ_r bracket closes on the deck's own value

Evaluate Table 2's two conditions on the **undegraded** Barton–Bandis envelope at the deck's
JRC 4.23 / JCS 153 MPa / φ_r 22.660°:

| stage | σ'ₙ | τ | BB limit | φ_peak | verdict | margin |
|---:|---:|---:|---:|---:|---|---:|
| 5 | 30.02 | 13.02 | 14.42 | 25.652° | holds | +10.7 % |
| **6** | 28.48 | 12.95 | **13.74** | 25.749° | **holds** | **+6.1 %** |
| **7** | 25.12 | 13.00 | **12.24** | 25.979° | **FAILS** | **−5.8 %** |

That is exactly what Table 2 requires. **φ_r = 22.660° is correct and the bracket is closed.**
Part I read the early burst as evidence of a weak envelope; it is not.

### 7.2 What actually causes the early burst

At the first crossing (t = 3670.5 s, stage 6) the run carried **9.11 µm of slip**, against
Table 2's **1.2 µm**, and the weakening law had already cut the limit by 13 %:

| slip at stage 6 | τ_limit | vs τ = 12.95 |
|---:|---:|---|
| 1.2 µm (measured) | 13.57 | holds |
| 4.0 µm | 12.89 | bursts |
| 9.11 µm (the run) | 11.45 | bursts |

`characteristic_slip_distance` = 15.2 µm converts the model's near-limit creep into envelope
loss, which closes the 6 % margin, which produces more creep. **A positive feedback the specimen
does not have.** The model creeps 1.5 µm through stages 1–5 — correct, measured 1.2 — and then
7.6 µm during the stage-6 ramp alone.

### 7.3 The one constant that is wrong: the slip-weakening residual

`slip_weakening_residual_friction_angle_degrees = 15.354°` came from
`atan(τ_last/σ'ₙ_last)` on Table 2's **last** stage: `atan(9.30/33.87) = 15.354°`.

**Table 2 shows OG-SC's slip frozen at 0.0254 mm from stage 10 onward. The joint is locked
there.** A locked joint sits *below* its limit, so `atan(τ/σ'ₙ)` at that stage is a **lower
bound on the residual, not a measurement of it.** The same derivation is legitimate on OG-SH,
which creeps through every hold and therefore is sliding when it is sampled — and OG-SH's
number is the one that behaves.

The residual must be read where the joint has just slid, which is stage 7, immediately after
the burst:

```
phi_res(OG-SC) = atan(9.73 / 25.12) = 21.17 deg        (deck: 15.354)
mu_res         = 0.3873                                 (deck: 0.2746)
```

Measured consequence — the model collapses to `mu = 0.2746` exactly and stays there:

| stage | τ meas | τ mod | σ'ₙ meas | σ'ₙ mod | a_h meas | a_h mod |
|---:|---:|---:|---:|---:|---:|---:|
| 7 | 9.73 | **4.85** | 25.12 | 22.30 | 1.92 | 1.08 |
| 13 | 9.30 | **3.04** | 33.87 | 30.26 | 0.58 | 0.65 |

and slip runs to 0.104 mm against a measured 0.025. That single constant carries most of
OG-SC's τ nRMSE of 120.

**Honest limit of this fix.** 21.17° alone does not restore the burst stage: at 9.11 µm of slip
it still bursts at stage 6, because §7.2's feedback is separate. Raising `D_c` far enough to
suppress the feedback (≳ 30 µm) then undershoots the 3.27 MPa burst drop the 22 µm of measured
slip has to deliver. **No single knob does both.** The quantity that has to change is the
7.6 µm of pre-burst creep, and that is `tangential_viscosity` — the hidden rate law, already on
record as worth 0.035–3.5 MPa in τ. Treat OG-SC's burst timing as a *rate* problem from here,
not an envelope or a `D_c` problem.

### 7.4 OG-SC's aperture law is saturated — a derived two-parameter fix

Stages 1–5 match on force to 1.4 % while `a_h` is already 31 % low, so the two are separable
and the aperture defect is clean. The material computes
(`ADOrcaRoughnessDamageFracturePermeability.C:486-493`)

```
opening(sigma'_n) = V_m * [ g(sigma_ref) - g(sigma'_n) ],   g(s) = s^p / (sigma_0^p + s^p),
sigma_0 = V_m * K_ni
```

The deck runs `V_m = 1.20 µm`, `K_ni = 1.25e13` ⇒ **σ₀ = 15.0 MPa**, `p = 4`, while OG-SC
operates at σ'ₙ = 28.5–36.1 MPa. So `σ'ₙ/σ₀` never leaves 1.9–2.4, where `g` is already
0.929–0.971: **the closure term is pinned near its ceiling and cannot respond.**

| stage | σ'ₙ | a_h meas | opening needed | deck delivers | factor |
|---:|---:|---:|---:|---:|---:|
| 2 | 34.59 | 1.18 | 0.150 | 0.0062 | 24 |
| 4 | 31.55 | 1.36 | 0.330 | 0.0236 | 14 |
| 6 | 28.48 | 1.60 | 0.570 | 0.0510 | 11 |

The whole 7.6 MPa of unloading moves `g` by 0.0425, so `V_m` sets a ceiling of 0.051 µm against
a measured swing of 0.570 µm. Refitting `V_m` and `σ₀` on those six points, with `p` held at the
deck's 4:

```
V_m     1.200 -> 2.651 um
sigma_0 15.00 -> 36.29 MPa        (i.e. inside the operating range, not below it)
K_ni    1.250e13 -> 1.369e13 Pa/m  -- essentially unchanged
RMS residual 25 nm on a 570 nm swing; worst stage 3.2 %
```

**`K_ni` was never the problem; `V_m` was**, and with it the placement of σ₀. These are two of
the eight constants the Kalantar MEMORY §7 lists as still-inherited Ye2018 fits, and §7's stated
precondition — *refit once the loading gate passes* — is now met on OG-SC's first five stages.

---

## 8. OG-SH: the residual is right, the distance to it is 5.7× too long

The end state is right and the path to it is not. `slip_weakening_residual_friction_angle_degrees`
= 25.930° reproduces Table 2's last stage exactly (`atan(18.97/39.01)` = 25.93°) and OG-SH is
sliding there, so unlike OG-SC that derivation is sound. The model just never arrives:

| | measured | model |
|---|---:|---:|
| in-plane slip, stage 1 → 9 | 48.0 µm | 55.2 µm |
| μ, stage 1 → 9 | 0.6080 → 0.4863 | 0.6001 → 0.5197 |
| fraction of the friction drop delivered | 100 % | **67 %** |

With `characteristic_slip_distance` = 150 µm and the law `μ = μ_r + (μ_p−μ_r)·exp(−(s/D)^1.4)`,
48 µm of slip is `s/D = 0.32`, worth **18 %** of the drop. The rest of the 67 % comes from
`roughness_state` and from σ'ₙ falling. **D is the lever, and it is the only one — the slip is
already right, so anything that adds slip makes the fit worse.**

### 8.1 The build-time stability assertion is 1.36× too strict, and that matters here

The assertion `D_c > Δτ/k_eff` is what stopped `D_c` being cut before. It assumes a **linear**
drop over `D`. The law is `exp(−(s/D)^n)` with `n = 1.4`, whose steepest slope is at
`s/D = ((n−1)/n)^(1/n) = 0.4087` and equals `0.7355·(μ_p−μ_r)/D`. So the true cap is
**0.7355×** the naive one.

The second correction is bigger. Only the **friction** part of the τ drop is the weakening law's
responsibility; the rest is σ'ₙ falling under injection, which `D_c` does not control. Charging
the whole 7.17 MPa to it inflates the cap by another 1.5×:

```
OG-SH   k_eff = 150.5 MPa/mm
        tau drop 7.17 MPa, of which 4.75 is friction (mu 0.6080 -> 0.4863)
        naive cap  dtau_mu / k_eff          = 31.6 um
        TRUE cap   0.7355 * dtau_mu / k_eff = 23.2 um     (below this = stick-slip)
        D for 90 % of the drop at 48 um     = 26.5 um
        verdict: STABLE, margin 1.14x
```

> **`characteristic_slip_distance` = 150 µm → ≈ 26.5 µm on OG-SH.** It reproduces the measured
> weakening at the measured slip **and** stays on the stable side of the corrected criterion,
> which is what the paper reports (OG-SH creeps through every hold, no burst).

The old cap of 47.7 µm would have forbidden this. It was wrong twice over, and the tension it
created — "reproduce the weakening" against "stay stable" — was an artefact of the arithmetic,
not a statement about the rock. **Price the constraint before obeying it.**

---

## 9. OG-T: the defect orders with tip clearance, not with axial load

`110_04` behaved identically to round 2 and stopped at t = 34.2 s with `dt` collapsing. The
preload inversion is unchanged: `bb_effective_normal_stress_pp` falls 30.79 → 24.17 MPa while
the paper-frame reporter rises 30.07 → 48.14.

Part I §3.4 named two suspects and put the **axial gate** first. On the completed round-3 runs
the ordering is decidable, because both surviving specimens ramp the same way. Window: the axial
ramp only, up to 98 % of peak σ₁, with the pore change carried explicitly —

```
requirement:  d sigma'_n = sin^2(theta) * d sigma_1  -  d p
```

| specimen | tip clearance | Δσ₁ | Δp | predicted Δσ'ₙ | measured | ratio |
|---|---:|---:|---:|---:|---:|---:|
| OG-SH | **14.92 mm** | 61.03 | 1.63 | +12.71 | +12.87 | **1.012** |
| OG-SC | **6.72 mm** | 30.07 | 1.63 | +5.89 | +4.88 | **0.830** |
| OG-T | **3.00 mm** | 82.63 | 0.89 | +17.32 | **−6.61** | **−0.382** |

Tip clearance is `(L − D/tan θ)/2`: the rock left between the fracture's extreme axial point and
the platen.

> **The ratio is monotonic in tip clearance and is not monotonic in Δσ₁.** OG-SH carries
> **twice** OG-SC's axial change and scores *better*, which is the wrong way round for a
> loading-magnitude cause. Suspect 2 is promoted over suspect 1.

The mechanism is consistent: both end faces are held at uniform axial displacement
(`bottom_nodeset` Dirichlet, `top_nodeset` penalty), so the whole shear offset between the two
wedges has to be accommodated within the clearance. At 3 mm the near-tip rock is a knife edge.
`bb_effective_normal_stress_pp` is an **area average over the interface**, so tip opening drags
the average down even while the centre stays closed.

**Two consequences, both cheap:**

1. **The 26° arm is not a rescue and must not be tried as one.** At θ = 26° the trace is
   102.47 mm in a 104.48 mm core: clearance **1.0 mm**, three times worse. The existing mesh
   makes this a decisive, nearly free falsifier — if the inversion gets *worse* at 26°, the
   clearance mechanism is confirmed; if it improves, it is dead.
2. **The preload probe (TODO #120) keeps its prediction but gains a sharper one.** Alongside
   `dσ'ₙ/dσ₁ ≈ −0.09`, write: *`czm_dn` at t = 25 s will be concentrated within ~5 mm of the two
   axial extremes of the fracture trace and near zero at mid-fracture.* Uniform opening
   falsifies the clearance mechanism outright.

*Method note.* This is the same shape as Part I §3.1 — an identity the model must satisfy,
evaluated across siblings — but run one level deeper: not "which specimen violates it" but
"what orders the violation". Two specimens were enough to break the tie because the two
candidate causes rank them in opposite orders. **When two suspects survive, look for the
variable that ranks the siblings differently, not for more evidence about the worst one.**

---

## 10. Round 4 — what to change, in order

| # | specimen | change | from → to | basis |
|---|---|---|---|---|
| 1 | OG-SC | `slip_weakening_residual_friction_angle_degrees` | 15.354° → **21.17°** | §7.3, measured at the one sliding stage |
| 2 | OG-SH | `characteristic_slip_distance` | 150 µm → **26.5 µm** | §8, measured drop at measured slip, stable by 1.14× |
| 3 | OG-SC | `bb_max_aperture_closure` (V_m) | 1.20 µm → **2.65 µm** | §7.4, 25 nm RMS on six points |
| 4 | OG-SC | `bb_initial_normal_stiffness` (K_ni) | 1.25e13 → **1.369e13** | §7.4, same fit |
| 5 | builder | correct the stability assertion to `0.7355·Δτ_μ/k_eff` | — | §8.1 |
| 6 | builder | derive the slip-weakening residual **only from a stage with non-zero slip increment**, and assert it | — | §7.3 |
| 7 | OG-T | run the preload probe with both predictions written first | — | §9 |

**Do not** touch OG-SC's `φ_r` (§7.1 closes it), OG-SH's slip-weakening residual (§8 confirms
it), or `use_mobilized_jrc` (§6). **Do not** treat OG-SC's burst stage as closed by items 1–4;
it is a rate problem and it needs `tangential_viscosity` priced separately.

**Preregistered nulls for round 4**, one number each, per the round-2 lesson:

1. *OG-SH's τ error at stage 9 falls from +9.7 % to under +3 %.* (item 2)
2. *OG-SC's τ at stage 7 is 9.73 ± 0.5 MPa.* (item 1 — it is what the constant is fitted to,
   so failure here means the burst dynamics, not the constant.)
3. *OG-SC's `a_h` at stage 6 is 1.60 ± 0.10 µm.* (items 3–4)
4. *OG-SC still bursts at stage 6, not 7.* Written as an expected **failure**: items 1–4 are
   not aimed at burst timing, and if the burst moves to stage 7 anyway then §7.2's feedback
   diagnosis is wrong and `tangential_viscosity` can be dropped from the plan.
