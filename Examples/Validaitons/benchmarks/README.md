# CZM benchmarks — cross-model verification against closed-form solutions

Two classical fracture-mechanics problems, each run with **all four** interface
constitutive laws configured to the *same* idealized interface. The point is not to
calibrate four models; it is that four independent implementations of contact and
friction, given identical physics, must land on the same closed-form answer.

Reference configurations follow the GEOS validation suite so the results are directly
comparable to a second, independent code.

| | Sneddon | Shear compression |
|---|---|---|
| Source | [GEOS sneddon](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/sneddon/Example.html) | [GEOS singleFracCompression](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/singleFracCompression/Example.html) |
| Interface state | **open**, fluid-pressurized | **closed**, frictionally sliding |
| Exercises | CZM kinematics, interface-kernel sign convention, fluid-pressure interface kernel, traction-free open state | Coulomb return map, contact normal stress, slip direction |
| Closed form | `w(s) = 4(1-ν²) p_f/E · √(b²-s²)` | `g_t(s) = 4(1-ν²)/E · σ sinψ [cosψ - sinψ tanθ] · √(b²-s²)`, `σ_n = -σ sin²ψ` |

The two are complementary: Sneddon is insensitive to the friction law (the crack never
touches), and shear compression is insensitive to the tensile branch (the fracture never
opens). Passing only one of them proves very little; passing both constrains the whole
contact/friction path.

## Configuring four different laws to the same physics

Each law is reduced to a constant-µ Coulomb interface with no dilation, no weakening and
no rate-and-state:

| Law | How it is reduced |
|---|---|
| `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` | `friction_rough = friction_smooth`, `cohesion_rough = cohesion_smooth = 0` makes the roughness interpolation inert; `use_dilatancy = false`, `use_rate_and_state = false` |
| `ADOrcaBartonBandisContactTractionFastADHardening` | `jrc = 0` collapses the roughness angle, so `φ_peak = φ_r`; `use_slip_weakening = false`, `use_dilatancy = false` |
| `ADOrcaBartonBandisFlowRSFContactTraction` | `jrc = 0`; `use_dilatancy = false`; **`rsf_a` cannot be zero** (see below) |
| `ADOrcaPeakShelfTailFlowRSFContactTraction` | `peak = shelf = tail` friction coefficient; `dilation_work_fraction = 0`; **`rsf_a` cannot be zero** |

### Finding: two laws cannot be reduced to a classical Coulomb interface

`ADOrcaBartonBandisFlowRSFContactTraction` and
`ADOrcaPeakShelfTailFlowRSFContactTraction` both range-check `rsf_a > 0`. Neither has a
switch to disable rate-and-state, so **neither can represent a rate-independent Coulomb
interface exactly**, and neither can be verified against a rate-independent closed form
in the strict sense.

These decks use `rsf_a = 1e-9`, which makes the direct effect `a·p·asinh(z)` about
`1e-1 Pa` against a `~1e7 Pa` normal stress — eight orders below the strength and far
below the discretization error, so the verification is still meaningful. But if either
law is to be presented as a general-purpose contact law rather than a calibration vehicle
for the injection experiments, it should gain a `use_rate_and_state = false` path.

## Results

### Sneddon — `w_max` against `4(1-ν²) p_f b / E = 7.5e-4 m`

| Law | `w_max` (m) | error | `|σ_n| / p_f` |
|---|---|---|---|
| CompressionTensile | 7.347888e-4 | 2.03 % | 0 |
| Barton–Bandis FastAD | 7.347888e-4 | 2.03 % | 3.1e-16 |
| BB flow/RSF | 7.347888e-4 | 2.03 % | 0 |
| Peak–shelf–tail | 7.347888e-4 | 2.03 % | 0 |

All four agree to **seven significant figures**, and the open crack carries no traction.
The residual 2.03 % is the physical-model error of the benchmark itself, not a code
error: the analytic solution is for an *infinite* medium while the deck uses a 40 m box
around a 2 m crack, with QUAD4 elements resolving a square-root-singular crack tip. GEOS
reports the same order of agreement for the same configuration.

**This 2 % should be driven down by refinement before the number goes in a paper** — see
"suggested extensions" below.

### Shear compression — `slip_max` against `4(1-ν²) b σ sinψ[cosψ - sinψ tanθ]/E = 3.80785e-3 m`

