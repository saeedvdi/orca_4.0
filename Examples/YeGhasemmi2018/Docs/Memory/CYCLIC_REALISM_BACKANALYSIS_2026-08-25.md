# Is the cyclic result physical? — a back-analysis of the 101-series null

**Date** 2026-08-25 · **Question asked** "In the real world, do we expect the same
behaviour under cycling? Do we need to adjust things so the shear slip also changes?
Do we need creep?"

The 101-series found that equal-peak cycling does essentially nothing (§1 of
`DISCUSSION_101_RESULTS.md`), and §6.6.6 of the manuscript already attributes that to
*"every history variable is monotone in slip"*. This document tests that attribution
against the data. **It is incomplete, and the missing half changes what the paper should
claim.**

---

## 1. Two conditions are needed for the null, and the paper states only one

For a repeat cycle to produce no new slip, two independent things must both hold:

| | condition | supplied by | in the manuscript? |
|---|---|---|---|
| **A** | the joint cannot **re-weaken** — the yield surface does not grow back | monotone-in-slip state variables | yes, §6.6.6 |
| **B** | the joint cannot **re-load** — the driving stress does not return to the yield surface | the displacement-controlled loading frame | **no** |

Condition A is correctly identified and correctly sourced. Every irreversible channel in
`ADOrcaBartonBandisContactTractionFastAD` — `cumulative_plastic_slip`,
`irreversible_dilation`, `roughness_state`, `maximum_reversible_normal_opening`,
`bb_unload_min_closure` — advances only with plastic slip, and plastic slip advances only
when τ reaches τ_limit. Verified in source.

Condition B is not a property of the constitutive law at all. It comes from the boundary
condition: `[axial_load]` is a `FunctionPenaltyDirichletBC`, i.e. a commanded axial
*displacement* through a series spring `penalty = k_machine/A`. Slip on an inclined joint
relieves the shear stress that drives it. Once cycle 1 has slipped, the joint sits below
yield, and returning to the same injection pressure does not bring it back.

**Condition B is the one that does not transfer to the field**, and the existing frame
bracket measures exactly how much it is doing.

## 2. The frame bracket already contains the answer — read as increments, not ratios

Group A and group E, SW-T1 unless noted. "Ratchet" is the slip change at the same hold
relative to cycle 1; the margin is `τ_limit − τ`, so positive means below yield.

| case | frame | margin at cycle-2 peak (MPa) | ratchet c1→c2 | ratchet c2→c3 |
|---|---|---:|---:|---:|
| `101_15` SW-T1 | ×2.0 | **+12.884** | **0.0000 µm** | (2-cycle deck) |
| `101_03` SW-S3 | ×1.0 | +0.679 | −0.052 µm (elastic) | +0.0001 µm |
| `101_02` SW-T2 | ×1.0 | +0.0000322 | +0.00054 µm | +0.00003 µm |
| `101_01` SW-T1 | ×1.0 | +0.0000439 | +0.0058 µm | +0.0008 µm |
| `101_04` SW-S4 | ×1.0 | −0.00158 | +0.528 µm | +0.022 µm |
| `101_16` SW-T1 | ×0.5 | +0.000331 | **+0.367 µm** | (2-cycle deck) |

Three things fall straight out:

1. **The ratchet is zero if and only if the joint is off the yield surface.** SW-T1 at ×2.0
   never returns to yield (+12.9 MPa of margin) and gives an exact zero. SW-S3 ends 0.68 MPa
   below yield and gives a *negative* change — elastic recovery, not slip. Every case that
   sits on yield gives a non-zero, positive ratchet.
2. **Halving the frame stiffness multiplies the first ratchet by 63×** (0.0058 → 0.367 µm),
   same specimen, same law, same schedule. Both are first increments, so the comparison is
   like-for-like.
3. **The model shakes down; it does not ratchet.** Every 3-cycle case decays hard —
   SW-S4 by 24× (0.528 → 0.022 µm), SW-T1 by 7.5×, SW-T2 by 18×. This is elastic shakedown
   in the plasticity sense, and it is the sharpest available statement of the difference
   from real rock, which under equal-amplitude cycling does not decay to zero.

`DISCUSSION_101_RESULTS.md` §5 concludes the null is *"robust to the frame stiffness"* on
the grounds that the cycle-2/cycle-1 ratio is ×1.000000 at ×2.0 and ×1.00077 at ×0.5. That
is true of the **ratio** and hides a 63× change in the **increment**. The claim is not
wrong, but "robust" is stronger than the data supports, and a reviewer looking at
increments will find this.

### What the ×0.5 factor of 63 is *not*

It is not the approach to critical stiffness. Computing the frame stiffness against the
slip-weakening slope for SW-T1 (σ'ₙ = 32.66 MPa, strength drop 26.33 MPa, D_c = 150 µm,
`SW_PEAK_SHAPE` = 0.7355):

| frame | k_eff (MPa/mm) | k_eff/k_crit at the **peak** of the weakening curve | local k_eff/k_weak **at the cycling state** |
|---|---:|---:|---:|
| ×2.0 | 314.3 | 2.43 | 5.1 |
| ×1.0 | 157.1 | **1.22** | 143 |
| ×0.5 | 78.6 | **0.61** | 5.7 × 10⁶ |

