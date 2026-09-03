# Fracture effective-stress coefficient — verification and bounds

Two decks and a script that answer a question raised by the Ye & Ghassemi (2018)
calibration: `fault_pressure_coefficient` is 0.86 on SW-S4, 0.87 on SW-S3 and 1.0 on
SW-T1/T2 — **is there an analytical way to determine it, rather than fitting it?**

The full argument is in Section 4 of the authoritative
[`theory.md`](../../../../Paper_1_Validations/General_Docs/Related_Theory/theory.md).
This directory supplies the numerical half.

## The claim being tested

```
σ'_n = σ_n + χ p        with        χ = 1 − A_c/A          [EXACT]
```

from a force balance across the fracture, `A_c` being the real solid–solid contact area.

## `chi_homogenized.i` — the operator check

Applies a uniform χ and checks that it comes back. This tests that the coefficient in the
code is the coefficient in the theory: acting on the right area, with the right sign, and
with no hidden normalization.

| | |
|---|---:|
| χ set | 0.860000 |
| χ measured | 0.860000 |
| `σ'_n` relative error | **6.0e-15** |
| max normal jump (fracture stayed closed) | −1.28e-6 m |

## `chi_resolved.i` — the physics check

Builds the contact patches **explicitly**. The fracture is divided into alternating strips:
contact strips carry a stiff contact law and no fluid; void strips carry a negligible
stiffness and the full fluid pressure at coefficient 1. **No χ is applied anywhere in the
deck** — it is recovered from the force balance the solver performs.

| realized `A_c/A` | `1 − A_c/A` | χ measured | rel. error | asperity stress |
|---:|---:|---:|---:|---:|
| 0.050000 | 0.9500000 | 0.9500001 | 1.1e-07 | 220.0 MPa |
| 0.100000 | 0.9000000 | 0.9000000 | 5.2e-08 | 120.0 MPa |
| 0.137500 | 0.8625000 | 0.8625000 | 3.3e-08 | 92.7 MPa |
| 0.200000 | 0.8000000 | 0.8000000 | 1.6e-08 | 70.0 MPa |
| 0.300000 | 0.7000000 | 0.7000000 | 1.4e-08 | 53.3 MPa |

The identity holds to eight significant figures across the range. Two guards run alongside:
the strip sidesets must tile the fracture exactly (`area_total` = 0.1 m), and the void
strips must carry no solid load (they carry 1.7 Pa against 93 MPa on the asperities).

### The asperity-stress column is the point

It is what makes the direction of the bound obvious. Since `σ'_n = (A_c/A) σ_c` and
`σ_c ≤ H`, the constraint is

```
χ ≤ 1 − σ'_n / H          [UPPER bound, not lower]
```

Smaller contact area means higher asperity stress, so the constraint bites at **high** χ.
`χ → 1` requires `A_c/A → 0` and `σ_c → ∞`. Fully plastic contact is the state of *minimum*
contact area, so it bounds χ from above — the opposite of the natural first guess.

| `H` | source | max χ at σ'_n = 30 MPa |
|---:|---|---:|
| 450 MPa | Tabor, `H ≈ 3 × UCS` | 0.933 |
| 2 GPa | mineral indentation, low | 0.985 |
| 5 GPa | mineral indentation, high | 0.994 |

So **χ = 1.0 is the value that is strictly unattainable**, and 0.86 — which needs the
asperities to carry only 214 MPa — is comfortably feasible. The saw-cut values were never
the problem; the identifiability of χ is (see the framework note).

## `chi_analytical.py`

```bash
python chi_analytical.py            # bounds, plus whatever decks have already run
python chi_analytical.py --sweep    # also runs chi_resolved.i at several A_c/A
python chi_analytical.py --no-plot
```

Writes `chi_verification_summary.csv` and `chi_bounds.png`. Needs numpy; matplotlib only
for the figure. `--sweep` needs `orca-opt` and runs on 4 ranks by default.

## Why this is not circular

The strips are a *geometric* construction, not a constitutive one. The only inputs are
where the contact patches are and how stiff they are. A wrong area normalization, a wrong
sign, or a fluid load applied over the wrong fraction would all show up here — and in none
of the GEOS benchmarks, none of which has a partially contacting fracture.

## Note on the deck structure

Everything is declared on the two sub-sidesets `contact_patches` / `void_patches`, never on
their parent `lower_upper`. MOOSE checks boundary-restricted material properties by
boundary ID rather than by geometric coverage, so a property declared on the two children
does **not** satisfy a request on the parent even though they cover the same surface.

The strips are also cut out of the **already broken** interface with `ParsedGenerateSideset`
rather than built as blocks. Blocks would put four subdomains at every strip edge, and
`BreakMeshByBlockGenerator` refuses to split a node touching more than two — welding the
interface at every strip boundary and corrupting the very force balance being measured.
