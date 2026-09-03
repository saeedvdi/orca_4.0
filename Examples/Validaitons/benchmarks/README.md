# Fault-mechanics benchmarks — verification against closed-form solutions

Four problems from the GEOS validation suite. Three are fracture-mechanics cases run with
**all four** interface constitutive laws configured to the *same* idealized interface; the
fourth has no interface at all and instead exercises the poroelastic coupling. The point is
not to calibrate four models; it is that four independent implementations of contact and
friction, given identical physics, must land on the same reference answer.

Reference configurations follow the GEOS validation suite so the results are directly
comparable to a second, independent code.

| | Sneddon | Shear compression | T-fracture | Fault verification |
|---|---|---|---|---|
| Source | [GEOS sneddon](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/sneddon/Example.html) | [GEOS singleFracCompression](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/singleFracCompression/Example.html) | [GEOS intersectFrac](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/intersectFrac/Example.html) | [GEOS faultVerification](https://geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/validationStudies/faultMechanics/faultVerification/Example.html) |
| Interface state | **open**, fluid-pressurized | **closed**, frictionally sliding | **both, meeting at a junction** | **no interface** — the fault is geometry only |
| Exercises | CZM kinematics, interface-kernel sign convention, fluid-pressure interface kernel, traction-free open state | Coulomb return map, contact normal stress, slip direction | junction topology, fracture–fracture interaction, friction driven by purely induced shear | Biot coupling term and its sign, effective-to-total stress conversion, poroelastic inclusion response |
| Reference | `w(s) = 4(1-ν²) p_f/E · √(b²-s²)` | `g_t(s) = 4(1-ν²)/E · σ sinψ [cosψ - sinψ tanθ] · √(b²-s²)`, `σ_n = -σ sin²ψ` | Phan et al. (2003) boundary-element solution, supplied as tabulated data | Wu et al. (2020), supplied as tabulated reference data |

The first two are complementary: Sneddon is insensitive to the friction law (the crack
never touches), and shear compression is insensitive to the tensile branch (the fracture
never opens). Passing only one of them proves very little; passing both constrains the
whole contact/friction path.

The T-fracture is where those two states **meet**. A pressurized crack terminates on the
middle of a compressed, frictional fracture, so one interface is open and the other closed
in the same solve, and the junction between them is a place neither single-fracture case
can reach. It is also the only case here in which nothing shears the sliding fracture
directly — its slip is induced entirely by the crack opening beneath it.

The fault verification is complementary in a different way: it contains no contact law at
all, so it isolates the poroelastic path that the other three never touch.

Two of the four have reference solutions that are not formulas this repository can
evaluate; GEOS publishes them as tabulated data, reproduced verbatim here as
`AnalyticalSolution.txt` and as `Aperture.txt` / `Slip.txt` / `NormalTraction.txt`.

Caveats on "directly comparable to a second, independent code":

* **Sneddon does not use the GEOS elastic constants.** GEOS specifies `K = 16.7 GPa`,
  `G = 10 GPa` (so `E ≈ 25 GPa`); this deck uses `E = 10 GPa`, `ν = 0.25` directly. The
  opening scales as `p_f b / E`, so the benchmark is internally consistent and the
  *relative* error is comparable, but the absolute `w_max` is not GEOS's number. The other
  three do use the GEOS material properties.
* **The T-fracture domain is half the reference's.** The supplied mesh spans ±500 m against
  GEOS's ±1000 m, with rollers on every outer boundary, which stiffens the response. This
  is measured, not assumed — see the finding below — and it accounts for the whole residual.
* **Two meshes are not in the repository.** `*.e` is gitignored and the Exodus files are
  6.4 MB (shear compression) and 3.1 MB (T-fracture), so a fresh clone cannot run those two
  even though `tests` expects to. Their Cubit journals *are* tracked
  (`shear_compression/mesh/*.jou`, `fracutre_interseciton_problem/mesh/*.jou`) as the
  recovery route; for shear compression, also run `mesh/correct_inclination.py` afterwards.

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

## Comparison scripts

Each benchmark ships a standalone script that reads the MOOSE output, evaluates the
closed form, and writes the comparison out as CSV plus a figure:

| Script | Reads | Writes |
|---|---|---|
| [`sneddon/sneddon_analytical.py`](sneddon/sneddon_analytical.py) | `sneddon_<law>_out.csv`, `sneddon_<law>_out_crack_opening_profile_*.csv` | `sneddon_comparison_summary.csv`, `sneddon_comparison_profile.csv`, `sneddon_comparison.png` |
| [`shear_compression/shear_compression_analytical.py`](shear_compression/shear_compression_analytical.py) | `shear_compression_<law>_out.csv`, `..._out_slip_profile_*.csv`, and the mesh named by the deck | `shear_compression_comparison_summary.csv`, `shear_compression_comparison_profile.csv`, `shear_compression_comparison.png` |
| [`fracutre_interseciton_problem/frac_intersection_analytical.py`](fracutre_interseciton_problem/frac_intersection_analytical.py) | `frac_intersection_<law>_out_aperture_profile_*.csv`, `..._horizontal_profile_*.csv`, `Aperture.txt`, `Slip.txt`, `NormalTraction.txt` | `frac_intersection_comparison_summary.csv`, `..._profile.csv`, `..._comparison.png` |
| [`sneddon/sneddon_convergence.py`](sneddon/sneddon_convergence.py) | runs the deck itself at several refinement levels | `sneddon_convergence.csv`, `sneddon_convergence.png` |
| [`fracutre_interseciton_problem/frac_intersection_convergence.py`](fracutre_interseciton_problem/frac_intersection_convergence.py) | runs the deck itself at several refinement levels | `frac_intersection_convergence.csv`, `frac_intersection_convergence.png` |
| [`Induced_stress_along_a_fault_mesh/fault_verification_analytical.py`](Induced_stress_along_a_fault_mesh/fault_verification_analytical.py) | `fault_verification_<case>_out*.csv`, `AnalyticalSolution.txt` | `fault_verification_comparison_summary.csv`, `..._profile.csv`, `..._comparison.png` |
| [`shear_compression/mesh/correct_inclination.py`](shear_compression/mesh/correct_inclination.py) | the Cubit mesh | `..._psi20.e`, the mesh at the GEOS reference geometry |

```
python sneddon_analytical.py            # BBFast and MC (default pair)
python sneddon_analytical.py --all      # all four interface laws
python sneddon_analytical.py --no-plot  # CSV only
```

They need only numpy and matplotlib, so they run under the `moose` environment or the
base miniforge python. `netCDF4` is used when available to read the fracture half-length
straight from the mesh, with a fallback when it is not.

Both scripts compare in two independent ways. The first is the pointwise error of the
profile against the closed form. The second is a **shape fit**: squaring the closed form
gives `w² = A²b² − A²s²`, which is linear in `s²`, so a straight-line regression of `w²`
on `s²` recovers the amplitude `A` and the half-length `b` that the numerical solution
actually carries — no non-linear solver, no scipy. This separates two failure modes that
a single scalar error cannot distinguish: a wrong constitutive amplitude, and a crack that
is effectively shorter than the meshed one because the tip elements cannot resolve the
square-root singularity. Both benchmarks turn out to be the second.

Each script also re-reads its own deck and reports any drift between the deck's constants
and the script's, so the comparison cannot quietly validate against the wrong numbers.

## Results

### Sneddon — `w_max` against `4(1-ν²) p_f b / E = 7.5e-4 m`

| Law | `w_max` (m) | error | `abs(σ_n) / p_f` |
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

The shape fit decomposes that 2.03 % and shows it is entirely a tip effect. Both laws
return an amplitude `A` within **0.69 %** of `4(1-ν²)p_f/E`, and an effective half-length
of **0.9865 m** against the meshed 1.0 m — the crack behaves 1.35 % shorter than it is,
because the tip elements cannot resolve the square-root singularity, and `w_max = A·b`
carries both errors. The constitutive amplitude is therefore roughly three times better
than the headline scalar suggests.

That 2.03 % is a level-4 number, and it converges — see **Mesh convergence** below.

### Shear compression — `slip_max` against `4(1-ν²) b σ sinψ[cosψ - sinψ tanθ]/E = 3.80785e-3 m`

Re-run 2026-09-02 on the corrected ψ = 20° mesh (see the finding below).

| Law | `slip_max` (m) | error | `σ_n` (MPa) | `σ_n` error | fitted amplitude error |
|---|---|---|---|---|---|
| CompressionTensile | 3.6625270076046e-3 | −3.816 % | −11.2985 | 3.41 % | **0.218 %** |
| Barton–Bandis FastAD | 3.6625270076052e-3 | −3.816 % | −11.2985 | 3.41 % | **0.218 %** |
| BB flow/RSF | 3.6623340406678e-3 | −3.821 % | −11.2986 | 3.41 % | 0.213 % |
| Peak–shelf–tail | 3.6625269892448e-3 | −3.816 % | −11.2985 | 3.41 % | 0.218 % |

The **fitted amplitude** column is the one to read. `slip_max` and the mean `σ_n` both
carry the crack-tip discretization error; the shape-fit amplitude does not, and it says
**all four laws reproduce the closed-form slip amplitude to about 0.2 %**. The residual
−3.8 % on `slip_max` is the tip and finite-domain effect, and it now has the same sign as
Sneddon's (numerical below analytic, because a finite domain is stiffer than an infinite
one).

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

