# ORCA publication strategy — two papers, HM then THM

**Written 2026-08-24.** Formalises the question "should all the validations go in both papers,
or should Ye2018 carry paper 1 and Kalantar carry paper 2?"

**Short answer.** Split them — but not the way the question was posed. The split should be
**HM / THM by physics**, not "one validation dataset each". Kalantar belongs to the HM paper
*scientifically*; it is being kept out only because it is unfinished. And Kalantar cannot
support the thermal claim at all, because those experiments are isothermal.

---

## 1. The selection rule

Do not ask *"which validations do I have?"* Ask:

> **Does this case constrain a parameter, or falsify a mechanism, that the paper claims?**

This is the same identifiability discipline already applied to parameters in this project —
`Q` is not an independent observable; JRC and cohesion are indistinguishable on Ye2018's
loading path; `τ` and `dL_s` are one measurement on Kalantar's. Applied to whole **cases**, it
says: a validation that does not constrain a claim is not evidence, it is surface area for a
reviewer.

By that rule "all validations in both papers" is the worst option. It inflates both and buries
each paper's actual claim.

**Corollary.** Every case included must have a named claim it supports. If the claim cannot be
written in one sentence, the case is padding.

---

## 2. Paper 1 — HM

### Scope

| block | content | claim it supports |
|---|---|---|
| Verification | Terzaghi, Mandel, Darcy/erfc, mass-balance storage, thermal storage | the discretisation solves the equations it says it does |
| Validation | Ye2018 four specimens, BBFast primary | the constitutive model reproduces measured joint behaviour |
| Baseline | Ye2018 four specimens, Mohr–Coulomb (94-series) | the *form* of the law matters, not just its calibration |
| Cross-check | Kalantar **cross-checks only** (§2.2) | external corroboration of the most leveraged inferred constant |
| Optional | cyclic and shut-in arms | predictive use beyond the calibration path |

Four specimens × two constitutive laws + four analytical verifications is already a full
paper. It does not need more cases; it needs the ones it has to be airtight.

### 2.1 Do not wait for Kalantar

Ye2018 is **finished** — four specimens final, scorecard complete, write-ups done. Kalantar is
**mid-diagnosis**: three specimens failing in three different places with opposite-signed
envelope errors, one of them not yet loadable at all. Round 2 verified both of its fixes and
the aggregate score still moved the wrong way.

That is not a campaign with a submission date. Chaining paper 1 to it converts a finished
result into an open-ended one.

### 2.2 But pull three Kalantar results forward

These are cheap, already established, and they strengthen paper 1's weakest points. They cost
a paragraph each, not a campaign.

1. **The frame stiffness.** `K_sys` is paper 1's most leveraged *derived* constant — a ×2
   bracket moves `Q` by −93.9 % / +408 %. Kalantar **measures** it. An independent measurement
   of the constant you had to infer is the single most valuable import.
2. **The independent reanalysis of the same four specimens.** Kalantar's Figure 8 Pedrosa fits
   cover Ye2018's specimens. Somebody else's numbers for your samples.
3. **The angle identity finding.** `tan θ = (σ'ₙ − σ₃ + P_p)/τ` caught a mis-reduced fracture
   angle in *two independent papers* by the same method. That is a methodological contribution
   in its own right and it belongs wherever the method is first stated.

**Action:** this is already task #113. Do it as part of the paper-1 write-up, and present it as
*corroboration*, explicitly not as a validation campaign — otherwise a reviewer will ask for
the full Kalantar results, which is exactly what we are avoiding.

### 2.3 Known open items paper 1 must resolve or scope out

Not new work, but they must not be left ambiguous in the text:

* `bb_jrc_mobilized` is **inert in all four Ye2018 specimens** — and now also in all three
  Kalantar ones. If the JRC-mobilisation channel never moves, the paper cannot claim it as an
  active mechanism. Either fix it or state plainly that weakening is carried by the cohesion
  and normal-stress channels. **This is the highest-leverage open item in the project**, because
  it is shared by both papers.
* SW-S4's cohesion channel is identically zero; SW-S3 fits two output-only reporting knobs.
  Both are documented; both need a sentence rather than silence.
