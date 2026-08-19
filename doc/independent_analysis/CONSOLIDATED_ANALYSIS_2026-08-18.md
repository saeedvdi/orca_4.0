# ORCA 4.0 consolidated analysis

**Repository:** `orca_4.0`  
**Branch / revision examined:** `orca_v6`, `c4ae680`  
**Consolidation date:** 2026-08-18  
**Benchmark:** Ye and Ghassemi (2018), four granite-fracture injection tests

This is the single synthesis of the independent analyses in `doc/`, updated with the results
that arrived after those reports were written. It is not a concatenation in chronological order:
several early reports describe parameterisations, meshes, data extractions, or reporting channels
that were later superseded. This document preserves what those studies established while treating
the 93-series results and the current source tree as authoritative.

Status terms used below:

- **authoritative** — current production deck or result;
- **historical** — useful calibration evidence, but superseded as a final result;
- **partial** — interpretable only over the part of the loading path reached;
- **open** — not answered by the artifacts currently in the repository.

---

## 1. Executive synthesis

1. **The four current BBFast validations are good on the declared campaign metric.** The
   93-series mesh-5 runs score 4.44% (SW-T1), 2.43% (SW-T2), 4.58% (SW-S3), and 6.05% (SW-S4)
   mean normalised RMSE over the five scored Table 2 columns. The result is strongest as a
   specimen-scale reproduction of stagewise hydro-mechanical response, not as proof that every
   fitted parameter is independently identifiable.

2. **The matched Mohr-Coulomb baseline is decisively worse.** The completed mesh-5 94-series
   scores are 25.27%, 23.14%, 18.47%, and 8.91%, respectively. Averaged across specimens,
   BBFast is 4.38% versus 18.95% for MC, a 77% reduction. The two laws are effectively identical
   before yielding; the separation appears on the weakening path. This supports a performance
   claim for the two-distance BBFast form, not a claim that the narrow stress path uniquely
   identifies the curvature of the Barton-Bandis envelope.

3. **The SW-S4 rate-and-state healing hypothesis was falsified.** The `b` bracket did not repair
   the deficient hold-stage slip, and velocity weakening produced a deterministic slip/arrest
   stall. The useful result is that the fitted Perzyna viscosity is not merely numerical: on
   SW-S4 it contributes 0.314 MPa mean and 0.871 MPa peak shear overstress during slipping.

4. **Matrix Biot sensitivity is specimen-dependent.** Changing `biot_coefficient` from 0.6 to
   0.2 moves the tensile-pair scores only from 4.44% to 4.21% and 2.43% to 2.74%, but degrades
   SW-S3 from 4.58% to 18.90% and SW-S4 from 6.05% to 9.60%. The assumed coefficient cannot be
   changed by fiat across the campaign.

5. **The fitted fracture pressure coefficient is not shown to be inert.** All four saw-cut
   probes that set `fault_pressure_coefficient = 1.0` stop before the peak Table 2 stage. The
   stored artifacts do not include termination logs, so the immediate cause cannot be assigned,
   but the repeated truncation proves that removing the 0.87/0.86 attenuation is not a harmless
   documentation cleanup. It requires a re-calibration and a controlled rerun.

6. **Cyclic injection produces a large retained first-cycle change on the tensile specimens and
   a small one on SW-S4.** At the same 8 MPa pressure before and after cycle 1, the retained
   permeability ratios are 5.61 (SW-T1), 4.14 (SW-T2), 1.65 (SW-S3), and 1.04 (SW-S4). Only
   SW-S4 completes all three cycles. From its cycle-1 floor to cycle-3 floor, permeability rises
   another 4.3% and flow 6.5%; almost all of that increment occurs on cycle 2, with cycle 3
   essentially saturated.

7. **The cyclic campaign is not complete.** SW-T1, SW-T2, and SW-S3 end during the second cycle,
   at 4602, 6644, and 6054 s against requested end times of 10375, 13882, and 15793 s. Their first
   cycles are valid, but they cannot support a three-cycle accumulation claim. No corresponding
   error logs are present in the repository.

8. **Shut-in causes prompt arrest in all four runs.** All 98-series runs complete. Net reported
   shear-slip changes after shut-in are between -0.00030 and -0.00015 mm; once injection pressure
   is within 1% of ambient, subsequent changes are at most 0.000015 mm. The model therefore does
   not reproduce delayed post-shut-in reactivation from diffusion alone.

9. **The main historical apparent failures were often measurement-path failures.** Correcting
   stress frames, stale point coordinates, output-only displacement fits, mesh geometry, and
   digitised validation series changed conclusions without changing constitutive physics. The
   durable method is: audit the plumbing, score the source data, localise the residual, and only
   then tune a parameter.