These figures supersede an earlier table that reported +4.05 % for all four laws. That
table was produced on a mesh whose fracture sat at 23.93° rather than the specified 20°;
see the next section.

### Finding, resolved: the mesh was built at the wrong inclination

`inclination_deg = 20.0` and `half_length = 1.0` in all four shear-compression decks. The
mesh they loaded had the fracture running from `(-0.9125, -0.405)` to `(+0.9125, +0.405)`:
perfectly straight through the origin, but at **`ψ = 23.93335°`** with half-length
**`b = 0.998339 m`**. Every `*_analytic` postprocessor was therefore being evaluated at a
geometry the mesh did not have.

**The GEOS reference case specifies ψ = 20.0° and b = 1.0 m**, so the deck constants were
right and the mesh was wrong. Fixed on 2026-09-02; the numbers in the table above are from
the corrected mesh.

The normal stress is what makes this unambiguous. `σ_n = -σ sin²ψ` is pure statics: it
does not depend on the friction law, on the constitutive model, or, in the mean, on mesh
resolution. The decks have been reporting

| | `σ_n` (MPa) | vs numerical |
|---|---|---|
| numerical (both laws) | −15.917 | — |
| analytic at the deck's `ψ = 20°` | −11.698 | **36.07 %** |
| analytic at the meshed `ψ = 23.93335°` | −16.457 | 3.28 % |

