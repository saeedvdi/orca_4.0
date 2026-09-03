# Using the verification benchmarks to constrain parameters — what is and is not defensible

**Purpose.** This note answers a question raised for the manuscript: *can the validation
points, in particular Sneddon and the intersecting-fracture case, be used to approximate
some of the model parameters?*

**Short answer.** Partly, and the precise version of the claim is both narrower and
stronger than the loose one. Stated loosely — "these benchmarks let us approximate model
parameters" — it is not defensible, because a verification benchmark compares the code to
a *known* answer and contains no experimental information. Stated precisely, three things
*are* defensible, and all three are quantitative:

1. **Identifiability.** Each closed form can be inverted analytically, and doing so shows
   exactly which parameters a measurement of that geometry can determine, and which are
   structurally invisible to it. Several of these inversions are one line.
2. **Conditioning.** The same inversion gives the amplification factor from measurement
   error to parameter error. For friction it is ~3.8×, which is the difference between a
   useful number and a useless one.
3. **An error floor.** The benchmarks measure the discretization bias of a given mesh
   against an exact answer. Any inversion performed on that mesh inherits that bias as a
   systematic floor, below which a fitted parameter cannot be trusted regardless of how
   good the data are.

What the benchmarks do **not** do is calibrate anything against experiment. The wording
suggested at the end of this note keeps that line clean.

---

## 1. What each benchmark can and cannot constrain

| Benchmark | Identifiable | Structurally NOT identifiable | Inversion |
|---|---|---|---|
| **Sneddon** | plane-strain modulus `E' = E/(1−ν²)`; fracture half-length `b` | **every fracture property** — the crack is open and traction-free, so no interface parameter enters at all | closed form |
| **Shear compression** | friction coefficient `tan θ` (given `E'`, `ψ`, `σ`, `b`) | cohesion (zero by construction); normal stiffness; anything tensile | closed form |
| **T-fracture** | `E'` and `μ` jointly, from three curves | roughness/state parameters; absolute `b` is prescribed by the junction | numerical only |
| **Fault verification** | Biot coefficient `α` (given `ν`) | anything frictional — there is no interface | closed form |

The right-hand column of exclusions is the part most worth carrying into the manuscript.
**Every one of these benchmarks deliberately reduces the constitutive law to a constant-µ
Coulomb interface**: `jrc = 0`, `use_dilatancy = false`, `use_slip_weakening = false`,
`rsf_a = 1e-9`. That is what makes four different laws comparable, and it is also why the
suite carries no information about JRC, JCS, `D_c`, `K_n`, the dilation angle, or the
rate-and-state parameters `a` and `b` — which are precisely the parameters the Ye and
Kalantar campaigns spend their effort on. The benchmarks constrain the *elastic and
frictional backbone* the calibration sits on, not the calibration itself.

---

## 2. The inversions

### 2.1 Sneddon → `E'` and `b`

```
w(s) = (4 p_f / E') · √(b² − s²)          E' ≡ E/(1 − ν²)
```

`w_max` alone cannot separate `E'` from `b` — only the product `b/E'` appears. The
separation comes from the **shape**. Squaring gives

```
w² = A²b² − A²s²      with A = 4 p_f / E'
```

which is *linear in s²*. A straight-line regression of `w²` on `s²` returns the slope
`−A²` and the intercept `A²b²`, hence `E'` from the slope and `b` from their ratio. No
non-linear solver, no initial guess. This is the same shape fit `sneddon_analytical.py`
already performs as a diagnostic; used the other way round it *is* the inversion, and it is
the standard basis of fracture-compliance estimation from injection tests.

**Measured floor** (shipped mesh, refinement 4, `../sneddon`):

| quantity | error against the exact solution |
|---|---:|
| amplitude `A` → `E'` | **0.693 %** |
| half-length `b` | **1.345 %** |

So on that mesh, `E'` cannot be recovered better than ~0.7 % and `b` better than ~1.3 %,
however clean the data. Both sensitivities are unity (`∂ln A/∂ln E' = −1`), so the
inversion is well conditioned — the error does not amplify.

### 2.2 Shear compression → the friction coefficient

This is the only benchmark in the suite whose closed form contains a *fracture* property:

```
g_t(s) = (4/E') · σ sinψ [cosψ − sinψ tanθ] · √(b² − s²)
```

Inverting for friction:

```
tanθ = cotψ − g_t,max E' / (4 b σ sin²ψ)
```

**Conditioning.** With `ψ = 20°`, `θ = 30°`:

```
|∂ln g / ∂ tanθ| = sinψ / [cosψ − sinψ tanθ] = 0.4608
```

