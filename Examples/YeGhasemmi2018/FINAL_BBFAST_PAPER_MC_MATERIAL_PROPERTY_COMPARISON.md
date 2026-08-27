# Final BBFast–experiment–Mohr–Coulomb material-property comparison

**Prepared:** 2026-08-27  
**Experimental reference:** Ye, Z., and A. Ghassemi (2018), *Injection-Induced Shear Slip and Permeability Enhancement in Granite Fractures*, JGR Solid Earth, 123, 9009–9032, [doi:10.1029/2018JB016045](https://doi.org/10.1029/2018JB016045).  
**Scope:** the four selected BBFast cases and their fixed 94-series Mohr–Coulomb (MC) controls. Values are active input-deck values, not historical values left in comments.

## 1. Essential interpretation

Neither **BBFast** nor **Mohr–Coulomb** was “provided by the experiment.” They are alternative constitutive-model choices made for the numerical study.

The experiment directly supplies only part of the parameter set: specimen dimensions, measured fracture orientation and JRC, intact-rock elastic/strength properties, fluid viscosity, loading conditions, and measured response histories. Hydraulic aperture and fracture permeability are **derived from measured flow**, rather than independently measured. Most fracture closure, shear weakening, cohesion, dilation, roughness-evolution, and hydraulic-retention parameters are therefore **inferred by calibration**.

The 94-series MC cases are also not independent full-physics alternatives. They deliberately retain the BBFast cases' bulk poroelastic model and, with limited case-specific exceptions, the same normal-closure, dilation, and hydraulic-aperture laws. The principal controlled difference is the **fracture shear-strength law**:

| Item | BBFast | 94-series MC | Experimental status |
|---|---|---|---|
| Active contact material | `OrcaBartonBandisContactTractionFastADHardening` | `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` | Neither model class is experimental; both are inferred modeling choices. |
| Peak shear envelope | Barton–Bandis, using JRC/JCS and a basic-friction angle, plus cohesion | Roughness-dependent linear Coulomb envelope, `tau = c(R) + mu(R) sigma_n'` | The stress/slip data constrain the envelope, but do not uniquely identify its decomposition into JRC, friction, and cohesion. |
| Post-peak weakening | Exponential slip weakening of friction and cohesion | Friction and cohesion interpolate with a decaying normalized roughness state | Inferred/calibrated in both models. |
| Mechanical normal closure | Nonlinear hyperbolic/power closure | The same closure family is retained | Calibrated; not a standalone MC-vs-BB difference. |
| Dilation | Decoupled slip-dependent dilation | The BBFast dilation angles and decay lengths are copied into MC | Calibrated and transferred; not an independent MC-vs-BB difference. |
| Hydraulic aperture/permeability | Roughness/damage aperture law and cubic-law permeability | The same aperture/permeability material is retained | Initial aperture is derived from flow; evolution parameters are calibrated. |

Accordingly, the comparison supports the statement that **the nonlinear Barton–Bandis shear-strength and weakening representation describes these four experiments better than the matched roughness-dependent MC shear envelope**. It does not, by itself, isolate the value of every BBFast submodel because several submodels are shared.

## 2. Provenance legend

| Code | Meaning | Evidential status |
|---|---|---|
| **EXP** | Directly reported or measured in Ye and Ghassemi (2018) | Independent experimental input |
| **DER** | Calculated from reported experimental quantities | Experiment-constrained, but not an independent measurement |
| **CAL** | Inferred/calibrated against the response data | Model-dependent estimate |
| **ASM** | Assumed, adopted from general water/rock data, or selected as a modeling convention | Not independently constrained by this experiment |
| **XFER** | Copied or transformed from the matched BBFast case into MC | Controlled-comparison parameter, not independent MC evidence |
| **NUM** | Numerical stabilization, limit, or solver regularization | Not a physical material property |

For vector entries below, the order is always **[SWT1, SWT2, SWS3, SWS4]**.

## 3. Cases included

| Sample | Final BBFast deck | Matched MC deck |
|---|---|---|
| SWT1 | [`SWT1_OrcaBartonBandisContactTractionFastADHardening.i`](SWT1/SWT1_OrcaBartonBandisContactTractionFastADHardening.i) | [`SWT1_OrcaMohrCoulombContactTraction.i`](SWT1/SWT1_OrcaMohrCoulombContactTraction.i), derived from `94_01` |
| SWT2 | [`SWT2_OrcaBartonBandisContactTractionFastADHardening.i`](SWT2/SWT2_OrcaBartonBandisContactTractionFastADHardening.i) | [`SWT2_OrcaMohrCoulombContactTraction.i`](SWT2/SWT2_OrcaMohrCoulombContactTraction.i), derived from `94_03` |
| SWS3 | [`SWS3_OrcaBartonBandisContactTractionFastADHardening.i`](SWS3/SWS3_OrcaBartonBandisContactTractionFastADHardening.i) | [`SWS3_OrcaMohrCoulombContactTraction.i`](SWS3/SWS3_OrcaMohrCoulombContactTraction.i), renamed from `94_05` |
| SWS4 | [`SWS4_OrcaBartonBandisContactTractionFastADHardening.i`](SWS4/SWS4_OrcaBartonBandisContactTractionFastADHardening.i) | [`SWS4_OrcaMohrCoulombContactTraction.i`](SWS4/SWS4_OrcaMohrCoulombContactTraction.i), renamed from `94_07` |

## 4. Experimentally reported specimen and rock properties

These are the quantities for which an experimental value exists. Geometry and boundary conditions are included separately from constitutive properties so that they are not accidentally described as material calibration.

| Quantity | Paper values [SWT1, SWT2, SWS3, SWS4] | BBFast values | MC values | Provenance and interpretation |
|---|---:|---:|---:|---|
| Fracture type | [tensile, tensile, saw-cut, polished saw-cut] | Same | Same | **EXP** |
| Specimen length (mm) | [128.80, 132.70, 123.40, 118.70] | Geometry-specific meshes/decks | Same meshes as matched cases | **EXP**; geometry, not a material property. |
| Specimen diameter (mm) | [50.52, 50.52, 50.53, 50.51] | [50.52, 50.52, 50.53, 50.51] | Same | **EXP** |
| Fracture inclination, `theta` (deg) | [32, 31, 29, 30] | [32, **30**, 29, 30] | [32, **30**, 29, 30] | **EXP** in the paper; SWT2's 30° model angle is a **DER/CAL** effective orientation and differs by 1° from Table 1. |
| Measured JRC | [15.32, 14.63, 1.96, 1.19] | [15.32, 14.63, 1.96, **5.00**] | Not used directly | **EXP**. SWT1–SWS3 retain the measured value; SWS4's effective JRC = 5 is **CAL** and should not be called measured. |
| Young's modulus, `E` (GPa) | 67 | 67 for all | 67 for all | **EXP**, shared. |
| Poisson's ratio, `nu` | 0.32 | 0.32 for all | 0.32 for all | **EXP**, shared. |
| UCS (MPa) | 150 | Used as `JCS = 150 MPa` | No JCS parameter | UCS is **EXP**. Equating JCS to UCS is a **DER/ASM proxy**, not a separate JCS measurement. |
| Intact-rock friction angle (deg) | 46 | Not used as fracture residual friction | Not used directly | **EXP** for intact granite; it must not be identified with the fracture's fitted friction angle. |
| Tensile strength (MPa) | 11 | Not active in the pre-existing-fracture contact law | Tensile cohesion disabled | **EXP**, but not an active calibration parameter for these already-fractured interfaces. |
| Matrix permeability (m²) | approximately `5e-19` to `1e-18` | `5e-19` for all | `5e-19` for all | **EXP**, lower reported bound selected and shared. |
| Initial hydraulic aperture (µm) | [1.63, 2.11, 1.22, 0.74] | Same | Same | **DER** from measured flow through the cubic law; not an independent aperture measurement. |
| Initial fracture permeability (m²) | approximately [`2.2e-13`, `3.7e-13`, `1.24e-13`, `4.6e-14`] | Computed as `a_h²/12` | Same | **DER** from the same flow/aperture reduction; it must not be counted as a second independent validation variable. |
| Water dynamic viscosity (Pa·s) | `1.002e-3` at 20 °C | `1.002e-3` | `1.002e-3` | **EXP/reported fluid property**, shared. |

### Experimental conditions, not material properties

| Quantity | Experimental value | BBFast and MC use | Provenance |
|---|---:|---:|---|
| Confining pressure | 30 MPa | 30 MPa | **EXP** |
| Production pressure | 5 MPa | 5 MPa | **EXP** |
| Injection-pressure schedule | 8, 12, 16, 20, 24, 28 MPa, followed by unloading | Same staged schedule | **EXP** |
| Loading control | Fixed piston displacement during injection | Finite loading-system stiffness used to reproduce stress relaxation | Control mode is **EXP**; effective machine compliance is **DER/CAL**. |

## 5. Shared bulk poroelastic and fluid material inputs

| Input property | Paper | BBFast [T1, T2, S3, S4] | MC [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---:|---|
| `youngs_modulus` (GPa) | 67 | [67, 67, 67, 67] | Same | **EXP/XFER** |
| `poissons_ratio` | 0.32 | [0.32, 0.32, 0.32, 0.32] | Same | **EXP/XFER** |
| `matrix_permeability` (m²) | `5e-19`–`1e-18` | [`5e-19`, `5e-19`, `5e-19`, `5e-19`] | Same | **EXP/XFER** |
| `initial_porosity` | Not reported | [0.001, 0.001, 0.001, 0.001] | Same | **ASM/XFER** |
| `biot_coefficient` | Not reported | [0.6, 0.6, 0.6, 0.6] | Same | **ASM/CAL/XFER** |
| `fluid_density_ref` (kg/m³) | Deionized water; density not tabulated | [1000, 1000, 1000, 1000] | Same | **ASM/XFER** |
| `fluid_viscosity_ref` (Pa·s) | `1.002e-3` | Same for all | Same | **EXP/XFER** |
| `fluid_bulk_modulus` (GPa) | Not tabulated | [2.2, 2.2, 2.2, 2.2] | Same | **ASM** standard water value, then **XFER** |
| `fault_pressure_coefficient` | Not reported | [1.00, 1.00, 0.87, 0.86] | Same | **CAL/XFER**; an effective pressure-transfer control, not Biot's coefficient. |
| Nominal fracture-flow thickness (mm) | Not reported as a continuum-interface thickness | [1, 1, 1, 1] | Same | **ASM/XFER** numerical continuum representation. |

## 6. Mechanical normal-closure properties

The normal law is calibrated in both formulations. MC retains the same law family, so these parameters do not constitute an independent MC model prediction.

| Property | Paper | BBFast [T1, T2, S3, S4] | MC [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---:|---|
| Hyperbolic/power normal closure enabled | Not specified | [yes, yes, yes, yes] | [yes, yes, yes, yes] | **CAL/XFER** |
| Initial mechanical normal stiffness, `K_ni` (Pa/m) | Not reported | [`2.443e11`, `2.443e11`, `2.443e11`, `2.443e11`] | Same | **CAL/XFER** |
| Maximum mechanical closure, `V_m` (µm) | Not reported | [55.00, 45.91, 45.91, 45.91] | Same | **CAL/XFER**; the renamed SWT1 MC center was aligned to the final BBFast refinement on 2026-08-27. |
| Mechanical closure exponent | Not reported | [3.28, 3.28, 3.28, 3.28] | Same | **CAL/XFER** |
| Mechanical closure offset (µm) | Not reported | [51.6707, 44.33, 44.33, 44.33] | Same | **CAL/XFER**; the renamed SWT1 MC center was aligned to BBFast. |
| BBFast unloading-retention fraction | Not reported | [0.94, 0.84, 0.00, 0.04] | Not present in active MC law | **CAL**; this is a BBFast history variable, not measured material retention. |
| Reclosure stiffness multiplier | Not reported | [1, 1, 1, default] | Not present | **ASM/CAL** |
| Unload activation slip (µm) | Not reported | [50, 50, 50, 50] | Not present | **CAL/NUM** |

## 7. Shear-strength and weakening properties

### 7.1 BBFast parameters

| Property | Paper | BBFast [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---|
| `jrc` | [15.32, 14.63, 1.96, 1.19] | [15.32, 14.63, 1.96, **5.00**] | **EXP** for T1/T2/S3; **CAL** effective value for S4. |
| `jcs` (MPa) | JCS not measured; UCS = 150 MPa | [150, 150, 150, 150] | **DER/ASM** proxy from experimental UCS. |
| BB basic/residual friction angle (deg) | Intact angle = 46°; fracture basic angle not tabulated in the target paper | [29.756, 29.756, 29.756, 22.72] | **CAL** for this paper comparison. Deck comments associate 29.756° with campaign saw-cut behavior, but it is not the paper's 46° intact-rock value. |
| Peak cohesion (MPa) | Not reported | [27.20, 33.20, 1.67, 0.00 implicit default] | **CAL** |
| Residual cohesion (MPa) | Not reported | [9.19, 9.71, 1.30, 0.00 implicit default] | **CAL**. Persistence of dilation/slip constrains it indirectly; it is not directly measured. |
| Characteristic weakening slip, `D_c` (µm) | Not reported | [150, 150, 60, 74.5] | **CAL** |
| Weakening exponent, `m` | Not reported | [1.40, 1.40, 1.40, 1.10] | **CAL** |
| Large-slip friction angle (deg) | Not reported | [29.756, 29.756, 8.45, 6.50] | **CAL** |
| JRC scale correction | Not reported | Disabled for all | **ASM/CAL** |
| Mobilized-JRC ramp | Not reported | Disabled for all | **ASM/CAL**; peak envelope is available at zero slip. |

### 7.2 MC shear-envelope parameters

The MC coefficients below were fitted/transformed so the linear roughness-dependent envelope could be compared with each BBFast sibling. They are **not values reported by Ye and Ghassemi (2018)**.

| Property | Paper | MC [T1, T2, S3, S4] | Equivalent angle [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---:|---|
| Rough-state friction coefficient, `mu_rough` | Not reported | [0.5536, 0.5528, 0.8818, 0.9804] | [28.969°, 28.934°, 41.406°, 44.433°] | **CAL/XFER** |
| Smooth-state friction coefficient, `mu_smooth` | Not reported | [0.5717, 0.5717, 0.1486, 0.1139] | [29.757°, 29.757°, 8.452°, 6.498°] | **CAL/XFER** |
| Friction–roughness exponent | Not reported | [1, 1, 1, 1] | — | **ASM/XFER** linear interpolation |
| Rough-state cohesion (MPa) | Not reported | [37.034, 42.959, 2.645, 3.225] | — | **CAL/XFER** |
| Smooth-state cohesion (MPa) | Not reported | [9.190, 9.710, 1.400, 0.000] | — | **CAL/XFER** |
| Cohesion–roughness exponent | Not reported | [1, 1, 1, 1] | — | **ASM/XFER** linear interpolation |
| Tensile cohesion | Pre-existing fractures; no interface tensile law fitted | Disabled for all | — | **ASM**, appropriate to an already fractured interface; the paper's 11 MPa intact tensile strength is not used. |

The fact that `mu_rough < mu_smooth` in SWT1 and SWT2 is not a claim that a rough tensile fracture is intrinsically less frictional. The calibrated cohesion term carries much of their peak interlock; the pair `(mu, c)` is only one linear decomposition of the observed strength over a limited stress range.

## 8. Dilation and roughness-evolution properties

| Property | Paper | BBFast [T1, T2, S3, S4] | MC [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---:|---|
| Initial normalized roughness state | No normalized state reported | [1.00, 1.00, 0.64, 0.45] | Same | **CAL/XFER**; this internal state is not JRC. |
| Residual normalized roughness state | Not reported | [0.10, 0.10, 0.10, 0.10] | Same | **CAL/XFER** |
| Roughness-decay distance (µm) | Not reported | [150, 150, 40, 80] | Same | **CAL/XFER** |
| Peak dilation angle (deg) | Dilation displacement reported, angle not directly measured | [16.442, 13.965, 26.0, 24.0] | Same | **CAL/XFER** |
| Residual dilation angle (deg) | Not reported | [16.442, 13.965, 26.0, 13.0] | Same | **CAL/XFER** |
| Dilation-decay distance (µm) | Not reported | [150, 150, 100, 100] | Same | **CAL/XFER** |
| Dilation-decay exponent | Not reported | Internal BB weakening form | [1, 1, 1, 1] | **ASM/XFER** |
| Dilation opens the joint | Dilation observed | Enabled for all | Enabled for all | Sign is **DER** from the measured opening direction; constitutive implementation is a model choice. |
| Accumulate irreversible dilation | Retained opening observed | Enabled for all | Embedded in MC dilation state | **DER/CAL** |
| BBFast maximum dilation increment (µm/step) | Not reported | [1.5, 0, 0, 0] | [0, 0, 0, 0] | **NUM**, not a material measurement. |

Because angles and decay distances are copied, the final BBFast–MC comparison does **not** test competing dilation laws with independently identified parameters. It tests how the different shear-strength/weakening laws drive a common target dilation representation.

## 9. Hydraulic-aperture and permeability properties

Both model families use `ADOrcaRoughnessDamageFracturePermeability` and compute intrinsic fracture permeability from hydraulic aperture. The paper's aperture and permeability values are calculated from flow; they are not additional independent observations.

| Property | Paper | BBFast [T1, T2, S3, S4] | MC [T1, T2, S3, S4] | Provenance |
|---|---:|---:|---:|---|
| Initial hydraulic aperture, `a_h0` (µm) | [1.63, 2.11, 1.22, 0.74] | Same | Same | **DER/XFER** from measured flow. |
| Mechanical-aperture scale | Not reported | [0.01512, 0.0177, 0.001, 0.001] | Same | **CAL/XFER**; the renamed SWT1/SWT2 MC centers were aligned to the final BBFast refinements on 2026-08-27. |
| Linear normal-stress aperture compliance (m/Pa) | Not reported | [0, 0, `2e-14`, `2e-14`] | Same | **CAL/XFER** |
| Reference effective normal stress (MPa) | Derived stress histories are reported | [65.47, 66.74, 32.1, 31.0] | Same | **DER/CAL/XFER** reference-state choice. |
| Nonlinear hydraulic closure enabled | Not specified | [no, yes, yes, yes] | Same | **CAL/XFER** |
| Maximum hydraulic closure (µm) | Not reported | [1.20 inactive, 1.20, 1.20, 1.05] | Same | **CAL/XFER** |
| Hydraulic closure initial stiffness (Pa/m) | Not reported | [`1.25e13` inactive, `1.25e13`, `1.25e13`, `1.43e13`] | Same | **CAL/XFER** |
| Hydraulic closure exponent | Not reported | [4 inactive, 4, 4, 2] | Same | **CAL/XFER** |
| Dilation-to-aperture scale | Not reported | [0, 0, 0.038, 0.0117] | Same | **CAL/XFER** |
| Residual roughness-retention factor | Not reported | [0.714876, 0.747331, 0.28, 0.28] | Same | **CAL/XFER** |
| Slip-damage/gouge term enabled | Not reported | [no, no, yes, yes] | Same | **CAL/XFER** |
| Slip-damage aperture scale (µm) | Not reported | [0 inactive, 0 inactive, 0.40, 0.28] | Same | **CAL/XFER** |
| Slip-damage onset (µm slip) | Not reported | [inactive, inactive, 30, 20] | Same | **CAL/XFER** |
| Slip-damage distance (µm slip) | Not reported | [inactive, inactive, 30, 30] | Same | **CAL/XFER** |
| Self-propping scale | Self-propping is observed qualitatively, but no constitutive scale is supplied | [0, 0, 0, 0] | Same | Disabled; **ASM/XFER**. Retention is represented through other calibrated state terms. |
| Self-propping exponent | Not reported | [1 inactive, 1 inactive, 1 inactive, 1 inactive] | Same | **ASM/XFER** inactive parameter. |
| Minimum hydraulic aperture (µm) | Initial derived aperture supplies a lower reference | [1.5105, 2.0045, 1.22, 0.74] | Same | T1/T2 are **CAL** floors; S3/S4 use the **DER** initial aperture as a floor. |
| Maximum hydraulic aperture (µm) | Not reported | [8, 8, 8, 8] | Same | **NUM** cap. |
| Permeability relation | Paper uses cubic-law reduction | `k_f = a_h²/12` | Same | **DER/literature relation**, shared. |

## 10. Numerical contact and regularization parameters

These values affect robustness and, in transient localization, can affect the computed path. They should be disclosed but never described as experimental material properties.

| Parameter | BBFast [T1, T2, S3, S4] | MC [T1, T2, S3, S4] | Status |
|---|---:|---:|---|
| Tangential penalty stiffness (Pa/m) | [`1e13`, `1e13`, `1e13`, `1e13`] | Same | **NUM** |
| Tangential viscosity (Pa·s/m) | [`4e11`, `4e11`, `4e11`, `3.5e12`] | Same | **NUM/CAL**, shared |
| MC normal fallback penalty (Pa/m) | Not used | [`2e13`, `2e13`, `2e13`, `2e13`] | **NUM**; nonlinear closure is active. |
| BBFast maximum plastic-slip increment (µm/step) | [5, 0, 0, 0] | MC uses [0, 0, 0, 0] | **NUM** |
| Contact-gap regularization (m) | `1e-8` explicitly in SWT1; otherwise default/deck-specific | `1e-8` explicitly in SWT1; otherwise default/deck-specific | **NUM** |
| Compressive normal-stress floor (Pa) | 1000 | Internal MC handling | **NUM** |

## 11. What is independently constrained and what is inferred

| Category | Independently supplied by the experiment | Inferred/calibrated in this study |
|---|---|---|
| Matrix | `E`, `nu`, matrix permeability range, UCS, intact friction angle, tensile strength | Porosity, Biot coefficient, and the selected value within the permeability range |
| Geometry/loading | Dimensions, nominal fracture angle, confining pressure, injection/production pressures, fixed-piston control | SWT2 effective 30° angle and loading-system compliance |
| Surface description | Fracture type and measured JRC | SWS4 effective JRC = 5 and all normalized roughness-state parameters |
| Normal response | Normal displacement/stress histories | Normal stiffness, closure capacity/offset/exponent, and unloading retention |
| Shear response | Shear stress and slip histories | BB friction/cohesion/weakening parameters and all MC `(mu, c)` envelope parameters |
| Dilation | Normal displacement history and observed retained opening | Dilation angles, decay distances, and irreversible-state implementation |
| Hydraulics | Flow rate; fluid viscosity; pressure stages | Initial aperture is **derived** from flow; aperture scales, closure, retention, and damage parameters are calibrated |
| Constitutive model | None | Choice of BBFast versus MC, including their mathematical state variables |

## 12. Recommended manuscript wording

> The experimental study provides specimen geometry, fracture type and JRC, intact-rock properties, fluid properties, loading conditions, and hydromechanical response histories. Hydraulic aperture and permeability are derived from measured flow through the cubic law and are therefore not independent observations. Neither the Barton–Bandis nor Mohr–Coulomb constitutive formulation is prescribed by the experiment. Closure, cohesion, frictional weakening, dilation, roughness evolution, pressure-transfer, and hydraulic-retention parameters are inferred by calibration where direct measurements are unavailable. The Mohr–Coulomb controls retain the matched bulk, normal-closure, dilation, and hydraulic-aperture descriptions; thus the comparison principally evaluates the alternative shear-strength and weakening laws. Under these controlled conditions, the Barton–Bandis formulation gives the more faithful representation of the four fracture responses.

## 13. Audit notes and cautions

1. **Do not label calibrated cohesion as measured.** The experimental persistence of slip/dilation may constrain residual interlock, but the paper does not directly measure a cohesion parameter.
2. **Do not label `JCS = 150 MPa` as measured JCS.** The measured quantity is UCS; its use as joint-wall compressive strength is a proxy.
3. **Do not label SWS4 `JRC = 5` as the experimental JRC.** The paper reports 1.19; 5 is the final model's effective calibrated value.
4. **Do not use the paper's 46° intact friction angle as a joint residual-friction measurement.** They refer to different strength descriptions.
5. **Do not score flow, hydraulic aperture, and permeability as three independent data channels.** The last two are derived from the first.
6. **Describe the 94-series model precisely.** It is a roughness-dependent, dilatant MC shear control embedded in the shared BBFast hydromechanical framework, not a bare constant-friction MC interface.

## 14. Sources audited

- [Ye and Ghassemi (2018), official article](https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029%2F2018JB016045)
- The eight active input decks listed in Section 3
- [`ADOrcaBartonBandisContactTractionFastADHardening.C`](../../src/InterfaceMaterial/ADOrcaBartonBandisContactTractionFastADHardening.C)
- [`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.C`](../../src/InterfaceMaterial/ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.C)
- [`ADOrcaRoughnessDamageFracturePermeability.C`](../../src/InterfaceMaterial/ADOrcaRoughnessDamageFracturePermeability.C)