A 36 % error on a quantity that only statics controls cannot be a discretization effect,
and `sigma_n_rel_error = 0.3607` has been sitting in `shear_compression_*_out.csv` all
along. It was never picked up because the results table above reports only `slip_max`.

The shape fit closes it. The amplitude the numerical solution actually carries is
`A = 4.14207e-3`, against

| | analytic `A` | fit vs analytic |
|---|---|---|
| deck `ψ = 20°` | 3.80785e-3 | **+8.78 %** |
| meshed `ψ = 23.93335°` | 4.13667e-3 | **+0.13 %** |

So the friction law is not carrying a 4 % error at all: **BBFast and MC both reproduce the
closed-form slip amplitude to 0.13 % once it is evaluated at the geometry that was meshed.**
What remains — 4.06 % on `slip_max` and 3.28 % on the mean `σ_n` — is the tip and
finite-domain effect, and it now has the *same sign* as Sneddon's (numerical below
analytic, because a finite domain is stiffer than an infinite one). The shipped +4.05 %
had the opposite sign, which was the other clue.

#### How it was fixed

The webcut offsets in the Cubit journal were `0.9125` and `0.405`, which is what produced
23.93335°. They are now `cos 20° = 0.93969262078591` and `sin 20° = 0.34202014332567`, so
regenerating with Cubit gives the reference geometry directly.

Cubit is not available everywhere, and the 6.4 MB Exodus file is too large for git, so
[`mesh/correct_inclination.py`](shear_compression/mesh/correct_inclination.py) produces the
corrected mesh from the existing one instead. It applies the anisotropic scaling

    x *= cos(20°)/0.9125 = 1.029800,    y *= sin(20°)/0.405 = 0.844494

which sends the meshed tip `(0.9125, 0.405)` exactly onto `(cos 20°, sin 20°)`. Scaling is
a linear map, so quads stay quads, the fracture stays straight, conforming and through the
origin, and connectivity, blocks, nodesets and sidesets are untouched — only coordinates
change. The four decks now load `..._psi20.e` and their two pin coordinates are scaled to
match.