10. **The manuscript and theory manual are now much closer to the code than the August 18 audit
    found, but the new 94/96/97/98 results have not been integrated.** In particular, the paper's
    pending MC, cyclic, and shut-in sections can now be partly or wholly written, and its claim
    that there is no evidence the saw-cut fracture-pressure coefficients buy agreement must be
    revised in light of the 96-series truncations.

---

## 2. Benchmark, model, and actual production configuration

### 2.1 What is being reproduced

The benchmark comprises four triaxially loaded granite specimens with an inclined fracture:

| specimen | fracture family | adopted angle | principal behaviour |
|---|---|---:|---|
| SW-T1 | tensile, rough and mated | 32.0° | abrupt slip and large permeability gain |
| SW-T2 | tensile, rough and mated | 30.0° | abrupt slip and large permeability gain |
| SW-S3 | saw cut | 29.0° | abrupt slip at the peak stage |
| SW-S4 | lapped saw cut | 30.0° | progressive, staged slip |

The experiment applies a specimen-specific injection-pressure history while production pressure
and confining pressure are controlled. Ye and Ghassemi's Table 2 reports eleven loading/unloading
hold stages. The model resolves bulk poroelasticity, interface contact and shear return mapping,
fracture storage and tangential flow, and the finite compliance of the loading train.

### 2.2 Formulation actually exercised by the 93-series

- The matrix follows Biot poroelasticity with `E = 67 GPa`, `nu = 0.32`, matrix permeability
  `5e-19 m2`, porosity `0.001`, and matrix Biot coefficient 0.6.
- The fracture is a zero-thickness cohesive interface. Normal contact uses a power-law closure,
  not the `p = 1` hyperbola formerly printed in the paper.
- Shear strength uses the BBFast cohesive Barton-Bandis form with slip weakening, roughness
  evolution, kinematic dilation, and viscous overstress.
- Fracture pressure acts through a constant coefficient `alpha_f`: 1.0 on SW-T1/T2, 0.87 on
  SW-S3, and 0.86 on SW-S4. A state-dependent form exists in the source but is disabled in every
  reported production run.
- Hydraulic aperture is a bounded additive law containing stress-aperture, mechanical-aperture,
  dilation-retention, optional self-propping, gouge, and clamp terms. The two tensile specimens
  route dilation once through the kinematic gap. The two saw cuts retain an additional fitted
  dilation feed, so their mechanical and hydraulic apertures are not generated by one common
  mechanism.

### 2.3 Current specimen parameters

| specimen | JRC | JCS (MPa) | residual angle | cohesion (MPa) | residual cohesion (MPa) | `eta_t` (Pa s/m) | closure exponent | aperture `chi` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| SW-T1 | 15.32 | 150 | 29.756° | 26.88 | 9.19 | `4.0e11` | 4.0 | 0.0160 |
| SW-T2 | 14.63 | 150 | 29.756° | 33.20 | 9.71 | `4.0e11` | 4.0 | 0.0165 |
| SW-S3 | 1.96 | 150 | 29.756° | 1.67 | 1.40 | `4.0e11` | 4.0 | 0.0010 |
| SW-S4 | 5.00 | 150 | 22.72° | 0 | 0 | `3.5e12` | 2.0 | 0.0010 |

These are calibrated sets, not eight independently measured material properties. Over the stress
range visited, cohesion and JRC produce envelope slopes differing by only about 3%; the loading
path constrains an effective strength combination much more strongly than it constrains either
parameter separately. SW-S4's adopted JRC of 5 is calibrated and differs from its measured 1.19.

---

## 3. Evidence and scoring protocol

### 3.1 What is scored

The operational campaign metric scores five Table 2 columns:

1. flow rate `Q`;
2. effective normal stress `sigma'_n`;
3. shear stress `tau`;
4. normal displacement `d_n`;
5. shear displacement `d_s`.

Hydraulic aperture and permeability are not scored because the paper derives both from `Q` using
the cubic law. Counting them would give the flow measurement three votes. The two stress columns
are measured projections of the same stress state and are therefore not statistically independent,
although both remain in the established five-column campaign score for continuity.

For each column, RMSE is divided by that specimen's measured range. The unweighted mean of those
five nRMSE values is the headline score. Model displacements are zeroed at stage 1; because that
forces agreement there, stage 1 is excluded from the `d_n` and `d_s` statistics.

Cross-machine repeats establish a reproducibility floor of about 0.08 percentage points in the
mean. Differences below about 0.1 points should not be ranked.

### 3.2 Why early full-history scores and current Table 2 scores differ

The 89- to 91-series reports often score eight digitised time histories, while the authoritative
93-series score uses five Table 2 columns. Both are useful, but they answer different questions:

- full-history scores are sensitive to exact event timing and show whether a curve changes too
  early or too late;
