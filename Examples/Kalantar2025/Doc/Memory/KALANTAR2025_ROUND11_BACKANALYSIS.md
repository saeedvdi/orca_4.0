# Kalantar 2025 — Round-11 back-analysis: the OG-T preload is undrained

**2026-08-31 · branch `orca_v11`.** Wave A returned three of three (`110_30`, `110_31`,
`110_32`). Wave B (`110_33`, `110_34`, `110_35`) is **not to be submitted** — see §5.

Reproduce the gate with `python3 scripts/score_110_round11.py`.

---

## 1. The verdict: the hypothesis is refuted and the null fired

| run | slope d(σ'ₙ)/d(σ_d) | target | ratio | peak τ/τ_limit | yields at σ_d | slip µm |
|---|---:|---:|---:|---:|---:|---:|
| `110_30` og_t platen bonded | **−0.1097** | +0.2204 | **0.520** | 3.246 | 57.6 | 1134 |
| `110_31` og_t platen base bonded | **−0.1021** | +0.2204 | **0.518** | 3.410 | 64.0 | 1187 |
| `110_32` og_t **locked joint (null)** | **−0.1025** | +0.2204 | **0.376** | 0.065 | — | **6.7** |
| `110_16` og_t traction probe (r7) | −0.1041 | +0.2204 | 0.515 | 3.491 | 64.0 | 2356 |
| `110_08` og_t bbfast (r4) | −0.1013 | +0.2204 | 0.520 | 1.588 | 64.9 | 643 |
| `110_13` og_sh (r6) | +0.2170 | +0.2500 | **0.999** | 1.002 | 51.3 | 27 |
| `110_15` og_sc (r6) | −0.4148 | +0.2500 | 0.930 | 1.073 | 27.5 | 45 |

The gate required ratio ≥ 0.93, slope +0.20 ± 0.04, and no crossing of τ/τ_limit = 1.0
below σ_d = 160.43 MPa. `110_30` fails all three. In-plane platen freedom is **not** the
mechanism.

**The null is the result.** `110_32` locks the joint; it moves 6.7 µm, effectively nothing,
and still shows ratio 0.376 and a negative slope. The preregistered reading of that
outcome was "the shielding is elastic and no platen BC repairs it". That is now the
finding, and it retires the whole family of mechanical hypotheses — platen stiffness
(round 7), tip clearance (round 6), mesh angle, load train, in-plane freedom (round 11).
**None of them was ever going to work, because the joint is not being shielded
mechanically at all.**

---

## 2. What is actually happening: the pore pressure rises 49 MPa during the preload

`110_32`, over the 2 → 55 s preload ramp:

| t (s) | σ_d MPa | interface p MPa | σ₃ (Biot-eff) MPa | σ'ₙ (BB) MPa | σₙ (paper frame) | ratio |
|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1.65 | **2.19** | 31.67 | 30.81 | 29.97 | 1.028 |
| 10 | 21.19 | 9.61 | 27.23 | 28.78 | 35.18 | 0.818 |
| 30 | 70.16 | 28.19 | 16.26 | 23.72 | 48.22 | 0.492 |
| 55 | 131.52 | **51.08** | 2.92 | 17.85 | 64.51 | **0.277** |

Two things follow immediately.

**σ₃ is not collapsing.** `sigma3_fault_mpa_pp` is a Biot-effective stress: the total σ₃
is held at its commanded 33 MPa throughout, and 0.6 × 48.9 = 29.3 MPa accounts for the
entire 28.75 MPa fall. The confining boundary is fine.

**The σ'ₙ deficit is the pore pressure, to first order exactly.** At t = 55 s the joint is
short by 64.51 − 17.85 = 46.7 MPa, against α_f·p = 1.0 × 51.1 MPa. Add α_f·p back and the
pre-slip slope turns positive and becomes indistinguishable between specimens:

| run | d(σ'ₙ)/d(σ_d) | d(σₙ_total)/d(σ_d) | sin²θ |
|---|---:|---:|---:|
| `110_32` OG-T null | −0.1003 | **+0.2767** | 0.2204 |
| `110_30` OG-T r11 | −0.1102 | **+0.3066** | 0.2204 |
| `110_08` OG-T r4 | −0.1015 | **+0.2747** | 0.2204 |
| `110_13` OG-SH | +0.2200 | **+0.2768** | 0.2500 |

The **total** normal stress transfer onto the fracture plane is positive, of the right
magnitude, and the same on OG-T and OG-SH. Nothing structural is wrong with how load
reaches the joint.

---

## 3. Why OG-T and not the other two: the fracture is its own drain

The pressurisation coefficient dp/dσ_d over the pre-slip ramp is a hard invariant of every
OG-T deck this campaign has built, across five rounds and **both** loading modes:

| run | axial BC | d(σ_d) MPa | d(p) MPa | **dp/dσ_d** |
|---|---|---:|---:|---:|
| `110_08` r4 | displacement (penalty Dirichlet) | 64.5 | 24.3 | **0.376** |
| `110_16` r7 | traction (Neumann) | 66.0 | 25.0 | **0.379** |
| `110_30` r11 | traction (Neumann) | 58.6 | 24.4 | **0.416** |
| `110_32` null | traction (Neumann) | 131.5 | 48.9 | **0.372** |
| `110_13` OG-SH | displacement | 49.3 | 0.86 | **0.017** |
| `110_15` OG-SC | displacement | 24.4 | 2.60 | **0.098** |

**OG-T pressurises 22× more per unit load than OG-SH.** Ruled out as the cause, each by
data rather than argument:

- **Poroelastic constants** — `biot_coefficient` 0.6, `initial_porosity` 0.0033,
  `matrix_permeability` 1.4e-20, `fluid_bulk_modulus` 2.2e9 are byte-identical in all
  three decks.
- **Preload ramp duration** — the `if(t<2, …, if(t<55, …))` ramp is identical in all three.
- **Drainage ports** — `source_in`/`source_out` are single-node `ExtraNodesetGenerator`
  Dirichlet points in all three.
- **Axial BC type** — displacement and traction control give 0.376 and 0.379 on the same
  specimen. Round 7's traction swap was testing a variable that does not matter.

**The variable that does differ is the fracture's own transmissivity:**

| specimen | a_h at preload | k_frac (1e-13 m²) | Q (mL/min) | Table 2 stage-1 a_h |
|---|---:|---:|---:|---:|
| OG-SH | **4.92 µm** | 20.2 | 0.63 | 4.87 µm |
| OG-SC | **1.42 µm** | 1.67 | 0.006 | 1.03 µm |
| OG-T | **0.10 µm** | 0.008 | **0.000** | **0.10 µm** |

a_h³ differs by a factor of **119 000** between OG-SH and OG-T. OG-SH's fracture spans the
specimen and connects both ports with a conductance thousands of times the matrix's, so it
bleeds the poroelastic overpressure away as fast as the ramp generates it. **OG-T has no
such path.** Its matrix is 1.4e-20 m² and its fracture carries no flow at all — Q is
0.0000 mL/min for the whole ramp.

So the OG-T specimen is loaded **undrained**, and it responds exactly as an undrained
poroelastic solid should. Measured Skempton coefficient B = Δp/Δσ_mean = 48.9/(160.4/3)
= **0.914**. Predicted from the deck's own constants, with
1/M = n/K_f + (α−n)/K_s, K_d = E/3(1−2ν) = 30.88 GPa, K_s = K_d/(1−α) = 77.2 GPa:

    M = 108.3 GPa,  B = αM/(K_d + α²M) = 0.930

**0.914 measured against 0.930 predicted.** The OG-T deck is not doing anything wrong.
It is doing correct undrained poroelasticity for a 53 s ramp on a rock that cannot drain
in 53 s.

---

## 4. The defect is the preload protocol, not any constitutive constant

The deck's `initial_hydraulic_aperture = 1.0e-7` is **faithful to the paper** — Kalantar's
Table 2 gives OG-T stage 1 as a_h = 0.10 µm, k = 0.02 D, Q = 0.000 mL/min. OG-T really is
a tight, non-flowing tensile fracture at stage 1. Nothing about the aperture is wrong.

What is wrong is that the model applies 160.43 MPa of differential stress in 53 s to a
saturated specimen with no drainage path, and then begins the injection schedule
immediately. The experiment does not do that. The specimen is brought to its preload and
held with the pore system connected, so the pore pressure has equilibrated at 6 MPa before
stage 1 begins. **The model starts stage 1 with 51 MPa of preload-generated overpressure
still in the rock**, which removes 47 MPa of effective normal stress, which is why
τ/τ_limit crosses 1.0 at σ_d ≈ 58–64 MPa instead of holding to 160.43, which is why OG-T
sheds 0.5–2.4 mm of slip before injection, which is why **no OG-T constitutive constant in
this campaign has ever been fitted against a valid specimen.** Five rounds of the failure
chain reduce to one cause.

Consolidation estimate, for scale: c = kM/µ = 1.4e-20 × 1.083e11 / 1e-3 = **1.5e-6 m²/s**,
and the far corners of the core sit ~40 mm from the nearest port, giving t ≈ L²/c ≈
**1.0e3 s**. The 53 s ramp is 5 % of one time constant. OG-SH is unaffected not because it
is faster but because its fracture short-circuits the matrix entirely.

---

## 5. What to do, and what not to do

**Do not submit round-11 wave B.** `110_33` (OG-SH), `110_34` (OG-SC) and `110_35` (OG-T
full cycle) were all gated on `110_30` passing. It failed, and `110_35` in particular would
spend a full 6800 s cycle reproducing the same undrained preload.

**Round 12, OG-T only, one probe deck.** Lengthen the preload ramp from 53 s to ≥ 1.0e4 s
(≈10 consolidation times) with everything else held, and run to t = 1.1e4 s. No rebuild —
this is one `ParsedFunction` and one `end_time`. Preregistered gate, in the campaign's
usual form:

- Δp over the ramp **≤ 3 MPa** (against 48.9 today)
- ratio σ'ₙ(BB)/σₙ(paper frame) **≥ 0.93** at the end of the preload (0.277 today)
- pre-slip slope d(σ'ₙ)/d(σ_d) **= +0.22 ± 0.04** (−0.10 today)
- τ/τ_limit **< 1.0** at σ_d = 160.43 MPa, i.e. the specimen survives its own preload
- cumulative slip at end of preload **< 10 µm** (0.5–2.4 mm today)

If it passes, every OG-T constitutive constant becomes fittable for the first time and the
campaign restarts at round 4 for that specimen. If Δp falls but the ratio does not follow,
the diagnosis in §2–§3 is wrong and this document is the thing to correct.

**A cheaper alternative worth pricing first:** solve the preloaded state with the pressure
equation at steady state and start the transient from it. That is what the experiment
physically is, and it costs one steady-state solve instead of 1e4 s of transient. It was
not chosen as the primary because the slow ramp reuses the existing deck structure
unchanged and therefore cannot introduce a new defect while testing for an old one.

**Do not read anything further into the OG-SC slope.** `110_15`'s −0.4148 is fitted over a
σ_d range of only 24 MPa on a specimen that pressurises 0.098 MPa/MPa; it is not the OG-T
signature at smaller amplitude and it should not be diagnosed until OG-T is fixed.

---

## 6. One thing that stays open

Even with α_f·p added back, the total-stress slope is **+0.277** on both OG-T and OG-SH,
against sin²28° = 0.2204 and sin²30° = 0.2500. The offset is +26 % on OG-T and +11 % on
OG-SH, it is common-mode, and it is **not** the OG-T defect — but it is unexplained. Most
likely candidates are the definition of `effective_normal_paper_frame_mpa_pp` (whether the
σ_d it divides by is the same σ_d the ramp commands) and the interface's mean normal
direction over a fracture that is not a perfect plane. Worth half an hour before round 12,
because if `σ_d` is the offender then the gate's own target is mis-stated.