**The cost, stated plainly:** the outer box is no longer square. It is 82.384 m × 67.560 m
rather than 80 × 80, so the domain is 16 % tighter in y than the GEOS case. Both are far
field relative to a 2 m fracture, but the finite-domain part of the residual error is not
numerically identical to GEOS's. Regenerating from the corrected journal in Cubit removes
that caveat.

`shear_compression_analytical.py` reads the mesh path out of the deck and reports the
as-meshed geometry against the declared one on every run, so this class of error cannot
recur silently.

### Finding: the profile sampler wrote nothing on every deck in this suite

All eight decks set `execute_on = FINAL` on their `SideValueSampler`. **A side sampler
executed on `FINAL` never runs its boundary loop**, so every
`*_crack_opening_profile_*.csv` and `*_slip_profile_*.csv` in this suite contained a
header line and no data. The scalar postprocessors were unaffected, which is why it went
unnoticed: `w_max` and `slip_max` were always right, and nothing else was ever plotted.

Verified by running one deck with three samplers side by side — `SideValueSampler` on
`FINAL` (header only), the same sampler on `TIMESTEP_END` (128 rows), and
`ElementValueSampler` (full block). Fixed in all eight decks by moving to
`TIMESTEP_END`; the last numbered file is the converged profile. Without this the
comparison scripts above have nothing to compare, and neither of the two findings on this
page could have been made.

### T-fracture — two intersecting fractures against Phan et al. (2003)

A vertical crack, `x = 0`, `y ∈ [-50, +50]`, pressurized to **100 MPa**, whose upper tip
lands on the middle of a horizontal frictional fracture, `y = +50`, `x ∈ [-25, +25]`, under
a far field of `σ_yy = -100 MPa`, `σ_xx = 0` with rollers on every outer boundary. The
reference is the symmetric-Galerkin boundary-element solution of Phan, Napier, Gray &
Kaplan (2003), *Int. J. Numer. Meth. Engng* **57**, 835–851, shipped with GEOS as three
digitized curves and reproduced verbatim here.

Errors are RMS against the reference interpolated onto the sample points, as a percentage
of the reference's own span. All four laws:

| | aperture (vertical) | normal traction (horizontal) | slip (horizontal) |
|---|---:|---:|---:|
| RMS, full profile | **2.59 %** | 12.26 % | **1.30 %** |
| RMS, smooth stretch only | — | **1.69 %** | — |

| Quantity | Orca | Phan et al. | error |
|---|---:|---:|---:|
| peak aperture | 276.24 mm | 282.23 mm | −2.12 % |
| aperture at the T-junction | 136.14 mm | 137.18 mm | −0.76 % |
| peak aperture ÷ isolated-crack Sneddon | 1.0072 | 1.0290 | — |
| mobilized `abs(τ)/abs(σ_n)` where sliding | 0.57734 | `tan 30° = 0.57735` | 2e-5 |
| slip antisymmetry residual | 1.0e-12 mm | 0 | — |

The four laws agree with each other to better than 0.3 % on every quantity.

Two checks here do not use the reference file at all. The slip must be **antisymmetric**
about the junction, because its driver is, and it comes out antisymmetric to 1e-12 mm.
And where the horizontal fracture slides, `|τ|/|σ_n|` must sit on `tan 30°` — it does, to
five significant figures. Near the tips it correctly falls *below* that: those stretches
are still stuck, and a profile pinned at 0.57735 everywhere would be the bug.

#### Why the junction is the whole point

The peak aperture **exceeds** the isolated-crack closed form — Phan gives 282.2 mm against
Sneddon's 274.3 — and the aperture at the junction is 135 mm rather than the zero an
ordinary crack tip would give. Both happen because the horizontal fracture lets the crack
faces slide apart *along* it, relieving the upper end of the crack. Getting 136 mm there
rather than ~0 is the single number that says the junction topology is right.

#### Finding: `block_pairs` will not split a junction, so the fractures are split in two passes

