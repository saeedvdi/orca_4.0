# The fracture pressure coefficient `χ` — is there an analytical solution?

**Question.** `fault_pressure_coefficient` is 0.86 on SW-S4, 0.87 on SW-S3, and 1.0 on
SW-T1 and SW-T2. The reference model used 0.935. Is there an analytical way to determine
it?

**Answer, in three parts.**

1. **Yes, it has an exact definition**: `χ = 1 − A_c/A`, where `A_c/A` is the real
   solid–solid contact-area fraction. This is verified numerically here to eight
   significant figures — see §4.
2. **There is a bound, and it runs the opposite way to intuition.** Asperities cannot
   carry more than the indentation hardness, which bounds χ **from above**:
   `χ ≤ 1 − σ'_n/H`. So **χ = 1.0 is the value that is strictly unattainable** — it
   requires zero contact area — while 0.86 is physically comfortable, needing the
   asperities to carry only 214 MPa. The saw-cut values are not the problem.
3. **But χ is not identifiable from a single-confining-stress injection test**, which is
   why it was available as a fitting lever at all. Ye ran all four specimens at 30 MPa.
   This is the part worth a sentence in the manuscript.

Verification decks and script:
[`../Validaitons/benchmarks/effective_stress_coefficient/`](../Validaitons/benchmarks/effective_stress_coefficient/).

---

## 1. What the coefficient is

In the decks it scales the fluid traction on the fracture faces:

```
pressure_traction_coefficient = -${fault_pressure_coefficient}
```

making the effective normal stress `σ'_n = σ_n + χ p`, and hence the Coulomb strength
`τ_f = c + μ (σ_n + χ p)`.

## 2. The exact definition

Force balance across the fracture over a nominal area `A`, of which `A_c` is in
solid–solid contact and the rest carries fluid at pressure `p` (compression positive):

```
S = (A_c/A) σ_c + (1 − A_c/A) p
```

The quantity governing friction is the solid-borne part per unit nominal area,
`σ'_n ≡ (A_c/A) σ_c`. Substituting,

```
σ'_n = S − (1 − A_c/A) p           =>       χ = 1 − A_c/A
```

Exact — the joint analogue of the Terzaghi/Nur–Byerlee result. **The question reduces
entirely to the contact-area fraction.**

## 3. The bound, and why it points the other way

The asperities carry the whole solid load, `σ'_n = (A_c/A) σ_c`, and cannot carry more
than the indentation hardness `H`. So `σ_c ≤ H`, hence

```
A_c/A ≥ σ'_n / H          =>          χ ≤ 1 − σ'_n / H          [UPPER BOUND]
```

**The direction matters and is easy to get backwards.** Fully plastic contact is the state
of *minimum* contact area — each asperity carrying the most it can — so it bounds χ from
*above*. Pushing χ toward 1 means shrinking the contact area, which drives the asperity
stress up without limit:

```
χ → 1    =>    A_c/A → 0    =>    σ_c → ∞
```

So χ = 1 is the unattainable end and small χ is the easy end. `H` is the main uncertainty,
spanning about a factor of seven:

| `H` | source | min `A_c/A` at σ'_n = 30 MPa | **max χ** |
|---:|---|---:|---:|
| 450 MPa | Tabor, `H ≈ 3 × UCS` | 0.0667 | **0.933** |
| 2 GPa | mineral indentation, low | 0.0150 | 0.985 |
| 5 GPa | mineral indentation, high | 0.0060 | 0.994 |

### The elastic estimate does not apply here

Persson's small-load elastic result, with the RMS slope `Z₂` from JRC through
Tse & Cruden (1979), gives χ = 0.982–0.997 — but the contact areas behind those numbers
imply asperity stresses of 1.7–9.9 GPa, past any credible hardness:

| JRC | `A_c/A` | χ | implied `σ_c` |
|---:|---:|---:|---:|
| 25 | 0.0030 | 0.997 | 9.93 GPa |
| 5 | 0.0125 | 0.988 | 2.40 GPa |
| 0 | 0.0178 | 0.982 | 1.69 GPa |

The asperities would yield and the area would grow until `σ_c = H`. The small-load elastic
limit is simply not the right regime at 30 MPa on granite. The script reports the implied
stress precisely so this is visible rather than hidden.

## 4. Numerical verification

Two decks, both in
[`../Validaitons/benchmarks/effective_stress_coefficient/`](../Validaitons/benchmarks/effective_stress_coefficient/).

**`chi_homogenized.i`** — the operator check. A uniform χ is applied and must be returned:

| | |
|---|---:|
| χ set | 0.860000 |
| χ measured | 0.860000 |
| `σ'_n` relative error | 6.0e-15 |

**`chi_resolved.i`** — the physics check. The contact patches are built **explicitly** as
alternating strips: contact strips carry a stiff law and no fluid, void strips carry a
negligible stiffness and the full fluid pressure at coefficient 1. **No χ is applied
anywhere.** It is recovered from the force balance the solver performs:

| realized `A_c/A` | `1 − A_c/A` | χ measured | rel. error | asperity stress |
|---:|---:|---:|---:|---:|
| 0.050000 | 0.9500000 | 0.9500001 | 1.1e-07 | 220.0 MPa |
| 0.100000 | 0.9000000 | 0.9000000 | 5.2e-08 | 120.0 MPa |
| 0.137500 | 0.8625000 | 0.8625000 | 3.3e-08 | 92.7 MPa |
| 0.200000 | 0.8000000 | 0.8000000 | 1.6e-08 | 70.0 MPa |
| 0.300000 | 0.7000000 | 0.7000000 | 1.4e-08 | 53.3 MPa |

