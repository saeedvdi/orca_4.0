# Kalantar 2025 — round-4 back-analysis

**2026-08-25.** All three runs complete for the first time in the campaign, OG-T included.
Method: `doc/back_analysis_method.md`. Arithmetic: `scripts/dc_bracket.py`,
`scripts/frame_stiffness.py`, `scripts/r3_stages.py`, `scripts/preload_slope.py`.

| | round 1 | round 2 | round 3 | **round 4** |
|---|---|---|---|---|
| OG-SH mean nRMSE | 62 | 67 | **17** | **31** ↑ worse |
| OG-SC mean nRMSE | — | — | 77 | **29** ↓ better |
| OG-T mean nRMSE | — | — | — | 58 *(control, see §4)* |

**The headline is that the preregistered nulls did their job.** Two failed, one passed, one
passed as the expected failure — and the two that failed failed *informatively*, in a direction
the preregistration had named in advance. That is worth more than the scores.

---

## 1. The scorecard against what was written before the run

| # | null | result | verdict |
|---|---|---|---|
| 1 | OG-SH τ error at stage 9 lands in **+3 % to +7 %** | **−19.6 %** | **FAILED** — overshot the low side |
| 2 | OG-SC τ at stage 7 is **9.73 ± 0.5 MPa** | **8.12** | **FAILED** by 1.6 MPa |
| 3 | OG-SC `a_h` at stage 6 is **1.60 ± 0.10 µm** | **1.53** | **PASSED** |
| 4 | OG-SC still bursts at stage 6, not 7 *(expected failure)* | bursts at stage 6 | **passed as written** |

Null 1's preregistration said: *"Below +3 % ⇒ two errors cancelled and neither is closed."* It
landed at −19.6 %, far past that, which is a third outcome the wording did not cover — and
tracing why is §2 and §3.

Null 3 is a clean, unambiguous win: **OG-SC's aperture channel went from nRMSE 39 to 10 with a
bias of +0.002 µm**, on two constants derived from Table 2 and never touched afterwards. The
saturated-closure diagnosis was right and the fix is finished.

---

## 2. Null 1: the D_c fit was conditioned on a quantity the model has to predict

Round 4 cut OG-SH's `characteristic_slip_distance` from 150 µm to 59.3 µm, fitted to Table 2's
measured `μ(s)` path. The run's slip went the wrong way — hard:

| | measured | round 3 (D_c 150 µm) | round 4 (D_c 59.3 µm) |
|---|---:|---:|---:|
| τ at stage 9 | 18.97 | 20.81 (**+9.7 %**) | 15.26 (**−19.6 %**) |
| σ'ₙ at stage 9 | 39.02 | 40.04 (+2.6 %) | 36.96 (−5.3 %) |
| slip at stage 9 | 48.0 µm | 55.2 µm (+15 %) | **122.5 µm (+155 %)** |

**The fit treated Table 2's `dL_s` as an independent variable. In the model it is an outcome.**
The joint slides until the frame's unloading meets the falling limit, so shortening `D_c`
weakens the joint, which produces more slip, which weakens it further. Fitting `τ(s_measured)`
prices the first step of that loop and none of the rest.

> **Rule: never fit a constant against a channel the model is going to solve for. Fit against
> the coupled response, or against a channel the boundary conditions pin.**

The measured stage-2 → stage-3 slip increment is 10 µm; round 4's is **76 µm**.

---

## 3. The bracket is SPLIT, and the reason is a frame stiffness counted twice

Rounds 3 and 4 differ in one constant, so they are a two-point bracket. Interpolating each
channel to its own target:

```
matching tau_9   needs D_c = 110 um
matching slip_9  needs D_c = 166 um
```

They disagree, and by `bracket-closure-test-table2` a split bracket means a **second defect**.
It is visible directly in the two runs. Across them, τ sheds **82.5 MPa per mm of slip**. The
frame identity that the whole gate is built on says it should shed `k_eff` = 150.5:

```
k_eff = K_sys cos^2(theta) sin(theta) / A = 150.5 MPa/mm     off by 1.82x
```

**The joint does not unload against the machine. It unloads against the machine in series with
the core**, because the deck's axial BC is a penalty spring of `K_sys/A` backed by an elastic
sample:

| | machine compliance | core compliance | series | k_eff |
|---|---|---|---|---|
| OG-SH (120 mm) | 2.4647e-12 | 1.7118e-12 m/Pa | **0.590×** | 150.5 → **88.8 MPa/mm** |
| OG-SC (100 mm) | 2.4647e-12 | 1.4265e-12 | 0.633× | 152.1 → 96.4 |
| OG-T (100 mm) | 2.4647e-12 | 1.4265e-12 | 0.633× | 148.5 → 94.1 |

**88.8 against a measured 82.5 — 8 %.** The model is right about its own mechanics; the
criterion was wrong.

### 3.1 Which of the two is wrong, and the answer is the deck

Table 2's own `ΔL_s = −A·Δτ/(K_sys sinθ cosθ)` identity verifies **with `K_sys` alone**, to
0.4–4 % on all three specimens. So the paper's `K_sys` is the stiffness of the whole loading
system, sample included — the name says so. The deck then adds the core's compliance a
**second** time, on top of a penalty already set to `K_sys/A`, and the joint unloads against
0.59 of the stiffness the experiment had.