- Table 2 scores compare defined experimental states and avoid overweighting dense digitisation;
- a case may have a good final state and a poor history if it fails hundreds of seconds early;
- prescribed injection pressure is not independent validation evidence.

Consequently, numerical rankings from the historical reports must not be placed directly beside
the five-column 93-series scores as if they used the same metric.

### 3.3 Data and reporting corrections that changed the result

- SW-S3's original permeability digitisation contradicted its measured flow by roughly a factor
  of five in transmissivity. The corrected series is consistent with the cubic law.
- SW-T1's early displacement CSVs contained an un-zeroed `-48.7 mm` baseline, a constant piston
  file, and mislabeled/sign-inconsistent channels. The current re-extraction resolves these.
- A differential-stress postprocessor mixed skeleton axial stress with total confining stress,
  biasing the result by approximately `alpha p`. This was reporting-only and required no rerun.
- Old SW-S4 point samplers remained at coordinates from the superseded mesh. Exact interface-node
  coordinates are now used.
- SW-S3 formerly used output-only reversible-opening parameters to improve `d_n`. Removing them
  changed its defensible mean score from 3.59% to 4.58%.

The conclusion is methodological as much as project-specific: a stable residual obtained through
the same wrong postprocessor on every run looks like reproducible physics. Sibling operators and
raw arithmetic must agree before a constitutive interpretation is made.

---

## 4. Calibration lineage: what the historical studies established

The 84- to 92-series analyses remain valuable as controlled sensitivity experiments, but their
recommended files are historical once a 93-series successor exists.

### 4.1 Early 84-89 comparisons

- For SW-S3, the old `84_01` baseline-Biot run best reproduced timing and post-event magnitude;
  setting matrix Biot to 0.6 without refitting caused failure roughly six minutes early. This was
  the first clear demonstration that physicalising a shared parameter can invalidate a specimen's
  existing strength calibration.
- SW-S4 case `89_06` improved kinematics over the paper-JRC case `89_01`, but still placed the
  event late and retained excessive post-failure shear stress.
- The paper audit then replaced invented saw-cut JRC/JCS combinations, corrected SW-T2 and SW-S4
  fracture geometry, introduced cohesion for the tensile pair, and corrected water bulk modulus.
- Endpoint agreement was repeatedly shown to be insufficient: several early cases finished near
  the right state only because they failed hundreds of seconds too early and spent the rest of the
  run on the residual branch.

### 4.2 Focused 90- and 91-series brackets

- SW-T1 cases `90_01` and `90_02` showed a regime boundary: raising peak cohesion from 26.39 to
  28.00 MPa changed the response from a coupled failure with 11.2% eight-history nRMSE to a locked
  specimen with 50.9%.
- The SWT2 cohesion bracket similarly showed that onset is quantised by the injection staircase;
  small strength changes can move failure by an entire stage.
- SW-S3 level/slope and residual-cohesion brackets showed that strength, displacement, and flow
  requested different interpolated parameter values. This is evidence of a missing relation, not
  a reason for another one-parameter sweep.
- SW-T1/T2 residual-cohesion brackets improved the unloading branch and produced the final
  residual cohesions of 9.19 and 9.71 MPa.
- SW-S4 JRC and `D_c` brackets closed in both directions. The central `D_c` is an optimum, but no
  value fits both the missed stage-4 burst and the final residual state.

### 4.3 The 92/93 transition

The 92-series fixed strength, unloading, geometry, and mesh variants. The 93-series then removed
the stress-frame mismatch (`ppfix`) and harmonised the diagnostic channels. This distinction is
important: a 92-to-93 score change may be a reporting correction rather than a new physical run.
The 93-series mesh-5 files are the final validation set used below.

---

## 5. Authoritative 93-series validation

### 5.1 Scores

| specimen | case | Q | `sigma'_n` | `tau` | `d_n` | `d_s` | **mean nRMSE** |
|---|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | `93_01` | 7.38% | 1.98% | 2.73% | 9.06% | 1.02% | **4.44%** |
| SW-T2 | `93_03` | 5.87% | 1.26% | 1.70% | 2.06% | 1.25% | **2.43%** |
| SW-S3 | `93_05` | 3.00% | 3.35% | 8.01% | 7.42% | 1.11% | **4.58%** |
| SW-S4 | `93_07` | 4.94% | 3.74% | 10.01% | 4.53% | 7.01% | **6.05%** |

### 5.2 Specimen-level interpretation

**SW-T1.** Slip magnitude and both stress channels are strong. The main residual is normal
displacement, followed by flow. Residual cohesion closes the stress branch better than the earlier
brackets, but the flow/displacement pair still asks for a somewhat different weakening response.

**SW-T2.** This is the lowest-error case across all five columns. The residual-cohesion bracket
closed consistently, making it the cleanest example of an identified scalar calibration in the
campaign.