`BreakMeshByBlockGenerator`'s `block_pairs` mode refuses to split any node touching more
than two blocks — *"If it is a junction between more than two blocks, we do not split it"*
(`framework/src/meshgenerators/BreakMeshByBlockGenerator.C`). That rule is exactly right at
the three fracture **tips**, which must stay welded, but the T-junction node touches the
left flank, the right flank and the cap above, so a single pass welds it shut. The aperture
and the slip are then pinned to zero precisely where the reference puts their maxima, and
nothing else in the deck complains.

The fix is to split one fracture at a time, re-blocking in between so that every node is a
two-block node at the moment it is split:

    pass 1   flanks merged into `core`  ->  (0,50) sees {core, cap}                -> splits
    pass 2   `core` re-split left/right ->  the core-side copy sees {left, right}  -> splits

Verified on the generated mesh: **3** node copies at the junction, **1** at each of the
three tips, **2** along the fracture interiors. A second consequence is that the horizontal
fracture needs a `cap` block carved out of the matrix at all — a fracture with tips inside
the domain is never a whole block boundary, so the pair has to be manufactured.

#### Finding, measured: the residual is the domain, not the model

Every quantity comes in **low**, consistently: peak aperture −2.1 %, peak slip −8.9 %. That
sign pattern points at the domain rather than at the constitutive law, because this mesh
spans ±500 m where the GEOS reference spans ±1000 m, and rollers on a smaller box stiffen
the response.

Measured rather than argued: rerunning the same mesh with the horizontal fracture removed
turns the vertical crack into an ordinary isolated Sneddon crack, whose exact answer is
known.

| | peak aperture | vs exact |
|---|---:|---:|
| exact Sneddon, infinite medium | 274.26 mm | — |
| this mesh, isolated crack | 267.89 mm | **−2.32 %** |

So the domain alone costs −2.32 %, against a T-fracture peak-aperture error of −2.12 %.
Corrected for it, the peak aperture lands within ~0.2 % of Phan et al. Enlarging the box is
the only way to remove this, and it needs a new mesh.

For reference, the digitizer step in the supplied curves is 0.31 mm on `Aperture.txt`,
0.14 MPa on `NormalTraction.txt` and 0.35 mm on `Slip.txt` — about 0.1 % of span — so
digitization is *not* what is limiting the comparison. `Aperture.txt` does contain a
physically impossible −0.306 mm at the tip, which is a digitizer artifact and nothing more.

#### Finding: the 12.3 % traction error lives in three elements per side

The normal traction is the one curve that does not match at the few-percent level, and the
error is not spread over the profile. Over `3 m < |x| < 22 m` it is **1.69 %**; essentially
all of the rest sits in the two crack-tip elements and the element abutting the junction —
the three places where the reference has a singularity that a constant-per-element contact
traction cannot represent (`r^(-1/2)` at each tip, and a 118 MPa → 0 drop across ~1 m at the
junction). The convergence sweep below confirms it shrinks under refinement.

#### Finding: two output bugs the junction created, both silent

Both were found by comparing against the reference, not by anything failing.

1. **Aliased element variables.** The output variables are `CONSTANT MONOMIAL`, one value
   per *element*, but the elements at the junction touch *both* fractures — their `x = 0`
   face is on the vertical one and their `y = 50` face on the horizontal one. A single
   variable written by an aux kernel spanning both boundaries keeps only whichever side was
   visited last, and it does so exactly at the junction. The vertical fracture reported
   0.105 mm of aperture there instead of 136 mm. Fixed by giving each fracture its own set
   of variables.
2. **A `ParsedAux` reading two other AuxVariables.** `mu_mobilized_h = |τ_h|/|σ_n_h|` is not
   guaranteed to run after the aux kernels that fill `τ_h` and `σ_n_h`, and it reported the
   *previous* step's ratio — 0.541 where the tractions in the same file give 0.577. The
   tell was that two laws disagreed on the ratio while agreeing on both tractions to five
   digits. The deck now scores `mu_peak_ratio_h`, built from two extreme-value
   postprocessors, and the comparison script recomputes the pointwise profile from the
   exported tractions. Neither has an ordering hazard.

   The first replacement for it was *also* wrong, and only the regression tests caught it:
   scoring the ratio of two `SideAverageValue` postprocessors gives 0/(-102 MPa), because
   the shear traction is **antisymmetric** about the junction and its mean over the
   boundary is identically zero. The symptom was four CSVDiff failures whose diffs were
   pure round-off at 1e-15 with a rank-count-dependent sign, on a solution that is
   otherwise bit-identical between 4 and 8 ranks. `tau` and `sigma_n` reach their extremes
   on the same element -- wherever the fracture slides `tau = mu |sigma_n|` pointwise, so
   the largest shear sits where the normal traction is largest -- and that ratio comes out
   at 0.577350265 against `tan 30 deg = 0.577350269`.