This is the same constant that dominated everything on Ye2018 — a ×2 bracket moved Q by
−93.9 %/+408 % — and here it was supposed to be *measured* rather than inferred. It was
measured. It was then softened by 1.7× in the deck.

**It also invalidates every stability cap this campaign has quoted.** All of them used the
machine-only `k_eff` while the model was running a frame 1.7× softer, so the cap that actually
applied in rounds 1–4 was **1.7× larger** than the one printed: OG-SH's was 35.2 µm, not 23.2.
Round 4 put `D_c` at 59.3 µm — still above even that — and produced a near-runaway anyway, so
the criterion is not merely mis-scaled; it is being asked to do more than a linearised
inequality can. *(Once round 5 stiffens the frame the two agree again by construction, and the
builder then prints 20.9 µm for OG-SH — that is the cap under the corrected frame, not a third
value.)*

> `C_ax` was calibrated on our own round-1 run to make the axial *gate* land σ₁ on target. That
> was legitimate for its own purpose and is being read here as if it were a property of the
> experiment. **A constant fitted to make one channel land is not evidence about the system.**

---

## 4. OG-T: complete for the first time, and it confirms the round-3 diagnosis

`110_08` ran all 6800 s. Its constitutive constants are byte-identical to round 3 by design, so
it is a control, and its mean nRMSE of 58 is **not** a constitutive result.

| t [s] | σ₁ | σ'ₙ (law) | σ'ₙ (reported) | ratio | slip |
|---|---|---|---|---|---|
| 0.5 | 33.35 | 30.79 | 30.07 | 1.02 | 0 |
| 30.0 | 115.75 | 24.17 | 47.79 | **0.51** | 15.7 µm |
| 60.3 | 77.02 | 30.59 | 38.80 | 0.79 | **517.7 µm** |

It sheds **518 µm before injection begins** and ends at 639 µm against the paper's 275 µm
total. The preload inversion is unchanged and now confirmed on a full run rather than a 0.5 %
fragment. The tip-clearance ordering from round 3 still stands (14.92 / 6.72 / 3.00 mm →
1.012 / 0.830 / −0.382).

---

## 5. OG-SC: the aperture is solved, the force channel is halfway

τ nRMSE 120 → **47**, `a_h` 39 → **10**. Post-burst τ is 8.12 against a measured 9.73, where
round 3 gave 4.85 — the residual correction recovered two thirds of the gap.

What remains is the same shape as OG-SH's: **slip is 2.8× too large** (64.9 µm against 23.1),
and σ'ₙ follows it down (−3.7 %). Post-burst the model's mobilised friction is
`8.12/24.19 = 0.336` — **below** the 21.175° residual it was given. A joint cannot sit below its
own residual while sliding, so either it has locked at a state the frame carried it to, or the
paper-frame τ and the constitutive σ'ₙ are not the same pair. **Check that before touching
another constant** — it is the `postprocessor-only-channels-can-fake-model-error` shape.

---

## 6. Round 5 — BUILT 2026-08-25

`110_10` OG-SH, `110_11` OG-T, `110_12` OG-SC, all `Syntax OK`. Verified by diff: the **only**
changes are the three axial-frame keys on all three decks, plus OG-SH's `D_c` reverted. OG-SC's
three round-4 constants and OG-T's constitutive block are untouched.

The frame stiffness is upstream of everything else here: it sets how much slip any weakening
produces, on all three specimens, and it is a **derived** constant with a measurement behind it,
not a fit. Fix it first and re-bracket afterwards — do not tune `D_c` against a soft frame.

| # | change | basis |
|---|---|---|
| 1 | **Stiffen the axial penalty so the SERIES stiffness equals `K_sys`**: `penalty = 1/(A/K_sys − C_ax)` — **3.27× on OG-SH, 2.37× on OG-SC/OG-T**, which raises the stiffness the *joint* sees by 1.695× and 1.579×. The two ratios are different; do not confuse them | §3 — the paper's `K_sys` is the system, and the deck counts the core twice |
| 2 | Rebuild the stability cap on the series `k_eff`, and keep it **reported** | §3.1 |
| 3 | **Revert OG-SH's `D_c` to 150 µm** for the frame-fix run, so round 5 changes one thing | §2 — its bracket is not interpretable against a soft frame |
| 4 | Keep OG-SC's residual, `V_m`, `K_ni` | null 3 passed; the residual recovered ⅔ of its gap |
| 5 | Verify OG-SC's post-burst τ/σ'ₙ pair before any new constitutive change | §5 |
| 6 | OG-T stays HELD, preload probe still owed | §4 |

**Preregistered nulls for round 5**, one number each:

1. **OG-SH's slip at stage 9 falls from 55.2 µm to 48 ± 5 µm** at the *unchanged* `D_c` of
   150 µm. This is the whole claim of item 1 and it is a direct consequence of a 1.70× stiffer
   frame. If slip does not move, the penalty is not what sets the joint's unloading stiffness
   and §3 is wrong.
2. **τ sheds 140 ± 15 MPa/mm across the round-3/round-5 pair**, against round 4's measured 82.5.
   This tests the *mechanism* rather than the outcome, so it is not redundant with (1).
3. **OG-SC's `a_h` at stage 6 stays 1.60 ± 0.10 µm.** A null of *no change*: the closure fit is
   independent of the frame, and if a frame change moves the aperture channel the two are
   coupled through something not yet identified.