**SW-S3.** Flow and shear displacement are strong; shear stress and normal displacement dominate
the mean. The corrected 123.40 mm mesh was introduced after the original preload setting, leaving a
roughly constant stage-1 shear offset. A preload re-gate is still justified, but should be reported
as such rather than silently absorbed into a strength parameter.

**SW-S4.** The error is concentrated at stage 4: the model is too strong and about 13 micrometres
short of the measured slip increment, then follows later stages more closely. The total slip budget
is approximately right but distributed over the wrong pressure windows. Because the specimen slips
on ramps rather than holds, neither a static strength shift nor a hold-healing term can repair that
shape without harming a neighbouring stage.

### 5.3 Identifiability limits

- Cohesion and JRC cannot be separated on this pressure path from envelope slope alone.
- The characteristic weakening length is unresolved for the three burst specimens because the
  transition occurs inside one Table 2 interval.
- The load-frame stiffness is best constrained on the large-slip tensile specimens and weakly
  constrained on the smooth saw cuts.
- Matrix Biot coefficient and fracture pressure coefficient both affect pressure-to-traction
  coupling, but the 96-series shows that their practical sensitivity is not uniform enough to call
  the redundancy harmless.
- `Q` is partly circular because the validation geometry factor was inverted from Table 2. The
  independent mesh-geometry flow channel remains the appropriate follow-up.

---

## 6. New result: matched Mohr-Coulomb baseline (94-series)

### 6.1 Comparison

The 94-series replaces only the BBFast shear-contact block with the matched roughness-dependent
Mohr-Coulomb law. Peak value and tangent are transferred at the last stick-stage stress; residual
strength, normal closure, aperture law, mesh, pressure schedule, and solver are retained.

| specimen | BBFast 93 | MC 94 | MC / BB error | BB reduction relative to MC |
|---|---:|---:|---:|---:|
| SW-T1 | 4.44% | 25.27% | 5.69x | 82.4% |
| SW-T2 | 2.43% | 23.14% | 9.52x | 89.5% |
| SW-S3 | 4.58% | 18.47% | 4.03x | 75.2% |
| SW-S4 | 6.05% | 8.91% | 1.47x | 32.1% |
| **specimen mean** | **4.38%** | **18.95%** | **4.33x** | **76.9%** |

Per-observable MC nRMSE:

| specimen | Q | `sigma'_n` | `tau` | `d_n` | `d_s` |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 22.88% | 18.67% | 25.85% | 31.05% | 27.90% |
| SW-T2 | 14.54% | 19.32% | 26.17% | 27.86% | 27.83% |
| SW-S3 | 9.59% | 8.19% | 19.55% | 27.49% | 27.54% |
| SW-S4 | 6.32% | 4.34% | 11.30% | 16.51% | 6.06% |

### 6.2 Where the laws separate

The build controls pass. At stage 1 the two laws agree to numerical precision. Through stages
1-4, differences in `Q`, `sigma'_n`, and `tau` are zero or negligible. The large difference is
created when weakening begins:

- at stage 5, SW-T1 MC has already accumulated 0.481 mm slip against the paper's 0.008 mm;
- SW-T2 MC has 0.517 mm against 0.015 mm;
- SW-S3 MC has 0.063 mm against 0.001 mm;
- SW-S4 remains much closer, with 0.049 mm against 0.041 mm.

By stage 6 the MC endpoints are often reasonable again, but the premature transition has already
created a large path error. This is not evidence for distinguishable envelope curvature: the
pre-yield envelopes were deliberately matched and the observed divergence is dominated by the
post-yield evolution. BBFast's separate strength-weakening and roughness/aperture distances are the
main expressive advantage demonstrated by this comparison.

The mesh-3 94-series files all end early and cannot be used to make a converged MC comparison.

---

## 7. Rate-and-state experiment (95-series)

Only the SW-S4 bracket was run. The level-matched `b = 0` control and `b = 0.005` completed;
the velocity-weakening `b = 0.015` case stalled at 1554.86 s.

Principal findings:

- stage-4 shear displacement moves only from 0.0037 to 0.0039 mm when `b` is added, against a
  target of 0.0170 mm;
- the same change worsens stage 5, so the hold-healing mechanism has the wrong leverage;
- the velocity-weakening case produces discrete events, state collapse, negative overstress, and
  active-set oscillation, making it a useful deterministic reproducer for the slip/arrest stall;
- replacing `eta V` with laboratory-scale direct effect improves `Q`, `sigma'_n`, and `tau`, but
  worsens both displacement columns. It is a trade, not a net validation improvement;
- `tangential_viscosity` must be reported as a constitutive rate term at its calibrated value, not
  hidden in a numerics table.

The result closes the proposed `D_rs` follow-up for this specimen. A rate/state term driven by slip
velocity cannot fix an onset-envelope error whose signature is a missing ramp-stage increment.