* `Q` is not an independent observable, and its `W/L` is circular (task #13). Say so.

---

## 3. Paper 2 — THM

### 3.1 The correction to the original plan

The plan as posed was: *Kalantar → add the thermal term → large-scale THM → thermal
short-circuiting.*

**Kalantar cannot earn the thermal capability.** Those experiments are isothermal, so they
supply **zero** thermal constraint. If paper 2's claim is "ORCA does THM", the first reviewer
question is "where is T validated?", and Kalantar does not answer it. Putting an HM validation
campaign inside a THM paper also makes the paper a grab-bag with two unrelated arguments.

So paper 2's critical path is thermal **from the first section**.

### 3.2 The capability is already there — checked 2026-08-24

`src/kernels/EnergyBalanceKernel/` contains:

```
OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel
OrcaFullySaturatedSinglePhaseHeatAdvectionKernel
OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel
OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel
OrcaHeatConduction / OrcaHeatConductionTimeDerivative
```

plus `OrcaTHMaterial`, and the mass kernel already carries the `−α_T dT/dt` storage term with a
regression test behind it (task #61).

**So paper 2 is a validation-and-application project, not a development one.** That is the
single most important fact for scoping it, and it moves the timeline substantially.

**One thing still unconfirmed:** whether heat transport is coupled *along the fracture
interface* (advection in the fracture with conduction into the matrix), as opposed to bulk
transport through an enhanced-permeability zone. The energy kernels listed above are bulk
kernels. **Check this before committing to the Lauwerier benchmark**, because that benchmark is
precisely a fracture-channel problem and it is the one that most directly supports the
short-circuiting claim.

### 3.3 Proposed structure

1. **Thermal verification, analytical.** Non-isothermal consolidation; then a point heat source
   in a saturated poroelastic medium (Booker & Savvidou), which exercises the full THM coupling
   against a closed form rather than just the T equation.
2. **Fracture heat transport.** The Lauwerier problem — heat advected along a fracture with
   conduction into the matrix. Canonical thermal-breakthrough benchmark; maps one-to-one onto
   short-circuiting. *Conditional on §3.2.*
3. **Code comparison at scale.** The DECOVALEX benchmark suite is the standard reference; pick
   the task whose geometry matches.
4. **Application: thermal short-circuiting.**

Treat 1–3 as *candidates to verify against the literature*, not settled citations. Confirm each
is the right fit and is reproducible from published data before building a deck.

### 3.4 Why short-circuiting is the right application

Short-circuiting is flow channelling into a high-aperture path, producing early thermal
breakthrough. **The channel is created by aperture heterogeneity — and aperture evolution under
Barton–Bandis closure plus slip dilation is exactly what paper 1 validates.**

So paper 2's argument becomes *"HM-evolved aperture heterogeneity controls thermal
breakthrough"*, which **uses** paper 1 rather than merely following it. That is a coupling
claim, not a capability demonstration, and it is the reason to write two papers in this order
instead of one large one.

It also means paper 1 is load-bearing for paper 2 and should be written to be cited that way —
in particular, the aperture law and its calibrated constants need to be stated in a form paper 2
can reference without restating.

---

## 4. Where the full Kalantar campaign ends up

**Not paper 2.** Options, in order of preference:

1. **Its own short validation note**, once it closes. Natural home, no forcing.
2. **An HM section in a later paper**, if a third paper emerges.
3. **Dropped to the cross-checks of §2.2 only**, if it does not close.

Deciding now is premature — it depends on whether round 3 lands and whether OG-T's preload
defect resolves (see `KALANTAR2025_ROUND3_BACKANALYSIS.md`). What matters today is that
**Kalantar is not blocking either paper.**

---

## 5. Decision summary

| question | answer |
|---|---|
| All validations in both papers? | **No.** One claim per case; the rest is surface area. |
| Ye2018 in paper 1? | Yes — four specimens, both laws, plus the verification suite. |
| Kalantar in paper 1? | **Cross-checks only** (frame stiffness, independent reanalysis, angle identity). Not the campaign. |
| Wait for Kalantar before submitting paper 1? | **No.** |
| Kalantar in paper 2? | **No** — it is isothermal and cannot support a thermal claim. |
| Does paper 2 need new code? | **Probably not** — the energy balance exists. Confirm fracture-interface heat transport first. |
| Paper 2 order? | Thermal verification → fracture benchmark → scale/code comparison → short-circuiting. |

---

## 6. Open items this document creates

* Confirm whether fracture-interface heat transport exists (§3.2). **Decides paper 2's scope.**
* Resolve or scope out the inert `bb_jrc_mobilized` channel (§2.3). **Affects both papers.**
* Task #113 — fold the three Kalantar cross-checks into the Ye2018 manuscript.
* Verify Booker & Savvidou, Lauwerier and the DECOVALEX task against the literature before
  building decks.
