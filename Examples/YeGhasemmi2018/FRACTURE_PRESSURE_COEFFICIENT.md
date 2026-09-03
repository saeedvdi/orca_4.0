# The fracture pressure coefficient `χ` — is there an analytical solution?

**Question.** `fault_pressure_coefficient` is 0.86 on SW-S4 and 0.87 on SW-S3, and 1.0 on
SW-T1 and SW-T2. Is there an analytical way to determine it?

**Answer.** Yes — the coefficient has an exact definition and a well-established estimate,
and both are computable from quantities already measured for these specimens. Applying
them gives **χ ≈ 0.93–0.99**, and it puts a **hard lower bound of χ ≥ 0.933** on Sierra
White granite at 30 MPa. The 0.86–0.87 in use on the saw cuts lies *below* that bound. The
1.0 on the tensile fractures is at the opposite edge, defensible to within ~2 %.

Separately, and more importantly for the manuscript: **χ is not identifiable from slip data
alone** — only the product `μχ` is. That is what makes it available as a fitting lever in
the first place, and it is why a fitted value of 0.86 does not contradict any data.

---

## 1. What the coefficient is

In the decks it scales the fluid traction applied to the fracture faces:

```
pressure_traction_coefficient = -${fault_pressure_coefficient}
```

which makes the effective normal stress on the fracture

```
σ'_n = σ_n + χ p
```

and hence the Coulomb strength `τ_f = c + μ (σ_n + χ p)`.

## 2. The exact definition

Write a force balance across the fracture over a representative area `A`, of which `A_c` is
in solid–solid contact and `A − A_c` carries fluid at pressure `p` (tension positive):

```
σ_n A  =  σ_c A_c  −  p (A − A_c)
```

The quantity that governs friction is the mean contact stress carried by the asperities,
`σ'_n ≡ σ_c A_c / A`. Substituting,

```
σ'_n = σ_n + p (1 − A_c/A)            =>       χ = 1 − A_c/A
```

This is exact — it is the joint analogue of the Terzaghi/Nur–Byerlee result. **The whole
question therefore reduces to the real contact-area fraction.** Two standard closures
bracket it.

## 3. Estimate A — plastic asperity contact (Tabor)

When asperities are fully yielded, the contact area is set by force balance against the
indentation hardness `H`, with Tabor's relation `H ≈ 3 Y`:

```
A_c/A = σ'_n / H,     H ≈ 3 · UCS = 3 × 150 MPa = 450 MPa
χ = 1 − σ'_n/H = 1 − 30/450 = 0.9333
```

Plastic contact **maximizes** the contact area for a given load, so this is a **lower bound
on χ**. It is also the estimate closest to the reference value: inverting it,

| χ | implied `A_c/A` | implied `H` | as a multiple of UCS |
|---:|---:|---:|---:|
| 1.000 | 0 | ∞ | — |
| **0.935** *(reference model)* | 0.065 | 461 MPa | **3.08 ×** ← Tabor's `H ≈ 3Y` |
| 0.933 *(this estimate)* | 0.067 | 450 MPa | 3.00 × |
| **0.870** *(SW-S3)* | 0.130 | 231 MPa | 1.54 × |
| **0.860** *(SW-S4)* | 0.140 | 214 MPa | 1.43 × |

The reference's 0.935 lands on `H = 3.08 × UCS`, i.e. Tabor's relation almost exactly. The
fitted 0.86 requires an indentation hardness of **1.43 × UCS** — well under the 3× that
indentation of a brittle solid gives, and only 43 % above the *uniaxial* strength. There is
no material-property reading of the granite that produces it.

## 4. Estimate B — elastic asperity contact (Persson)

For elastic contact of a randomly rough surface, in the small-load limit,

```
A_c/A ≈ 4 σ'_n / (√π · E* · Z₂),      E* = E / (2(1−ν²)) = 37.3 GPa
```

with `Z₂ = √⟨|∇h|²⟩` the RMS surface slope, obtainable from JRC through Tse & Cruden
(1979), `JRC = 32.2 + 32.47 log₁₀ Z₂`:

| surface | JRC | `Z₂` | `A_c/A` | **χ** |
|---|---:|---:|---:|---:|
| decks' saw-cut value | 25 | 0.600 | 0.0030 | **0.997** |
| moderately rough | 5 | 0.145 | 0.0125 | **0.988** |
| smoothest the correlation reaches | 0 | 0.102 | 0.0178 | **0.982** |

Elastic contact gives χ between 0.98 and 0.997 — i.e. very close to 1.