---

## 8. New result: poroelastic consistency probes (96-series)

### 8.1 Matrix Biot coefficient, 0.6 to 0.2

All four `alpha = 0.2` probes complete.

| specimen | production `alpha=0.6` | probe `alpha=0.2` | change |
|---|---:|---:|---:|
| SW-T1 | 4.44% | 4.21% | -0.23 points |
| SW-T2 | 2.43% | 2.74% | +0.31 points |
| SW-S3 | 4.58% | 18.90% | +14.32 points |
| SW-S4 | 6.05% | 9.60% | +3.55 points |

The tensile pair is nearly insensitive at the aggregate level, within a few tenths of a point.
The saw cuts are not. In particular, SW-S3's error redistributes across every mechanical channel:
`sigma'_n = 10.11%`, `tau = 23.98%`, `d_n = 28.30%`, and `d_s = 25.97%`. A single shared `alpha`
is physically desirable, but the campaign cannot change it without refitting the saw-cut strength
and coupling response.

### 8.2 Fracture pressure coefficient, saw cuts to 1.0

| case | change | requested end (s) | CSV end (s) | Table 2 stages reached |
|---|---|---:|---:|---:|
| `96_04` SW-S3 | `alpha_f: 0.87 -> 1.0` | 4802 | 2474.9 | 5 |
| `96_05` SW-S3 | `alpha: 0.2`, `alpha_f: 1.0` | 4802 | 2510.2 | 5 |
| `96_07` SW-S4 | `alpha_f: 0.86 -> 1.0` | 3500 | 1668.5 | 5 |
| `96_08` SW-S4 | `alpha: 0.2`, `alpha_f: 1.0` | 3500 | 1673.4 | 5 |

Every `alpha_f = 1.0` saw-cut result stops before the peak stage. Scores over five pre-peak stages
must not be compared with full 11-stage means. Because no termination logs accompany these CSVs,
the safe conclusion is sensitivity and incomplete execution—not a proved constitutive or solver
failure mechanism. The repeated result nevertheless contradicts any assertion that the fitted
attenuation is demonstrably irrelevant.

---

## 9. New result: cyclic injection (97-series)

### 9.1 Completion state

| specimen | requested end (s) | CSV end (s) | status |
|---|---:|---:|---|
| SW-T1 | 10375.4 | 4602.4 | partial, second up-ramp |
| SW-T2 | 13881.5 | 6644.1 | partial, second peak |
| SW-S3 | 15792.7 | 6054.1 | partial, second up-ramp |
| SW-S4 | 10815.9 | 10815.9 | complete |

All four complete cycle 1, so first-cycle retention can be measured. Only SW-S4 supports a
cycle-1-to-cycle-3 comparison.

### 9.2 Retained change after cycle 1

The comparison below samples the first loading crossing of 8 MPa and the cycle-1 8 MPa floor
hold. Pressure is therefore identical and the elastic pressure dependence is controlled.

| specimen | aperture ratio | permeability ratio | flow ratio | retained `d_n` (mm) | retained `d_s` (mm) |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 2.328 | 5.610 | 12.598 | -0.13907 | 0.53378 |
| SW-T2 | 2.019 | 4.144 | 8.228 | -0.13180 | 0.57013 |
| SW-S3 | 1.289 | 1.645 | 2.141 | -0.03676 | 0.07541 |
| SW-S4 | 1.031 | 1.041 | 1.093 | -0.03232 | 0.08468 |

The tensile fractures retain the largest hydraulic change because their hydraulic aperture is
kinematically tied to the large mechanical opening. SW-S4 retains large mechanical slip and
opening but only a 4.1% permeability gain at the same pressure, consistent with its deliberately
decoupled hydraulic-aperture fit.

### 9.3 SW-S4 across all three cycles

Values at the 8 MPa floor holds:

| cycle | aperture (um) | flow (mL/min) | `d_n` (mm) | `d_s` (mm) | roughness state |
|---:|---:|---:|---:|---:|---:|
| 1 | 0.76287 | 0.00542 | -0.032319 | 0.084683 | 0.22180 |
| 2 | 0.77894 | 0.00576 | -0.035552 | 0.094563 | 0.20749 |
| 3 | 0.77907 | 0.00577 | -0.035576 | 0.094637 | 0.20739 |

From cycle 1 to cycle 3, aperture rises 2.12%, permeability 4.29%, flow 6.51%, slip 11.75%, and
opening magnitude 10.08%. The cycle-3 increments are only about 0.8% of the corresponding cycle-2
increments for aperture, slip, and opening. The model therefore permits a modest second-cycle
increment and is effectively saturated by the third cycle. This is the expected structural limit
of histories driven monotonically by cumulative slip: without cycle-count fatigue, subcritical
crack growth, or another time-dependent damage variable, equal-peak cycles cannot keep producing
new damage once slip arrests.