| Law | `slip_max` (m) | error | runtime (8 ranks) |
|---|---|---|---|
| CompressionTensile | 3.9619744716535e-3 | 4.048 % | 27.3 s |
| Barton–Bandis FastAD | 3.9619744716544e-3 | 4.048 % | 27.1 s |
| BB flow/RSF | 3.9617038672728e-3 | 4.040 % | 30.8 s |
| Peak–shelf–tail | 3.9619744457263e-3 | 4.048 % | 30.9 s |

The CompressionTensile and Barton–Bandis laws agree to **twelve significant figures**, and
peak–shelf–tail to nine. These are completely independent implementations — a
roughness-interpolated Coulomb law with a coupled (γ, g_np) return map, a JRC/JCS law with
a bracketed Real-arithmetic return map and an implicit-function-theorem tangent, and a
three-stage friction law — so the agreement is a strong statement that all three land on
the same yield surface.

BB flow/RSF differs in the fifth significant figure, by 7e-7 m. That is the residual
`rsf_a = 1e-9` rate-and-state direct effect, which cannot be switched off in that law (see
above). The size of the discrepancy is exactly what that term predicts, which is itself a
useful confirmation.

The common +4.05 % offset is the benchmark's own model error, the same character as
Sneddon's 2.03 %: an 80 m domain around a 2 m fracture against a closed form derived for an
infinite medium, with QUAD4 elements resolving a square-root-singular tip. The four laws
bracket it identically, so it is not a constitutive error.

#### Sensitivity checks run while building this case

| Change | `slip_max`/load | vs analytic |
|---|---|---|
| `K_n = K_t = 1e12` (shipped) | 3.962e-3 | +4.0 % |
| `K_n = K_t = 1e10` | 4.529e-3 | +18.9 % |

The penalty stiffness must stay high: the extra compliance of a soft interface appears
directly as excess slip. This is also a useful confirmation that the benchmark is sensitive
to the quantity it is meant to measure.

## A Jacobian NaN found by this benchmark

The shear-compression case did not run at all when it was first assembled: it died at 10 %
of the load ramp with `DIVERGED_NANORINF` at linear-solve iteration 0, under **both** hypre
BoomerAMG and a direct SuperLU_DIST solve, at every time-step size down to 1e-4, while the
Newton residual itself converged quadratically.

The cause was in `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`: six
derivative sites evaluated the power-rule factor `p·base^(p-1)` with `pow`, and at
`base == 0` **both** MetaPhysicL overloads produce a NaN derivative —
`pow(dual, dual)` through `b'·log(a) = 0·(-inf)`, and `pow(dual, Real)` through
`b·a^(b-1) = 0·(+inf)` when `b == 0`. The residual stays finite, so only the Jacobian is
poisoned.

`normalized_roughness = (R - R_res)/(1 - R_res)` reaches exactly zero — not nearly zero —
once `(R_0 - R_res)·exp(-γ/L_R)` underflows below the double-precision spacing of `R_res`.
With this benchmark's slip rate that took two steps, which is precisely when the solve died.

Fixed by `OrcaCompressionTensile::powerRuleFactor`, which returns exactly 1 when `p == 1`
(never evaluating `pow(base, 0)`) and floors the base otherwise. Verified by a falsification
test: setting `roughness_decay_distance = 1.0` so the roughness never saturates made the
unfixed code run clean, with an unchanged slip amplitude.

Effect of the fix on this benchmark: fails at 10 % of load, 12 NaNs, 5.5 min → completes,
**0** NaNs, **27 s**. The 12x speedup is because every NaN forced a `dt` cutback.

Two of the six sites are latent on the production path: `dilationFromSlip` evaluates
`pow(cumulative_slip/L, m-1)`, and the cumulative slip is exactly zero on every step before
first yield, with `use_dilatancy = true` in every Ye (2018) deck.

## Suggested extensions (not yet implemented)

1. **Mesh/domain convergence for both benchmarks.** Refine the crack-region blocks and
   enlarge the outer box; show the error decreasing. This converts "2 % agreement" into
   "converging to the analytic solution", which is a much stronger statement.
2. **A 3D Sneddon (penny-shaped crack)** — `w_max = 8(1-ν²) p_f a / (π E)` — routed
   through `OrcaFaultInterface3DGenerator` rather than `BreakMeshByBlockGenerator`. The
   production decks use the former and it is currently unverified; this would also close
   the nodeset-propagation question raised by `fracture_flow/cubic_law`.
3. **A uniform-stress patch test.** An interface embedded in a uniformly stressed block
   must transmit the traction exactly with zero displacement jump, for any interface
   orientation. Cheap, and it catches rotation and sign errors that both benchmarks above
   can mask because their fractures are axis-aligned or singly-inclined.