**The two estimates bracket χ ∈ [0.93, 1.0].** Real surfaces are partly plastic at asperity
tips and partly elastic, so the truth sits inside that band. Nothing in this range reaches
0.86.

A useful side result: the elastic model gets the **direction** right. A smoother surface
has a smaller RMS slope, hence *more* contact area, hence a *lower* χ. So χ genuinely
should be lower on a saw cut than on a rough tensile fracture — which is the pattern the
decks encode. The spread the physics predicts is ~1.5 %, though, not the 14 % in use.

## 5. χ is not a constant

`χ = 1 − σ'_n/H` depends on the effective normal stress, which is exactly what injection
reduces:

| `σ'_n` | 30 MPa | 20 MPa | 10 MPa | 5 MPa |
|---|---:|---:|---:|---:|
| χ | 0.933 | 0.956 | 0.978 | 0.989 |

So a constant χ has the wrong trend as well as, on the saw cuts, the wrong level: the true
coefficient **rises toward 1 as the fracture unclamps**, which makes the late stages of each
injection more sensitive to pressure than a constant 0.86 represents. If one number must be
used, it should be evaluated at the effective stress of the stage that matters most.

## 6. Why 0.86 was reachable at all — the identifiability problem

The Coulomb strength is

```
τ_f = c + μ (σ_n + χ p)      =>      ∂τ_f/∂p = μ χ
```

A multi-stage injection test measures that **slope**, which is the *product* `μχ`. The
individual factors do not appear anywhere on their own. Concretely:

| χ | μ | `μχ` |
|---:|---:|---:|
| 0.860 | 0.5774 (φ = 30°) | 0.4965 |
| 1.000 | 0.4965 (φ = 26.4°) | 0.4965 |

**These two parameter sets are indistinguishable from slip data.** χ is identifiable only
when μ is fixed by an independent measurement; in these decks μ is itself calibrated through
JRC, JCS and φ_r, so χ and the strength envelope trade off exactly.

The SW-S3 header states this outright, and explains why the fit landed where it did:

> *"ONSET TIME IS ILL-CONDITIONED AGAINST THE STRENGTH ENVELOPE … Any strength lever (jrc,
> jcs, phi_r; PST peak_mu) has this pathology … THE WELL-CONDITIONED LEVER IS THE LOAD SIDE:
> fault_pressure_coefficient sets d(sigma'n)/d(injection), so it shifts onset TIME ~linearly
> (~96 s per 0.01)"*

So χ was selected as a **timing lever** — the numerically best-behaved knob for matching
slip onset — not as a material property. Both saw-cut decks label it honestly
(`CONTROL: legacy fitted fault-pressure attenuation`). The physics above says that lever
was pushed about 8 % past the edge of the feasible set, and that whatever it is
compensating for lives somewhere else in the model.

## 7. What to do

| | action |
|---|---|
| **If χ is to be a material property** | Set it from §3: `χ = 1 − σ'_n/(3·UCS) ≈ 0.93` for both saw cuts, and ~0.98–0.99 for the tensile fractures, then recalibrate the strength envelope. This removes a fitted parameter and replaces it with a derived one. |
| **If the fitted values are kept** | Report them as fitted coupling coefficients, not as effective-stress coefficients, and state that they lie below the plastic-contact bound. Do not present 0.86 as a physical property of the saw cut. |
| **Either way** | State that χ and μ are identifiable only as the product `μχ` from these experiments. This is a genuine result about the experiment, not a limitation of the model, and it is worth a sentence in the manuscript. |
| **Worth testing** | The candidate that would legitimately produce a low apparent χ is a fracture pressure that is systematically too high in the model — check the fracture pressure field against the port pressures on the saw cuts, whose smaller aperture means a steeper gradient than the tensile fractures. That would explain both the saw-cut/tensile split and the direction. |

## 8. Numbers used

| | value | source |
|---|---:|---|
| `E` | 67 GPa | paper, EXP |
| `ν` | 0.32 | paper, EXP |
| UCS | 150 MPa | paper, EXP (also used as JCS) |
| confining stress | 30 MPa | paper |
| `E*` = `E/(2(1−ν²))` | 37.32 GPa | derived |
| `H` ≈ 3·UCS | 450 MPa | Tabor |

Related: [`FINAL_BBFAST_PAPER_MC_MATERIAL_PROPERTY_COMPARISON.md`](FINAL_BBFAST_PAPER_MC_MATERIAL_PROPERTY_COMPARISON.md),
[`../Validaitons/benchmarks/PARAMETER_IDENTIFIABILITY_FRAMEWORK.md`](../Validaitons/benchmarks/PARAMETER_IDENTIFIABILITY_FRAMEWORK.md).