By the time cycling starts, s/D_c is 3.6 (×1.0) and 7.7 (×0.5), so W is 0.003 and 0.000 and
the local weakening slope has collapsed. All three frames are far above critical *during*
cycling; no instability is available. **The 63× is not explained by any mechanism identified
here** — Δs ∝ 1/k_eff predicts only 2×. This is the one open number in this analysis and it
is what a ×0.25 rung would pin down.

Worth carrying separately: the first column shows the **calibrated frame sits only 22% above
critical stiffness on the initial ramp**, and the ×0.5 arm is formally below it. That belongs
in the limitations beside the existing −93.9%/+408% flow bracket.

## 3. Healing is already built, already measured, and is the wrong sign

`ADOrcaBartonBandisRateStateHardening` (branch `orca_v6`) adds
`σ'ₙ[a ln(1+V/V₀) − b ln(1+V_θ/V₀)]` with the ageing law, and θ keeps healing through
elastic stick. The 95-series ran the b bracket. Measuring the healing term directly from
`95_14` (SW-S4, a = 0.010, b = 0.005), θ spans **5.09 → 1817 s** over the test:

| b | strength recovered over the whole test, at mean σ'ₙ = 23.5 MPa |
|---|---:|
| 0.005 | 0.350 MPa |
| 0.010 | 0.700 MPa |
| 0.015 (lab granite) | **1.049 MPa** |

Per single 1600 s hold at lab b, θ 100 → 1700 s: **0.24 MPa**.

Set that against the other terms in the same runs:

- Perzyna η·V, the rate term already in the finals: **0.314 MPa mean, 0.871 MPa peak**
- frame-stiffness uncertainty: **−93.9% / +408% on Q**
- SW-S3's margin after cycle 1: **0.679 MPa**

So healing is third-order. **And it points the wrong way.** After cycle 1 the joint is
*below* yield; healing raises τ_limit and pushes it further below. Under displacement
control, healing makes re-slip harder, not easier. It cannot be the mechanism for
equal-peak ratcheting under any value of b.

This is worth stating positively in the paper: the absence named in §6.6.6 is not just
named, it is **built, run, and bounded at ≤1.05 MPa of the wrong sign**. A quantified
absence is much stronger than a listed one.

## 4. Creep — separate the two kinds, only one is missing

**Shear creep is present and is the only thing producing the numbers in §2.** Perzyna η·V
(and RSF in the 95-series) lets τ exceed τ_limit and bleed slip at a rate set by the
overstress. It is gated on being at yield, and the frame takes the joint off yield — which
is why the shut-in test found no delayed slip. The largest post-shut-in advance anywhere
was 0.21 µm and the net was negative on five of six cases. **That null is a boundary-condition
result too**, not evidence that the rock does not creep.

**Normal/closure creep is genuinely absent.** Pressure solution and asperity indentation
creep close a joint at constant stress over 10⁵–10⁷ s. The self-propping claim
(×1.45–1.61, "rate-independent") was tested over a 150 → 1500 s bleed-off bracket. That
range is three to five orders of magnitude short of the pressure-solution timescale, so the
correct statement is *rate-independent over the observation window*, not asymptotically.
One sentence, and it matters much more for the THM paper, where temperature drives
pressure-solution rates hard.

The unexplained item: **SW-S4 ratchets 90× more than SW-T1 at the same frame** (0.528 vs
0.0058 µm) despite carrying 9× the tangential viscosity, which should *suppress* creep for a
given overstress. The candidate alternative is that this is the tail of the pre-injection
elastic settling flagged by the failed falsifier (1.186 µm, said to have relaxed by t ≈ 99 s
against a cycle-1 peak at t = 2619 s — so probably not, but it has not been excluded).

---

## 5. Recommendation

**Do not recalibrate to make the slip change per cycle.** Ye & Ghassemi's protocol is
monotonic. Nothing in the calibration dataset constrains cycle-to-cycle behaviour, so any
per-cycle increment tuned in is unfalsifiable against the data used to fit it — the same
trap as fitting against a channel the model solves for. The knob that *would* do it is the
tangential viscosity, which is the one the 2026-08-18 audit flagged as a fitted parameter
wearing a "numerics" label.

**Do not add fatigue or subcritical-growth mechanisms for paper 1.** §6.6.6 already names
them correctly. Adding an unvalidated damage law converts a clean, defensible negative
result into an unfalsifiable positive one.

**Do add three things that cost no runs:**

1. Reframe the null in §6.6.6 as jointly constitutive **and** boundary-condition, with the
   0 / 0.0058 / 0.367 µm frame ladder. This is the single most reviewer-exposed gap.
2. Qualify §5's "robust to the frame stiffness" — true of the ratio, 63× on the increment.
3. Replace the *named* absence of healing with the *measured* bound from §3 (≤1.05 MPa at
   lab b, wrong sign), citing the 95-series.

**One optional deck**, if the frame question is to be closed rather than qualified: SW-T1
equal-peak 3-cycle at ×0.25 frame — one number changed (`axial_bc_penalty`), no new mesh, so
§6.6.7's cost objection does not apply. It distinguishes "the null is constitutive" from
"the null is a stiff testing machine" and pins the unexplained 63×. Expect a stall risk:
`95_16` showed this solver meeting a dynamic instability and stopping dead, and ×0.25 is
well below critical stiffness on the initial ramp. A stall would itself be informative but
is not a deliverable.