so `Δtanθ = (relative error in g) / 0.4608`, and in relative terms the amplification is

> **3.76×** — a 1 % error in slip becomes a 3.8 % error in `tanθ`.

| slip error | `Δ tanθ` | recovered `θ` | |
|---:|---:|---|---:|
| 3.82 % *(shipped mesh)* | 0.0829 | 26.31° – 33.43° | **+3.4 / −3.7°** |
| 2 % | 0.0434 | 28.10° – 31.83° | ±1.9° |
| 1 % | 0.0217 | 29.06° – 30.92° | ±0.94° |
| 0.5 % | 0.0109 | 29.53° – 30.46° | ±0.47° |

This is the single most useful number in the note. **The friction angle is nearly four
times harder to determine than the slip is to measure**, so quoting a friction angle to
better than a degree requires slip to better than ~1 %. The shipped benchmark mesh is not
good enough for that, and neither is a laboratory slip measurement at typical scatter.

The amplification worsens as `ψ → 0` (a fracture nearly parallel to the loading axis
barely slips, so friction barely registers) and as `sinψ tanθ → cosψ` (approaching lock-up,
where the bracket goes to zero and the inversion becomes singular).

### 2.3 Fault verification → the Biot coefficient

Inside a laterally extensive pressurized layer the poroelastic response collapses to a
one-dimensional limit that is exact:

```
Δσ_xx + Δσ_zz = −α Δp (1 − 2ν)/(1 − ν)
        =>     α = −(Δσ_xx + Δσ_zz)(1 − ν) / [Δp (1 − 2ν)]
```

Unit sensitivity in the stress sum, and `∂ln α/∂ν = 1.68`, so a 0.01 error in Poisson's
ratio costs 1.7 % in `α`. **Measured floor:** the benchmark returns −15.19 MPa against an
exact −14.824, i.e. 2.5 %, so `α` is recoverable to about 2.5 % on that mesh.

### 2.4 T-fracture → jointly `E'` and `μ`, and a consistency test

There is no closed form here; Phan et al. (2003) is tabulated. What the geometry buys is
**over-determination**: one experiment yields three independent curves — the aperture of
the pressurized fracture, and the normal traction *and* slip of the frictional one — from
the same two parameters. Two unknowns against three curves means the extra curve is a
consistency check rather than another fitting degree of freedom, which is exactly what a
parameter estimate needs to be credible.

Two structural features make it more informative than the sum of its parts:

* The junction **couples the open and closed branches**. The aperture at the junction
  (136 mm measured, 137 mm reference) exists only because the frictional fracture lets the
  crack faces slide apart along it, so an *opening* observable carries information about
  the *friction* coefficient. No single-fracture geometry does that.
* The peak aperture exceeds the isolated-crack value by ~3 %, and that excess is
  interaction, not elasticity — so it constrains the coupling rather than `E'`.

**Measured sensitivity** — see §2.6. It is the best friction conditioning in the suite. The
measurement itself also carries a warning, §2.5.

### 2.5 The T-fracture has a stability limit, and it is close

Perturbing the friction angle away from 30° to measure `∂(observable)/∂θ` **failed at 25°**:
the solve stalled at t = 1.51 of 2.0 and never completed the pressure ramp. Lower friction
means the horizontal fracture slides more freely, the crack below opens further, which
unclamps the fracture further — a positive feedback with no equilibrium once friction drops
far enough.

That is a genuine property of the configuration, not a solver artifact, and it matters for
any inversion: **the T-fracture response is not smooth in `μ` over a wide range**, so a
gradient-based fit can walk into a region where the forward problem has no steady solution.
A useful inversion has to bracket friction from above and step carefully.

### 2.6 Measured: the junction aperture is a friction gauge

Perturbing the friction angle by ±2° about 30° and re-running (four ranks, ~3 min each)
gives the sensitivity of each observable directly:

| observable | 28° | 30° | 32° | `∂ln X/∂θ` | 1 % error in `X` → |
|---|---:|---:|---:|---:|---:|
| peak aperture | 277.14 mm | 276.24 mm | 275.43 mm | −0.155 %/° | ±6.5° |
| **aperture at the junction** | 142.79 mm | 136.14 mm | 129.95 mm | **−2.359 %/°** | **±0.42°** |
| **peak slip** | 64.86 mm | 61.28 mm | 57.95 mm | **−2.822 %/°** | **±0.35°** |
| min normal traction | −128.27 MPa | −128.73 MPa | −129.17 MPa | +0.035 %/° | ±29° |

Three things follow, and the first is the answer to the original question.