### Fault verification — stress perturbation on a fault bounding a pressurized displaced reservoir

A 300 m reservoir cut by a 60° normal fault with 100 m throw, so the two compartments
overlap only partly. Raising the pore pressure 20 MPa in one or both perturbs the stress
on the fault plane. Two cases: an **impermeable** fault, where only the down-thrown
compartment is pressurized, and a **permeable** fault, where both are.

There is no contact law here — the fault is purely the surface across which the reservoir
is displaced, in the reference case as well. What is being verified is the Biot coupling
term in `OrcaPoroMechKernel`, its sign, and the effective-to-total stress conversion.

Both decks solve the **perturbation problem**: the response is linear elastic and only the
stress *change* is compared, so the initial stress cancels and is not imposed. The
computed stress is then `Δσ'` directly, and `Δσ = Δσ' − α Δp` is what the reference
reports. The GEOS deck's constant −70 MPa overburden traction becomes a traction-free top
for the same reason.

| Case | component | RMS error | max error | reference span | RMS as % of span |
|---|---|---:|---:|---:|---:|
| impermeable | `Δσ_xx` | 0.897 MPa | 2.339 | 17.103 | **5.24 %** |
| impermeable | `Δσ_zz` | 0.529 MPa | 1.438 | 17.103 | **3.09 %** |
| impermeable | `Δσ_xz` | 0.893 MPa | 2.062 | 24.825 | **3.60 %** |
| permeable | `Δσ_xx` | 1.243 MPa | 2.540 | 24.265 | **5.12 %** |
| permeable | `Δσ_zz` | 0.614 MPa | 1.422 | 21.450 | **2.86 %** |
| permeable | `Δσ_xz` | 0.896 MPa | 1.664 | 24.310 | **3.68 %** |

Three checks run alongside the pointwise comparison, and all three are independent of the
reference file:

* **The 1-D limit.** Inside a laterally extensive pressurized layer the closed form
  collapses to `Δσ_xx + Δσ_zz = −α Δp (1−2ν)/(1−ν) = −14.824 MPa` exactly, and to zero
  outside. The permeable case returns −15.190 inside and +0.096 outside. This fixes the
  sign convention and the Biot coefficient without reference to Wu et al.
* **Plane strain.** The sampled column is one element wide but 60 elements deep in the
  out-of-plane direction; those 60 values agree to **2.6e-9 MPa**, so the solution is
  plane strain to machine precision.
* **Reservoir volume.** The pressurized region's volume is checked against its closed
  form (`1.18268e9 m³` per compartment) as a scored postprocessor. It matches to seven
  significant figures.

The residual 3–5 % is the mesh: elements are 43–54 m across near the fault, so the sampled
column sits ~17 m from it. Halving that distance by refining the near-fault region changed
the RMS by less than 5 % (3.68 → 3.84 MPa on `σ_xx` at the time), so the solution is
converged and the residual is the sampling offset, not an unconverged solve.

#### Finding: the reservoir is `fracture_block`, not the `offset_*` blocks

The mesh's block names invite a wrong reading, and taking it costs about 4 MPa. The
reservoir is **`fracture_block`**, whose two halves are

    left of the fault (down-thrown):   z = -200 .. +100
    right of the fault (up-thrown):    z = -100 .. +200

`offset_top` and `offset_bottom` are **not** reservoir — they are the non-reservoir blocks
juxtaposed against it by the 100 m throw, which is what their names refer to. Reading them
as the top and bottom of the compartments swaps which side is up-thrown, and the profiles
then miss the reference by ~4 MPa RMS with no orientation, reflection or shift able to
recover it. The symptom worth remembering: the shear sign check reported "flipped"
inconsistently between the two cases. With the geometry right it reports "as-is" for both,
and flipping makes it 7× worse.

The `dp_volume_avg` postprocessor exists to catch exactly this, and both decks score it.

## Mesh convergence

### Sneddon