The incomplete tensile/SW-S3 runs are also a robustness result: three-cycle behaviour cannot be
claimed until those runs are completed and their termination cause is captured.

---

## 10. New result: shut-in (98-series)

All four runs reach their requested end time. “Near ambient” below means the injection pressure is
within 1% of its peak-to-ambient excursion, approximately 691 s after shut-in for the imposed
150 s exponential time constant.

| specimen | net slip after shut-in (mm) | slip after near-ambient (mm) | end/pre-injection aperture | end/pre-injection permeability |
|---|---:|---:|---:|---:|
| SW-T1 | -0.000225 | -0.000001 | 2.290 | 5.405 |
| SW-T2 | -0.000154 | -0.000001 | 1.884 | 3.616 |
| SW-S3 | -0.000295 | -0.000001 | 1.231 | 1.511 |
| SW-S4 | -0.000170 | +0.000015 | 0.968 | 0.929 |

There is no delayed forward reactivation. The small negative changes are relaxation/reconstruction
of the reported slip channel, not continued accumulation. SW-S4's 0.000015 mm late increase is
15 nanometres, only 0.018% of its approximately 0.084 mm slip, and is not a material reactivation.

The hydraulic residual is specimen-dependent. The tensile pair and SW-S3 retain substantial
aperture/permeability after depressurisation. SW-S4 ends slightly below its pre-injection hydraulic
aperture even though it retains mechanical opening, again demonstrating that its flow channel is
not a direct opening measurement.

The paper-level conclusion is negative and useful: within this quasi-static, specimen-scale model,
ordinary fracture/matrix diffusion is insufficient to produce post-shut-in slip. Explaining delayed
field reactivation requires physics or scales absent here, such as spatial poroelastic stress
transfer, rate/state evolution on a heterogeneous fault, dynamic rupture, or a larger drainage
domain.

---

## 11. Mesh, source, and verification audits

### 11.1 Mesh state

- SW-T1 is correctly meshed at 32°.
- SW-T2's printed 31° conflicts with the paper's own Table 2 reduction, which gives 30.001°; the
  corrected production mesh uses 30°.
- SW-S3 remains at 29° but was rebuilt from 124.40 to the paper's 123.40 mm length.
- SW-S4 was corrected from a 28.99°, 2.85 mm off-centre plane to a centred 30° plane.
- Every mesh change must be followed by an exact source-node check. `use_closest_node = true` can
  silently select a bulk node rather than the fracture.

SW-S4 is now the only complete 93-series two-mesh comparison. Its mesh-5 score is 6.05% and its
mesh-3 score is 6.26%, a +0.22 point penalty. The conclusion of practical mesh insensitivity for
this benchmark survives, while the other three post-slip mesh comparisons remain incomplete.

### 11.2 Source comparison, resolved chronologically

The August 15 comparison found the backup source to be a strict subset of `orca_4.0`: 53 shared
files identical, 9 different, and 40 files present only in `orca_4.0`. The live issues were the
stale split mass-balance kernels and historical unphysical `biot_coefficient = 1e-12` decks.

Current interpretation:

- the combined `kernel_SV` path used by production decks contains the intended Biot storage and
  poromechanical coupling;
- the old split pair remains legacy physics and should be fixed or retired before it is called a
  control;
- the contradictory combined-kernel comment identified in the old TODO is now corrected in source;
- all four 93-series decks use `biot_coefficient = 0.6`; the `1e-12` values remain only in
  historical decks;
- removal of external `SinglePhaseFluidProperties` support is intentional;
- the state-dependent fracture coefficient, absent at the time of the first source comparison,
  now exists as an opt-in feature but is disabled in production;
- `OrcaTestApp` in `main.C` is a registration superset and has no physics implication.

### 11.3 Verification state

Implemented coverage includes Terzaghi consolidation, Mandel's problem, pressure diffusion,
mass storage, thermal storage, simple diffusion, Barton-Bandis cohesion, and Biot modulus. The
theory manual now distinguishes these from specified but unimplemented single-element interface,
cubic-law, Sneddon, and inclined-fracture tests.

Important verification findings already established:

- Terzaghi and Mandel verify coupled consolidation and the Mandel-Cryer overshoot;
- pressure diffusion agrees with the erfc half-space solution;
- the thermal storage test exposed and fixed an unseeded lagged thermal-expansion coefficient;
- the Bakhtar aperture substitution is not unstable because of excessive local slope; it removes
  several bounded negative-feedback terms at once;
- `--check-input` is insufficient after a constitutive block swap because material-property
  resolution happens at initial setup. A two-step smoke run is required.

---

## 12. Documentation reconciliation