The identity holds to 8 significant figures. The asperity-stress column is the diagnostic
that makes the bound's direction obvious: **smaller contact area means higher asperity
stress**, so the constraint bites at high χ, not low.

## 5. χ is not a constant

`χ ≤ 1 − σ'_n/H` and injection reduces `σ'_n`, so the ceiling **rises toward 1** as the
fracture unclamps:

| `p` | 0 | 5 | 10 | 15 | 20 MPa |
|---|---:|---:|---:|---:|---:|
| min `A_c/A` | 0.0667 | 0.0562 | 0.0455 | 0.0345 | 0.0233 |
| max χ | 0.933 | 0.944 | 0.955 | 0.966 | 0.977 |

A constant χ therefore has the wrong *trend* whatever value is chosen. If one number must
be used, evaluate it at the effective stress of the stage that matters most.

## 6. Verdict on the values in use

| | χ | `A_c/A` | asperity stress | verdict |
|---|---:|---:|---:|---|
| SW-T1 / SW-T2 | 1.000 | 0.0000 | ∞ | **impossible in the strict sense** — needs zero contact |
| reference model | 0.935 | 0.0650 | 462 MPa | feasible only if `H > 3 × UCS` |
| SW-S3 | 0.870 | 0.1300 | 231 MPa | **feasible** |
| SW-S4 | 0.860 | 0.1400 | 214 MPa | **feasible** |

The saw-cut values are physically comfortable. χ = 1.0 on the tensile fractures is the
strictly unattainable one, though as an idealization it is only ~1–7 % past the bound,
and "χ ≈ 1 for a fracture" is the standard assumption.

More importantly, **the ordering the decks encode is the physically expected one**: a
better-mated saw cut has more contact area and therefore a lower χ; a rough tensile
fracture has less and sits near 1. The physics supports the choice qualitatively. What it
does not supply is the specific value 0.86, and §7 explains why nothing in the data does
either.

## 7. Why 0.86 was reachable at all — the identifiability problem

The Coulomb strength is `τ_f = c + μ(S − χp)`, so a strength envelope measured at **one**
confining stress gives two observables — an intercept `c + μS` and a slope `−μχ` — against
three unknowns. The system is underdetermined, and χ, μ and the cohesion trade off
directly. Concretely, from slip data alone:

| χ | μ | `μχ` |
|---:|---:|---:|
| 0.860 | 0.5774 (φ = 30°) | 0.4965 |
| 1.000 | 0.4965 (φ = 26.4°) | 0.4965 |

**Two confining stresses break the degeneracy.** With `μ(S₁ − χ p₁) = τ₁` and
`μ(S₂ − χ p₂) = τ₂`, two equations in two unknowns are generically solvable. **Ye ran all
four specimens at 30 MPa**, so their data cannot separate χ from μ — which is exactly why
χ was available as a free lever.

The SW-S3 header says as much:

> *"ONSET TIME IS ILL-CONDITIONED AGAINST THE STRENGTH ENVELOPE … Any strength lever (jrc,
> jcs, phi_r; PST peak_mu) has this pathology … THE WELL-CONDITIONED LEVER IS THE LOAD SIDE:
> fault_pressure_coefficient sets d(sigma'n)/d(injection), so it shifts onset TIME ~linearly
> (~96 s per 0.01)"*

χ was selected as a **timing lever**, not measured. Both saw-cut decks label it honestly
(`CONTROL: legacy fitted fault-pressure attenuation`). The physics says the value is
admissible; the experiment says it is not determined.

## 8. What to do

| | action |
|---|---|
| **Keep the fitted values** | Defensible. They are inside the feasible set and in the physically expected order. Report them as calibrated coupling coefficients constrained to `χ ≤ 1 − σ'_n/H`, not as measured surface properties. |
| **Reconsider χ = 1.0 on SW-T1/T2** | It is the one value strictly outside the bound. `χ = 0.98` costs little and is defensible; if 1.0 is kept, state it as the standard idealization. |
| **State the identifiability limit** | χ and μ are separable only across two or more confining stresses, and Ye's four specimens are all at 30 MPa. This is a genuine result about the experiment, not a limitation of the model. |
| **For future experiments** | Run at least one specimen at a second confining stress. That single change turns χ from a fitted lever into a measured property. |
| **Optional refinement** | Replace the constant with `χ(σ'_n) = 1 − σ'_n/H`, which supplies the correct rising trend during injection at the cost of one material constant. |

## 9. Numbers used

| | value | source |
|---|---:|---|
| `E` | 67 GPa | paper, EXP |
| `ν` | 0.32 | paper, EXP |
| UCS | 150 MPa | paper, EXP (also used as JCS) |
| confining stress | 30 MPa | paper, all four specimens |
| `E*` = `E/(2(1−ν²))` | 37.32 GPa | derived |
| `H` ≈ 3·UCS | 450 MPa | Tabor |
| `H` (mineral indentation) | 2–5 GPa | quartz/feldspar hardness, bulk granite |

Related: [`FINAL_BBFAST_PAPER_MC_MATERIAL_PROPERTY_COMPARISON.md`](FINAL_BBFAST_PAPER_MC_MATERIAL_PROPERTY_COMPARISON.md),
[`../Validaitons/benchmarks/PARAMETER_IDENTIFIABILITY_FRAMEWORK.md`](../Validaitons/benchmarks/PARAMETER_IDENTIFIABILITY_FRAMEWORK.md).