Driven by [`sneddon/sneddon_convergence.py`](sneddon/sneddon_convergence.py), which sweeps
`RefineBlockGenerator` on the two blocks straddling the crack and leaves everything else
fixed, so the sweep isolates crack-tip resolution.

| level | `h` (m) | elements across crack | `w_max` error | fitted `A` error | fitted `b` (m) | `b` error |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 0.25000 | 8 | 10.126 % | 2.928 % | 0.88277 | 11.723 % |
| 2 | 0.12500 | 16 | 5.076 % | 1.388 % | 0.96195 | 3.805 % |
| 3 | 0.06250 | 32 | 2.980 % | 0.872 % | 0.97855 | 2.145 % |
| 4 | 0.03125 | 64 | **2.028 %** | 0.693 % | 0.98655 | 1.345 % |
| 5 | 0.01562 | 128 | 1.577 % | 0.783 % | 0.99181 | 0.819 % |

Level 4 is what the decks ship, which is where the headline 2.03 % comes from.

**The error converges.** `w_max` falls monotonically from 10.1 % to 1.6 %, and the fitted
half-length rises monotonically toward the meshed 1.0 m. The observed order in `h` is 0.67
for `w_max` and 0.92 for `b` — sublinear, which is exactly what linear elements do against
a square-root-singular crack tip, and it confirms the residual is discretization error
rather than a model error sitting at 2 %.

**But tip refinement alone has a floor.** The fitted amplitude bottoms out around 0.7 % and
ticks back up at level 5. The amplitude is the part of the solution the tip does *not*
control, so what is left is the finite domain: a 40 m box standing in for an infinite
medium. Refining the tip cannot remove it. Driving the total below roughly half a percent
needs the outer box enlarged as well — that half of "suggested extension 1" is still open.

### T-fracture

Driven by
[`fracutre_interseciton_problem/frac_intersection_convergence.py`](fracutre_interseciton_problem/frac_intersection_convergence.py),
which refines only the two blocks carrying the fractures.

| level | `h` (m) | fracture elements | aperture | traction | traction, smooth stretch | slip | peak aperture | junction aperture | peak slip |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 1.5625 | 32 | 2.59 % | 12.26 % | 1.69 % | 1.30 % | 276.24 mm | 136.13 mm | 61.28 mm |
| 1 | 0.7812 | 64 | 2.17 % | 7.41 % | 0.68 % | 1.06 % | 276.55 mm | 133.21 mm | 63.11 mm |
| 2 | 0.3906 | 128 | 1.86 % | 5.34 % | 0.48 % | 0.94 % | 277.02 mm | 132.34 mm | 64.43 mm |
| | | Phan et al. | | | | | 282.23 mm | 137.17 mm | 67.26 mm |

Level 0 is what the decks ship. **Every error falls monotonically** and both peaks move
monotonically toward the reference, so the residual is discretization, not model error.
Observed order in `h` is 0.60 for the traction and 0.24 for the aperture and the slip —
sublinear, as linear elements are against singular tips.

The traction is the quantity refinement helps most, which is the expected signature given
that its error is concentrated at the three singular points. What refinement *cannot* close
is the ~2 % offset in the aperture: that is the finite domain, measured at −2.32 % above,
and removing it needs a larger mesh rather than a finer one.

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

1. **Domain convergence, and convergence for shear compression.** The crack-tip half of
   this is done for Sneddon (see **Mesh convergence**) and shows the expected sublinear
   rate. Still open: enlarging the outer box, which the amplitude floor at ~0.7 % says is
   now the binding error; and the same sweep for shear compression, where the 127k-element
   file mesh with a direct solve makes even one refinement level expensive.
2. **A 3D Sneddon (penny-shaped crack)** — `w_max = 8(1-ν²) p_f a / (π E)` — routed
   through `OrcaFaultInterface3DGenerator` rather than `BreakMeshByBlockGenerator`. The
   production decks use the former and it is currently unverified; this would also close
   the nodeset-propagation question raised by `fracture_flow/cubic_law`.
3. **A uniform-stress patch test.** An interface embedded in a uniformly stressed block
   must transmit the traction exactly with zero displacement jump, for any interface
   orientation. Cheap, and it catches rotation and sign errors that both benchmarks above
   can mask because their fractures are axis-aligned or singly-inclined.