The August 18 document audit found six formulation mismatches and several stale claims. The current
paper/theory files have since corrected most of them:

| audit finding | current state |
|---|---|
| state-dependent `alpha_f` described as adopted | corrected: constant production values and disabled alternative are explicit |
| closure equation omitted exponent | corrected |
| hydraulic-aperture equation incomplete / double counting hidden | corrected, including per-specimen active terms |
| Bakhtar instability attributed to excessive slope | corrected to loss of the feedback stack |
| 40% envelope-slope discrimination claim | retracted; identifiability limit stated |
| nonexistent verification suite presented as implemented | corrected into implemented vs specified tests |
| 93-series results absent | corrected with the authoritative Table 2 scores |
| stale production parameters | corrected in the manuscript tables |
| reporting-frame sign reversal described as constitutive | retained only as a historical diagnostic lesson |
| rate/viscosity role omitted | corrected and quantified |

Items still needing integration:

1. Replace the pending §5.5/§6.3 MC blocks with the 94-series results in §6 of this document.
2. Replace the pending shut-in block with the complete negative result in §10.
3. Report the cyclic campaign as one complete three-cycle result plus three partial runs—not as
   four completed cases—and include the valid first-cycle retention table.
4. Update the pressure-coefficient discussion: the 96-series does not support the statement that
   the saw-cut attenuation buys no agreement; all four `alpha_f = 1` variants are incomplete.
5. Update mesh convergence: SW-S4 mesh 3 is complete at 6.26%; the other three remain partial.
6. Complete data/code availability, final references, and editorial placeholders before submission.

---

## 13. Integrated back-analysis method

The campaign's durable workflow is:

1. **Audit the plumbing.** Verify mesh plane, source nodes, boundary nodesets, units, stress frame,
   postprocessor meaning, and whether an “output-only” parameter has been fitted.
2. **Recompute the score from raw output before reading a prior interpretation.** Agreement in
   arithmetic localises any disagreement to interpretation.
3. **Score the source, not a convenient derivative.** Prefer Table 2 states; exclude algebraically
   derived columns and constructed datum rows.
4. **Normalise and preserve raw errors.** nRMSE ranks; MPa, micrometres, and seconds diagnose.
5. **Localise by load window.** Separate ramps from holds and loading from unloading.
6. **Ask whether the proposed parameter can generate the missing shape.** A scalar level cannot
   repair an absent rate or path dependence.
7. **Interpolate each observable across a bracket.** Agreement identifies a parameter; a split
   proves that one knob is doing two jobs.
8. **Use an independent channel to test the suspected second mechanism.** Controls where that
   mechanism is inactive are part of the evidence.
9. **Bracket in both directions and write the prediction before running.** A negative result can
   close a hypothesis permanently.
10. **Price damage to already-correct observables before building the next deck.** Quantised load
    stages and mesh geometry often make the apparent “small adjustment” impossible.
11. **Use minimal-diff baselines and validate them with a short execution, not parsing alone.**
12. **Record negative results and superseded recommendations.** They prevent the same failed
    mechanism from being proposed again.

---

## 14. Research implications beyond the present validation

The Hosseini, Paluszny, and Zimmerman (2025) reading notes support a narrower second-paper direction
than “add all rate/state fault physics to ORCA.” Their heterogeneous-fault work supplies the
rate/state, nucleation, quasi-dynamic, aseismic-front, and cascade context, but it does not include
the validated slip-dependent aperture evolution available here.

The defensible extension is therefore:

- retain the validated specimen-scale friction/aperture formulation;
- verify any new rate/state implementation against a recognised benchmark before using it for
  physics claims;
- isolate how slip-dependent permeability changes aseismic-front propagation and post-slip fluid
  redistribution relative to a constant-aperture fault;
- avoid transferring specimen JRC/JCS directly to field scale while the Barton size corrections
  remain unvalidated;
- distinguish a constitutive performance claim from an earthquake-cycle claim, since the current
  quasi-static solver cannot represent dynamic rupture.

The current 95- and 98-series negative results sharpen that scope: local hold healing and ordinary
specimen-scale diffusion do not produce the missing delayed response. Heterogeneity, larger-scale
poroelastic stress transfer, or explicitly dynamic/rate-state processes must be introduced as new,
separately verified hypotheses.

---

## 15. Prioritised remaining work

### Blocking a complete paper result

1. Diagnose and rerun the incomplete SW-T1, SW-T2, and SW-S3 cyclic cases, preserving their current
   CSVs and capturing stdout/stderr. Do not infer a common failure cause from truncation alone.
2. Insert the completed 94-series and 98-series results into the manuscript.
3. Insert the partial/complete 97-series result with its limits stated explicitly.
4. Reconcile manuscript §6.2 with the 96-series coefficient sensitivity.
5. Re-gate SW-S3 preload on the corrected-length mesh or retain the current offset as a declared
   limitation.