**The junction aperture determines friction almost as well as the slip does** — −2.36 %/°
against −2.82 %/°. That is the coupling made quantitative: an *opening* measurement,
which involves no sliding at all, carries nearly the full friction signal because the
crack can only open at its upper end by sliding along the frictional fracture. Away from
the junction the same measurement is worthless for friction: the peak aperture moves
0.155 %/°, fifteen times less.

**This geometry is the best-conditioned friction estimator in the suite.** Comparing like
for like, a 1 % measurement error gives

| | → friction angle |
|---|---:|
| shear compression, slip | ±0.94° |
| **T-fracture, peak slip** | **±0.35°** |
| **T-fracture, junction aperture** | **±0.42°** |

a factor of ~2.7 better than the single inclined fracture, because the far-field stress
holds the fracture clamped while the crack pressure does the driving, instead of one
remote stress having to do both jobs.

**The normal traction is not a friction observable.** At +0.035 %/° it would need a 1 ‰
measurement to place friction within 3°. It is a good check on the *solution* and a poor
check on the *parameter* — a distinction worth keeping straight when choosing what to
report.

---

## 3. Worked example — the fracture pressure coefficient `χ`

This is the question the framework is most useful for, and it is treated in full in
Section 4 of the authoritative
[`theory.md`](../../../Paper_1_Validations/General_Docs/Related_Theory/theory.md).
The short version, because it illustrates every point above:

* `χ` enters as `σ'_n = σ_n + χ p`, so the Coulomb strength is `τ_f = c + μ(σ_n + χ p)`.
* A strength envelope at **one** confining stress gives two observables (intercept, slope)
  against three unknowns (`c`, `μ`, `χ`) — underdetermined. `χ = 0.86` with `μ = 0.5774` is
  indistinguishable from `χ = 1` with `μ = 0.4965` (`φ = 26.4°`). **Two confining stresses
  break the degeneracy**; Ye ran all four specimens at 30 MPa, so their data cannot.
* There *is* an analytical constraint: `χ = 1 − A_c/A` exactly — verified numerically to
  eight significant figures in
  [`effective_stress_coefficient/`](effective_stress_coefficient/) — with the upper bound
  `χ ≤ 1 − σ'_n/H` from the asperity hardness. It runs the opposite way to intuition:
  `χ = 1` is the unattainable end, and the fitted 0.86 is comfortably inside.

This is the framework working as intended: the closed form says which combination the data
constrain, independent physics supplies a bound the data cannot, and the two together turn
"0.86 is a fitted number" into "0.86 is admissible but undetermined, and one more confining
stress would determine it".

---

## 4. Suggested wording for the manuscript

> The verification cases are not used to calibrate the model. They serve three purposes
> that bear on parameter estimation. First, each closed form can be inverted, which
> establishes analytically which parameters a measurement of that geometry determines:
> the Sneddon configuration constrains the plane-strain modulus and the fracture length
> but, because the crack is traction-free, carries no information about any interface
> property; the inclined-fracture configuration is the one that constrains the friction
> coefficient; and the poroelastic case constrains the Biot coefficient. Second, the same
> inversions give the conditioning — a 1 % error in measured slip propagates to a 3.8 %
> error in the friction coefficient — which sets the measurement precision a given
> parameter tolerance requires; the intersecting-fracture configuration is the
> best-conditioned of the four, in which the aperture at the junction responds to friction
> almost as strongly as the slip does, because the pressurized crack can open at its upper
> end only by sliding along the intersecting fracture. Third, the benchmarks measure the
> discretization bias of
> the mesh against the exact solution, and any parameter inferred on that mesh inherits
> that bias as a systematic floor: 0.7 % on the plane-strain modulus and 2.5 % on the Biot
> coefficient for the meshes used here.

**Do not write** that the benchmarks "approximate" or "calibrate" the fracture parameters.
They exercise a constant-µ Coulomb interface with roughness, dilation and rate-and-state
switched off, so they are silent on JRC, JCS, `D_c`, `K_n` and the state parameters.

---

## 5. Summary table

| | inverts to | conditioning | measured floor |
|---|---|---:|---:|
| Sneddon | `E'`, `b` | 1.0× (unit) | 0.69 % / 1.35 % |
| Shear compression | `tanθ` | **3.76×** | ±3.7° at the shipped mesh |
| Fault verification | `α` | 1.0× in the stress sum; 1.68× in `ν` | 2.5 % |
| T-fracture | `E'`, `μ` jointly | **0.35–0.42° per 1 % of slip or junction aperture — the best in the suite** | 2.6 % aperture, 1.3 % slip |
