# ORCA 4.0 consolidated analysis

**Repository:** `orca_4.0`  
**Branch / revision examined:** `orca_v6`, working tree based on `de7ee16`<br>
**Consolidation date:** 2026-08-18; result and coverage updates through 2026-08-20
**Benchmark:** Ye and Ghassemi (2018), four granite-fracture injection tests

> **SUPERSEDED IN TWO PLACES, 2026-08-25.** Every Mohr–Coulomb score below predates a fix to
> `scripts/table2_gate.py`. The two constitutive materials decompose their reported normal opening
> differently (the MC material's `normal_opening_total` has no elastic term), so the campaign's
> `d_n` channel was not the same observable on the two sides of the comparison. Scoring now uses
> the global kinematic jump. **No Barton–Bandis score changed**; the MC finals became
> SW-T1 25.31, SW-T2 23.18, SW-S3 18.23, **SW-S4 7.07** (was 8.97), taking SW-S4's BB/MC ratio
> from 1.46× to 1.15×. Separately, the BB/MC comparison here is a matched *transfer*, and an
> archived campaign of 52 independently calibrated MC runs reaches 4.40 % on SW-S4 and 6.07 % on
> SW-S3 — so "MC cannot reproduce this dataset" is not a supported reading of the tables below.
> Both corrections, with provenance and caveats, are in
> `doc/independent_analysis/MC_ARCHIVE_RECOVERY_2026-08-25.md`. The BBFast content of this
> document is unaffected.

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
   current 93-series mesh-5 files score 4.44% (SW-T1), 2.43% (SW-T2), 4.57% (SW-S3), and 6.14% (SW-S4)
   mean normalised RMSE over the five scored Table 2 columns. The result is strongest as a
   specimen-scale reproduction of stagewise hydro-mechanical response, not as proof that every
   fitted parameter is independently identifiable.

2. **The eight targeted 99-series probes are complete and produce two clear improvements.**
   Increasing SW-T1 maximum closure from 45.91 to 50.00 micrometres reduces its mean from 4.44%
   to 3.68% and improves all five scored observables. Increasing SW-T2 aperture scale from
   0.0165 to 0.0170 reduces its mean from 2.43% to 2.24%, mainly through flow. SW-S3 residual
   cohesion at 1.30 MPa gives a smaller 4.57% to 4.45% gain with a shear-slip tradeoff. Both
   SW-S4 changes worsen the total score, so `93_07` remains preferred there.

   The six completed 100-series runs refine three specimens. SW-T1 `100_01` is the strongest
   resolved improvement: `maximum_closure = 55 um` lowers the mean to 2.688632%. SW-T2 reaches
   2.131869% at `aperture_scale = 0.0177`, but `0.0175` differs by only 0.003869 points. SW-S3
   `100_06` is the nominal physical minimum at 4.353781%; its 0.097-point gain over `99_06` is
   below the reproducibility floor. The latter two selections are brackets, not exact property
   identifications.

3. **The matched Mohr-Coulomb baseline is decisively worse.** The completed mesh-5 94-series
   scores are 25.27%, 23.14%, 18.47%, and 8.97%, respectively. Averaged across specimens,
   BBFast is 4.39% versus 18.96% for MC, a 77% reduction. The two laws are effectively identical
   before yielding; the separation appears on the weakening path. This supports a performance
   claim for the two-distance BBFast form, not a claim that the narrow stress path uniquely
   identifies the curvature of the Barton-Bandis envelope.

4. **The SW-S4 rate-and-state healing hypothesis was falsified.** The `b` bracket did not repair
   the deficient hold-stage slip, and velocity weakening produced a deterministic slip/arrest
   stall. The useful result is that the fitted Perzyna viscosity is not merely numerical: on
   SW-S4 it contributes 0.314 MPa mean and 0.871 MPa peak shear overstress during slipping.

5. **Matrix Biot sensitivity is specimen-dependent.** Changing `biot_coefficient` from 0.6 to
   0.2 moves the tensile-pair scores only from 4.44% to 4.21% and 2.43% to 2.74%, but degrades
   SW-S3 from 4.57% to 18.90% and SW-S4 from 6.14% to 9.60%. The assumed coefficient cannot be
   changed by fiat across the campaign.

6. **The fitted fracture pressure coefficient is not shown to be inert.** All four saw-cut
   probes that set `fault_pressure_coefficient = 1.0` stop before the peak Table 2 stage. The
   stored artifacts do not include termination logs, so the immediate cause cannot be assigned,
   but the repeated truncation proves that removing the 0.87/0.86 attenuation is not a harmless
   documentation cleanup. It requires a re-calibration and a controlled rerun.

7. **The corrected 101-series cyclic campaign is complete.** All four equal-peak three-cycle runs
   reach their requested end times. At matched 8 MPa floor holds, cycle-3/cycle-1 permeability
   ratios are 1.000002 (SW-T1), 0.999997 (SW-T2), 1.000002 (SW-S3), and 1.000383 (SW-S4).
   Equal-peak repetition therefore produces no material additional enhancement. Escalating peaks
   expose specimen-specific thresholds instead: SW-T1 changes abruptly at 28 MPa, SW-T2 largely
   saturates after its 26 MPa event, and SW-S3 continues evolving through both increments.

8. **The preregistered SW-S4 101-series validity check fails.** Retiming the fitted loading-frame
   terms causes 0.001186 mm slip before injection begins at 800 s. All four SW-S4 101 trajectories
   are numerically complete but qualified; they cannot be presented as clean frozen-frame controls
   without a redesigned settling window and rerun.

9. **Shut-in still produces arrest, including the slow-bleed control.** In every 101 shut-in run,
   the global slip-rate maximum precedes shut-in. Removing the hold produces only small immediate
   forward transients before relaxation. The valid SW-T1 `tau = 1500 s` run has zero resolved
   forward growth and -0.000222 mm net change, so the negative result is not an artefact of the
   original 150 s pressure-decay time. The SW-S4 direction agrees but remains qualified by item 8.

10. **The main historical apparent failures were often measurement-path failures.** Correcting
   stress frames, stale point coordinates, output-only displacement fits, mesh geometry, and
   digitised validation series changed conclusions without changing constitutive physics. The
   durable method is: audit the plumbing, score the source data, localise the residual, and only
   then tune a parameter.

11. **All current result files are indexed and the main findings are integrated into the manuscript.** The
    ranking covers every valid monotonic simulation result; non-monotonic 97/98/101 results,
    retired runs, duplicates, and derived summaries are explicitly classified in the coverage
    indexes. The paper now reports the 94/96/99/100/101 findings and the qualified SW-S4 limit;
    final editorial and data-availability work remains outside this analysis update.

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
| SW-T2 | 14.63 | 150 | 29.756° | 33.20 | 9.71 | `4.0e11` | 4.0 | 0.0177* |
| SW-S3 | 1.96 | 150 | 29.756° | 1.67 | 1.40 | `4.0e11` | 4.0 | 0.0010 |
| SW-S4 | 5.00 | 150 | 22.72° | 0 | 0 | `3.5e12` | 2.0 | 0.0010 |

These are calibrated sets, not eight independently measured material properties. Over the stress
range visited, cohesion and JRC produce envelope slopes differing by only about 3%; the loading
path constrains an effective strength combination much more strongly than it constrains either
parameter separately. SW-S4's adopted JRC of 5 is calibrated and differs from its measured 1.19.
The asterisk marks the nominal 100-series SWT2 selection; `0.0175–0.0177` is unresolved at the
campaign reproducibility floor, while the 93-series `0.0165` deck remains the locked validation
control.

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
  changed its defensible mean score from 3.58% to 4.57% in the current result set.

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
| SW-S3 | `93_05` | 3.00% | 3.33% | 8.01% | 7.42% | 1.11% | **4.57%** |
| SW-S4 | `93_07` | 5.01% | 3.87% | 10.10% | 4.63% | 7.08% | **6.14%** |

The SW-S3 changes relative to the August 18 table are below the reproducibility floor. The SW-S4
repeat is 0.091 percentage points higher than the earlier file, essentially at that floor; the
ranking CSV now reports the scores recomputed from the result files currently present rather than
retaining stale numbers tied to overwritten copies.

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
| SW-S3 | 4.57% | 18.47% | 4.04x | 75.2% |
| SW-S4 | 6.14% | 8.97% | 1.46x | 31.6% |
| **specimen mean** | **4.39%** | **18.96%** | **4.32x** | **76.8%** |

Per-observable MC nRMSE:

| specimen | Q | `sigma'_n` | `tau` | `d_n` | `d_s` |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 22.88% | 18.67% | 25.85% | 31.05% | 27.90% |
| SW-T2 | 14.54% | 19.32% | 26.17% | 27.86% | 27.83% |
| SW-S3 | 9.59% | 8.18% | 19.55% | 27.49% | 27.54% |
| SW-S4 | 6.32% | 4.41% | 11.41% | 16.55% | 6.18% |

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

The delivered SW-S4 mesh-3 MC result, `94_08`, now completes and scores 8.84%, versus 8.97% for
mesh 5. The 0.14-point difference is small and does not change the constitutive comparison. The
other three mesh-3 MC files remain incomplete.

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
| SW-S3 | 4.57% | 18.90% | +14.32 points |
| SW-S4 | 6.14% | 9.60% | +3.47 points |

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

## 11. New result: targeted material-property probes (99-series)

### 11.1 Completion and scoring state

All eight 99-series runs reach their requested end time and all eleven Table 2 stages. Each is a
one-parameter change from the corresponding mesh-5 93-series parent, so the response difference
can be assigned to that axis without a multi-parameter interaction. The table uses the same
stage-1 displacement datum and five-observable range-normalised RMSE as the rest of this document.

| specimen | case | one changed value | Q | `sigma'_n` | `tau` | `d_n` | `d_s` | **mean** | change from 93 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| SW-T1 | `93_01` | parent | 7.38% | 1.98% | 2.73% | 9.06% | 1.02% | **4.44%** | -- |
| SW-T1 | `99_01` | `maximum_closure`: 45.91 to 50.00 um | 6.15% | 1.69% | 2.32% | 7.28% | 0.96% | **3.68%** | **-0.76** |
| SW-T1 | `99_02` | `aperture_scale`: 0.0160 to 0.0155 | 5.30% | 1.99% | 2.74% | 9.07% | 1.02% | **4.02%** | **-0.41** |
| SW-T2 | `93_03` | parent | 5.87% | 1.26% | 1.70% | 2.06% | 1.25% | **2.43%** | -- |
| SW-T2 | `99_03` | `residual_cohesion`: 9.71 to 8.74 MPa | 4.46% | 1.06% | 1.43% | 2.36% | 2.63% | **2.39%** | -0.04 |
| SW-T2 | `99_04` | `aperture_scale`: 0.0165 to 0.0170 | 4.89% | 1.26% | 1.71% | 2.06% | 1.26% | **2.24%** | **-0.19** |
| SW-S3 | `93_05` | parent | 3.00% | 3.33% | 8.01% | 7.42% | 1.11% | **4.57%** | -- |
| SW-S3 | `99_05` | unload retention: 0.06 to 0.03 | 2.98% | 3.37% | 8.09% | 7.05% | 1.11% | **4.52%** | -0.06 |
| SW-S3 | `99_06` | `residual_cohesion`: 1.40 to 1.30 MPa | 3.09% | 3.01% | 7.25% | 6.83% | 2.07% | **4.45%** | **-0.12** |
| SW-S4 | `93_07` | parent | 5.01% | 3.87% | 10.10% | 4.63% | 7.08% | **6.14%** | -- |
| SW-S4 | `99_07` | weakening exponent: 1.10 to 1.05 | 4.95% | 3.69% | 9.60% | 5.31% | 7.67% | **6.24%** | **+0.11** |
| SW-S4 | `99_08` | viscosity: 3.5e12 to 3.0e12 Pa s/m | 4.81% | 3.67% | 9.54% | 5.59% | 8.15% | **6.35%** | **+0.21** |

Differences smaller than 0.1 percentage points are listed for completeness but are not treated as
resolved rankings. The updated machine-readable CSV contains exact six-decimal values and ranks.

### 11.2 Interpretation and selection

**SW-T1: accept `99_01` as the strongest candidate.** Recomputing the closure offset preserved
the initial seating while the larger closure capacity improved unloading recovery. Unlike a
purely hydraulic fit, it also lowers both stress errors and shear-slip error. Its 0.76-point gain
is much larger than the reproducibility floor and all five observables improve. `99_02` confirms
that a smaller aperture scale can repair flow, but it leaves the displacement residual untouched
and is therefore the weaker explanation.

**SW-T2: use `99_04` as the parent of the 100-series refinement; do not promote `99_03` on score alone.** The aperture-scale increase
removes enough of the peak-flow deficit to improve the mean by 0.19 points while mechanical
metrics move by at most 0.01 points. Lower residual cohesion improves the two stress columns but
nearly doubles the shear-slip nRMSE; its 0.04-point mean gain is below the ranking floor and
reproduces the already-known `91_03` bracket.

**SW-S3: `99_06` is a provisional balanced-score improvement, not a clean identification.** The
1.30 MPa residual cohesion lowers effective-normal-stress, shear-stress, and normal-displacement
errors enough to clear the 0.1-point floor, but shear-slip nRMSE rises from 1.11% to 2.07%.
`99_05` changes only the unloading branch as intended and improves `d_n`, but the 0.06-point total
gain is below reproducibility. The corrected-length-mesh preload offset should still be re-gated
before treating 1.30 MPa as a newly identified material property.

**SW-S4: reject both 99-series changes and retain `93_07`.** Lower exponent and lower viscosity
both reduce the stress residual, including part of the stage-4 error, but they purchase that gain
with worse normal and shear displacement. This confirms the earlier diagnosis: a single scalar
change cannot move slip into stage 4 without damaging the subsequent slip budget. Further
one-dimensional weakening or viscosity sweeps are not warranted from this evidence.

### 11.3 SWT2 aperture-scale refinement (100-series)

Both completed 100-series runs reach 2852.53 s and all eleven Table 2 stages. They change only
SWT2 `aperture_scale` from the `99_04` value of 0.0170; contact, strength, loading, mesh, and
reporting channels are unchanged.

| case | `aperture_scale` | Q | `sigma'_n` | `tau` | `d_n` | `d_s` | **mean** | change from `99_04` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `99_04` | 0.0170 | 4.892625% | 1.263352% | 1.708291% | 2.061925% | 1.256864% | **2.236611%** | -- |
| `100_03` | 0.0175 | 4.364306% | 1.271138% | 1.718877% | 2.065487% | 1.258877% | **2.135737%** | **-0.100874** |
| `100_04` | 0.0177 | 4.335516% | 1.274194% | 1.723031% | 2.066893% | 1.259708% | **2.131869%** | **-0.104743** |

The refinement behaves as intended: almost the entire gain comes from flow. From `99_04` to
`100_04`, Q nRMSE falls by 0.557109 points, while each mechanical nRMSE changes by no more than
0.014740 points. The flow residual changes sign across the path—peak-stage underprediction is
reduced while unloading-stage overprediction grows—so the aggregate minimum is shallow rather
than a uniformly better stagewise match.

`100_04` is the exact numerical winner and is retained as the nominal calibrated candidate, but
its 0.003869-point advantage over `100_03` is twenty-five times smaller than the 0.1-point
resolution criterion. The identified result is therefore a bracket (`0.0175–0.0177`), not an
exact four-decimal material property. No finer aperture-scale sweep is warranted without a more
precise independent flow constraint. Relative to the locked 93-series control, the nominal mean
improves by 0.295952 points (2.427821% to 2.131869%).

### 11.4 SWT1 and SWS3 100-series refinements

The four remaining 100-series runs also complete all eleven stages and are now included in the
ranking.

| specimen | case | principal change | Q | `sigma'_n` | `tau` | `d_n` | `d_s` | **mean** |
|---|---|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | `99_01` | 50 um parent | 6.154969% | 1.685639% | 2.317053% | 7.280400% | 0.956031% | **3.678819%** |
| SW-T1 | `100_01` | maximum closure 55 um | 4.510711% | 1.439992% | 1.978421% | 4.583625% | 0.930413% | **2.688632%** |
| SW-T1 | `100_02` | 50 um plus aperture scale 0.0155 | 4.029055% | 1.690447% | 2.323676% | 7.292947% | 0.957575% | **3.258740%** |
| SW-S3 | `99_06` | residual cohesion 1.30 MPa parent | 3.092301% | 3.006069% | 7.253266% | 6.833630% | 2.069985% | **4.451050%** |
| SW-S3 | `100_05` | residual cohesion 1.25 MPa | 3.168550% | 2.851208% | 6.898029% | 6.604122% | 2.656679% | **4.435718%** |
| SW-S3 | `100_06` | 1.30 MPa plus zero unload retention | 3.060460% | 3.069703% | 7.391637% | 6.173958% | 2.073149% | **4.353781%** |

`100_01` is a resolved SW-T1 improvement: its 0.990187-point gain over `99_01` is large relative
to the 0.1-point floor and all five channels improve. `100_02` confirms the independent hydraulic
gain but preserves the larger normal-displacement residual, so it is not the preferred combined
fit.

For SW-S3, `100_06` is the nominal physical minimum and is 0.220541 points better than the locked
`93_05` control. It is only 0.097269 points better than `99_06`, however, and `100_05` lies between
them with a stress/slip tradeoff. The defensible result is therefore a narrow unresolved
`99_06`/`100_05`/`100_06` bracket, not identification of zero unloading retention.

### 11.5 Previously unfinished monotonic results

The delivered result set completes one older file that the August 18 ranking marked partial:
SW-S4 mesh-3 Mohr-Coulomb case `94_08` now reaches 3500 s and scores 8.84%. The remaining partial
records still stop before all eleven stages and remain excluded. In particular, fresh copies of
the SW-T1/SW-T2/SW-S3 mesh-3 files, the saw-cut `fault_pressure_coefficient = 1` probes, and the
velocity-weakening rate/state run are still truncated; copying them into the result set did not
complete their trajectories.

| specimen | remaining partial case | stages reached | current end time (s) |
|---|---|---:|---:|
| SW-S3 | `86_02_sw3_bbfast_biot0p6_phir9p00_m0_kernel_SV` | 2/11 | 1304.250000 |
| SW-S3 | `93_06_sw3_final_resc1p40_ppfix_mesh3` | 6/11 | 2833.500000 |
| SW-S3 | `94_06_sw3_mc_final_mesh3` | 6/11 | 2804.250000 |
| SW-S3 | `96_04_sw3_fpc1p0` | 5/11 | 2474.913206 |
| SW-S3 | `96_05_sw3_biot0p2_fpc1p0` | 5/11 | 2510.213260 |
| SW-S4 | `95_16_sw4_rsf_a010_b015` | 5/11 | 1554.859285 |
| SW-S4 | `96_07_sw4_fpc1p0` | 5/11 | 1668.494440 |
| SW-S4 | `96_08_sw4_biot0p2_fpc1p0` | 5/11 | 1673.376124 |
| SW-S4 | `68_02_sw4_bbfast_tail6p75_eta3p25_m0_kernel_SV` | 0/11 | 75.000000 |
| SW-S4 | `68_03_sw4_bbfast_tail6p50_eta3p25_m0` | 2/11 | 717.316353 |
| SW-T1 | `93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3` | 0/11 | 70.500000 |
| SW-T1 | `94_02_swt1_mc_final_mesh3` | 1/11 | 372.000000 |
| SW-T2 | `92_05_swt2_final_theta30_resc9p71_mesh3` | 5/11 | 2217.000000 |
| SW-T2 | `93_04_swt2_final_theta30_resc9p71_ppfix_mesh3` | 4/11 | 1773.750000 |
| SW-T2 | `94_04_swt2_mc_final_mesh3` | 4/11 | 1806.000000 |

These files have neither matching recoverable checkpoints nor copied termination logs. Their
`*_hpc_nochk.sh` launchers explicitly disable checkpoint output, so they cannot be continued from
the last CSV row; each requires a fresh HPC run after its termination mode is identified. They
remain marked `partial`, with blank error/accuracy fields, rather than receiving misleading scores
from truncated loading paths.

### 11.6 Corrected cyclic and shut-in campaign (101-series)

All 16 101-series runs complete. The full preregistered metrics and tables are in
`doc/DISCUSSION_DECKS_101.md` and the three `DISCUSSION_101_*.csv` files. The principal results are:

- equal-peak cycle-3/cycle-1 floor permeability differs by no more than 0.0004 for any specimen;
- escalating peaks produce an abrupt final-step response on SW-T1, early response followed by
  saturation on SW-T2, and continuing increments on SW-S3;
- the SW-T1 half-stiffness frame arm adds 0.000367 mm second-cycle slip while the double-stiffness
  arm adds effectively none, supporting the predicted loading-frame control in direction but at
  only a 0.026% aperture effect;
- the global slip-rate maximum precedes shut-in in all six shut-in controls; the valid slow-bleed
  SW-T1 arm has no resolved forward post-shut-in growth;
- all four SW-S4 101 runs fail their preregistered pre-injection check with 0.001186 mm slip at
  800 s and are therefore qualified, despite being numerically complete.

---

## 12. Mesh, source, and verification audits

### 12.1 Mesh state

- SW-T1 is correctly meshed at 32°.
- SW-T2's printed 31° conflicts with the paper's own Table 2 reduction, which gives 30.001°; the
  corrected production mesh uses 30°.
- SW-S3 remains at 29° but was rebuilt from 124.40 to the paper's 123.40 mm length.
- SW-S4 was corrected from a 28.99°, 2.85 mm off-centre plane to a centred 30° plane.
- Every mesh change must be followed by an exact source-node check. `use_closest_node = true` can
  silently select a bulk node rather than the fracture.

SW-S4 is now the only complete 93-series two-mesh comparison. Its mesh-5 score is 6.14% and its
mesh-3 score is 6.37%, a +0.23 point penalty. The conclusion of practical mesh insensitivity for
this benchmark survives, while the other three post-slip mesh comparisons remain incomplete.

The newly completed SW-S4 MC mesh pair is similarly close: 8.97% on mesh 5 and 8.84% on mesh 3.

### 12.2 Source comparison, resolved chronologically

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

### 12.3 Verification state

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

## 13. Documentation reconciliation

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

Integration completed through 2026-08-20:

1. The matched 94-series comparison is reported in manuscript §5.5 and §6.3.
2. The corrected 101-series cyclic and shut-in controls replace the partial 97/98 conclusions;
   all 16 runs are complete and the four SW-S4 controls are explicitly qualified.
3. The 96-series pressure-coefficient discussion now states that all four `alpha_f = 1` saw-cut
   arms are incomplete and cannot establish a score comparison.
4. Mesh convergence now reports the complete SW-S4 BBFast (6.14%/6.37%) and MC
   (8.97%/8.84%) pairs while retaining the other three specimen pairs as incomplete.
5. The 99/100 calibration refinements and their reproducibility limits are reported.

Data/code availability, final references, and removal of editorial-plan material remain submission
tasks rather than analysis-coverage gaps.

---

## 14. Integrated back-analysis method

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

## 15. Research implications beyond the present validation

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

## 16. Prioritised remaining work

### Blocking a complete paper result

1. Redesign the SW-S4 101 settling window so its loading-frame terms do not trigger pre-injection
   slip, then rerun the four qualified SW-S4 controls.
2. Insert the completed 94/96/99/100/101 results into the manuscript.
3. Treat the 97/98 results as superseded design lineage and report the corrected 101 controls.
4. Reconcile manuscript §6.2 with the 96-series coefficient sensitivity.
5. Re-gate SW-S3 preload on the corrected-length mesh or retain the current offset as a declared
   limitation.

### High-value verification and robustness

6. Complete the three missing post-slip mesh comparisons; the complete SW-S4 BBFast and MC pairs
   already show small 0.23- and 0.14-point changes.
7. Score and report the independent mesh-geometry flow channel so the fitted `W/L` route is not the
   only hydraulic comparison.
8. Fix or retire the stale split mass-balance kernels.
9. Implement the specified single-element normal-closure, return-map, envelope, and cubic-law tests.
10. Treat `alpha_f = 1` and state-dependent `alpha_f` as new calibration campaigns, not toggles.

### Not recommended without new evidence

- another one-dimensional `D_c`, cohesion, JRC, weakening-exponent, or viscosity sweep for SW-S4;
- further `b` or `D_rs` brackets for hold-stage healing;
- adopting RSF because it is more physical despite no net score improvement;
- quoting four fitted JRC/JCS/cohesion values as independently measured properties;
- interpreting incomplete 96 or 97 files as completed physics results;
- a field-scale extrapolation before quantifying the disabled size correction.

---

## 17. Source map and authority

| source document | contribution to this consolidation | authority |
|---|---|---|
| `89_01_89_06_vs_validation_description.md` | early four-specimen history comparisons | historical |
| `90_01_90_02_vs_validation_analysis.md` | focused strength brackets and event timing | historical |
| `90_01_91_01_91_02_vs_validation_analysis.md` | SW-T1 residual-cohesion bracket | historical |
| `91_05_vs_validation_analysis.md` | SW-S3 residual-cohesion diagnosis | historical |
| `HPC_90_91_92_TABLE2_ERROR_ANALYSIS.md` | scoring convention, 92/93 selection, residual tables | historical method/result lineage; current scores are in the ranking CSV |
| `TABLE2_ERROR_ACCURACY_RANKING.csv` | every available monotonic simulation result, completion state, overall ranks, and model-family ranks; unphysical historical arms remain explicitly labelled | authoritative machine-readable result index |
| `MC_BASELINE_94_SERIES.md` | matched MC construction and transfer | authoritative design; results added here |
| `V6_RATE_STATE_AND_POROELASTIC_PROBES.md` | 95 design/results and 96 design | authoritative; 96 results added here |
| `DISCUSSION_DECKS_97_98.md` | cyclic/shut-in design and preregistered metrics | authoritative design; results added here |
| `DISCUSSION_DECKS_101.md` | corrected cyclic/shut-in design, completed results, and failed SW-S4 falsifier | authoritative 101-series design and interpretation |
| `independent_analysis/DISCUSSION_101_*.csv` | 101 run inventory and cyclic/shut-in metrics | authoritative machine-readable 101 result index |
| `independent_analysis/INPUT_DECK_ANALYSIS_COVERAGE.csv` | disposition of all 174 repository inputs: 166 specimen decks and 8 verification tests | authoritative coverage index |
| `independent_analysis/RESULT_FILE_ANALYSIS_COVERAGE.csv` | disposition of all 111 simulation/derived result CSVs | authoritative coverage index |
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
| `Paper/paper_draft_ye_ghassemi_validation.md` | manuscript narrative | current results draft; remaining work is editorial/submission preparation |
| `TODO.md` | work log and historical queue | useful chronology; individual statuses may lag current artifacts |

### Reproduction entry points

```bash
# Current Table 2 score for any completed monotonic run
python3 scripts/table2_gate.py path/to/results.csv

# Recompute the complete monotonic ranking
python3 scripts/update_table2_ranking.py --write

# Recompute 101 metrics and exhaustive deck/result coverage
python3 scripts/analyze_101.py
python3 scripts/audit_analysis_coverage.py

# Cross-sample digitised-history scorecard
python3 scripts/sample_scorecard.py

# Geometry and source-node audits
python3 scripts/check_mesh_geometry.py
python3 scripts/check_source_nodes.py --deck path/to/deck.i

# Paper-parameter audit
python3 scripts/paper_parameter_audit.py
```

For the 97/98 and corrected 101 calculations, values were sampled at the hold times written into the decks.
Cyclic retention compares equal-pressure 8 MPa states. Shut-in “near ambient” is defined as within
1% of the peak-to-ambient pressure excursion. Ratios use the model's reported hydraulic aperture,
permeability, and validation-flow channels without refitting.

---

## 18. Final statement

The strongest result is not that one constitutive law matches four plots. It is that a consistent
audit-and-score workflow separated four kinds of discrepancy that initially looked alike:
reporting errors, data-reduction errors, identifiable parameter errors, and genuine model-form
limits. After those separations, BBFast reproduces the monotonic benchmark substantially better
than a matched Mohr-Coulomb baseline; repeated cycling mostly saturates where it completes; and
shut-in produces no delayed reactivation in the valid controls. Those negative and comparative results define the next
model more sharply than another marginal improvement to the calibrated score would. Within the
targeted 99/100-series, the SW-T1 closure-capacity and SW-T2 aperture-scale changes are material
improvements; the latter is identified only to the `0.0175–0.0177` bracket. SW-S3 remains an
unresolved narrow tradeoff. The SW-S4 monotonic negative result closes the proposed scalar
weakening/viscosity adjustment, while its four 101-series discussion runs remain qualified by
their failed pre-injection falsifier.