### High-value verification and robustness

6. Complete the three missing post-slip mesh comparisons; the complete SW-S4 pair already shows a
   small 0.22-point change.
7. Score and report the independent mesh-geometry flow channel so the fitted `W/L` route is not the
   only hydraulic comparison.
8. Fix or retire the stale split mass-balance kernels.
9. Implement the specified single-element normal-closure, return-map, envelope, and cubic-law tests.
10. Treat `alpha_f = 1` and state-dependent `alpha_f` as new calibration campaigns, not toggles.

### Not recommended without new evidence

- another one-dimensional `D_c`, cohesion, or JRC sweep for SW-S4;
- further `b` or `D_rs` brackets for hold-stage healing;
- adopting RSF because it is more physical despite no net score improvement;
- quoting four fitted JRC/JCS/cohesion values as independently measured properties;
- interpreting incomplete 96 or 97 files as completed physics results;
- a field-scale extrapolation before quantifying the disabled size correction.

---

## 16. Source map and authority

| source document | contribution to this consolidation | authority |
|---|---|---|
| `89_01_89_06_vs_validation_description.md` | early four-specimen history comparisons | historical |
| `90_01_90_02_vs_validation_analysis.md` | focused strength brackets and event timing | historical |
| `90_01_91_01_91_02_vs_validation_analysis.md` | SW-T1 residual-cohesion bracket | historical |
| `91_05_vs_validation_analysis.md` | SW-S3 residual-cohesion diagnosis | historical |
| `HPC_90_91_92_TABLE2_ERROR_ANALYSIS.md` | scoring convention, 92/93 selection, residual tables | authoritative method/result lineage |
| `MC_BASELINE_94_SERIES.md` | matched MC construction and transfer | authoritative design; results added here |
| `V6_RATE_STATE_AND_POROELASTIC_PROBES.md` | 95 design/results and 96 design | authoritative; 96 results added here |
| `DISCUSSION_DECKS_97_98.md` | cyclic/shut-in design and preregistered metrics | authoritative design; results added here |
| `MESHES.md` | geometry provenance and node-placement rules | authoritative |
| `biot_alpha_study_2026-08-15.md` | early Biot A/B evidence | historical; superseded by 93/96 production probes |
| `sample_parameter_unification_2026-08-16.md` | cross-specimen/data audit | authoritative diagnosis; some parameter tables historical |
| `paper_vs_model_audit_2026-08-16.md` | paper-property and geometry audit | authoritative provenance with applied fixes |
| `SOURCE_COMPARISON.md` | source-tree comparison | historical snapshot, reconciled with current source here |
| `DOC_AUDIT_2026-08-18.md` | formulation/document mismatch audit | authoritative audit snapshot; most fixes now applied |
| `back_analysis_method.md` | general campaign method | authoritative synthesis |
| `back_analysis_method_claude_raw_analysis.md` | raw precursor to the method document | superseded; no separate authority |
| `reading_hosseini2025_rsf_heterogeneous_fault.md` | rate/state foundations and paper-2 scope | literature synthesis |
| `Theory/orca_czm_theory.md` | complete formulation and implementation manual | current technical reference, subject to implemented-test limits |
| `Paper/paper_draft_ye_ghassemi_validation.md` | manuscript narrative | current draft; pending blocks identified in §12 |
| `TODO.md` | work log and historical queue | useful chronology; individual statuses may lag current artifacts |

### Reproduction entry points

```bash
# Current Table 2 score for any completed monotonic run
python3 scripts/table2_gate.py --tag hpc path/to/results.csv

# Cross-sample digitised-history scorecard
python3 scripts/sample_scorecard.py

# Geometry and source-node audits
python3 scripts/check_mesh_geometry.py
python3 scripts/check_source_nodes.py --deck path/to/deck.i

# Paper-parameter audit
python3 scripts/paper_parameter_audit.py
```

For the new 97/98 calculations, values were sampled at the hold times written into the decks.
Cyclic retention compares equal-pressure 8 MPa states. Shut-in “near ambient” is defined as within
1% of the peak-to-ambient pressure excursion. Ratios use the model's reported hydraulic aperture,
permeability, and validation-flow channels without refitting.

---

## 17. Final statement

The strongest result is not that one constitutive law matches four plots. It is that a consistent
audit-and-score workflow separated four kinds of discrepancy that initially looked alike:
reporting errors, data-reduction errors, identifiable parameter errors, and genuine model-form
limits. After those separations, BBFast reproduces the monotonic benchmark substantially better
than a matched Mohr-Coulomb baseline; repeated cycling mostly saturates where it completes; and
shut-in produces no delayed reactivation. Those negative and comparative results define the next
model more sharply than another marginal improvement to the calibrated score would.
