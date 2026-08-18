# Manuscript draft — JGR: Solid Earth

**Working title:** Injection-Induced Shear Slip and Permeability Enhancement in Granite
Fractures: A Cohesive-Zone Hydromechanical Model Validated Across a Roughness Range

**Status:** original draft 2026-08-07, revised 2026-08-11, audited against the source PDF
2026-08-16, **findings applied to the model 2026-08-16 (branch `orca_v5`)**.

The audit pass compared every physical property in the decks, meshes and this draft against
Ye & Ghassemi (2018) directly, and inserted `[bracketed]` correction notes wherever the draft
asserted something the setup did not support. Those findings have now been acted on. Three of the
four are **resolved in the model**; one remains a drafting decision:

| audit finding | status |
|---|---|
| SW-S4 meshed at 28.99° and 2.85 mm off centre; SW-T2 at 31° against its own data's 30° | **fixed** — corrected meshes ported; decks `89_01`, `89_03`, `89_05`, `89_06` |
| SW-S3/SW-S4 JRC, JCS and φ_r invented rather than measured | **fixed** — refitted to the paper's Table 1 and Sec. 2.1; decks `89_01`, `89_02` |
| SW-T1/SW-T2 need φ_r = 44–46°, above any granite basic friction angle | **fixed** — `cohesion`/`residual_cohesion` added to the law; decks `89_04`, `89_05` |
| §1/§3.5.3 claim a dissipation bound the *validated* law does not implement | **fixed** — §1, §3.5.3, §6.5 and conclusion 6 now scope the bound to the Mohr–Coulomb formulation, and claim it only as an admissibility diagnostic on the published data |

**§5 now reports the 93-series runs.** The scores quoted in §5.2 are the completed mesh-5
Barton–Bandis runs `93_01`, `93_03`, `93_05` and `93_07`, scored by
`scripts/table2_gate.py` with an independent recomputation, and cross-checked in
`Examples/YeGhasemmi2018/HPC_90_91_92_TABLE2_ERROR_ANALYSIS.md`. What remains outstanding is
§5.5 and §6.3 (the four Mohr–Coulomb runs, built and smoke-tested, queued), §6.6 and §6.7 (the
cyclic and shut-in runs, likewise), and the post-slip branch of the mesh-convergence comparison.

Working and derivations: `doc/paper_vs_model_audit_2026-08-16.md`;
`scripts/paper_parameter_audit.py` (states the problem);
`scripts/refit_joint_constants_from_paper.py` (derives every new constant);
`scripts/build_paper_corrected_decks.py` (generates the decks);
`Examples/YeGhasemmi2018/MESHES.md` (mesh provenance).

Revised 2026-08-18 against the current source and the four validated decks. That revision corrected
six places where the stated formulation did not match the code that produced the results — the
normal-closure exponent (§3.4), the hydraulic-aperture law and its per-specimen term activation
(§3.6), the reason the Barton–Bandis–Bakhtar closed form was not adopted (§3.6), the scope of the
dissipation bound (§3.5.3), the envelope-discriminability premise (§3.5.2), and the fracture
pressure–area coefficient, which is a fitted constant rather than the state-dependent function an
earlier draft described (§3.6.1). It also wrote §5 from the completed runs and retired a
long-standing §6.4 discrepancy that turned out to be a reporting-frame error. Full audit:
`doc/DOC_AUDIT_2026-08-18.md`.

The Methodology (§3–§4) is written to submission standard. Every number in this document that is
not yet measured is marked `[PENDING]`; nothing is invented.

---

# PART 0 — EDITORIAL PLAN

*Not part of the manuscript. Delete before submission.*

## 0.1 Section list, with rationale

| § | Section | Why it belongs |
|---|---|---|
| — | Key Points (3 × ≤140 char) | AGU requirement. One for the model, one for the discriminating result, one for the honest limitation. |
| — | Abstract (≤250 words) | AGU requirement. |
| — | Plain Language Summary (≤200 words) | AGU requirement, and reviewers do read it. |
| 1 | Introduction | Frames injection-induced slip as the coupled problem it is, and states what a *validation* paper has to demonstrate that a *model* paper does not. |
| 2 | The benchmark experiment | Ye & Ghassemi (2018) in enough detail that the setup in §4 is checkable, plus what the published data does and does not constrain. This section is where the double-counting argument goes, and where §2.3 establishes the tensile/saw-cut hierarchy that organises §5. |
| 3 | Model formulation | The physics and the discretisation. Complete, because a validation claim is worthless if the reader cannot tell what was validated. Sub-sections 3.5 (plasticity: yield, flow rule, the dissipation bound, kinematic routing, softening stability), 3.7 (what each characteristic slip distance controls), 3.8 (admissible vs inadmissible limiters) and 3.9 (numerical implementation) carry the methodological novelty and should not be cut for length — they are what distinguishes this from an application note. **Barton–Bandis is the model** (full derivation, §3.5.2); linear Mohr–Coulomb is stated in one short paragraph as the *baseline* it is compared against in §5, not derived as a coequal candidate. |
| 4 | Model setup and parameter determination | Geometry, BCs, and — critically — the table separating *measured*, *derived* and *calibrated* parameters. This is the section a sceptical reviewer will read first. |
| 5 | Results | Verification first, then validation of BBFast against all four specimens, then the MC baseline comparison (§5.5) showing what the nonlinear envelope buys. |
| 6 | Discussion | Three substantive strands, in order: (i) §6.3, whether the Barton–Bandis law outperforms the Mohr–Coulomb baseline under a matched calibration; (ii) §6.6, how much permeability enhancement survives the first of three injection cycles, and whether the law contains a mechanism for multi-cycle gain at all; (iii) §6.7, whether slip continues after shut-in. Around them: §6.1–6.2 on what the published data can and cannot constrain, §6.4–6.5 on what SW-S4 and the plasticity formulation reveal, then limitations and field-scale implications. §6.6 is written to be publishable on a negative result: the admissible outcomes and what each would mean are stated before the runs (§6.6.4–6.6.5), so a saturating result is a bounded statement about missing physics rather than an absence of findings. |
| 7 | Conclusions | Short, numbered, no new material. |
| A | Appendix A: recovering fracture orientation and load-frame compliance from the published table | The derivation is a genuine methodological contribution and is too long for §4. |
| B | Appendix B: measuring flow rate in a split-node interface formulation | A trap other MOOSE/FEM users will fall into; worth the page. |
| C | Appendix C: comparing the meshed fracture with a tomographic reconstruction | Pre-empts the "why is a rough fracture a plane?" question with a quantitative bound and a stated protocol, and says plainly that no CT data were available. Could go to supporting information if space is tight. |
| — | Open Research / Data Availability | AGU requirement. Must name the archived repository and DOI. |
| — | Notation table | Recommended; this paper carries two different effective-stress coefficients and two different apertures. |

## 0.2 What must **not** be included, and why

1. **Fracture permeability as a separate validation target.** The paper reports both $a_h$ and
   $k$, but $k = a_h^2/12$ by definition and $a_h$ is itself back-computed from the measured $Q$
   through the cubic law. Scoring the model against $Q$, $a_h$ *and* $k$ presents one measurement
   three times. The independent observables are five: $Q$, $\sigma'_n$, $\tau$, $d_n$, $d_s$.
   State this explicitly in §2 — a reviewer who spots it unaided will not be generous.
2. **The cubic-law diagnostic presented as a simulated flow rate.** Evaluating
   $Q = (W/L)\,a_h^3\Delta P/12\mu_f$ on the model's own aperture and comparing it to the
   published $Q$ is circular: it is the relation the published $a_h$ was inverted from. Report
   the solved flux. Keep the cubic-law value only as a labelled diagnostic, if at all.
3. **Per-sample fitted loading-frame stiffness.** Four samples ran on one machine. Presenting
   four fitted machine stiffnesses spanning 32× invites the obvious objection. Appendix A shows
   the quantity the experiment actually constrains is the *series* compliance, and that the
   machine term is not separately identifiable for the smooth samples. Say that instead.
4. **Constitutive laws that are not exercised.** The code implements four interface laws. Only
   Barton–Bandis is exercised as the model; describing the other three is model-paper material
   and dilutes a validation claim. Linear Mohr–Coulomb is the sole exception, and only as a
   **baseline**: state its equation in one paragraph (§3.5.2), no derivation of its own flow rule
   or dilation coupling, and use it in §5 solely to show what BBFast's nonlinear envelope buys
   you. It is not a coequal candidate being discriminated against BBFast — say so explicitly the
   first time both appear together, so a reviewer doesn't read §5.5 as a two-model comparison
   paper in disguise.
5. **Calibration history.** Deck lineages, parameter sweeps and abandoned variants belong in the
   archived repository, not the manuscript.
6. **Aperture agreement quoted tighter than ~7 %.** The published $a_h$ carries a systematic of
   that size from an ambiguity in how the flow path length $L$ was measured (Appendix A.4).
   Quoting 2 % agreement on a quantity with a 7 % systematic is not a stronger result; it is a
   weaker one, because it invites the question.
7. **Any claim of predictive capability.** Parameters were determined with knowledge of the
   outcome. This is a validation study, not a blind prediction, and §6 should say so in one
   sentence rather than let a reviewer say it.

## 0.3 Figures and tables (proposed)

| # | Content | Notes |
|---|---|---|
| F1 | Experimental configuration + model domain, side by side | Include the compliant-frame spring schematic; it matters in §4.2. |
| F2 | Yield surface in the $(\sigma'_n, \tau)$ plane, Barton–Bandis with the linear MC baseline overlaid for reference, injection stress path overlaid, four specimens' stress ranges marked | Shows visually why a nonlinear envelope is needed across these stress ranges — MC appears only as the dashed reference it fails to match. |
| F2b | Dilation: nominal $\tan\psi$ against realised $\Delta g_n^{p}/\Delta\gamma$, with the bound $(1-\epsilon_D)\mu$ drawn | One panel that shows which calibrations are saturated at the limiter. Cheap, and it pre-empts the reviewer question in §6.5. |
| F3 | 2×4 panel: $\sigma_d$, $\tau$, $\sigma'_n$, $d_s$, $d_n$, $a_h$, $Q$, $P_i$ vs time — one column per sample | The main validation figure, BBFast only. |
| F4 | Slip onset: BBFast simulated vs the paper's last-stick/first-slip window, all samples, with MC's onset shown as a baseline error bar | BBFast is the result; MC quantifies what the baseline misses. |
| F5 | Aperture and flow: simulated vs published, with the geometry-factor correction shown | Where the honest disagreement lives. |
| T1 | Specimen properties and test conditions | From Ye & Ghassemi Table 1. |
| T2 | Discretised fracture area against the exact ellipse, both meshes | Geometric verification; costs no simulation time and answers the meshing question before it is asked. |
| T3 | Surface area omitted by the planar interface, estimated from JRC | The quantitative form of the saw-cut/tensile hierarchy. Labelled an estimate, not a measurement. |
| T4 | Model parameters classified measured / derived / calibrated | **The most important table in the paper.** |
| T5 | Quantitative agreement per sample per observable, BBFast, with MC baseline column | RMS and peak error; MC column exists to be beaten, not analysed in its own right. |
| F6 | Cyclic: $P_i$, $d_s$, $d_n$, $a_h$ against time over three cycles, one row per specimen, with the three floor holds marked | The floor-to-floor comparison of §6.6 read straight off the figure. |
| T6 | Mohr–Coulomb baseline scores, five observables, four specimens | The comparison of §6.3; pairs with F2. |
| T7 | The three-cycle injection schedules | Design of §6.6.1. Fold into the text if space is tight. |
| T8 | Measured cycle-1 retention, from Ye & Ghassemi Table 2 stages 1 and 11 | The anchor for §6.6 — first-cycle enhancement is *already measured*, and is zero on SW-S4. |
| T9 | The four slip-history channels as calibrated, per specimen | Shows two of the four channels are inert on most specimens. **Keep**: it is what makes the cyclic prediction specimen-specific rather than generic. |
| T10 | Exhaustion of each channel at the end of cycle 1 | Arithmetic on calibrated parameters, stated before the runs — the pre-registration of §6.6. |
| T11 | Barton block-size corrections evaluated at 1, 10, 100 m | Bounds the field-scale extrapolation (§6.9.1). Must be labelled *not used in any run reported here*. |
| T12 | Verification results (mesh convergence, mass balance, preload gate) | Can go to supporting information if space is tight. |

## 0.4 Drafting cautions specific to this study

- Two effective-stress coefficients appear: $\alpha \approx 0.6$ for the matrix, constant, and a
  state-dependent $\alpha_f(\sigma'_n) \in (0,1)$ for the fracture (§3.6.1) that reduces to the
  historically-assumed unit coupling only in the open, unstressed limit. Define both at first use
  and never write "the Biot coefficient" unqualified, and never call $\alpha_f$ "exactly 1" — that
  was the pre-2026-08 assumption this revision replaces.
- Two apertures appear: mechanical $a_m$ and hydraulic $a_h$. Same rule.
- SW-S4 is qualitatively different from the other three (slip begins two stages earlier and grows
  progressively rather than in a burst). Resist smoothing this over; it is the most informative
  sample.
- The angle for SW-T2 given in the paper's Table 1 (31°) disagrees with the value implied by its
  own Table 2 (30°). Appendix A resolves this. Flag it once, politely, and move on. **Resolved in
  the setup on 2026-08-16: SW-T2 and SW-S4 are both meshed at 30° and centred, verified by fitting
  a plane to the meshed interface rather than by trusting the journal. Appendix A resolving
  something on paper is not the same as the runs honouring it, and this was the one inconsistency
  that would have embarrassed the paper's central claim.**
- ~~Two of the four specimens report $\sigma'_n$ through different operators.~~ **Fixed
  2026-08-16.** SW-S4 was the only specimen without a paper-frame postprocessor: it compared a raw
  fault-averaged interface traction against a Table 2 column that had been reduced through eq (3)
  with $P_p = \tfrac12(P_i+P_o)$, while its three siblings compared like with like. The 89-series
  SW-S4 decks carry `effective_normal_paper_frame_mpa_pp` and `shear_stress_paper_frame_mpa_pp`
  with $\sin^2\theta = 0.25$ and $\sin\theta\cos\theta = 0.4330$ at the corrected 30°. Any §5 score
  quoted from a 68-series run is on the old operator and must be regenerated.
  Those are not the same quantity, and it is the likely reason SW-S4 alone needs a
  fault-pressure coefficient of 0.86. Either give SW-S4 the paper-frame postprocessor or say in
  §5.3 which operator each specimen's $\sigma'_n$ score uses — do not present them in one table as
  though they were comparable.
- **Naming collision to fix in copy-editing:** "Table 2" currently refers both to Ye and Ghassemi's
  data table (≈15 occurrences) and, until this revision, to our own parameter table. Our tables are
  now T1–T6; every reference to the source data must read "Ye and Ghassemi's Table 2" explicitly.
- Three words are used for fracture area and they are not interchangeable: *projected* (what the
  mesh carries), *true* (the rough surface), and *contact* (a state variable). §4.1.2 and Appendix
  C depend on the distinction; do not let it blur in editing.

---

# PART 1 — MANUSCRIPT

## Key Points

`[NOTE: AGU wants exactly 3 (≤140 char each) — this now lists 4 since adding the MC-baseline point;
trim before submission, likely by folding the new #3 into #1 or dropping the flow-rate point to
Results-only.]`

1. A cohesive-zone hydromechanical model with a Barton–Bandis interface law reproduces
   injection-induced shear slip in four granite fractures to 2.4–6.1 % normalised RMS error
2. The published data over-determines fracture orientation and load-frame compliance, allowing
   calibration without free geometric parameters
3. A linear Mohr–Coulomb baseline is compared under a matched calibration procedure
   `[PENDING: state the outcome once §5.5 numbers are in]`
4. Simulated flow is about half the reported rate at matching aperture, a geometry-factor
   difference rather than a constitutive error

---

## Abstract

*(target ≤250 words; current draft 238)*

Fluid injection reduces the effective normal stress on a pre-existing fracture, drives shear
slip, and enhances permeability through dilation. Reproducing that sequence quantitatively
requires a model in which mechanical and hydraulic responses are solved together, because
aperture couples them in both directions. We present a three-dimensional finite-element
hydromechanical model in which the fracture is represented as a zero-thickness cohesive
interface embedded in a Biot poroelastic matrix, and validate it against the laboratory
experiments of Ye and Ghassemi (2018) on four Sierra White granite cores. The four specimens
span a wide roughness range — two tensile fractures and two saw cuts, with joint roughness
coefficients from 1.96 to 15.32 — and each was subjected to an eleven-stage injection cycle
under 30 MPa confinement at constant piston displacement. We show that the published data
over-determines two quantities usually treated as free: the fracture orientation and the series
compliance of the loading column are both recoverable from the tabulated stress and displacement
histories alone, to within 0.03° and 3 % respectively. This removes the geometric parameters from
the calibration and makes the remaining comparison a test of the interface constitutive law. The
model reproduces the eleven-stage flow, stress and displacement histories to a mean normalised RMS
error of 2.4 % to 6.1 % across five independent observables. We compare a linear Mohr–Coulomb
envelope with a Barton–Bandis envelope under a matched calibration procedure `[PENDING]`, and show
that this loading path cannot separate cohesion from joint roughness, so the two must be reported as
one constrained combination. Simulated flow rates fall consistently below the reported values at
matching hydraulic aperture; we show this reflects the difference between a one-dimensional slab
reduction and the three-dimensional flow field, and quantify it.

---

## Plain Language Summary

*(target ≤200 words; current draft 176)*

Pumping fluid into deep rock can make existing cracks slip. This matters for geothermal energy,
where slip opens cracks and lets water circulate, and for the small earthquakes that sometimes
follow injection. Predicting it is difficult because the rock and the fluid affect each other:
pressure pushes the crack faces apart, which lets more fluid through, which changes the pressure
again.

We built a computer model that solves both effects together, and tested it against a laboratory
experiment in which four granite cylinders, each containing a single crack, were squeezed and
then injected with water in steps. Two of the cracks were rough natural breaks and two were
smooth saw cuts, which lets us check whether one model works across very different surfaces.

We also found that the published laboratory table contains more information than was previously
used. The angle of each crack and the stiffness of the testing machine can both be recovered
from the measurements themselves, rather than being adjusted to fit. That makes the comparison
between model and experiment more honest, because fewer quantities are free to be tuned.

---

## 1. Introduction

Injection-induced shear slip on pre-existing fractures is central to two problems that are
usually studied separately. In enhanced geothermal systems it is the intended mechanism of
permeability creation: shear displacement on a rough surface produces dilation, dilation
increases the hydraulic aperture, and because transmissivity scales with the cube of aperture,
a small displacement can raise flow by orders of magnitude (Barton et al., 1985; Willis-Richards
et al., 1996). In induced seismicity it is the mechanism to be avoided, or at least bounded
(Ellsworth, 2013; Grigoli et al., 2018). The two framings share a physical core: pore pressure
reduces the effective normal stress, frictional strength falls with it, and slip begins when the
resolved shear traction reaches the strength.

What makes the problem genuinely coupled, rather than a sequence of one-way effects, is that the
aperture appears on both sides. Mechanics sets the aperture; the aperture sets the
transmissivity; the transmissivity sets how fast pressure propagates and therefore how fast the
effective stress falls; and the resulting slip changes the aperture again. Models that solve the
two directions sequentially, or that prescribe an aperture evolution rather than solving for it,
cannot represent this feedback faithfully. Fully coupled formulations exist — using embedded
discontinuities (Garipov et al., 2016), discrete-fracture networks (McClure & Horne, 2011),
phase-field approaches (Wilson & Landis, 2016), and cohesive-zone interfaces (Ucar et al., 2018;
Jha & Juanes, 2014) — but validation against controlled laboratory data remains sparse relative
to the number of formulations proposed.

Validation is a stricter requirement than agreement. A model with enough adjustable parameters
will match almost any single experiment, and matching a single experiment therefore demonstrates
little. Three things distinguish a validation study. First, the parameters must be classified:
which were measured independently, which follow from the data by derivation, and which were
adjusted. Second, the number of genuinely independent observables must be stated, because
reported quantities are often related by definition and scoring against all of them
double-counts. Third, the disagreements must be reported with the agreements, and attributed.

This paper sets out to meet those three requirements against the experiments of Ye and Ghassemi
(2018), which are unusually well suited to the purpose. Their four Sierra White granite specimens
span joint roughness coefficients from 1.19 to 15.32 — from a polished saw cut to a rough tensile
fracture — under an identical loading and injection protocol. A model calibrated on one specimen
must therefore work on the others without re-tuning the constitutive form, and the roughness
range is wide enough to discriminate between a linear Mohr–Coulomb strength envelope and a
pressure-dependent Barton–Bandis envelope, which can be made tangent at one effective normal
stress but diverge elsewhere.

We make four contributions.

1. **A cohesive-zone hydromechanical formulation with a thermodynamically bounded,
   kinematically routed dilation.** The fracture is a zero-thickness interface carrying its own
   Reynolds-equation flow, embedded in a Biot poroelastic matrix, with contact, friction, dilation
   and closure solved by a local return map that supplies an exact consistent tangent (§3). Two
   elements distinguish it from the non-associative interface plasticity in common use. The
   dilation is constrained by an explicit dissipation inequality,
   $\tan\psi \leq (1-\epsilon_D)\mu$, evaluated against the *Coulomb* strength rather than the
   regularised branch traction. In the Mohr–Coulomb formulation this bound is enforced, and it is
   frequently the active constraint, so that a nominal dilation angle above it is never realised
   and should not be reported as calibrated. Applied instead as an *admissibility diagnostic* to
   the published measurements, the same inequality shows that both saw-cut specimens report a
   dilation angle exceeding their own mobilised friction angle — which no amount of shear dilation
   can produce, and which identifies elastic joint decompression inside the LVDT signal (§3.5.3).
   The dilation is routed kinematically as a normal eigen-opening rather than as a
   contact-stress reduction, which reverses the sign of its feedback on strength and produces a
   normal displacement jump directly comparable with an LVDT measurement (§3.5.4).
2. **An explicit account of what each characteristic slip distance controls, and of which
   limiters are admissible.** Every history-dependent term carries its own distance; we tabulate
   what each governs, which observable identifies it, and how it fails at either extreme (§3.7).
   We also draw a line between limiters that express physics and limiters that express numerical
   convenience, and refuse the latter: per-step increment caps on slip and dilation are rejected
   at input parsing, on the evidence that in one calibration the slip cap bound on 14 time steps
   and supplied about 30 % of the total accumulated slip — a numerical parameter setting a
   physical result (§3.8).
3. **A demonstration that the published data over-determines the fracture orientation and the
   series compliance of the loading column.** Both follow from the tabulated stress and
   displacement histories without adjustment, to 0.03° and 3 % respectively (Appendix A). This
   removes two parameters from the calibration, resolves a discrepancy in the published specimen
   table, and — through the softening-stability criterion of §3.5.5 — ties the admissible
   constitutive softening rate to a measured rather than a fitted machine property.
4. **An attributed account of where the model disagrees.** Simulated flow falls near half the
   reported rate at matching aperture; we show this is a flow-geometry difference between the
   one-dimensional slab used to reduce the data and the three-dimensional field the model solves,
   and not a constitutive error (§5.4, Appendix B).

---

## 2. The Benchmark Experiment

### 2.1 Configuration

Ye and Ghassemi (2018) tested four cylindrical Sierra White granite specimens, each containing a
single through-going fracture inclined to the core axis. Two fractures were created in tension
and two by saw cutting, one of the latter subsequently polished, giving joint roughness
coefficients from 1.19 to 15.32 (Table 1). Each specimen was loaded triaxially to a confining
pressure $\sigma_3 = 30$ MPa and an axial stress sufficient to bring the fracture close to but
below its frictional strength. Fluid was then injected through a borehole intersecting the
fracture on one side and produced from a matching borehole on the other, with the production
pressure held at $P_o = 5$ MPa.

The injection pressure was raised in five steps from 8 to 28 MPa and then lowered in five steps
back to 8 MPa, giving eleven hold stages. At each hold the flow rate, differential stress, shear
displacement and normal displacement were recorded. The axial piston was held at constant
displacement throughout, so the axial stress was free to fall as the fracture slipped — the
feature that makes the experiment a test of the coupled system rather than of the fracture alone.

**Table 1.** Specimen properties and test conditions. *(from Ye & Ghassemi, 2018, Table 1;
$\theta$ column as revised in Appendix A)*

| Specimen | Surface | JRC | $\theta$ (published) | $\theta$ (Appendix A) | Length (mm) | Diameter (mm) |
|---|---|---|---|---|---|---|
| SW-T1 | tensile fracture | 15.32 | 32° | 32.00° | 128.8 | 50.52 |
| SW-T2 | tensile fracture | 14.63 | 31° | **30.00°** | 132.7 | 50.52 |
| SW-S3 | saw cut | 1.96 | 29° | 29.03° | 123.4 | 50.53 |
| SW-S4 | polished saw cut | 1.19 | 30° | 30.02° | 118.7 | 50.51 |

`[SETUP CAVEAT — RESOLVED 2026-08-16. The θ column headed "Appendix A" is the value the`
`published stress data was reduced at, and it is the value the model must be built at.`
`Two of the four meshes were not: SW-T2 was cut at the printed 31°, and SW-S4 at 28.99°`
`— its journal had inherited SW-S3's fracture plane verbatim (bit-identical z-span),`
`which also left it 2.85 mm off centre. Corrected meshes are now in the repository the`
`production decks run from, and the angle in each .e file was re-derived here by fitting`
`a plane to the nodes shared by the two element blocks rather than trusting the journal.`
`All four specimens now honour their Appendix-A angle, so the claim in §1 and the`
`Abstract that the geometry is recovered rather than fitted is no longer contradicted by`
`the setup. Inventory: Examples/YeGhasemmi2018/MESHES.md. The last outstanding item, the`
`SW-S3 mesh at 124.40 mm against Table 1's 123.40 mm, was closed when that mesh was`
`rebuilt on 2026-08-16; every deck from the 90-series onward, including the SW-S3 final`
`92_03 that Table 5 reports, runs on it. Re-measured directly from the four .e files`
`used by the production decks: length 128.80 / 132.70 / 123.40 / 118.70 mm and diameter`
`50.52 / 50.52 / 50.53 / 50.51 mm, each equal to its Table 1 entry to the quoted`
`precision, and fracture angles of 32.000° / 30.000° / 29.000° / 30.000° against the`
`Appendix-A values 32.00 / 30.00 / 29.03 / 30.02°. No specimen dimension or orientation`
`in the model now differs from the published one by more than 0.03°.]`

### 2.2 What the published data constrains

The paper's Table 2 reports, for each specimen and each of the eleven hold stages: injection
pressure, flow rate $Q$, normal displacement $d_n$, shear displacement $d_s$, effective normal
stress $\sigma'_n$, shear stress $\tau$, hydraulic aperture $a_h$, and fracture permeability $k$.

Two of these eight are not independent measurements. The permeability is defined as
$k = a_h^2/12$, and the hydraulic aperture is not measured directly but back-computed from the
measured flow rate through the cubic law,

$$
a_h = \left( \frac{12\,\mu_f\,L\,Q}{W\,\Delta P} \right)^{1/3},
$$

where $W$ and $L$ are the width and length of a rectangle of equal area to the elliptical
fracture, and $\Delta P = P_i - P_o$. Consequently $k \propto Q^{2/3}$ and carries no information
beyond $Q$. **The independent observables are five, not eight**: $Q$, $\sigma'_n$, $\tau$, $d_n$
and $d_s$. We score the model against those five only.

A third quantity, $\sigma'_n$, is itself a reduction rather than a direct measurement. The
authors resolve the applied stresses onto the fracture plane using

$$
\sigma'_n = (\sigma_3 - P_p) + \sigma_d \sin^2\theta, \qquad
\tau = \sigma_d \sin\theta\cos\theta, \qquad
P_p = \tfrac{1}{2}(P_i + P_o),
$$

with $\sigma_d = \sigma_1 - \sigma_3$ the differential stress. The assumption $P_p =
\frac{1}{2}(P_i + P_o)$ — that the mean fracture pressure is the arithmetic mean of the two
borehole pressures — is a modelling choice on the authors' part, not a measurement, and §5.3
examines how well it survives once the fracture dilates.

### 2.3 How the fractures were made, and what each kind isolates

The four specimens are not four replicates of one experiment. They span two of the three ways a
laboratory fracture is created, and the choice is the reason the dataset can separate mechanisms
that are ordinarily measured together. Because the distinction governs which submodels each
specimen exercises, we set it out before the model is introduced.

**Tensile (Mode I) fractures — SW-T1 and SW-T2.** The core is split in tension, so the two surfaces
are *conjugate*: every asperity on one face has the void that produced it on the other, because an
instant earlier they were one continuous solid. Three consequences follow.

1. *The surfaces are perfectly mated at zero shear offset.* Contact is distributed over nearly the
   whole nominal area, the mechanical aperture is close to zero, and the initial normal stiffness is
   correspondingly high. This is why SW-T1's pre-slip joint is an order of magnitude stiffer than
   its post-slip joint (§5.4), and why a single Barton–Bandis closure curve fits one branch or the
   other but not both.
2. *Roughness is set by the rock, not by the operator.* In Sierra White granite the crack follows
   grain boundaries, so the asperity wavelength is the grain size and JRC comes out high — 15.32 and
   14.63 here, near the top of the Barton scale.
3. *Any shear offset destroys the mating.* Asperities must ride over one another, so slip is
   strongly dilatant and permeability rises steeply; but the same asperity contacts are also being
   damaged, producing gouge that fills the void and pushes permeability back down. Dilatancy,
   comminution and frictional resistance evolve together and cannot be separated from a single
   test.

A fourth property matters specifically for a validation study: a tensile fracture is only
*approximately* planar, and it goes where the rock sends it. Its inclination θ must be measured
after the fact, and it is the largest single uncertainty in reducing the data, because θ enters the
resolved stresses through $\sin^2\theta$ and $\sin\theta\cos\theta$ (§2.2). Appendix A shows the
published θ for SW-T2 to be inconsistent with the specimen's own stress data by one degree.

**Saw-cut fractures — SW-S3 and SW-S4.** The core is cut through with a diamond saw at a prescribed
inclination and the two halves are reassembled; SW-S4 was additionally lapped. The surfaces are
therefore *not* conjugate — each was generated independently by the saw, and they meet on the
highest points of two nominally flat planes. This inverts every property above.

1. *The geometry is manufactured, not measured.* The inclination is a machining setting, the plane
   is genuinely planar, and both are known a priori. The dominant uncertainty in the stress
   reduction is removed rather than estimated.
2. *Roughness is minimal and, after lapping, nearly absent:* JRC 1.96 and 1.19. Shear dilatancy is
   correspondingly small, and asperity damage during slip is negligible, so slip is close to pure
   sliding.
3. *There is no interlock.* Strength is the intrinsic rock-on-rock friction, without the
   roughness term $\mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n)$ that dominates on the tensile
   specimens.

**Shear fractures**, the third kind, are produced by loading intact rock past its peak so that it
fails on its own plane. They are the closest laboratory analogue to a natural fault, and for that
reason the least suitable here: the orientation is chosen by the rock rather than by the
experimenter, and the plane arrives with a layer of comminuted gouge that is a third phase with its
own porosity, compaction law and permeability. Ye and Ghassemi use none, and the present study
does not model gouge.

#### 2.3.1 The events the saw cuts separate

Injection at constant confining stress and constant piston displacement sets off at least five
processes at once:

| | process | effect on aperture |
|---|---|---|
| (i) | pore pressure rises, $\sigma'_n$ falls | — |
| (ii) | the joint elastically decompresses and opens | **increase**, no slip required |
| (iii) | shear stress reaches the strength envelope and the fracture slips | — |
| (iv) | slip on a rough surface forces the walls apart (dilation) | **increase** |
| (v) | slip grinds the contacting asperities (damage, gouge) | **decrease** |

Processes (ii) and (iv) both raise permeability, and (v) opposes them. In a rough tensile fracture
all three run simultaneously, and a measured permeability rise cannot be assigned among them from
the flow record alone. This is the identifiability problem that makes single-specimen studies of
injection-induced permeability enhancement difficult to interpret.

The saw cut resolves it by construction. With JRC ≈ 1 there is almost no dilation and almost no
asperity damage, so (iv) and (v) are suppressed and the aperture change during the loading half of
the schedule is attributable to (ii) alone. The unloading half then closes the argument: pressure is
returned to 8 MPa, (ii) reverses elastically, and whatever aperture *does not* recover is the
permanent, slip-induced part. Comparing that residual between SW-S3 (JRC 1.96) and SW-S4 (JRC 1.19)
isolates the roughness dependence of the permanent enhancement at otherwise matched conditions.

The saw cuts also make the *strength* measurement a one-parameter measurement. A reassembled saw cut
has no cohesion and no tensile strength, so its failure envelope is a friction line through the
origin and the onset of slip determines a single number, μ. On a tensile fracture the same onset
confounds μ with interlock and with the stress-dependent roughness term, so onset alone cannot
calibrate the envelope.

#### 2.3.2 A saw cut is a manufactured discontinuity, not a damaged continuum

The distinction is not merely descriptive; it changes what a cohesive-zone model has to represent,
and it is worth stating plainly because it is the main reason SW-S3 and SW-S4 carry more weight in
this study than their unremarkable data would suggest.

For SW-S3 and SW-S4 the specimen is two rock halves with a pre-existing plane between them. The
discontinuity is present at $t = 0$ with known geometry, zero cohesion and zero tensile strength.
Nothing has to break, so:

- **No decohesion or softening branch is exercised.** The cohesive-zone law degenerates to
  unilateral contact plus friction. The loss of solution uniqueness that accompanies softening
  (§3.5.5) cannot occur, so it is excluded as an explanation for anything observed on these two
  specimens — including the convergence behaviour discussed in §5.1.
- **The initial state is defined rather than inferred.** It is contact under $\sigma'_n$ with an
  aperture fixed by the normal-closure law, not a state of partial damage that must itself be
  calibrated.
- **The initial aperture is a manufacturing quantity** — saw-mark amplitude, modified by lapping —
  and it is constrained independently by the initial permeability, before any of the mechanical
  parameters are involved.
- **The meshed interface is the object itself, not an idealisation of one.** §4.1 shows that the
  planar elliptical interface reproduces the true fracture area of the saw-cut specimens to better
  than one per cent, where for the tensile specimens the unrepresented surface area is four per
  cent.

The tensile specimens, by contrast, require the full law: a rough surface with a curved,
stress-dependent envelope, strong dilatancy under a dissipation bound, and a normal-closure response
that changes character once mating is lost. The two pairs therefore form a hierarchy rather than a
set of repeats — SW-S3 and SW-S4 test contact, friction and flow with the fewest free parameters and
the most exactly represented geometry; SW-T1 and SW-T2 add roughness, dilatancy and damage on top of
an already-validated base. We report them in that order in §5.

### 2.4 Why these four specimens are a useful test

SW-S4 behaves qualitatively differently from the other three, and this is the most informative
feature of the dataset. In SW-T1, SW-T2 and SW-S3 the shear displacement is negligible through
the first five hold stages and then jumps by two orders of magnitude at the 28 MPa stage: a
sharp, essentially unstable slip event. In SW-S4 slip begins at the 20 MPa stage and grows
progressively, reaching its final value without a distinct burst. The differential stress falls
correspondingly early and smoothly.

A model that reproduces the three burst specimens but not the progressive one has not
demonstrated that its strength envelope is right; it has demonstrated that it can produce a
burst. The SW-S4 behaviour is the discriminating case.

---

## 3. Model Formulation

### 3.1 Overview

The model solves quasi-static Biot poroelasticity in the rock matrix, with the fracture
represented as a zero-thickness interface across which the displacement field is discontinuous.
Three interface contributions are assembled: the mechanical traction supplied by the constitutive
law, the fluid pressure acting normal to the two walls, and in-plane flow governed by a Reynolds
equation with a cubic-law transmissivity. Primary unknowns are the displacement vector
$\boldsymbol{u}$ and the pore pressure $p$, solved monolithically.

The implementation is built on the MOOSE finite-element framework (Permann et al., 2020), which
supplies the residual-based assembly, the parallel infrastructure and the forward-mode automatic
differentiation used to construct exact Jacobians.

### 3.2 Bulk poroelasticity

With $\boldsymbol{\sigma}$ the total Cauchy stress (tension positive), $\boldsymbol{\varepsilon}
= \frac{1}{2}(\nabla\boldsymbol{u} + \nabla\boldsymbol{u}^\mathsf{T})$ the small strain tensor and
$\varepsilon_v = \operatorname{tr}\boldsymbol{\varepsilon}$, the governing equations are

$$
\begin{aligned}
\nabla\cdot\boldsymbol{\sigma} &= \boldsymbol{0}, \\
\boldsymbol{\sigma} &= \mathbb{C}:\boldsymbol{\varepsilon} - \alpha\,p\,\boldsymbol{I}, \\
\frac{1}{M}\dot{p} + \alpha\,\dot{\varepsilon}_v + \nabla\cdot\boldsymbol{q} &= 0, \\
\boldsymbol{q} &= -\frac{\mathbf{k}}{\mu_f}\left(\nabla p - \rho_f\,\boldsymbol{g}\right),
\end{aligned}
$$

where $\mathbb{C}$ is the drained isotropic elasticity tensor, $\alpha$ the Biot coefficient,
$\mathbf{k}$ the intrinsic permeability tensor, $\mu_f$ the fluid dynamic viscosity, and $M$ the
Biot modulus,

$$
\frac{1}{M} = \frac{\alpha-\phi}{K_s} + \frac{\phi}{K_f}
            = \frac{(1-\alpha)(\alpha-\phi)}{K_d} + \frac{\phi}{K_f},
$$

with $\phi$ the porosity, $K_f$ the fluid bulk modulus, $K_s$ the solid grain bulk modulus and
$K_d$ the drained bulk modulus.

The same coefficient $\alpha$ must appear in the effective-stress relation and in the storage
term; the system is symmetric only if it does. Substituting the porosity for $\alpha$ in the mass
balance — a natural-looking substitution, since $\phi\rho_f$ is the fluid mass per unit volume —
changes the consolidation coefficient by the factor $\alpha/\phi$, which for the granite modelled
here is a factor of six hundred.

Taking test functions $\boldsymbol{\psi} = \psi_i \boldsymbol{e}_c$ and integrating by parts gives
the momentum residual for component $c$,

$$
R_i^{(c)} = \int_\Omega \left[ \boldsymbol{\sigma}^{\mathrm{eff}}_{c\bullet}\cdot\nabla\psi_i
   - \alpha\,p\,\partial_c\psi_i \right] \mathrm{d}\Omega,
$$

and the mass-balance residual

$$
R_i^{(p)} = \int_\Omega \left[ \rho_f\left(\frac{\dot{p}}{M} + \alpha\dot{\varepsilon}_v\right)\psi_i
   + \rho_f \frac{\mathbf{k}}{\mu_f}\nabla p \cdot \nabla\psi_i \right] \mathrm{d}\Omega .
$$

Both are multiplied by fluid density so that the assembled equation is a mass balance, and both
are tagged into an auxiliary residual vector so that nodal reactions — and hence injected and
produced mass fluxes — can be recovered exactly (Appendix B).

### 3.3 The fracture as a zero-thickness interface

The fracture is a surface $\Gamma$ across which $\boldsymbol{u}$ may be discontinuous. The mesh is
split along $\Gamma$ so that coincident node pairs exist on either side, and the displacement jump

$$
[\![\boldsymbol{u}]\!] = \boldsymbol{u}^{+} - \boldsymbol{u}^{-}
$$

is available pointwise. A local orthonormal frame $\boldsymbol{R} = [\boldsymbol{n},
\boldsymbol{s}_1, \boldsymbol{s}_2]$ is constructed at each quadrature point from the deformed
surface normal, and the jump is rotated into it,

$$
\boldsymbol{g} = \boldsymbol{R}^\mathsf{T} [\![\boldsymbol{u}]\!]
   = (g_n, g_{t1}, g_{t2}),
$$

so that $g_n$ is the normal opening (positive) or closure (negative) and $\boldsymbol{g}_t =
(g_{t1}, g_{t2})$ is the in-plane slip. The constitutive law is written entirely in this local
frame: it maps $\boldsymbol{g}$ and the stored state to a local traction $\boldsymbol{t}^{\rm loc}$,
which is rotated back, $\boldsymbol{t} = \boldsymbol{R}\,\boldsymbol{t}^{\rm loc}$, and assembled
with opposite sign on the two sides.

Choosing a zero-thickness interface rather than a thin equivalent-continuum layer avoids the
element-aspect-ratio problem that a physically thin layer creates, and keeps the aperture a
kinematic quantity rather than an inferred strain.

### 3.4 Unilateral contact and nonlinear normal closure

The two walls must not interpenetrate. With the contact pressure $p_c \geq 0$ (compression
positive, so the normal traction is $t_n = -p_c$), the exact statement is the Signorini system

$$
g_n \geq 0, \qquad p_c \geq 0, \qquad g_n\,p_c = 0 .
$$

This is regularised by a penalty, $p_c = k_n \langle -g_n \rangle_+$, with the non-smoothness at
$g_n = 0$ removed by a smooth transition of width $\epsilon_g$ so that Newton's method has a
continuous tangent through the contact/separation event.

A constant $k_n$ is not adequate here, because the experiment sweeps the effective normal stress
over a factor of four and the closure response of a real joint is strongly nonlinear. We use a
Bandis-type hyperbolic closure with a stress exponent,

$$
v(\sigma'_n) = \frac{v_m\,{\sigma'_n}^{\,p}}{\sigma_0^{\,p} + {\sigma'_n}^{\,p}}
\qquad\Longleftrightarrow\qquad
\sigma'_n(v) = \sigma_0 \left[\frac{v}{v_m - v}\right]^{1/p},
\qquad \sigma_0 = K_{ni}\,v_m ,
$$

evaluated on the pre-seated closure $v = \langle -g_n \rangle_+ + c_0$, where $v_m$ is the maximum
closure, $K_{ni}$ the initial normal stiffness, $\sigma_0$ the effective normal stress at which
half the maximum closure is reached, and $c_0$ a pre-seating offset representing the closure
already accumulated at the reference confining stress.

Setting $p = 1$ recovers the classical Bandis hyperbola $v = \sigma'_n/(K_{ni} + \sigma'_n/v_m)$
exactly. We do not use $p = 1$, and the exponent is the reason this form is adopted rather than the
hyperbola: the tangent normal stiffness scales as ${\sigma'_n}^{\,(p+1)}$ for
$\sigma'_n \gg \sigma_0$, so $p$ in the range 2–4 reproduces the three- to fourfold unloading
stiffening that Table 2's normal-displacement recovery requires and that the hyperbola cannot
produce at any $K_{ni}$. The calibrated values are $p = 4$ for SW-T1, SW-T2 and SW-S3, and $p = 2$
for SW-S4 (Table 4).

Two bounds keep the tangent finite. For $p > 1$ the exact tangent behaves as $v^{1/p-1}$ and is
singular as $v \to 0$, so below a linearisation closure of $\min(10^{-9}\ \mathrm{m},\,0.01\,v_m)$
the law is replaced by its secant; and the closure is capped at a fixed fraction of $v_m$, beyond
which the joint is treated as fully closed.

Pre-seating matters: without it, applying the 30 MPa confinement at the start of the simulation
would drive a large closure transient that the compliant loading frame would convert into a
spurious axial stress excursion.

An unloading hysteresis is available, in which a fraction $f$ of recovered closure is retained,
representing the fact that a joint which has slipped does not recover its original closure state
when re-clamped. Section 5.3 shows this is the controlling parameter for the post-slip stress
recovery.

The same power-law closure is available a second time inside the hydraulic-aperture model, as the
stress-aperture term of §3.6. It is enabled there for SW-T2, SW-S3 and SW-S4; SW-T1 instead runs a
linear stress-aperture compliance, so its hydraulic closure is linear while its mechanical closure
is not.

### 3.5 Interface elastoplasticity

#### 3.5.1 Kinematics and the elastic predictor

The tangential response is rate-independent elastoplasticity, formulated in the local frame of
§3.3. The tangential jump is decomposed additively into recoverable and plastic parts,

$$
\boldsymbol{g}_t = \boldsymbol{g}_t^{e} + \boldsymbol{g}_t^{p},
\qquad
\boldsymbol{t}_t = k_t\,\boldsymbol{g}_t^{e} = k_t\left(\boldsymbol{g}_t - \boldsymbol{g}_t^{p}\right),
$$

with $k_t$ the tangential penalty stiffness. A single scalar internal variable, the cumulative
plastic slip

$$
s = \int_0^t \lVert \dot{\boldsymbol{g}}_t^{p} \rVert \, \mathrm{d}\tau
$$

drives every history-dependent quantity in the law. Over a load increment the state is advanced by
an elastic predictor followed by a plastic corrector: the trial traction

$$
\boldsymbol{t}_t^{\rm trial} = k_t\left(\boldsymbol{g}_t^{n+1} - \boldsymbol{g}_t^{p,n}\right),
\qquad
\tau^{\rm trial} = \lVert \boldsymbol{t}_t^{\rm trial} \rVert
$$

is formed by freezing the plastic state, and the yield condition is tested there.

#### 3.5.2 Yield surface

Sliding begins when the shear traction magnitude reaches the strength,

$$
F(\boldsymbol{t}, \boldsymbol{q}) = \lVert \boldsymbol{t}_t \rVert - Y(\boldsymbol{q}) \leq 0,
\qquad
\Delta\gamma \geq 0,
\qquad
F\,\Delta\gamma = 0,
$$

the last two being the Kuhn–Tucker loading–unloading conditions, with $\Delta\gamma$ the plastic
multiplier and $\boldsymbol{q}$ the internal variables. In the traction plane
$(\sigma'_n, \tau)$ the surface is a cone opening to the right with half-angle $\arctan\mu$ and
apex at $\sigma'_n = -c/\mu$.

Two strength envelopes are compared.

*Linear Mohr–Coulomb with roughness-dependent parameters.*

$$
Y = c(\bar{R}) + \mu(\bar{R})\,\sigma'_n,
$$

where the friction coefficient and cohesion interpolate between rough and smooth end members
through a normalised roughness state $\bar{R} \in [0, 1]$:

$$
\mu(\bar{R}) = \mu_s + (\mu_r - \mu_s)\,\bar{R}^{\,m_\mu},
\qquad
c(\bar{R}) = c_s + (c_r - c_s)\,\bar{R}^{\,m_c},
\qquad
\bar{R} = \frac{R - R_r}{1 - R_r},
$$

with the raw roughness state decaying exponentially with slip,

$$
R(s) = R_r + (R_0 - R_r)\exp\!\left(-\frac{s}{L_R}\right).
$$

*Barton–Bandis.*

$$
Y = c(s) + \sigma'_n \tan\!\left[ \phi_r + \mathrm{JRC}\,\log_{10}\!\left(\frac{\mathrm{JCS}}{\sigma'_n}\right) \right],
\qquad
c(s) = c_{\text{res}} + (c - c_{\text{res}})\,W(s),
$$

with $\phi_r$ the residual friction angle, JRC the joint roughness coefficient, JCS the joint wall
compressive strength, and $W(s) = \exp[-(s/D_c)^m]$ the slip-weakening factor of §3.7. The
frictional part is concave in $\sigma'_n$: the mobilised friction angle *rises* as the effective
normal stress falls, because asperities override rather than shear through at low confinement.

The cohesion $c$ is not decoration and is not Barton's. Barton's roughness term is
**mobilisation-limited** — $\mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n) \to 0$ as
$\sigma'_n \to \mathrm{JCS}$ — which correctly encodes asperities shearing *through* rather than
overriding at high normal stress, but leaves the resulting strength with nowhere to go, because in
Barton's form every term is proportional to $\sigma'_n$. Asperity shear-through is a cohesion: it
is the strength of the rock bridges, and it does not scale with confinement. For a **mated Mode-I
fracture** held near $\sigma'_n/\mathrm{JCS} \approx 0.4$ — which is exactly where SW-T1 and SW-T2
sit — this is the dominant term, and a purely frictional fit is forced to absorb it into $\phi_r$,
producing values above any measured granite basic friction angle (§4.3, note (b)). We therefore
carry $c$ explicitly and let it decay on the *same* curve $W(s)$ as friction, since the asperities
that carry it are the ones slip destroys, with a residual $c_{\text{res}}$ for the interlock that
survives a single slip event. Setting $c = c_{\text{res}} = 0$ recovers Barton exactly.

This envelope has one property that the purely frictional form does not: because cohesion does not
scale with confinement, it does not appear in $\mathrm{d}Y/\mathrm{d}\sigma'_n$, so two
parameterisations that agree on strength at a calibration point need not agree on how fast strength
is shed as injection proceeds.

**How far that distinction can be pushed against this dataset is limited, and we state the limit
here rather than in the discussion.** The two envelopes are tangent at one effective normal stress
by construction and diverge away from it, and injection does sweep $\sigma'_n$ in the direction of
divergence — from 66 to 30 MPa on the rough specimens and 31 to 15 MPa on the smooth ones. But over
that range the separation is small: matched parameterisations differ by roughly 3 % in
$\mathrm{d}\tau/\mathrm{d}\sigma'_n$. Cohesion and JRC are consequently not separately identifiable
on this loading path — a trade between them can be absorbed almost exactly, and the reported JRC,
JCS and $c$ should be read as one calibrated combination rather than three independently
constrained properties. §5.5 therefore compares the two forms on their ability to reproduce
Table 2 under a matched calibration procedure, which the data can settle, rather than on envelope
shape, which they cannot.

#### 3.5.3 Flow rule and the dissipation bound on dilation

**A note on scope, made here because it governs how the rest of this subsection should be read.**
The dissipation inequality derived below is *enforced* in the Mohr–Coulomb formulation used as this
paper's constitutive baseline (§5.5). It is not enforced in the Barton–Bandis law that produced the
results of §5: that law bounds the dilation angle with explicit minimum and maximum angles instead,
neither of which is set in any of the four calibrations, and evolves $\psi$ through the decay law
given below. We therefore do not claim that the bound constrains the reported runs. What we do claim
is narrower and, we think, more interesting: applied as an admissibility *diagnostic* to the
published data rather than as a constraint inside a solver, the inequality identifies a property of
Table 2 that is otherwise easy to miss. That argument is made at the end of this subsection.

The flow rule is **non-associative**. The tangential direction follows the shear traction,

$$
\Delta\boldsymbol{g}_t^{p} = \Delta\gamma\,\boldsymbol{m},
\qquad
\boldsymbol{m} = \frac{\boldsymbol{t}_t}{\lVert \boldsymbol{t}_t \rVert},
$$

while the normal component is governed by a separate dilation angle $\psi$ rather than by the
friction angle:

$$
\Delta g_n^{p} = \Delta\gamma\,\tan\psi(s),
\qquad
\psi(s) = \psi_r + (\psi_p - \psi_r)\,e^{-s/L_\psi},
\qquad
\psi \in [\psi_{\min}, \psi_{\max}].
$$

The interpolation is on the angle, not on its tangent, and it is a plain exponential in cumulative
plastic slip $s$ — the same variable that drives slip weakening, but with its own decay length
$L_\psi$ and no separate exponent. The clamp is inactive in every run reported here: all four
calibrated angles lie between 13° and 26°, inside the default $[0°, 30°]$ bounds. Note that this
form permits $\psi_p = \psi_r$, in which case the dilation angle is a constant and the decay channel
does no work at all; §6.6.3 shows that this is how three of the four specimens are calibrated.

Associativity would force $\psi = \phi$ and over-predict dilation severely: for SW-T1 the mobilised
friction angle at onset is $49.4°$, against a dilation angle of $16.4°$ implied by
Table 2 — $\arctan(|d_n|/d_s) = \arctan(0.157/0.532)$. Non-associativity is therefore not a
refinement here but a requirement.

Non-associativity brings an obligation with it. Because $\psi$ is prescribed independently of
$\mu$, nothing in the flow rule alone prevents the dilation from doing more work against the normal
stress than frictional sliding supplies, which would violate the second law. We therefore impose
the dissipation inequality explicitly. Plastic work per increment is
$\tau\,\Delta\gamma - p_c\,\Delta g_n^{p} \geq 0$; with a margin $\epsilon_D \in [0,1)$ this becomes

$$
\boxed{\;
p_c\,\Delta g_n^{p} \;\leq\; (1 - \epsilon_D)\, Y \, \Delta\gamma
\quad\Longleftrightarrow\quad
\tan\psi \;\leq\; (1 - \epsilon_D)\,\mu \;}
$$

**Where it is enforced, this bound binds often enough to change how calibrated dilation angles
should be reported.** For a smooth saw cut with $\mu \approx 0.4$ and $\epsilon_D = 10^{-8}$, any
$\psi$ above $\approx 22°$ is inadmissible; a deck specifying $\psi_p = 50°$ therefore does not
produce $\tan 50° = 1.19$ but the limiter value $\mathrm{d}g_n^{p}/\mathrm{d}\gamma \approx \mu$. In
that regime the nominal dilation angle is decorative and the realised dilation is set by the
friction coefficient. Any calibration that quotes $\psi$ without also reporting the realised ratio
$\Delta g_n^{p}/\Delta\gamma$ is quoting a number the model may never have used, and we recommend
reporting both as a general practice — it costs one column and it distinguishes a fit from a
saturated limiter.

For the runs of §5 the point is a conditional rather than an observation: the Barton–Bandis law does
not evaluate this inequality, so we cannot report how often it would have bound. What we can say is
that the calibrated dilation angles for the two saw cuts, 26.0° and 24.0°, sit close to the bound
their friction coefficients would impose, so a reader should not assume those two numbers are
freely fitted.

A subtlety in the work budget is worth stating because it silently couples a numerical parameter to
a physical one. The right-hand side must be the *Coulomb* strength $Y\Delta\gamma$. If instead the
full branch traction $\tau^{\rm trial} - k_t\Delta\gamma$ is used — which at convergence equals
$Y + \eta_t\Delta\gamma/\Delta t$ once viscous regularisation is present (§3.9) — then the
admissible dilation is inflated by the viscosity, and the realised dilation angle becomes a
function of the time step. We use $Y$.

**The bound is informative even where it is not enforced, and this is a result rather than a
caveat.** Evaluating $\arctan(|d_n|/d_s)$ on the loading path of Ye and Ghassemi's Table 2 gives
a dilation angle of 16.4° for SW-T1 and 14.0° for SW-T2, comfortably below their mobilised
$\arctan\mu$ of 49.4° and 51.7°. On the two saw cuts it gives 31.8° (SW-S3) and 28.7° (SW-S4)
against $\arctan\mu$ of 31.3° and 24.6° — that is, **the dilation angle implied by the published
displacements exceeds the friction angle those same specimens mobilise**. Read as shear dilation
it is thermodynamically inadmissible.

The resolution is the decomposition already set out in §2.3.1: on a saw cut the measured $d_n$ is
not process (iv) alone. It contains process (ii), the elastic decompression of the joint as
$\sigma'_n$ falls by half over the injection cycle, and attributing the whole of $d_n$ to slip is
what pushes $\psi$ past $\arctan\mu$. A rough tensile fracture with $\mu > 1$ has enough headroom
that the distinction changes nothing; a lapped saw cut with $\mu \approx 0.46$ does not. This is
the quantitative form of the identifiability argument in §2.3.1, and it is the reason the
calibrated $\psi$ for the two saw cuts (26.0° and 24.0°) sits below the value a naive reading of
Table 2 would demand.

#### 3.5.4 Kinematic routing of dilation

There are two ways to make dilation act, and they produce opposite signs.

Under a **compliant** treatment, accumulated dilation is applied as a reduction of contact stress
at fixed jump: as the fracture dilates, $\sigma'_n$ falls, strength falls and slip accelerates. The
fracture never visibly opens.

Under **kinematic** routing, which we adopt, the accumulated plastic normal jump $g_n^{p}$ is a
normal *eigen-opening*. The contact overlap becomes

$$
c = c_0 + g_n^{p} - g_n,
$$

so that at fixed jump, dilating *increases* the overlap and hence the contact pressure; the walls
must physically separate to relieve it, and the displacement field opens. This is the physical
statement — riding up an asperity separates the walls — and it is the only form that produces a
normal displacement jump comparable with an LVDT measurement, which is what Table 2 reports.

Kinematic routing also determines the aperture bookkeeping. Because $g_n$ already contains the
dilation, adding a separate cumulative-dilation term to the hydraulic aperture counts the same
mechanism twice, so the consistent choice is to omit it. §3.6 gives the resulting aperture model,
together with the two specimens whose calibration does not follow this rule and what that costs
them.

#### 3.5.5 Softening, and when the quasi-static problem ceases to have a solution

Both envelopes soften: $Y$ falls with $s$ through $\bar{R}(s)$ in the Mohr–Coulomb form and through
slip-weakening of $\phi_r$ in the Barton–Bandis form. Softening plasticity is only conditionally
stable. If the strength drop per unit slip exceeds the elastic unloading stiffness of the
surrounding system,

$$
\left| \frac{\mathrm{d}Y}{\mathrm{d}s} \right| > k_{\rm sys},
\qquad
k_{\rm sys} = \left( \frac{L}{E} + \frac{A}{k_{\rm machine}} \right)^{-1}
   \times \frac{\cos^2\theta}{A} \;\; \text{(resolved on the fracture)},
$$

then no stable quasi-static branch exists: the fracture accelerates dynamically. In a quasi-static
code this appears as a collapsing time step, which is easily and wrongly attributed to the solver.

This criterion connects the constitutive calibration directly to the loading-frame compliance
derived in Appendix A, and it is the reason we treat that compliance as a measured rather than an
adjustable quantity. A strength drop $\Delta Y$ spread over a characteristic distance $w$ is stable
only while $\Delta Y / w < k_{\rm sys}$; halving $w$ to sharpen a stress drop, or softening the
frame to deepen one, can each move a calibration across that threshold without any warning in the
parameters themselves. We report $|\mathrm{d}Y/\mathrm{d}s|$ against $k_{\rm sys}$ for each
calibration in §5.3.

#### 3.5.6 Reversible normal opening

In addition to the irreversible dilation $g_n^{p}$, the *reported* normal displacement contains a
recoverable elastic component that closes as the effective normal stress recovers on the unloading
branch:

$$
d_{\rm rev} = C_n \left\langle \sigma_{\rm ref} - \sigma'_n \right\rangle_+ ,
\qquad
d_n^{\rm reported} = g_n^{p} + d_{\rm rev} .
$$

This is a decomposition of the measured quantity, not an additional force: it is computed from the
converged effective normal stress and does not enter the residual, the Jacobian or the hydraulic
aperture. Its role is to separate the permanent from the recoverable part of $d_n$. Table 2 reports
both a peak and a partially recovered final value, and lumping the two into the irreversible
dilation angle necessarily produces a normal-displacement history that is flat after the peak,
because $g_n^{p}$ is monotone by construction. Setting $\sigma_{\rm ref}$ to the effective normal
stress of the final hold stage makes $d_{\rm rev}$ vanish there, so that $g_n^{p}$ is calibrated
against the *permanent* dilation and $C_n$ against the recovery, with no overlap between them.

### 3.6 Aperture, transmissivity and interface flow

Two apertures must be distinguished. The **mechanical aperture** $a_m$ is the geometric
separation of the walls, which the mechanics solves. The **hydraulic aperture** $a_h$ is the
separation of an equivalent pair of smooth parallel plates transmitting the same flow. Because a
real fracture has contact patches, tortuosity and roughness, $a_h < a_m$ always, and the ratio is
not constant.

The hydraulic aperture is modelled as a bounded additive construction,

$$
a_h = \mathrm{clamp}\Big[\;
a_{h0}
\;+\; a_\sigma(\sigma'_n)
\;+\; \chi\,a_m
\;+\; \lambda\,\Delta_{\rm cum}\,r(R)
\;+\; a_{\rm prop}(R)
\;-\; a_{\rm gouge}(s)
\;;\; a_{\min},\, a_{\max}\Big],
$$

term by term:

* $a_{h0}$ is the reference hydraulic aperture at the initial stress state — back-calculated from
  the measured initial flow rate, and therefore absorbing the roughness and tortuosity reduction at
  that condition;
* $a_\sigma(\sigma'_n)$ is a stress-aperture term, zero at the reference effective normal stress. It
  runs the *same* power-law closure as §3.4 for SW-T2, SW-S3 and SW-S4, and a linear compliance for
  SW-T1;
* $\chi\,a_m$ couples the solved mechanical aperture to the hydraulic one, with $\chi$ a propping
  coefficient much smaller than unity — the hydraulic aperture responds to only a small fraction of
  the geometric opening, which is the standard $a_h < a_m$ statement made quantitative;
* $\lambda\,\Delta_{\rm cum}\,r(R)$ is an *optional* separate feed from the cumulative shear
  dilation $\Delta_{\rm cum}$, modulated by a retention factor $r(R) = r_{\rm res} + (1-r_{\rm res})R$
  in the roughness state $R$ — discussed below, because it is the one term that is not active on all
  four specimens;
* $a_{\rm prop}(R) = a_{\rm prop,0}R^{\,n}$ is a self-propping aperture held open by residual
  roughness. It is present in the implementation and set to zero in all four calibrations, so it
  plays no part in the results reported here;
* $a_{\rm gouge}(s) = a_g\left[1 - \exp\!\left(-\langle s - s^{*}\rangle_+/s_c\right)\right]$
  represents wear products progressively filling the void. This is what decouples the hydraulic from
  the mechanical aperture on unloading: a fracture that has slipped does not recover its original
  conductivity when re-clamped.

The clamps are not cosmetic. Because transmissivity goes as $a_h^3$, a transient mechanical
excursion before contact is established — during the confinement ramp, for instance — would raise
the permeability by orders of magnitude and wreck the coupled Newton solve; $a_{\max}$ bounds it,
and $a_{\min}$ keeps $a_h > 0$ without forbidding hydraulic closure.

**Which terms are active, and an asymmetry we state rather than hide.** Under the kinematic dilation
routing of §3.5.4 the shear dilation already lives inside $a_m$, so feeding $\Delta_{\rm cum}$ in a
second time through $\lambda$ counts the same mechanism twice. The correct configuration is
therefore $\lambda = 0$. That is what the two tensile fractures run. The two saw cuts do not:

| | $a_\sigma$ law | $\chi$ | $\lambda$ | $r_{\rm res}$ | gouge | dilation counted |
|---|---|---:|---:|---:|---|---|
| SW-T1 | linear | 0.0160 | 0 | 0.715 | off | once |
| SW-T2 | power law | 0.0165 | 0 | 0.747 | off | once |
| SW-S3 | power law | 0.0010 | 0.038 | 0.28 | on | **twice** |
| SW-S4 | power law | 0.0010 | 0.0117 | 0.28 | on | **twice** |

On SW-S3 and SW-S4 the hydraulic aperture therefore carries a fitted dilation feed on top of the
kinematic one, and $\lambda$ was reduced during calibration — on SW-S4 by a factor of about 17 — to
hold $a_h$ against the measured flow rate. The consequence is measurable and is reported in §5.4:
the correlation between hydraulic aperture and mechanical normal opening is 1.000, 0.999 and 0.946
on SW-T1, SW-T2 and SW-S3, but only 0.562 on SW-S4. On that specimen the flow channel is reporting
a stress state rather than an opening, and its flow and dilation results must be read as two
findings rather than one. We report this as a limitation of the present calibration
(§6.8) rather than repairing it post hoc, because refitting $\lambda \to 0$ on the saw cuts would
change the Table 2 scores that the rest of this paper reports.

We also tested, and do not adopt, the closed form these terms are motivated by,
$a_h \propto a_m^2/\mathrm{JRC}^{2.5}$ (Barton et al., 1985). Substituting it destabilised the
coupled Newton solve at the slip/arrest transition, reproducibly and in two independent
implementations. The mechanism is worth stating precisely, because the obvious explanation is the
wrong one. It is *not* that the power law is too stiff: with the offset that matches the two models'
initial apertures, the measured logarithmic sensitivity $\mathrm{d}\ln T/\mathrm{d}\ln a_m$ reaches
only 0.74 over the range these specimens actually visit, the aperture clamp never binds, and the
ratio of Bakhtar to additive transmissivity stays between 1.00 and 1.45 everywhere. Two laws that
close to each other cannot themselves be the instability. What the substitution really does is
remove the additive form's entire negative-feedback stack in one step — the bounded power-law
closure, the retention-modulated dilation term and the gouge reduction all disappear together — and
it is the loss of those saturating terms, not the exponent, that leaves the aperture–pressure
coupling without a restoring mechanism at the limit point. We report this as a statement about which
feedbacks a two-way coupled solve requires, not as a claim that the closed form is wrong at the
joint scale it was fitted to.

Transmissivity follows the cubic law,

$$
T = \frac{a_h^3}{12\mu_f}, \qquad k_f = \frac{a_h^2}{12},
$$

and mass conservation between the walls gives a Reynolds equation on the interface,

$$
\frac{\partial}{\partial t}\left(\rho_f a_h\right) + \nabla_t\cdot\left(\rho_f \boldsymbol{q}_f\right) = 0,
\qquad \boldsymbol{q}_f = -T\,\nabla_t p .
$$

The storage term is assembled directly as $\partial(\rho_f a_h)/\partial t$, which captures both
the aperture change and the fluid compressibility exactly without splitting them.

The fluid pressure in the fracture also acts mechanically on the walls, contributing a normal
traction $-\alpha_f\,p_f\boldsymbol{n}$.

#### 3.6.1 The pressure–area coefficient, and why it is a constant here

The historical assumption is $\alpha_f = 1$ exactly, on the grounds that the fluid acts across the
entire nominal fracture area. That assumption is already an approximation: at any finite effective
normal stress the walls are in contact over some fraction of the nominal area, and fluid pressure
cannot act where the walls are touching.

**What the reported runs use.** A single constant per specimen, calibrated once:

| specimen | $\alpha_f$ |
|---|---:|
| SW-T1 | 1.00 |
| SW-T2 | 1.00 |
| SW-S3 | 0.87 |
| SW-S4 | 0.86 |

The two tensile fractures apply no attenuation at all; only the two saw cuts do, and by less than
15 %. This is worth stating plainly because it bounds how much of this study's agreement with
Table 2 can be attributed to the coefficient: on half the specimens, none of it.

**A state-dependent alternative is implemented but not used.** The contact material can instead
export

$$
\alpha_f(\sigma'_n) = \frac{\sigma_0}{\sigma_0 + \sigma'_n},
$$

a saturating hyperbola with $\sigma_0$ the stress at which $\alpha_f = 1/2$, so that
$\alpha_f \to 1$ for an open or barely loaded fracture and falls as the load-bearing contact
fraction grows. It is disabled in every run reported here, and we flag it rather than describe it as
adopted, because the distinction matters for what §6 may claim: a coupling that steepens as the
joint approaches failure is a different physical model from a constant, and this paper does not test
it. Enabling it and repeating the calibration is the obvious next experiment, and §6.8 records it as
an open question rather than a result.

This fracture-scale coefficient is conceptually distinct from the matrix Biot coefficient
$\alpha \approx 0.6$: $\alpha$ answers what fraction of the matrix's porosity is hydraulically
connected, a property of the rock; $\alpha_f$ answers what fraction of the fracture plane is not in
load-bearing contact, a property of the joint's current mechanical state. Neither should be called
"the effective-stress coefficient" unqualified (§0.4).

### 3.7 Characteristic distances and what each one does to the plastic response

Every history-dependent term in §3.5 is written as an exponential in $s$ with its own
characteristic distance. They are not interchangeable, they act on different observables, and each
has a distinct failure mode when mis-set. Because these are the parameters a reader is least able
to check and most likely to see quoted without explanation, we state them explicitly.

| Distance | Symbol | Governs | Observable it controls | Failure mode if too short | Failure mode if too long |
|---|---|---|---|---|---|
| Roughness decay | $L_R$ | $\mu(\bar R)$, $c(\bar R)$ | rate of the stress drop | $|\mathrm{d}Y/\mathrm{d}s| > k_{\rm sys}$: no stable branch, time step collapses (§3.5.5) | drop too gradual; slip continues to accumulate through later hold stages |
| Dilation decay | $L_\psi$ | $\psi(s)$ | curvature of $d_n$ against $d_s$ | dilation saturates before peak slip; the $d_n$ peak is under-predicted while $d_s$ is right | dilation keeps growing on the unloading branch, where Table 2 shows it recovering |
| Slip weakening (BB) | $D_c$ | $\phi_r \to \phi_r^{\rm res}$ | post-slip residual $\tau$ | as $L_R$ | residual strength never reached within the test |
| Gouge accumulation | $s_c$, onset $s^{*}$ | $a_{\rm gouge}(s)$ | hysteresis of $a_h$ between branches | conductivity collapses during the slip event itself | aperture recovers fully on unloading, and the measured hysteresis is lost |
| Reversible-opening gate | $s_0$, $D_{\rm rev}$ | activation of $d_{\rm rev}$ | pre-slip flatness of $d_n$ | elastic opening appears before yield, where Table 2 shows none | recovery switches on after the unloading branch has begun |

Two general points follow, and both bear on how such a model should be reported.

First, **the distances are identifiable only against observables that resolve them**. $L_R$ is
constrained by the *shape* of the stress drop, so it is identifiable in SW-S4, whose slip is
progressive across three hold stages, and effectively unidentifiable in SW-T1, SW-T2 and SW-S3,
where the drop occupies a single stage and any $L_R$ below that stage duration gives the same
tabulated result. Reporting a fitted $L_R$ for the burst specimens would suggest a constraint that
the data does not supply. This is the same identifiability argument made for the load-frame
compliance in §6.1, applied to a constitutive parameter, and it has the same remedy: state the
share of the response that the parameter actually controls.

Second, **the distances interact through the stability criterion, not only through the fit**.
$L_R$ and $D_c$ both set $|\mathrm{d}Y/\mathrm{d}s|$, and the same total strength drop delivered
over half the distance doubles it. A calibration that shortens a characteristic distance to sharpen
a stress drop is therefore moving toward the instability threshold of §3.5.5 even though the
strength parameters are untouched, and the symptom — a failed time step — appears nowhere near the
parameter responsible.

### 3.8 Admissible and inadmissible limiters

A distinction is enforced throughout between limiters that express physics and limiters that
express numerical convenience. The first are kept; the second are refused, because they let a
numerical parameter set a physical result.

**Admissible.** The dissipation bound of §3.5.3, $\tan\psi \leq (1-\epsilon_D)\mu$, is a statement
of the second law and binds regardless of discretisation. So are the irreversibility constraints
$\Delta\gamma \geq 0$ and $g_n^{p} \geq g_n^{p,\rm old}$, and the requirement $\sigma'_n \geq 0$
under unilateral contact. These are enforced exactly at every quadrature point, not approached
iteratively.

**Inadmissible: per-step increment caps.** An earlier formulation offered
`max_plastic_slip_increment` and `max_dilation_increment`, which clamp $\Delta\gamma$ and
$\Delta g_n^{p}$ within a step. These are now refused at input parsing, and the reason is empirical
rather than aesthetic. In one SW-S4 calibration the slip cap was found to bind on 14 time steps and
to contribute approximately 30 % of the total accumulated slip. A cap that binds is not a safety
net: it is a constitutive law, and one whose parameters are the time step and the cap value rather
than any property of the joint. Two runs of the same deck at different time steps would then report
different slip and be indistinguishable in the output.

The legitimate substitutes act on the integration rather than on the answer: reduce the time step,
subdivide within the step (§3.9), or add viscosity and report it. All three converge to the same
result as the step is refined, which is the property a cap lacks.

**A limiter that is admissible only with the right budget.** The residual shear-strength floor
$\tau_{\min}$ (§3.9) removes the $\tau_{\rm limit} \to 0$ singularity that arises as
$\sigma'_n \to 0$. It is admissible as a representation of residual asperity interlock provided it
is far below the measured residual strength, and inadmissible if it is comparable to it, in which
case it is propping the strength rather than regularising the solve. We use $10^5$ Pa against a
measured residual of $2.3$ MPa — 4 % — and report the ratio.

### 3.9 Numerical implementation

#### 3.9.1 Two-level Newton

The coupled system is solved monolithically by Newton's method with an $\ell_2$ line search,
preconditioned by algebraic multigrid. Within each global iteration, every interface quadrature
point solves its own small nonlinear system: the elastic-predictor / plastic-corrector return map
of §3.5.1. For the Mohr–Coulomb law with kinematic dilation this is a $2\times 2$ system in
$(\Delta\gamma, g_n^{p})$, because the normal and tangential responses are coupled through the
eigen-opening; for the Barton–Bandis law it reduces to a scalar root-find in $\Delta\gamma$.

**Bracketing rather than pure Newton.** The local residual $R(\Delta\gamma)$ is monotone decreasing
for a hardening law but need not be for a softening one, so a pure Newton iteration can leave the
admissible interval. The scalar solve therefore brackets the root in

$$
\Delta\gamma \in \left[\,0,\;\frac{\tau^{\rm trial}}{k_t + \eta_t/\Delta t}\,\right],
$$

the upper limit being the slip that would relax the entire trial overstress, and falls back to
bisection whenever a Newton step leaves the bracket. This costs more per iteration and cannot
diverge — the correct trade for a law that is deliberately softening.

#### 3.9.2 Scale-aware local tolerances

A fixed absolute tolerance on the local residual cannot work across the stress range of interest.
A tolerance of $10^{-8}$ Pa on a residual formed as the difference of two $10^{7}$ Pa quantities
sits below the double-precision floor ($\sim 10^{-9} \times 10^{7} = 10^{-2}$ Pa) and can never be
met. The local solvers therefore use

$$
\mathrm{tol} = \mathrm{tol}_{\rm abs} + 10^{-9}\max\!\left(\tau^{\rm trial}, \sigma_{\rm reg}\right),
$$

which is meaningful at both laboratory (MPa) and unit-test (Pa) scale. The elastic/plastic
pre-check must use the *same* tolerance as the loop; if it does not, states between the two
thresholds are routed into the return map, converge at $\Delta\gamma = 0$, and are reported as
slipping when they are not.

The same scale argument applies at the global level and explains a failure mode of the present
study. The Barton–Bandis flow form has a transition band whose quadrature-point residuals floor at
$\sim 4\times10^{-5}$ N, so a global `nl_abs_tol` of $10^{-6}$ is unreachable for that law family
irrespective of the physics. One specimen was configured that way and failed for that reason, not
a constitutive one (§5.1).

#### 3.9.3 Event-aware substepping

A single global step may carry the interface across a state boundary — contact activation, yield
onset, damage initiation. Integrating straight through such a boundary with one return map is
first-order inaccurate at best. The jump path is therefore parameterised,

$$
\boldsymbol{g}(\lambda) = \boldsymbol{g}^{n} + \lambda\left(\boldsymbol{g}^{n+1} - \boldsymbol{g}^{n}\right),
\qquad \lambda \in [0,1],
$$

the $\lambda$ at which each event occurs is located by bisection on the corresponding sign change,
the events are sorted and de-duplicated, and the return map is integrated segment by segment. A
segment that fails to converge is bisected recursively; exhausting the substep budget raises an
exception that the framework converts into a global time-step cut, so a local failure never
silently returns a wrong state.

One rule makes this consistent rather than merely finer: **rate-dependent terms must use the
substep increment $\Delta t(\lambda_{i+1} - \lambda_i)$, not the full $\Delta t$.** Otherwise the
viscous contribution depends on how many substeps happened to be taken, and mesh or step
refinement changes the answer.

#### 3.9.4 Consistent tangent by automatic differentiation

The global Jacobian requires $\partial \boldsymbol{t}/\partial [\![\boldsymbol{u}]\!]$ *including*
the sensitivity of the converged plastic state. Differentiating the return map by hand is possible
but must be redone for every constitutive variant; differencing it is expensive and ill-conditioned
near active-set changes. We instead carry forward-mode automatic differentiation through the entire
local solve, and apply one exact AD Newton step at the converged point to inject the implicit
sensitivities given by the implicit function theorem. The resulting tangent is exact to machine
precision.

This is not a matter of convenience. With an inconsistent tangent, Newton degrades from quadratic
to linear convergence exactly where the physics is most nonlinear — at the slip event — which is
where the step budget is already tightest.

#### 3.9.5 Regularisation: a complete account

Regularisation is where numerical methods most often leak into physical results, and where papers
are least specific. We therefore give the full inventory: what is regularised, the exact form, what
the regularisation buys, what it costs, and — for each — whether the cost vanishes under refinement.

**Why any of it is needed.** The interface law as written in §3.4–§3.5 is not differentiable. It
contains three hard branches: contact versus separation at $g_n = 0$; stick versus slip at
$F = 0$; and, when a cohesive branch is active, intact versus damaged. Newton's method requires a
Jacobian, and at a hard branch the Jacobian does not exist. Worse, the branch location moves
between iterations, so a Newton step computed on one side of a branch can be evaluated on the
other, producing the iteration-to-iteration oscillation ("active-set chatter") that manifests as a
collapsing time step. Regularisation replaces each branch with a *semismooth* transition of finite
width, which is enough for Newton to converge.

##### 3.9.5.1 Inventory

| # | Regularisation | Parameter | Symbol | Where it enters | Value used |
|---|---|---|---|---|---|
| R1 | smooth positive part | `contact_gap_regularization` | $\epsilon_g$ | contact/open active set; irreversible-dilation target | $10^{-14}$ m |
| R2 | smooth positive part | `cohesive_gap_regularization` | $\epsilon_c$ | cohesive effective separation | $10^{-14}$ m |
| R3 | smooth maximum | `stress_regularization` | $\sigma_{\rm reg}$ | strength memory, retained shear support, dissipation-limit denominator | $10^{-8}$ Pa |
| R4 | viscous (Perzyna) overstress | `tangential_viscosity` | $\eta_t$ | yield residual | $4\times10^{11}$ (SW-T1/T2/S3), $3.5\times10^{12}$ (SW-S4) |
| R5 | event-aware substepping | `max_local_substeps`, `event_fraction_tolerance` | — | integration of the jump path | 32, $10^{-10}$ |
| R6 | residual strength floor | `min_tau_limit` | $\tau_{\min}$ | Barton–Bandis strength (SW-S decks only) | $10^{5}$ Pa |

R1–R3 regularise *geometry and branch structure*; R4 regularises *time*; R5 regularises
*integration*; R6 regularises a *degenerate limit*. They are independent and are reported
separately.

**R4 is not purely numerical at the values used, and calling it a regularisation understates it.**
The Perzyna term adds $\eta_t V$ to the mobilised strength at slip rate $V$, so it is negligible
only while $\eta_t V \ll Y$. On SW-T1, SW-T2 and SW-S3 that condition holds. On SW-S4 it does not:
$\eta_t$ is 8.75 times larger there, and the resulting overstress averages 0.31 MPa and peaks at
0.87 MPa on the loading ramps, against a shear strength of order 10 MPa. A parameter worth several
per cent of the strength is a constitutive choice, and we report it as one rather than burying it in
a numerics table.

Two things keep this from contaminating the comparison of §5. The overstress is proportional to slip
rate, so it relaxes to zero during the hold stages at which Table 2 is tabulated and at which every
score in §5.2 is taken; and it is reported per specimen above rather than as a single range, so a
reader can see which specimen carries it. What it does affect is the transient between stages — the
ramp on which SW-S4's stage-4 slip deficit occurs (§5.3) — which is a caution about interpreting
that residual, not about the scores. A separate experiment replacing the viscous term with an
explicit rate-and-state formulation confirmed that it is doing rate-law work: the rate-and-state
runs reproduced the same strength inflation, and did not improve the hold-stage fit.

##### 3.9.5.2 Smooth positive part and smooth maximum (R1–R3)

The positive part $\langle x\rangle_+ = \max(x, 0)$ is replaced by

$$
\boxed{\;\langle x \rangle_+^{\epsilon} = \tfrac{1}{2}\left(x + \sqrt{x^2 + \epsilon^2}\right)\;}
\qquad
\frac{\mathrm{d}}{\mathrm{d}x}\langle x \rangle_+^{\epsilon}
   = \tfrac{1}{2}\left(1 + \frac{x}{\sqrt{x^2+\epsilon^2}}\right),
$$

and the maximum of two arguments by

$$
\max{}^{\epsilon}(a,b) = \tfrac{1}{2}\left(a + b + \sqrt{(a-b)^2 + \epsilon^2}\right),
\qquad
w_a = \frac{\partial \max^\epsilon}{\partial a} = \tfrac{1}{2}\left(1 + \frac{a-b}{\sqrt{(a-b)^2+\epsilon^2}}\right).
$$

Three properties matter, and the third is the one usually omitted.

1. **Exactness away from the branch.** For $|x| \gg \epsilon$ the smoothed form agrees with the
   exact one to $O(\epsilon^2/|x|)$. The regularisation is therefore inactive everywhere except
   within a band of width $\sim\epsilon$ around the branch.
2. **A defined derivative on the branch.** At $x = 0$ the derivative is exactly $\tfrac{1}{2}$
   rather than undefined, and it varies smoothly through the transition. This is what makes the
   Jacobian assembleable and the tangent consistent. The blending weight $w_a$ is used directly to
   interpolate the two branch tangents, so the tangent is consistent with the smoothed residual
   rather than with either branch.
3. **A bias, not merely a smoothing.** $\langle 0 \rangle_+^{\epsilon} = \epsilon/2 \neq 0$. The
   smoothed positive part does not pass through the origin. Physically this means a small spurious
   opening — or, on the contact side, a small interpenetration — of order $\epsilon/2$ persists
   even at exact contact. **This is a systematic offset and must be sized against a physical
   length, not merely made "small".**

For R1 and R2, $\epsilon_g = 10^{-14}$ m gives a bias of $5\times10^{-15}$ m against a hydraulic
aperture of $0.75$–$2.1\times10^{-6}$ m, i.e. a relative offset below $10^{-8}$. For R3,
$\sigma_{\rm reg} = 10^{-8}$ Pa against strengths of $10^{6}$–$10^{8}$ Pa is a relative offset
below $10^{-14}$. Both are far below the convergence tolerances of the solve and can be ignored;
the point is that the check was made and the number is quotable.

##### 3.9.5.3 Viscous overstress (R4): the one with physical consequences

The yield residual is augmented by an overstress term proportional to the plastic slip rate:

$$
\boxed{\;
F = \tau^{\rm trial} - k_t\,\Delta\gamma - \left[\,Y(\boldsymbol{q}) + \underbrace{\eta_t \frac{\Delta\gamma}{\Delta t_{\rm sub}}}_{\text{viscous}} + \tau_{\rm RSF}\,\right] = 0
\;}
$$

so the mobilised strength during sliding is $Y + \eta_t V$ with $V = \Delta\gamma/\Delta t_{\rm sub}$
the plastic slip rate. This is a Perzyna (rate-dependent plasticity) regularisation, and it is
formally identical to the radiation-damping term $\xi V$ used in quasi-dynamic earthquake models,
though its purpose here is numerical rather than a proxy for wave radiation.

**What it buys.** Two distinct things, and they should not be conflated.

- *It removes the stick/slip kink.* Without it, $\Delta\gamma$ jumps discontinuously from zero as
  the yield surface is crossed. With it, $\partial F/\partial \Delta\gamma$ contains the strictly
  negative term $-\eta_t/\Delta t_{\rm sub}$, so the residual is monotone in $\Delta\gamma$ and the
  local root-find is well posed.
- *It restores positive-definiteness of the consistent tangent at the softening limit point.*
  This is the more important effect. §3.5.5 shows that when $|\mathrm{d}Y/\mathrm{d}s| > k_{\rm sys}$
  the quasi-static problem has no stable branch. The viscous term adds $\eta_t/\Delta t$ to the
  effective stiffness, so the condition becomes
  $|\mathrm{d}Y/\mathrm{d}s| > k_{\rm sys} + \eta_t/\Delta t$, and the solver can advance *through*
  a limit point that would otherwise collapse the step. In effect it converts a static instability
  into a fast but finite-rate transient.

**What it costs.** The strength is inflated by $\eta_t V$, which is not physical. The requirement
is $\eta_t V \ll Y$ at the slip rates of interest. For the values used here, at the pre-slip creep
rate $V \sim 10^{-9}$ m/s the inflation is $\sim 5\times10^{3}$ Pa against a strength of
$10^{7}$ Pa — negligible. Through the slip burst, where $V$ may reach $10^{-6}$–$10^{-5}$ m/s, the
inflation reaches $10^{6}$–$10^{7}$ Pa and is *not* negligible. This is the honest statement:
**the viscous term is inactive during the hold stages that Table 2 reports, and active during the
transient between them.** Because the comparison is made at the hold stages, the reported
agreement is not contaminated; the *duration* of the slip event is.

**Two implementation requirements, both of which we have had to fix, and both of which are easy
to get wrong.**

*(i) The rate must use the substep increment, not the global step.* When a global step is
subdivided into substeps (§3.9.3), $\Delta\gamma$ is the slip accumulated within the *current
substep*, so dividing by the full $\Delta t$ understates $V$ by the substep fraction. The
consequence is that the answer depends on how many substeps happened to be taken — a
mesh-refinement-like sensitivity to an internal algorithmic choice, which is the worst kind because
it does not show up in any convergence study the user thinks to run. The code uses
$\Delta t_{\rm sub} = \Delta t \cdot (\lambda_{i+1} - \lambda_i)$ throughout, consistently with the
Duvaut–Lions relaxation of the cohesive branch.

*(ii) The viscous force must be excluded from the dissipation budget.* The dilation bound of
§3.5.3 caps $p_c\,\Delta g_n^p$ by the frictional work. If that budget is formed from the total
branch traction $\tau^{\rm trial} - k_t\Delta\gamma$, then at convergence it equals
$Y + \eta_t\Delta\gamma/\Delta t + \tau_{\rm RSF}$ — so the viscous overstress *inflates the
admissible dilation*. We measured this: with $\eta_t = 5\times10^{12}$ Pa·s/m at
$V \sim 10^{-7}$ m/s the inflation is $\approx 0.5$ MPa against a strength of 3–12 MPa, and since
the dilation limiter is what actually controls $\mathrm{d}d_n/\mathrm{d}s$ in the smooth-specimen
decks, **a numerical regularisation parameter was setting a physical result.** The budget is formed
from the Coulomb strength $Y$ alone.

##### 3.9.5.4 Regularised rate-and-state, where used (R4b)

The framework also supports a rate-and-state term, written as a *perturbation about* the Coulomb
strength rather than an absolute friction law:

$$
Y \;\mathrel{+}=\; p_c\,a\left(\operatorname{asinh}\!\left[\frac{V}{2V_0}\left(\frac{V_0\theta}{D_c}\right)^{b/a}\right] - \operatorname{asinh}\tfrac{1}{2}\right),
\qquad
\dot\theta = 1 - \frac{V\theta}{D_c}.
$$

Three regularisations are embedded here and each fixes a specific failure.

- The $\operatorname{asinh}$ form replaces $\ln V$, which is singular at $V = 0$. A quasi-static
  simulation spends most of its time with $V = 0$, so the logarithmic form is unusable.
- The $-\operatorname{asinh}(1/2)$ **reference** makes the term vanish identically at $V = V_0$,
  $\theta = D_c/V_0$. Without it, $a\operatorname{asinh}(z)$ adds a persistent multi-MPa offset at
  every slip rate, which delays onset and freezes the post-peak weakening — the roughness Coulomb
  strength already plays the role of the reference friction $f_0$, so an absolute add-on
  double-counts it.
- $\theta$ is taken at the **previous** step, so the in-step strength depends on the rate only
  through $\operatorname{asinh}(V)$. Coupling $\theta$ implicitly would make the local system
  singular near $V \to 0$.

A fourth guard, `rate_and_state_nonnegative`, is worth describing because it is a concrete example
of how a regularisation can create a new failure. The referenced form is *negative* as $V \to 0$,
approaching $-0.481\,a\,p_c$. The slip-branch strength at vanishing slip rate therefore sits
**below** the stick limit, so the stick$\leftrightarrow$slip transition is a non-monotone jump of
$0.481\,a\,p_c$, and the global Newton can limit-cycle across it — exactly at slip onset and again
at re-stick. We observed this as a time-step collapse at $t \approx 1830$–$1880$ s at
$V \approx 1.4\times10^{-8}$ m/s during re-sticking. Clamping the term at zero makes the slip
strength at $V \to 0^{+}$ equal the stick limit and removes the jump.

##### 3.9.5.5 Which costs vanish under refinement, and which do not

This is the distinction that determines what may be presented as a converged result.

| Regularisation | Controlled by | Behaviour as the control $\to 0$ | Converges away? |
|---|---|---|---|
| R1, R2 smooth positive | $\epsilon_g$, $\epsilon_c$ | bias $\epsilon/2 \to 0$; Jacobian sharpens | **yes**, but Newton fails before $\epsilon = 0$ |
| R3 smooth maximum | $\sigma_{\rm reg}$ | offset $\to 0$ | **yes**, same caveat |
| R4 viscous overstress | $\eta_t$, **and** $\Delta t$ | $\eta_t V \to 0$ as $\eta_t \to 0$; but for fixed $\eta_t$, refining $\Delta t$ *raises* $V$ and the inflation persists | **only in $\eta_t$** |
| R4b rate-and-state | $a$ | term $\to 0$ | yes, but it is a constitutive model, not a regulariser |
| R5 substepping | substep count | approaches the exact path integral | **yes**, monotonically |
| R6 strength floor | $\tau_{\min}$ | the $\tau_{\rm limit}\to 0$ singularity returns | **no** — it is a modelling choice |

The row that matters is R4. **Refining the time step does not remove the viscous inflation**,
because $V = \Delta\gamma/\Delta t$ and both shrink together. Only reducing $\eta_t$ removes it,
and reducing $\eta_t$ reinstates the instability it was introduced to survive. There is therefore
no limit in which the viscous regularisation is simultaneously absent and the softening event
tractable — which is precisely why the value must be reported, and why we report agreement at the
hold stages rather than during the transient.

R6 is not a numerical parameter at all in the limit: $\tau_{\min}$ is a statement that a real joint
retains some asperity interlock as $\sigma'_n \to 0$. It is admissible only while it is far below
the measured residual strength; §3.8 states the ratio actually used, $10^{5}$ Pa against a measured
$2.3$ MPa, i.e. 4 %.

##### 3.9.5.6 Why regularisation reduces total cost

It is counter-intuitive that adding work per step makes the simulation faster. The mechanism is

$$
\text{smoother Jacobian} \Rightarrow \text{fewer Newton iterations} \Rightarrow
\text{fewer step rejections} \Rightarrow \text{larger stable } \Delta t ,
$$

and the asymmetry is that a rejected step costs its entire work *plus* a step cut whose effect
persists over many subsequent steps before the adaptive controller recovers. In this framework,
removing a single Jacobian discontinuity in one benchmark converted a run that failed after
5.5 minutes at 10 % of the load into one that completed in 27 seconds — a 12× speed-up obtained
purely by eliminating step rejections, with no change to the physics.

##### 3.9.5.7 How regularisation is reported here

Every regularisation parameter appears in the classified parameter table (Table 4) rather than in a
solver appendix, because three of them ($\eta_t$, $\tau_{\min}$, and the rate-and-state $a$) have
physical consequences and the reader needs them to reproduce the result. For $\eta_t$ we
additionally report the ratio $\eta_t V/Y$ at the hold stages, which is the quantity that decides
whether the comparison is contaminated.

#### 3.9.6 Time stepping and boundary reactions

Time stepping is adaptive, targeting a fixed number of nonlinear iterations per step and cutting
back on failure. Injected and produced fluid mass fluxes are recovered from a tagged residual
vector rather than by per-kernel accumulation; Appendix B explains why this distinction is not
cosmetic in a formulation where the injection node is duplicated by the interface split.

---

## 4. Model Setup and Parameter Determination

### 4.1 Geometry and discretisation

Each specimen is meshed as a right circular cylinder of its Table 1 dimensions, cut by a planar
elliptical fracture at the angle recovered in Appendix A. The mesh is generated with hexahedral
elements at three refinement levels, with the interface conforming to the fracture plane at every
level:

| Specimen | coarse | medium | fine |
|---|---|---|---|
| SW-T1 | 10 752 | 117 232 | 331 200 |
| SW-T2 | 10 752 | 116 480 | 345 600 |
| SW-S3 | 10 368 | 100 048 | 322 240 |
| SW-S4 | 9 216 | 100 048 | 285 988 |

Production results use the fine mesh; the coarse mesh is used for parameter gating and mesh
convergence (§5.1).

The injection and production points are single nodes on the fracture, located 6 mm inside the
sidewall for SW-T1, SW-T2 and SW-S4 and 2.1 mm for SW-S3, following the reported borehole
placement. Because the node-selection utility searches the whole mesh and runs before the
interface split, an injection coordinate that is merely *near* the fracture can attach to a matrix
node without raising an error; each coordinate is therefore pinned to the exact fracture node and
verified after every mesh regeneration. The consequence of getting this wrong is severe and silent:
the injection pressure would be imposed inside the matrix, and fluid would reach the fracture only
through the $5\times10^{-19}$ m² matrix permeability.

#### 4.1.1 Verification of the discretised fracture area

Every extensive fracture quantity the model reports is an integral over the discretised interface:
the flow rate through it, the integrated dilation volume, and the area-averaged fracture pressure
that enters $\sigma'_n$. An error in the meshed area propagates to all of them by the same factor,
and it does so silently — no residual is sensitive to it. Because the fracture here is a plane
cutting a right circular cylinder, the exact area is available in closed form, so this is one of the
few geometric properties of the model that can be verified rather than assumed.

For a plane inclined at θ to the axis of a cylinder of radius $R$, the intersection is an ellipse
with semi-minor axis $R$ and semi-major axis $R/\sin\theta$, hence

$$
A_{\rm exact} = \frac{\pi R^2}{\sin\theta}.
$$

**Table 2.** Discretised fracture area against the exact ellipse. $A_{\rm mesh}$ is the sum of the
interface quadrilaterals the interface kernels integrate over; $h = \sqrt{A_{\rm mesh}/N_{\rm faces}}$;
$\theta_{\rm mesh}$ is recovered from the best-fit plane of the interface nodes; planarity is the
maximum out-of-plane deviation of those nodes.

| Specimen | mesh | faces | $h$ (mm) | $A_{\rm mesh}$ (mm²) | $A_{\rm exact}$ (mm²) | ratio | $\theta_{\rm mesh}$ | planarity |
|---|---|---|---|---|---|---|---|---|
| SW-T1 | coarse | 384 | 3.13 | 3770.3 | 3779.7 | 0.9975 | 32.000° | 0.0 nm |
| SW-T1 | medium | 1724 | 1.48 | 3779.9 | 3779.7 | 1.0000 | 32.000° | 0.0 nm |
| SW-T2 | coarse | 384 | 3.23 | 3995.5 | 4005.9 | 0.9974 | 30.000° | 0.0 nm |
| SW-T2 | medium | 1820 | 1.48 | 4006.2 | 4005.9 | 1.0001 | 30.000° | 0.0 nm |
| SW-S3 | coarse | 432 | 3.09 | 4122.1 | 4131.4 | 0.9978 | 29.000° | 0.0 nm |
| SW-S3 | medium | 1924 | 1.47 | 4133.3 | 4131.4 | 1.0005 | 29.000° | 0.0 nm |
| SW-S4 | coarse | 384 | 3.23 | 3993.9 | 4005.9 | 0.9970 | 30.000° | 0.0 nm |
| SW-S4 | medium | 1924 | 1.44 | 4004.6 | 4005.9 | 0.9997 | 30.000° | 0.0 nm |

The area error is 0.25–0.30 % on the coarse mesh and at most 0.05 % on the medium mesh, falling at
an apparent order between 2.1 and 5.9 — at least the second order expected from chording an
elliptical boundary with straight-sided elements. The interface is planar to within numerical
precision, and the recovered inclination reproduces the value each mesh was built at to three
decimal places. The meshes for SW-S3 and SW-S4 were built at exactly 29.000° and 30.000°, against
the 29.03° and 30.02° recovered in Appendix A; the difference is worth 0.09 % and 0.06 % in area,
below the coarse-mesh discretisation error, and no remesh was made for it.

#### 4.1.2 What a planar interface does not represent, and how large that is

$A_{\rm exact}$ is the *projected* area of the fracture. The true surface area of a rough fracture
exceeds it, by a factor that for a surface with r.m.s. slope $Z_2$ is approximately
$\sqrt{1+Z_2^2}$. Converting the reported JRC through the Tse and Cruden (1979) correlation
$\mathrm{JRC} = 32.2 + 32.47\log_{10}Z_2$ bounds the omission.

**Table 3.** Surface area omitted by the planar interface, estimated from JRC. $Z_2$ is the r.m.s.
slope of the surface profile; the amplification is an estimate, not a measurement (Appendix C).

| Specimen | surface | JRC | $Z_2$ | $A_{\rm true}/A_{\rm proj}$ |
|---|---|---|---|---|
| SW-T1 | tensile | 15.32 | 0.302 | 1.045 |
| SW-T2 | tensile | 14.63 | 0.288 | 1.041 |
| SW-S3 | saw cut | 1.96 | 0.117 | 1.007 |
| SW-S4 | polished saw cut | 1.19 | 0.111 | 1.006 |

This is a quantitative statement of the hierarchy argued in §2.3.2. For the saw-cut specimens the
planar-interface idealisation is geometrically exact to better than one per cent, so no part of the
SW-S3 or SW-S4 comparison is contaminated by surface area the model does not carry. For the tensile
specimens it is low by four per cent, and that deficit sits in precisely the terms — contact area,
asperity dilation, damage — that the roughness model is being asked to supply. It is not a
correction we apply, because the constitutive parameters are calibrated on the same projected area
and would absorb it; it is a bound on how much of the SW-T residual can be geometric rather than
constitutive.

Appendix C sets out how this estimate could be replaced by a direct measurement if computed
tomography of the specimens were available, and what resolution such a measurement requires.

### 4.2 Boundary and initial conditions

Confining pressure is applied as a radial traction on the cylindrical surface. The base is fixed
in the axial direction. The axial load is applied at the top face through a penalised Dirichlet
condition,

$$
t_z = k_{\rm pen}\left(u_z - \bar{u}_z(t)\right),
$$

which represents the servo-controlled piston together with the elastic compliance of the load
train. Setting $k_{\rm pen}$ to a finite value is not a numerical convenience: the experiment is
run at constant piston displacement, so the axial stress must be free to fall as the fracture
slips, and how far it falls is controlled by the series stiffness of rock, frame and fracture.
A rigid condition would suppress the stress drop entirely.

The prescribed displacement $\bar{u}_z$ ramps to its final value during an initial loading phase
and is then held for the remainder of the simulation.

Injection pressure is imposed as a time-dependent Dirichlet condition at the injection node,
following the eleven-stage schedule; the production node is held at 5 MPa. The initial pore
pressure is 5 MPa throughout.

### 4.3 Parameter classification

**Table 4.** Model parameters, classified. *This table is the core of the validation claim.*

| Parameter | Symbol | Value | Class | Source |
|---|---|---|---|---|
| Young's modulus | $E$ | 67 GPa, all four | measured | Ye & Ghassemi §2.1 |
| Poisson's ratio | $\nu$ | 0.32 | measured | Ye & Ghassemi §2.1 |
| Biot coefficient (matrix) | $\alpha$ | 0.6 | literature | not reported by Ye & Ghassemi |
| Fracture pressure–area coefficient | $\alpha_f$ (§3.6.1) | 1.00, 1.00, 0.87, 0.86 | calibrated | constant per specimen; not identifiable separately from $\alpha$ (§6.2) |
| Porosity | $\phi$ | 0.001 | **assumed** | not reported; below the 0.005–0.01 typical of granite |
| Matrix permeability | $k_m$ | $5\times10^{-19}$ m² | measured | Ye & Ghassemi §2.1 (low end of $5\times10^{-19}$–$1\times10^{-18}$) |
| Fluid density | $\rho_f$ | 1000 kg m⁻³ | literature | — |
| Fluid viscosity | $\mu_f$ | $1.002\times10^{-3}$ Pa s | measured | Ye & Ghassemi §2.5, water at 20 °C |
| Fluid bulk modulus | $K_f$ | 2.2 GPa | literature | water at 20 °C; **was 4.78 GPa (2.17× too stiff) in the pre-audit decks** |
| Confining pressure | $\sigma_3$ | 30 MPa | measured | Ye & Ghassemi §2.4 |
| Production pressure | $P_o$ | 5 MPa | measured | Ye & Ghassemi §2.4 |
| Joint roughness coefficient, SW-T1/T2 | JRC | 15.32, 14.63 | measured | Ye & Ghassemi §2.2 |
| Joint roughness coefficient, SW-S3 | JRC | 1.96 | measured | Ye & Ghassemi §2.2; **was 23.35 in the pre-audit decks** |
| Joint roughness coefficient, SW-S4 | JRC | 5.0 | calibrated | measured value is 1.19; see note (a) |
| Joint wall strength, all four | JCS | 150 MPa | substituted | UCS, Ye & Ghassemi §2.1; **was 300 MPa for the saw cuts** |
| **Fracture angle** | $\theta$ | 29.03–32.00° | **derived** | **Appendix A.1**; all four meshes now honour it |
| **Series compliance** | $\Omega$ | $1.61$–$4.42\times10^{-12}$ m Pa⁻¹ | **derived** | **Appendix A.2** |
| **Flow geometry factor** | $W/L$ | 0.813–0.817 | **derived** | **Appendix A.3** |
| Reference hydraulic aperture | $a_{h0}$ | 0.745–2.10 µm | derived | cubic-law inversion of stage-1 $Q$ |
| Reversible normal compliance | $C_n$ | $3.1$–$47\times10^{-13}$ m Pa⁻¹ | derived | $\Delta d_n / \Delta \sigma'_n$, stages 6–11 |
| Axial preload | $\bar{u}_z$ | per specimen | **gated** | matched to stage-1 $\tau$, §5.1 |
| Normal-closure exponent | $p$ | 4, 4, 4, 2 | calibrated | unload stiffening, §3.4 |
| Barton–Bandis residual angle | $\phi_r$ | 29.756° (×3), 22.72° | calibrated | slip onset; note (b) |
| Joint cohesion | $c$, $c_{\text{res}}$ | see below | calibrated | last stick stage; note (b) |
| Dilation angles | $\psi_p$, $\psi_r$ | per specimen | calibrated | permanent $d_n$ |
| Dilation-propping coefficient | $\chi$ | 0.0160, 0.0165, 0.0010, 0.0010 | calibrated | $a_h$ at peak |
| Cumulative-dilation feed | $\lambda$ | 0, 0, 0.038, 0.0117 | calibrated | saw cuts only; §3.6 |
| Unload retention fraction | $f$ | per specimen | calibrated | $d_n$ recovery |
| Viscous regularisation | $\eta_t$ | $4\times10^{11}$ (×3), $3.5\times10^{12}$ | calibrated | §3.9; not purely numerical, see §6.8 item 11 |

Values are listed in the order SW-T1, SW-T2, SW-S3, SW-S4 wherever four are given. The calibrated
strength parameters, per specimen:

| | JRC | JCS (MPa) | $\phi_r$ (°) | $c$ (MPa) | $c_{\rm res}$ (MPa) |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 15.32 | 150 | 29.756 | 26.88 | 9.19 |
| SW-T2 | 14.63 | 150 | 29.756 | 33.20 | 9.71 |
| SW-S3 | 1.96 | 150 | 29.756 | 1.67 | 1.40 |
| SW-S4 | 5.0 | 150 | 22.72 | 0 | 0 |

Three features of this table are worth pointing out rather than leaving to be noticed. The residual
friction angle is the *same* on three of the four specimens, and it is not a fitted value but the
basic friction angle measured on this campaign's own saw cut — so those three envelopes are pinned
by cohesion alone. SW-S4 is the exception on two counts: its cohesion is identically zero, which is
correct for a lapped saw cut with no interlock but leaves $\phi_r$ and $D_c$ carrying the entire
response (§6.4), and its JRC is calibrated rather than measured. And by the identifiability argument
of §3.5.2, JRC, JCS and $c$ are not three independent constraints but one combination; they should
be read as a set.

Three of these rows were calibrated in earlier versions of this model and are now measured,
substituted or derived. How that happened is worth recording, because in each case the earlier
calibration reproduced the *peak* strength correctly and failed on a quantity the peak does not
constrain.

**(a) The saw cuts: JRC, JCS and residual friction were compensating one another.** Ye and Ghassemi
measure JRC = 1.96 (SW-S3) and 1.19 (SW-S4) by 3-D laser scan and the Yu and Vayssade correlation,
and report a UCS of 150 MPa. Earlier versions of these decks ran JRC = 23.35 and 17.50 — 11.9 and
14.7 times the measured values, and in SW-S3's case outside Barton's 0–20 scale — together with
JCS = 300 MPa, and compensated both with residual friction angles of 8.45° and 7.50°, below any
measured granite. The three errors cancel at the calibration point, so both specimens still
reproduced their measured peak $\tau$. What did not survive was
$\mathrm{d}\tau/\mathrm{d}\sigma'_n$, 28 % too flat on both — and that derivative is what this
experiment exists to measure, because injection sweeps $\sigma'_n$ down by a factor of two.

Refitting with the paper's own JRC and JCS = UCS, holding each envelope through its specimen's last
stick stage, gives $\phi_r = 29.76°$ for SW-S3. Two independent checks say this is the right
parameterisation rather than merely a different one. It lands in the measured granite
basic-friction range, where 8.45° lands nowhere. And the refitted envelope is nearly flat in $\mu$
across the injection sweep — on SW-S4, 0.456 rising to 0.464 — where the old one rose steeply,
0.462 to 0.580. That steep rise is the strength "lock" the deck lineage spent four tuning
generations fighting, and it was an artefact of the invented JRC: the paper's own SW-S4 data are
fitted almost exactly by a single straight Coulomb line. Flattening it also moves SW-S4's
slip-weakening slope from just above the measured system stiffness ($1.326\times10^{11}$ against
$k_{\rm sys} = 1.25\times10^{11}$ Pa/m) to just below it ($1.224\times10^{11}$) — off the strength
cliff of §3.5.5, which is why the specimen became tractable.

SW-S4 retains a calibrated JRC of 5.0 rather than its measured 1.19. At the measured value the
onset stage was missed; the fitted value recovers it, and brackets either side score worse. We flag
it as calibrated in Table 4 rather than presenting the specimen as fully measured-parameter driven.

**(b) The tensile pair: a cohesion was being carried as a friction angle.** SW-T1 and SW-T2 already
used their measured JRC and JCS, yet required $\phi_r = 44.1°$ and $46.3°$, because both sustain
$\mu = \tau/\sigma'_n$ of 1.17–1.27 while still stuck. The cause is structural. Barton's roughness
term is mobilisation-limited — it decays to zero as $\sigma'_n$ approaches JCS — and these specimens
sit at $\sigma'_n/\mathrm{JCS} \approx 0.38$, where the measured JRC buys only 6.4° of roughness
angle. A $\mu$ of 1.17 then has nowhere to live except $\phi_r$, because the law as originally
implemented had no cohesion term at all.

But shearing *through* asperities is a cohesion, not a friction: its strength does not scale with
confinement. The law now carries a cohesion and a residual cohesion, decaying on the same
slip-weakening curve as friction (§3.5.2). Refitting with $\phi_r$ fixed at the basic friction angle
measured on this campaign's own saw cut, 29.756°, gives $c = 26.88$ MPa for SW-T1 and 33.20 MPa for
SW-T2. Those are 89 % and 110 % of the 30.30 MPa intact-rock cohesion implied by the paper's own
UCS = 150 MPa and intact $\phi = 46°$. The two straddle the intact value, and nothing in the
derivation knows about it — which is the expected signature of a fully mated Mode-I fracture whose
asperities *are* intact rock, and the physical statement the old $\phi_r = 44$–$46°$ was standing in
for.

**(c) Fluid bulk modulus.** Earlier decks used 4.78 GPa, 2.17 times too stiff for water at 20 °C.
It is read in exactly one place, the matrix constitutive model, and the fracture flow uses the
transmissivity instead, so the correction to 2.2 GPa changes matrix storage by about 6 % and nothing
else. We record it because an earlier version of this note asserted that the stiff value was being
handed to the fracture fluid, where it would have mattered during the burst. It was not.

Three quantities usually treated as free — the fracture angle, the load-train compliance and the
flow geometry factor — are here *derived* from the published table without adjustment. Their
derivations are given in Appendix A, and each is over-determined: the fracture angle is recovered
independently at all eleven hold stages, and the compliance from two independent regressions that
agree to four significant figures.

The axial preload is *gated* rather than calibrated: it is adjusted so the pre-slip shear traction
matches the stage-1 value, an operation that is decoupled from the constitutive parameters because
the joint is still stuck at that instant (§5.1).

### 4.4 Verification and validation protocol

We separate the two. **Verification** asks whether the equations are solved correctly;
**validation** asks whether the equations describe the experiment. Verification results are §5.1;
validation is §5.2 onwards.

Verification comprises: (i) mesh convergence of the pre-slip elastic state and of the peak slip;
(ii) a global fluid mass balance across the injection and production boundaries; (iii) an
independent check of the flow rate that uses neither a boundary reaction nor a fitted geometry
factor (Appendix B); (iv) confirmation that the fracture area, orientation and injection-node
placement in the mesh match the intended geometry; and (v) the preload gate.

---

## 5. Results

### 5.1 Verification

**Geometry.** The fracture angle in each mesh agrees with the value recovered from the published
table (Appendix A.1) to within 0.03° for all four specimens, and the meshed interface is planar to
within numerical precision. The interface area matches the exact ellipse to 0.30 % on the coarse
mesh and 0.05 % on the medium mesh, converging at second order or better; Table 2 gives the full
comparison. `[Verified 2026-08-07.]`

**Injection point.** All injection and production coordinates lie exactly on fracture nodes, with
zero snap distance. `[Verified 2026-08-06.]`

**Preload gate.** Pre-slip shear traction at the first hold stage, against Table 2, for the four
reported runs:

| Specimen | simulated $\tau$ (MPa) | Table 2 (MPa) | error |
|---|---:|---:|---:|
| SW-T1 | 67.58 | 67.16 | +0.63 % |
| SW-T2 | 73.86 | 74.87 | −1.35 % |
| SW-S3 | 13.73 | 14.70 | −6.59 % |
| SW-S4 | 12.35 | 12.56 | −1.70 % |

Three of the four gate to better than 2 %. SW-S3 does not, and the reason is procedural rather than
physical: its axial preload was gated on an earlier mesh, and the specimen was subsequently remeshed
to the corrected 123.40 mm fracture length (§4.1) without the gate being re-applied. The residual is
a constant offset present from stage 1, not an accumulating error, and it propagates into that
specimen's shear-stress score (8.01 % nRMSE, the second worst of the four). Re-gating SW-S3 is
outstanding and would be expected to improve it; we report the ungated number rather than an
estimate of the improvement.

**Mass balance.** Injected and produced mass fluxes, recovered from the tagged residual vector,
balance to 4.3 % at steady state during the first hold stage. `[Measured on SW-T1.]`

**Mesh convergence.** The four reported runs use the medium mesh. Coarser-mesh siblings were run
for all four; at the time of writing they are incomplete, so convergence is demonstrated over the
pre-slip branch only, on the stages both meshes reached:

| Specimen | stages compared | medium-mesh mean nRMSE | coarse-mesh mean nRMSE |
|---|---:|---:|---:|
| SW-T2 | 5 | 1.73 % | 1.72 % |
| SW-S3 | 4 | 2.08 % | 2.00 % |
| SW-S4 | 10 | 6.34 % | 6.54 % |

The pre-slip response is effectively mesh-insensitive on all three. SW-S4, which reaches ten of
eleven stages and therefore spans its slip event, carries a mesh penalty of +0.20 points, with the
largest systematic shift through unloading about 0.0018 mm in shear slip. Refinement slightly
improves $Q$ and both stresses at the peak stage and slightly worsens both displacement channels.
SW-T1 reached no Table 2 stage on the coarse mesh and supplies no evidence; separately, its two
meshes differ by 3.1 % in injection–production separation, so that pair would not be a pure
discretisation comparison even when complete. We therefore claim mesh-insensitivity of the pre-slip
state, and note that SW-S4's stage-4 residual (§5.3) persists under refinement, which is what
identifies it as constitutive rather than an artefact of discretisation.

### 5.2 Stress and displacement histories

Table 5 gives the five-observable comparison against Table 2 for all four specimens. Errors are
normalised RMS: the root-mean-square residual over the eleven hold stages, divided by the range of
the Table 2 values for that observable, so that quantities with different units and very different
absolute magnitudes can be placed on one scale. The case score is the unweighted mean over the five
independent quantities identified in §2.2. Because the model displacements are zeroed at stage 1 to
match Table 2's convention, stage 1 is a constructed zero and is excluded from the two displacement
statistics.

**Table 5.** Normalised RMS error against Table 2, five independent observables.

| Specimen | $Q$ | $\sigma'_n$ | $\tau$ | $d_n$ | $d_s$ | **mean** |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 7.38 % | 1.98 % | 2.73 % | 9.06 % | 1.02 % | **4.44 %** |
| SW-T2 | 5.87 % | 1.26 % | 1.70 % | 2.06 % | 1.25 % | **2.43 %** |
| SW-S3 | 3.00 % | 3.35 % | 8.01 % | 7.42 % | 1.11 % | **4.58 %** |
| SW-S4 | 4.94 % | 3.74 % | 10.01 % | 4.53 % | 7.01 % | **6.05 %** |

In absolute terms the stress residuals are 0.64 MPa mean absolute error on $\sigma'_n$ and 1.02 MPa
on $\tau$ for SW-T1, against stresses of 30–67 MPa; 0.42 and 0.72 MPa for SW-T2; 0.47 and 0.82 MPa
for SW-S3; and 0.44 and 0.73 MPa for SW-S4, against stresses of 12–31 MPa. Shear-slip residuals are
4.3 µm (SW-T1), 6.2 µm (SW-T2), 0.6 µm (SW-S3) and 4.1 µm (SW-S4).

Three points about the table are worth making before the specimen-by-specimen discussion.

**The ranking is not a ranking of physics.** Each specimen's nRMSE is normalised by its own
measured range, and the four ranges differ by a factor of five in stress. The numbers are comparable
between calibrations of the same specimen and should not be read as a statement that SW-T2 is
"better modelled" than SW-S4.

**Differences below about 0.1 points are not meaningful.** Running an identical deck on a different
machine reproduces $Q$, $\sigma'_n$ and $\tau$ to seven significant figures but moves the
normal-displacement error metric by up to 10.8 %, giving a floor of roughly 0.08 points on the mean.
No conclusion in this paper rests on a difference smaller than that.

**One score is worse than it could be, deliberately.** SW-S3's $d_n$ error is 7.42 %. An earlier
calibration reported 2.46 %, and a mean of 3.59 % rather than 4.58 %. The difference is not a model
change: it is the removal of two output-only settings that rescaled and partially retained the
reported normal opening without entering the residual, the Jacobian or the hydraulic aperture. With
them removed, all four specimens report the raw kinematic jump on the same basis. The worse number
is the defensible one, and we report it in preference to the better one because a fit applied in the
reporting path rather than the model is not a fit to anything.

### 5.3 Slip onset and the post-slip stress path

The signed residuals identify where each specimen's error is concentrated, and the pattern differs
between the burst specimens and the progressive one.

**The three burst specimens.** SW-T1, SW-T2 and SW-S3 each collapse within a single injection stage,
and for all three the largest residuals sit at the 28 MPa peak stage and on the unloading branch
that follows, not before. SW-T1 is systematically strong throughout, by +0.26 to +0.93 MPa in
$\sigma'_n$ and +0.42 to +1.48 MPa in $\tau$ — a level offset rather than a shape error, since the
sign never changes. SW-T2 crosses zero between stages 3 and 4, running weak early and strong late.
SW-S3's residual is dominated by the peak stage (+1.18 MPa in $\sigma'_n$, +2.24 MPa in $\tau$),
which is where the constant preload offset of §5.1 and the stress drop coincide.

Because the drop occupies one stage on all three, the characteristic slip distance is
unidentifiable for them: any $L_R$ shorter than the stage duration produces the same tabulated
result. This is the constitutive counterpart of the load-frame identifiability argument of §6.1, and
we report no fitted $L_R$ for these three.

**SW-S4, the progressive specimen.** Its residual is concentrated at a single stage and its
character is different. At stage 4 ($P_i = 20$ MPa) the model is +1.41 MPa strong in $\sigma'_n$,
+2.71 MPa strong in $\tau$, and 13.4 µm short in shear slip — the largest single-stage error in the
whole campaign. Every subsequent stage is smaller and of one sign. The model misses a slip increment
that the specimen produced during the *ramp* into stage 4, and then tracks the remainder of the test
with residuals a third that size.

Two things follow. First, the error is quantised by the injection schedule: a missed burst appears
as a single stage that is too strong, not as a drift, so "a few hundred seconds early or late" and
"one stage too weak" are the same statement. Second, this is the specimen where the slip-weakening
distance $D_c$ *is* identifiable, and it is over-determined in the unhelpful sense — stage 4 is
fitted by $D_c \approx 58\ \mu$m and stage 11 by 74 µm, and no single value satisfies both. Brackets
either side of the chosen value were run and both scored worse (16.9 % and 18.9 % mean nRMSE against
6.05 %), so the split is not resolvable by moving $D_c$. §6.4 gives the mechanism: this specimen's
cohesion channel is identically zero, so $D_c$ carries the post-peak response with nothing to trade
against.

**The pore-pressure basis does not survive slip.** The
assumption $P_p = \frac{1}{2}(P_i + P_o)$ used to reduce the published data holds before slip and
fails after it.
Before slip, the simulated mean fracture pressure sits at 0.55–0.67 of $(P_i - P_o)$ above $P_o$,
close to the assumed 0.50. After slip it rises to 0.85, because the dilated fracture equilibrates
toward the injection pressure. The reported and simulated $\sigma'_n$ therefore stop being
like-for-like on the unloading branch, and any comparison there must state which pressure basis
is being used.

### 5.4 Aperture and flow rate

Simulated hydraulic aperture at the first hold stage agrees with Table 2 to 1.3 % for SW-T1
(1.610 µm against 1.63 µm). Flow rate over the full cycle is scored in Table 5, at 3.00 % to 7.38 %
nRMSE across the four specimens — the best-fitted of the five observables on SW-S3 and among the
worst on SW-T1. Hydraulic aperture and permeability are not scored, because Table 2 obtains them
from $Q$ through the cubic law rather than measuring them (§2.2), so comparing them adds no
independent information.

**The flow channel does not report the same thing on every specimen.** Under the aperture model of
§3.6 the hydraulic aperture is sourced from the mechanical opening for the two tensile fractures,
and carries an additional fitted dilation feed on the two saw cuts. The consequence is visible in
the correlation between hydraulic aperture and normal opening over the injection cycle: 1.000 on
SW-T1, 0.999 on SW-T2, 0.946 on SW-S3, and 0.562 on SW-S4. On the first three, $Q$ is effectively a
readout of the fracture's opening and can be discussed as such. On SW-S4 it is not; it tracks the
effective normal stress instead, because the dilation feed was reduced roughly seventeen-fold to
hold the aperture against the measured flow. SW-S4's flow result and its dilation result are
therefore two findings, and the natural inference — that a good $Q$ score there confirms a good
aperture prediction — does not hold.

The flow rate does not agree as well as the aperture, and the disagreement is systematic rather
than random. At
the first hold stage of SW-T1, with the pressure drop at exactly 3.000 MPa:

| quantity | value (mL min⁻¹) |
|---|---|
| solved injection flux | 0.0277 |
| independent flux integral (Appendix B) | 0.0257 |
| cubic law evaluated on the simulated aperture | 0.0508 |
| Ye & Ghassemi Table 2 | 0.053 |

The two independent simulated measures agree with each other to 7 %, and both fall to about half
the reported value. The cubic-law evaluation, by contrast, reproduces the reported value to 4 % —
but that agreement is circular, since the reported $Q$ and the cubic law are related by the same
equation used to obtain the reported $a_h$.

The interpretation is a flow-geometry difference. The published reduction replaces the elliptical
fracture with an equivalent rectangle of width $W$ and length $L$, giving $W/L = 0.814$
(Appendix A.3). The model solves the actual two-dimensional field on an ellipse with point
injection and production, whose effective $W/L$ is approximately 0.43. Part of the difference is
already visible in the published reduction itself: a purely geometric estimate of the borehole
separation measured in the fracture plane gives 77 mm for SW-S4 rather than the 70 mm implied by
Table 2, which alone would lower $W/L$ to about 0.67. The remainder is the convergence of flow
into a point source rather than a distributed inlet.

This is worth stating plainly rather than absorbing into a fitted parameter. The apertures agree;
the flow rates differ by a geometry factor that the published data cannot resolve, because the
paper does not report $W$ or $L$.

### 5.5 Comparing the two strength envelopes

The Barton–Bandis envelope of §3.5.2 is compared against a linear Mohr–Coulomb baseline built for
this purpose. The baseline is not a fresh calibration: each specimen's linear envelope is a
tangent-match transfer of its own already-fitted Barton–Bandis envelope at the onset effective
normal stress, so a pair differs in constitutive *form* rather than in fitted strength, and the
comparison is not confounded by one law having been tuned harder than the other. Everything the
two decks share — mesh, boundary conditions, injection schedule, flow constants, solver — is
byte-identical.

One thing the pair deliberately does **not** test is normal closure. The Mohr–Coulomb decks carry
the same power-law closure law of §3.4, with the same $K_{ni}$, $v_m$ and exponent, as their
Barton–Bandis siblings. The comparison therefore isolates the shear response: a log-curved envelope
against a straight line through the onset tangent, an exponential weakening path against one linear
in the roughness state, and one characteristic distance instead of two. Any claim about nonlinear
*closure* would require a different pair of decks, and we make none.

`[PENDING — Table 6 and Figure F2: the five-observable scores for the four Mohr–Coulomb runs
alongside Table 5, and the per-stage comparison. The decks are built and validated; the runs are
queued. Three build checks must pass before the numbers are believed: slip onset must land on the
same injection stage as the Barton–Bandis sibling, since the peak envelopes agree to 0.09 MPa;
$Q$ must agree to better than 1 % at stages 1–5, before anything has yielded; and $\sigma'_n$ and
$\tau$ must agree at stage 1.]`

A caveat that will shape how the result can be read, whichever way it falls. The two envelopes are
tangent by construction at the onset stress, and they separate only as $\sigma'_n$ moves away from
it. Over the range this experiment actually sweeps, that separation is small: the two
parameterisations differ by about 3 % in $\mathrm{d}\tau/\mathrm{d}\sigma'_n$, not by the large
factor a wider stress sweep would produce. This dataset therefore cannot be expected to
discriminate the two *forms* on envelope slope alone, and §6.3 treats the comparison as a
performance question — which law reproduces Table 2 better, under a matched calibration procedure —
rather than as a test of which envelope shape is correct.

---

## 6. Discussion

### 6.1 What the published data constrains, and what it does not

The central methodological result of this study is that a well-reported laboratory table can
contain more constraint than it appears to. Ye and Ghassemi tabulate both $\sigma'_n$ and $\tau$
at every stage; because these are two projections of one stress state, the fracture angle follows
from their ratio without any free parameter, at every stage independently. The eleven estimates
agree, and they agree with the meshed geometry to 0.03°. The same table, combined with the
constant-piston-displacement condition, yields the series compliance of the loading column.

The corollary is equally useful: the same analysis shows what the data *cannot* constrain. The
load-frame stiffness is separately identifiable only when it forms a substantial fraction of the
total series compliance. For the two rough specimens, which slip more than half a millimetre, it
accounts for about half; for the smooth specimens, which slip a tenth as much, it accounts for
19 % or less, and for SW-S3 the inferred series compliance falls below the compliance of the rock
column alone. Attempting to fit a machine stiffness to the smooth specimens produces a number, but
not an identifiable one. Reporting four per-specimen machine stiffnesses spanning a factor of 32
would misrepresent this as physical variability.

### 6.2 What the pressure–area coefficient cannot be constrained to

The fracture pressure–area coefficient $\alpha_f$ is the parameter this dataset constrains least,
and saying so precisely is more useful than reporting a fitted value.

**It is nearly inert on half the specimens.** SW-T1 and SW-T2 run $\alpha_f = 1$ — the historical
assumption, unattenuated — and reproduce Table 2 at 4.44 % and 2.43 % mean nRMSE. Whatever
mechanism $\alpha_f$ would represent, the two tensile fractures do not need it. The two saw cuts
carry 0.87 and 0.86, an attenuation of under 15 %, and they are also the two specimens whose
scores are worst. There is no evidence here that a fitted $\alpha_f$ is buying agreement.

**It is not separately identifiable from the matrix Biot coefficient.** Both enter slip onset
through the same channel — how much of a pore-pressure increment is converted into a reduction of
the normal traction the walls feel. With $\alpha = 0.6$ assumed for the matrix rather than measured
(§4.3), a change in $\alpha_f$ can be absorbed almost exactly by a compensating change in $\alpha$
over the range these specimens sweep. Reporting both as independently calibrated quantities would
misrepresent that. This is the same identifiability argument §6.1 makes for the load-frame
stiffness, applied to a coupling coefficient rather than a compliance, and it has the same remedy:
report the combination the data constrain, and state which individual parameter was held.

**No measurement exists to check it against.** Real contact-area fraction was not measured on these
specimens, so unlike $\sigma'_n$ or $\tau$ there is no observable to compare a trajectory to. This
is a materially weaker form of constraint than the rest of this paper's parameters carry, and §6.8
lists it as a limitation for that reason.

**A state-dependent form is implemented and untested.** §3.6.1 gives
$\alpha_f(\sigma'_n) = \sigma_0/(\sigma_0+\sigma'_n)$, which would make the coupling steepen as the
joint approaches failure — injection lowers $\sigma'_n$, a falling $\sigma'_n$ raises $\alpha_f$,
and a rising $\alpha_f$ converts the same pore-pressure increment into a larger traction reduction.
That is a positive feedback a constant coefficient cannot produce, and it would sharpen predicted
onset beyond what the strength envelope alone supplies. It is disabled in every run reported here.
We flag it as the next experiment rather than a finding: the test is whether a state-dependent run,
recalibrated by the same procedure, places onset inside the observed window on specimens where the
constant form does not — and §5.3 identifies which those are.

### 6.3 Roughness and the choice of strength envelope

`[PENDING — the four Mohr–Coulomb runs, §5.5. The claim to make is a performance claim: which law
reproduces Table 2 better across four specimens under a matched calibration procedure. Write it as
a comparison of scores against Table 5, per observable, not only on the mean.]`

Two things about that comparison should be settled in advance of the numbers, because they
determine what the result is allowed to mean.

**It is not a test of envelope shape, and it is not a test of closure.** §5.5 establishes both
limits: the two envelopes differ by about 3 % in slope over the range injection sweeps, and the
Mohr–Coulomb decks carry the same nonlinear closure law as their Barton–Bandis siblings by
construction. A result in either direction therefore says which *form* better organises the fit —
a curved envelope with two characteristic distances against a straight one with a single roughness
state — and says nothing about whether real joints close hyperbolically.

**The interesting outcome is the one where the difference is small.** If the two laws score within
the reproducibility floor of each other, the honest conclusion is that this experiment does not
require the Barton–Bandis form, and the argument for using it has to rest on parameter provenance
instead of fit quality — that JRC, JCS and the basic friction angle are quantities a laboratory can
measure independently, whereas a fitted $\mu$ and $c$ are not. That is a weaker claim than "the
nonlinear envelope is necessary," and it is the one the data would support. We prefer to state that
conditional now rather than discover the temptation to overclaim after seeing the scores.

**Where the two laws should genuinely diverge is on the specimen that slips progressively.** SW-S4
sheds strength across three hold stages rather than in one, so it is the only specimen whose
response resolves the *shape* of the weakening path rather than just its endpoints (§5.3). If the
comparison produces a difference anywhere, that is where to look for it — and by the same argument,
a difference confined to the three burst specimens would be evidence about onset timing, not about
the weakening law.

### 6.4 Why SW-S4 is the informative specimen

Two independent arguments converge on this specimen. The first is structural, and was made in
§2.3.2: as a lapped saw cut, SW-S4 is a manufactured discontinuity with no cohesion, no tensile
strength and no softening branch, whose geometry is a machining setting rather than a measurement
and whose planar idealisation is exact to 0.6 % in surface area. It exercises the smallest number
of constitutive mechanisms of the four, and every one of them is exercised in isolation. The second
is behavioural, and is the one the data force.

SW-S4 slips progressively rather than in a burst, and its differential stress falls smoothly from
the 20 MPa stage rather than collapsing at 28 MPa. Any model that produces an instability will
match the other three; only a model with the right strength *and* the right post-peak stiffness
will match SW-S4. In an earlier calibration, SW-S4 was also the specimen on which the model failed
most clearly: the Barton–Bandis case drove the differential stress through zero and into tension,
which is physically impossible in a triaxial compression test. The cause was traced to the
unloading branch of the normal-closure law recovering roughly three times more closure than Table 2
allows, which under a held piston sheds several megapascals of axial stress. This is a useful
illustration of the coupling: an error in the *normal* closure response appears as a failure in
the *axial stress* history, because the loading frame connects them. That specific failure is fixed
(task #12).

**A second episode on this same specimen is worth reporting, because it was a reporting error
masquerading as a constitutive one and the distinction is the whole lesson.** For most of this
calibration the simulated post-slip shear stress on SW-S4 appeared to go *negative* while Table 2
stayed small and positive. A sign reversal is not a magnitude error, so it could not be absorbed by
rescaling a friction parameter, and it was pursued for several deck generations as a genuine defect
of the dilation and residual-friction calibration. It was neither. The plotted differential stress
was being taken in the skeleton frame while Table 2 reports it in the total-stress frame, so the
model curve was low by $\alpha p$ throughout — an error that grows exactly as injection proceeds,
which is why it looked like a post-slip failure. It was caught by requiring two sibling
postprocessors that should agree to actually agree, and corrected in the reporting channel; no
constitutive parameter changed. SW-S4's final score is 6.05 % mean nRMSE (§5.2).

The general point is worth more than the specific bug. A postprocessor-only channel can fabricate a
model error that survives repeated calibration attempts, because every attempt is scored through
the same faulty channel and therefore fails consistently — which reads as a robust physical finding.
Before attributing a persistent residual to the constitutive law, check who computes the compared
quantity and in which frame, and prefer diagnostics that two independent operators can be made to
agree on.

What remains genuinely open on SW-S4 is narrower and is stated in §6.8: its cohesion channel is
identically zero, so the slip-weakening distance $D_c$ has no second parameter to trade against, and
its bracket splits — the stage-4 response wants $D_c \approx 58\ \mu$m while stage 11 wants 74 µm.
No single value satisfies both, which is why the specimen retains the largest shear-stress residual
of the four (10.01 % nRMSE on $\tau$).

### 6.5 What the plasticity formulation adds, and where it constrains the calibration

Three features of §3.5 change what can be claimed from a fit, independently of how well the fit
turns out.

**The dilation bound is a constraint on what a calibrated dilation angle can mean, whether or not a
solver enforces it.** Non-associative interface plasticity is standard, and the dilation angle is
normally reported as a calibrated property. The dissipation inequality
$\tan\psi \leq (1-\epsilon_D)\mu$ makes that reporting conditional: where the bound is enforced,
any $\psi$ above it produces the limiter value rather than $\tan\psi$, so the nominal angle is
decorative. For the two saw-cut specimens, with $\mu \approx 0.4$–$0.5$, it sits near $22$–$27°$ —
and their calibrated angles, 26.0° and 24.0°, sit just inside it. Those two numbers are therefore
close to a hard limit rather than freely fitted, which a reader cannot tell from the value alone.
We recommend reporting the realised ratio $\Delta g_n^{p}/\Delta\gamma$ alongside $\psi$ as general
practice: it costs one column and it distinguishes a fit from a saturated limiter.

The same inequality is more informative still when it is *not* used as a constraint but applied to
the measurements. §3.5.3 shows that both saw cuts report a Table 2 dilation angle exceeding their
own mobilised friction angle, which is inadmissible as shear dilation and identifies elastic joint
decompression inside the LVDT record. A thermodynamic bound thereby becomes a data-reduction
diagnostic, and it is the reason the saw-cut decks carry dilation angles below the value a naive
reading of the published displacements would demand.

**Kinematic routing determines the sign of a feedback, not merely its size.** Under compliant
routing, dilation reduces the contact stress and therefore accelerates slip; under kinematic
routing it increases the contact stress and decelerates it. A model that reproduces a measured
stress drop with the wrong routing is compensating one error with another, and will not transfer
to a different frame stiffness. The two are distinguishable in this dataset because Table 2
reports the normal displacement independently: only kinematic routing produces an opening
comparable with the LVDT record. Put more sharply, the data do not merely favour kinematic
routing, they rule out compliant routing outright: a fracture that dilates without its walls
separating cannot produce a normal-displacement record at all, regardless of what other parameters
are adjusted to compensate. This is a statement about how real fractures dilate, not only about
which implementation choice fits Table 2 better.

**The softening-stability criterion ties the constitutive fit to a measured machine property.**
$|\mathrm{d}Y/\mathrm{d}s| > k_{\rm sys}$ marks the end of the quasi-static branch, and $k_{\rm sys}$
contains the load-frame compliance derived in Appendix A. This is the practical reason to insist
that the compliance be derived rather than fitted: with it fitted, the stability threshold moves
with the calibration and a run that fails to converge cannot be diagnosed, because the criterion
and the parameter under test are the same object. With it measured, a failed run is an informative
result — the calibration has been pushed past the physical stability limit.

### 6.6 Cyclic injection: how much enhancement survives the first cycle

Cyclic or "soft" stimulation is proposed on the grounds that repeated pressurisation produces
permeability gain comparable to a monotonic injection at a lower peak pressure and with smaller
induced events. The mechanism usually invoked is progressive: each cycle damages the asperities a
little further — by fatigue of the contacting points, by subcritical growth of the cracks that root
them, by comminution of the material they shed — so that gain accumulates across cycles even though
no later cycle visits a pressure the first one did not. That is a claim about the constitutive
behaviour of a joint under repeated loading, and a model calibrated against a single monotonic cycle
can be asked directly whether it contains such a mechanism. The answer is informative either way,
and the negative answer is the more useful one, because it localises the missing physics.

#### 6.6.1 The numerical experiment

Each validated deck is rerun with one change and no others: the injection function becomes three
cycles to the specimen's own peak pressure, each followed by a bleed to the 8 MPa post-peak floor
that the published schedules themselves return to, with 200 s holds at both the peak and the floor.
Everything else — mesh, every constitutive parameter, every boundary condition, the solver and its
tolerances — is identical to the run scored in §5, so the pair isolates loading history alone.

**Table 7.** The three-cycle schedules. Each specimen keeps its own peak, its own ambient pressure
and its own pressurisation rate, all inherited from the parent deck of §5; the bleed limb uses the
same rate as the rise limb, so no specimen is cycled faster or slower than it was validated.

| Specimen | deck | ambient (MPa) | peak (MPa) | floor (MPa) | rise limb (s) | hold (s) | total (s) | parent (s) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| SW-T1 | `97_01` | 5.00 | 28.00 | 8.00 | 1638 | 200 | 10 375 | 3 500 |
| SW-T2 | `97_02` | 5.00 | 28.00 | 8.00 | 2278 | 200 | 13 881 | 2 853 |
| SW-S3 | `97_03` | 5.75 | 28.57 | 8.00 | 2567 | 200 | 15 793 | 4 802 |
| SW-S4 | `97_04` | 5.00 | 27.96 | 8.00 | 1719 | 200 | 10 816 | 3 500 |

Three features of the design carry the argument, and each of them rules out a specific confound.

*The peaks are equal.* A rising staircase — the design a stimulation engineer would actually run —
would confound gain produced by cycling with gain produced by reaching a pressure never previously
visited. Because every peak here is the same, any difference between cycle 1 and cycle 3 is
attributable to history alone. The cost is that the experiment answers a narrower question than a
field trial does; that is the intended trade.

*The readings are taken at holds, not on the limbs.* Two things contaminate a reading taken while
the pressure is moving. The viscous regularisation of §3.9 contributes an overstress $\eta_t\dot{s}$
that is first order on the ramps and relaxes to zero at rest — on SW-S4 it reaches 0.87 MPa — and the
matrix, at $k_m = 5\times10^{-19}$ m², has not equilibrated with the fracture. The 200 s holds let
both settle, so each cycle is read in the same state.

*The comparison is floor-to-floor.* The quantity of interest is hydraulic aperture and flow rate at
the 8 MPa hold, cycle 1 against cycles 2 and 3. Enhancement retained at the same low pressure, with
the fracture re-clamped onto its own asperities, is irreversible enhancement. Anything measured at
the peak conflates it with the reversible part of the closure law, which by construction returns
whatever it took (§3.4) and would inflate every cycle equally.

#### 6.6.2 The monotonic control is already in hand — with one qualification

The comparison does not need a separate control run. The 93-series decks of §5 are the same
specimens, the same parameters and the same meshes taken once to the same peak and back to the same
floor, so cycle 1 of each cyclic deck is a near-replica of a run that has already been scored
against measured data. This matters: it means any multi-cycle behaviour reported below is anchored
to a validated first cycle rather than to an unvalidated one.

The qualification is that "near-replica" is not "replica". The published schedule is an eleven-stage
staircase; the cyclic decks rise linearly to the same peak over the same interval. The endpoints,
the rate and the duration match, but the intermediate structure does not, and that structure is not
cosmetic — the campaign found that slip onset in these specimens is quantised by the injection step
that triggers it, so cycle 1 will not reproduce the §5 onset *time* exactly even though it
reproduces the peak state. The floor-to-floor ratios are ratios within a single run and are immune
to this; a direct comparison of cycle 1 against Table 2 stage by stage would not be, and is not
made.

Table 2's own first and last stages are, however, exactly a floor-to-floor pair for cycle 1: both
sit at the 8 MPa floor, one before injection and one after the specimen has been taken to peak and
bled back. The measured first-cycle retention is therefore already known, and it is strikingly
uneven across the four specimens:

**Table 8.** Measured cycle-1 retention, from Ye & Ghassemi Table 2 stages 1 and 11 (both at the
8 MPa floor). $a_h$ is their reported hydraulic aperture; the transmissivity ratio is its cube.

| Specimen | $a_h$ stage 1 (µm) | $a_h$ peak (µm) | $a_h$ stage 11 (µm) | retained | $T$ ratio |
|---|---:|---:|---:|---:|---:|
| SW-T1 | 1.63 | 4.05 | 3.36 | +106 % | 8.8 |
| SW-T2 | 2.11 | 4.92 | 4.21 | +100 % | 7.9 |
| SW-S3 | 1.22 | 2.10 | 1.64 | +34 % | 2.4 |
| SW-S4 | 0.74 | 1.07 | 0.74 | 0 % | 1.0 |

The first cycle is worth a factor of 8 in transmissivity on a rough tensile fracture and *nothing at
all* on the polished saw cut, which returns to its starting aperture to the reported precision. Any
statement about what cycles 2 and 3 add has to be read against that spread, and the polished saw cut
sets a floor on the whole argument: a joint with no roughness to damage has no first-cycle gain to
extend.

#### 6.6.3 What the constitutive law contains

Four history variables in §3.5 and §3.6 depend on cumulative plastic slip $s$. All four are monotone
in $s$, none of them reverses on unloading, and their signs do not all agree:

$$
W(s) = \exp\!\left[-\left(\frac{s}{D_c}\right)^{m}\right],
\qquad
\psi(s) = \psi_r + (\psi_p - \psi_r)\,e^{-s/L_\psi},
$$

$$
g_n^p(s) = \int \tan\psi\,\mathrm{d}s^p ,
\qquad
a_{\rm gouge}(s) = a_g\left[1 - e^{-(s-s^\ast)_+/L_g}\right].
$$

$W$ multiplies both the friction coefficient and the cohesive intercept, so it carries the entire
strength drop; $\psi$ sets how much normal opening each increment of slip produces; $g_n^p$ is that
opening accumulated, and is the source of retained aperture; and $a_{\rm gouge}$ *subtracts* from the
hydraulic aperture, representing wear products filling the void. The first three raise permeability
and the fourth lowers it.

Their calibrated values are not uniform across the four specimens, and two of the four channels are
switched off by parameter choice on most of them:

**Table 9.** The slip-history channels as calibrated. $\psi_p = \psi_r$ means the dilation angle is
constant, so the decay channel is inert; a dash means the term is disabled in the deck.

| Specimen | $D_c$ (µm) | $m$ | $\psi_p \to \psi_r$ (°) | $L_\psi$ (µm) | $a_g$ (µm) | $s^\ast$ (µm) | $L_g$ (µm) |
|---|---:|---:|---|---:|---:|---:|---:|
| SW-T1 | 150 | 1.4 | 16.44 → 16.44 | 150 | — | — | — |
| SW-T2 | 150 | 1.4 | 13.97 → 13.97 | 150 | — | — | — |
| SW-S3 | 60 | 1.4 | 26.00 → 26.00 | 100 | 0.40 | 30 | 30 |
| SW-S4 | 74.5 | 1.10 | 24.00 → 13.00 | 100 | 0.28 | 20 | 30 |

**SW-S4 is the only specimen whose dilation angle decays at all**, and the two saw cuts are the only
ones carrying a gouge term. On SW-T1 and SW-T2 the calibration is monotone-positive throughout:
nothing in the law makes later slip open the joint less than earlier slip, and nothing closes it. On
SW-S4 both negative channels are active at once. The four specimens are therefore not four samples
of one prediction — they are four different combinations of the available mechanisms, which is what
makes the comparison worth running.

#### 6.6.4 How much of each mechanism the first cycle already spends

Substituting each specimen's *measured* end-of-cycle-1 slip into the expressions above gives the
state the joint is in when cycle 2 begins. This is arithmetic on the calibrated parameters, not a
model result, so it can be stated before the runs:

**Table 10.** Exhaustion of each slip-history channel at the end of cycle 1, evaluated at the
measured final slip of Ye & Ghassemi Table 2.

| Specimen | slip (µm) | $W$ | strength spent | $\psi$ (°) | dilation decay spent | gouge spent |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 521 | 0.003 | 99.7 % | 16.44 | inert | inactive |
| SW-T2 | 552 | 0.002 | 99.8 % | 13.97 | inert | inactive |
| SW-S3 | 73 | 0.268 | 73.2 % | 26.00 | inert | 76 % (0.305 of 0.40 µm) |
| SW-S4 | 79 | 0.344 | 65.6 % | 17.99 | 55 % | 86 % (0.241 of 0.28 µm) |

Three readings follow, and they pull in different directions.

The tensile fractures reach residual strength within the first cycle and stay there — $W$ is
$3\times10^{-3}$, so the cohesive intercept that carries most of their peak strength (§6.3) has been
destroyed. But their dilation channel is untouched, because $\psi$ is constant: *if* cycles 2 and 3
produce slip, that slip opens the joint at exactly the same rate as cycle 1's did, and there is no
gouge term to take it back. For SW-T1 and SW-T2 the model contains no saturating mechanism in the
aperture channel at all.

The saw cuts are the opposite. Their strength is only two-thirds spent, so more weakening is
available, but their gouge terms are 76 % and 86 % exhausted — the characteristic slip $L_g = 30$ µm
is small against the 73–79 µm the first cycle produces. What remains is 0.095 µm of closure on
SW-S3 and 0.039 µm on SW-S4, against apertures of 1.64 and 0.74 µm. The gouge term can therefore
*reduce* a later cycle's gain but, at these parameters, cannot plausibly drive the aperture below
its cycle-1 floor by more than a few per cent. **The net-negative third cycle is possible but not
predicted; it would require cycles 2 and 3 to produce very little new slip while spending what
little gouge capacity remains.**

The dilation decay is a live channel on SW-S4 alone, where $\psi$ has fallen from 24° to 18.0° —
just over half way to its residual. That is the one specimen in which later slip genuinely does
dilate less per unit slip than earlier slip.

#### 6.6.5 Three admissible outcomes, and what each would mean

The runs can only land in one of three places, and the design is such that each is interpretable.

1. **No new slip.** The load frame sheds differential stress as the fracture slips (§3.5.5,
   §6.9), so by the time cycle 1 ends the driving shear stress may sit below the residual strength.
   Returning to the same peak pressure then reactivates nothing, every subsequent excursion is
   elastic, and the floor-to-floor ratio is 1.000 to solver precision. This is the most likely
   outcome for SW-T1 and SW-T2, whose strength is fully spent and whose stress drop was largest. Its
   meaning is sharp: in this model *permeability enhancement is a function of the highest pressure
   ever reached, not of the number of times it is reached*, and cycling at a fixed peak buys nothing
   whatsoever.
2. **Diminishing gain.** Some new slip occurs each cycle, dilating at the surviving angle, and the
   floor-to-floor increment shrinks monotonically. This is saturation, and it is the outcome that
   most resembles the field observation while still failing to explain it, since the field claim is
   that the increment persists.
3. **Net loss on the saw cuts.** Gouge outruns dilation and the cycle-3 floor sits below the
   cycle-1 floor. Table 10 bounds how large this can be — a few per cent of aperture, hence at most
   ten per cent or so of transmissivity — so if a large loss is observed it is not the gouge term
   and the run should be re-examined.

Outcome 1 and outcome 2 are distinguished by whether cumulative plastic slip increases at all after
cycle 1, which is a directly reported quantity; no inference is required.

#### 6.6.6 What the law cannot produce, whichever outcome occurs

None of the three outcomes is accumulation. That is not an accident of the calibration but a
structural property of the formulation: **every history variable is monotone in slip and every one
of them is either spent or spending, so nothing in the model makes a repeat cycle more damaging than
the first.** The mechanisms the soft-stimulation literature invokes for multi-cycle gain are all
absent by construction —

- *asperity fatigue*, which requires damage to accumulate with the number of load reversals rather
  than with the slip they produce, and therefore requires a cycle counter or a damage variable
  driven by stress amplitude; there is none;
- *subcritical crack growth* in the wall rock, which requires a time- and stress-dependent
  strength-degradation law with no slip in it at all;
- *progressive roughness degradation* independent of slip — the roughness state here is a function
  of $s$ alone, so a cycle that produces no slip produces no roughness change;
- *thermal effects*, excluded here by design (§2.4), which in the field contribute a contraction
  that reopens the joint on each cool-down.

If the runs saturate, the finding to report is therefore not "cyclic stimulation does not work". It
is that a constitutive law calibrated to reproduce four monotonic injection tests to 2.4–6.1 %
reproduces first-cycle enhancement and contains no mechanism for multi-cycle gain, so whatever
produces that gain in field trials lies outside it — and the model would systematically
under-predict the benefit of cycling for exactly that reason. Naming the missing mechanism, and
bounding how much of the observed effect it has to supply, is more useful to the next model than
reporting a gain factor from this one.

#### 6.6.7 Why the experiment is at specimen scale

It would be natural to ask this question on a field-scale fault instead, and we do not, for three
reasons in descending order of weight.

First, the Barton–Bandis formulation carries explicit scale corrections to JRC and JCS which are
disabled in all four calibrations (§6.9). Moving to field scale means switching on precisely the one
term this dataset does not validate, and Table 11 shows it is not a small correction.

Second, the claim would change character. At specimen scale, cyclic-against-monotonic is a
controlled numerical experiment on a validated model: same mesh, same parameters, same boundary
conditions, only the loading history differs, and the control has been scored against measured data.
At field scale it is an unvalidated demonstration in which every parameter has been extrapolated and
no residual can be computed. The first supports a conclusion about the constitutive law; the second
supports only an illustration.

Third, cost — a new mesh, a new in-situ stress state, new boundary conditions and new solver tuning
— for a result that would still rest on the extrapolation the first reason objects to.

The field-scale statement this study can support is made instead through the compliance argument of
§6.9, which transfers a mechanism rather than a parameter set.

`[PENDING — the four cyclic runs. Report: (i) floor-to-floor $a_h$ and $Q$ ratios, cycle 2 and
cycle 3 against cycle 1; (ii) cumulative plastic slip at each floor, which decides between outcomes
1 and 2 above; (iii) retained $d_n$ at each floor, to separate dilation-driven from
damage-driven enhancement; (iv) $W$, $\psi$ and $a_{\rm gouge}$ per cycle, to attribute the result
to the channels of Table 9; and (v) the peak-to-floor ratio within each cycle, which isolates the
reversible part. SW-S4 must be reported separately for the reason given in §5.4 — its flow channel
does not track its opening, so its $Q$ ratio and its $d_n$ ratio are two findings, not one.]`

Two caveats will travel with the result. SW-S4's parent deck carries fitted, time-anchored
loading-frame terms — a piston relaxation and a confinement bleed — which saturate and then hold, so
they do not diverge over a run three times longer than the one they were fitted on, but they do sit
at their saturated values for most of it. And cycles 2 and 3 start from the 8 MPa floor rather than
from ambient, so cycle 1's excursion is the longest in pressure range even though all three share a
peak; this is a second reason the comparison is made floor-to-floor rather than cycle-total to
cycle-total.

### 6.7 Shut-in: whether slip continues once injection stops

The shut-in runs ask a narrower question with a clean yes/no answer: after the injection pressure
has fallen back toward ambient, does slip keep growing? Each deck ramps to its own peak, holds past
onset, then relaxes exponentially toward ambient with a 150 s time constant as a proxy for wellbore
fall-off, and is then observed for a further 3000 s.

The reason this is not a trivial question is that the fracture and the matrix do not depressurise
together. The fracture bleeds through its own transmissivity, which the slip event has just
increased; the matrix bleeds by diffusion at $k_m = 5\times10^{-19}$ m². A pressure perturbation
that has diffused into the wall rock during injection therefore continues to feed the fracture after
the well is shut, and the effective normal stress on the joint can keep falling for some time after
the injection pressure has stopped. Whether that is enough to sustain slip depends on the balance
between the two drainage timescales and the residual strength — which is a model output, not an
input.

`[PENDING — the four shut-in runs. Report: whether shear slip continues to rise after injection
pressure has returned near ambient (the headline yes/no); the lag between the shut-in instant and
the peak slip rate; and residual hydraulic aperture at the end of observation against its
pre-injection value.]`

The field relevance is direct and is worth stating even if the answer is negative. Post-shut-in
seismicity is routinely observed and is the operationally awkward case, because it occurs when the
obvious control — stop injecting — has already been applied. A hydromechanical model that reproduces
delayed reactivation from diffusion alone, with no rate-and-state or poroelastic-stress-transfer
machinery added for the purpose, would locate part of that phenomenon in ordinary coupled
poroelasticity. A model that arrests promptly would say the opposite: that the observed delays
require a mechanism this formulation lacks, and would point at which one.

### 6.8 Limitations

1. Parameters were determined with knowledge of the experimental outcome. This is a validation
   study, not a blind prediction.
2. The fracture is planar and its roughness enters only through constitutive parameters, not
   through geometry. Aperture heterogeneity, channelling and contact-patch evolution are
   represented in an averaged sense.
3. The flow geometry factor cannot be resolved against this dataset (§5.4), so absolute flow rates
   carry a systematic that the aperture comparison does not. The same bias — a rectangular-slab
   reduction applied to a source that is not a distributed line inlet — plausibly affects other
   published aperture-from-flow inversions that use the same reduction; it is not specific to this
   dataset, only quantified for it here.
4. Injection is applied at a single node rather than over a finite borehole radius.
5. The quasi-static formulation with viscous regularisation cannot represent the dynamic phase of
   an unstable slip event; it represents the quasi-static states before and after.
6. The published $a_h$ carries a ~7 % systematic from the ambiguity in the flow path length
   (Appendix A.3), so aperture agreement should not be quoted tighter than that.
7. The fracture pressure–area coefficient $\alpha_f$ is a fitted constant per specimen (1.00, 1.00,
   0.87, 0.86), not independently validated against a measured contact-area fraction, and not
   separately identifiable from the assumed matrix Biot coefficient $\alpha = 0.6$ (§6.2). The
   state-dependent form the material implements is disabled in every run reported here.
8. On SW-S3 and SW-S4 the hydraulic aperture carries a fitted cumulative-dilation feed in addition
   to the kinematic one (§3.6), so on those two specimens flow and mechanical opening are not a
   single mechanism. The effect is quantified on SW-S4, where the correlation between hydraulic
   aperture and normal opening is 0.562 against 0.946–1.000 on the other three: its flow channel
   reports a stress state rather than an opening, and §5.4's flow result and §5.2's dilation result
   must be read separately there. Refitting the saw cuts with the dilation feed removed is the
   clean fix and would change their Table 2 scores.
9. SW-S4's cohesion channel is identically zero, so the slip-weakening distance $D_c$ carries the
   post-peak response alone. Its bracket splits between stages (§6.4) and no single value fits
   both ends of the test. This is the specimen's largest remaining residual.
10. The characteristic slip distance $L_R$ is identifiable only on SW-S4, whose slip is progressive
    across three hold stages. On the three burst specimens any $L_R$ below the stage duration gives
    the same tabulated result, so a fitted value for those would suggest a constraint the data do
    not supply (§3.7).
11. The viscous regularisation $\eta_t$ is not purely numerical at the calibrated values (§3.9).
    SW-S4 runs $3.5\times10^{12}$ Pa·s/m, 8.75 times the other three, and the resulting overstress
    reaches 0.87 MPa on the loading ramps. It relaxes to zero during the hold stages against which
    Table 2 is scored, so the reported comparison is not contaminated, but transient shear stresses
    between stages carry it.
12. The reported hydraulic-aperture model (§3.6) is the bounded, additive construction, not the
    closed-form Barton–Bandis–Bakhtar power law it is motivated by. The closed form was implemented
    and tested but destabilised the coupled solve at the slip/arrest transition (§3.6); it was not
    carried to a completed run, so this study offers no accuracy comparison against it, only the
    numerical reason it was not adopted.
13. Cohesion and JRC are not separately identifiable on this loading path (§6.3): the two
    parameterisations' envelopes differ by about 3 % in slope over the range injection sweeps.
    Reported JRC, JCS and $c$ values should be read as one calibrated combination, not three
    independently constrained properties.
14. Mesh convergence is demonstrated over the pre-slip response only (§5.1). The finer mesh-3 runs
    are still in progress at the time of writing, so the post-slip branch is not yet covered, and
    SW-T1's mesh-5/mesh-3 pair differs by 3.1 % in source-node separation, which is a geometry
    difference rather than a discretisation one.
15. Repeat runs of an identical deck on different machines agree to seven digits in $Q$,
    $\sigma'_n$ and $\tau$ but differ by up to 10.8 % in the normal-displacement error metric, giving
    a floor of about 0.08 percentage points on mean nRMSE. Differences below roughly 0.1 points
    between calibrations are therefore not meaningful and no ranking in §5 rests on one.
16. Two of the four slip-history channels are inert in most of the calibrations (§6.6.3). The
    dilation angle is constant on SW-T1, SW-T2 and SW-S3 — the fits chose $\psi_p = \psi_r$ — so
    only SW-S4 exercises the dilation-decay law, and the gouge term is enabled only on the two saw
    cuts. The monotonic tests these parameters were fitted to do not distinguish a decaying dilation
    angle from a constant one, which is why the fits are free to collapse it; a cyclic or
    reverse-shear test would.
17. The Barton block-size corrections to JRC and JCS are disabled in every run (§6.9.1). This is
    correct at the 95–104 mm fracture trace length of these specimens, but it means the study
    supplies no evidence for the one term a field-scale application must enable, and Table 11 shows
    the correction is large — at a 10 m joint length it would remove three-quarters of SW-T1's JRC
    and compress the four-specimen roughness contrast from 7.8× to 2.3×.

### 6.9 Implications

The load frame is not a laboratory inconvenience to be calibrated away; it performs physical work
that a field analogue must also perform. Because the axial boundary condition is a penalised
displacement (§4.2) rather than a fixed stress, the amount by which differential stress is free to
fall as the fracture slips is set by the *series* compliance of rock, frame and fracture together
(§3.5.5, Appendix A.2) — a rigid frame would suppress the stress drop entirely, and an infinitely
soft one would let it fall without bound. At field scale, the role the machine plays here is played
by the compliance of the host rock mass surrounding the fault: the same fault embedded in
compliant, fractured country rock unloads differently, under the same injected pressure, than it
would in stiff, intact rock — for exactly the mechanism §3.5.5's stability criterion makes
explicit, since $k_{\rm sys}$ is a property of the surroundings, not of the fault alone, and it
determines whether a given strength drop can be shed quasi-statically or must go dynamic. A
reservoir model that imposes remote stress as fixed — implicitly an infinitely stiff surrounding
medium — is the field equivalent of this experiment's rigid-frame limit, and by §3.5.5's own
criterion that is the limit in which the *least* slip is stably absorbed and dynamic rupture is
most easily triggered. Ignoring host-rock compliance is therefore not a neutral simplification: it
biases a hazard assessment toward under-predicting how much slip a given pressure perturbation can
accommodate aseismically before an unstable transient becomes necessary.

The calibrated dilation and retention parameters carry a second implication, for permeability rather
than stress. Because transmissivity scales with $a_h^3$ (§3.6), and because on the two tensile
fractures $a_h$ is sourced from the same normal eigen-opening that produces the LVDT-comparable
displacement (§3.5.4), the permeability enhancement predicted for those two is not a separately
fitted curve: it is the mechanical dilation, cubed. On the two saw cuts it is partly fitted, and
§5.4 quantifies how much — which is itself the useful warning, because a model that reports
permeability through a channel calibrated against the flow it is meant to predict will always look
successful.

`[PENDING — once §6.6's cyclic runs are complete: state the enhancement factor implied by each
specimen's calibrated dilation angle and retention fraction, and compare the roughness range's
spread in that factor against its spread in JRC, to say whether joint roughness alone is a useful
predictor of field-scale permeability gain or whether the retention fraction — which forms no part
of the published JRC characterisation — dominates it instead.]`

#### 6.9.1 What the calibrated roughness parameters may and may not be carried to

A caution about extrapolating any of this numerically. The Barton–Bandis formulation carries
explicit block-size corrections,

$$
\mathrm{JRC}_n = \mathrm{JRC}_0 \left(\frac{L_n}{L_0}\right)^{-0.02\,\mathrm{JRC}_0},
\qquad
\mathrm{JCS}_n = \mathrm{JCS}_0 \left(\frac{L_n}{L_0}\right)^{-0.03\,\mathrm{JRC}_0},
$$

in which $L_0$ is the laboratory reference length and $L_n$ the length of the joint being modelled.
Both exponents are negative and both are proportional to $\mathrm{JRC}_0$, so a joint longer than
the laboratory sample is predicted to be *both smoother and weaker-walled*, and the reduction is
steepest for the specimens that were roughest to begin with. The corrections are disabled in all
four calibrations reported here. That is the correct choice at laboratory scale — the fracture
trace length, the major axis of the ellipse of §4.1.1, is 95–104 mm against the 100 mm reference, so
$L_n/L_0 \approx 1$ and the correction would do nothing — but it means this study supplies no
evidence whatever for the one term that any field-scale extrapolation would have to switch on.

The size of that gap can be priced without running anything, by evaluating the corrections at the
calibrated $\mathrm{JRC}_0$ of each specimen:

**Table 11.** The Barton block-size corrections evaluated on this study's calibrated roughness, for
joints 1, 10 and 100 m long against the $L_0 = 0.1$ m laboratory reference. JCS is 150 MPa for all
four specimens. No run reported in this paper uses these values; the table exists to bound the
extrapolation, not to license it.

| $L_n$ | | SW-T1 | SW-T2 | SW-S3 | SW-S4 |
|---|---|---:|---:|---:|---:|
| 0.1 m (lab) | JRC | 15.32 | 14.63 | 1.96 | 5.00 |
| | JCS (MPa) | 150 | 150 | 150 | 150 |
| 1 m | JRC | 7.57 | 7.46 | 1.79 | 3.97 |
| | JCS (MPa) | 52.1 | 54.6 | 131.0 | 106.2 |
| 10 m | JRC | 3.74 | 3.80 | 1.64 | 3.15 |
| | JCS (MPa) | 18.1 | 19.9 | 114.4 | 75.2 |
| 100 m | JRC | 1.85 | 1.94 | 1.50 | 2.51 |
| | JCS (MPa) | 6.3 | 7.2 | 99.9 | 53.2 |

Two consequences deserve emphasis, because neither is apparent from the formulas at a glance.

**The correction is not a mild adjustment on the rough specimens.** At a 10 m joint length SW-T1
retains 24 % of its JRC and 12 % of its JCS. Since JCS enters the strength envelope inside a
logarithm and JRC multiplies it, the roughness angle $\mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n)$
falls from fifteen degrees or more to a few, and at high effective stress the logarithm can reach
zero and the roughness contribution vanish altogether — the mobilisation limit already discussed in
§3.5.2, but reached at field scale by ordinary reservoir stresses rather than by the extreme ones it
takes in the laboratory. The calibrated envelope does not survive the transfer in a recognisable
form, and neither does the aperture law that reads the same JRC (§3.6).

**The correction collapses the contrast this study is built on.** The four specimens were chosen
because they span JRC 1.96 to 15.32, a factor of 7.8, and §6.3 turns on comparing their behaviour
across that range. Applying the corrections compresses that spread to 4.2× at 1 m, 2.3× at 10 m and
1.7× at 100 m; by 100 m the roughest tensile fracture is *smoother* than the polished saw cut was in
the laboratory. Taken at face value, Barton's correction says that at field scale a fault's
laboratory roughness class barely matters — which, if true, would limit the transferability of any
laboratory roughness calibration, this one included. Whether it is true is not something these
experiments can address: the corrections were established on joint-length series in jointed rock
masses, not on 100 mm cores, and nothing in this dataset varies $L_n$ at all.

We therefore make no numerical transfer of JRC, JCS or the fitted cohesions to a larger joint. The
implications drawn above are mechanistic — they are carried by $k_{\rm sys}$ and the stability
criterion of §3.5.5, which are statements about how a compliant surrounding medium interacts with a
weakening interface and contain no length scale of their own.

A cheap way to close part of the gap, which we recommend to anyone extending the model rather than
attempt here, is to rerun the existing decks unchanged except for the scale correction enabled at
two or three values of $L_n$, and report how much of the calibrated strength and permeability
response it removes. That is a one-parameter sensitivity on a validated deck: no new mesh, no new
stress state, no new solver tuning, and it prices the extrapolation directly. It would not
*validate* the correction — only a joint-length series can do that — but it would convert an
unquantified caveat into a bounded one, which is the more defensible position for a formulation that
will eventually be asked to run at reservoir scale.

---

## 7. Conclusions

1. A three-dimensional cohesive-zone hydromechanical formulation, in which the fracture is a
   zero-thickness interface carrying its own Reynolds-equation flow within a Biot poroelastic
   matrix, reproduces the injection-induced slip and permeability enhancement measured in four
   granite fractures spanning JRC 1.96 to 15.32 to a mean normalised RMS error of 2.43 % to 6.05 %
   across five independent observables, with stress residuals of 0.4 to 1.0 MPa against stresses of
   12 to 67 MPa.
2. The published laboratory table over-determines the fracture orientation and the series
   compliance of the loading column. Both are recoverable without adjustment — the orientation to
   0.03° and the compliance from two independent regressions agreeing to four significant figures —
   which removes them from the calibration.
3. The same analysis shows the load-frame stiffness is not separately identifiable from the smooth
   specimens, because it forms less than a fifth of their total series compliance. The same is true
   of three constitutive quantities: cohesion and JRC trade against one another to within 3 % in
   envelope slope over the stress range injection sweeps, and the fracture pressure–area coefficient
   trades against the matrix Biot coefficient. Each should be reported as a constrained combination
   rather than as independently determined properties.
4. Simulated flow rates fall to about half the reported values at matching hydraulic aperture.
   This is a flow-geometry difference between the one-dimensional slab used to reduce the
   measurements and the three-dimensional field the model solves, not a constitutive error.
5. Of the eight quantities tabulated per stage, only five are independent; hydraulic aperture and
   permeability are algebraic consequences of the measured flow rate.
6. The dissipation inequality $\tan\psi \leq (1-\epsilon_D)\mu$ is informative as an admissibility
   *diagnostic* applied to the published measurements, independently of whether a solver enforces
   it. Both saw-cut specimens report a dilation angle exceeding their own mobilised friction angle
   — 31.8° against 31.3°, and 28.7° against 24.6° — which no amount of shear dilation can produce.
   The measured normal displacement on a low-friction joint therefore contains elastic joint
   decompression, not geometric override alone, and calibrating a dilation angle against the raw
   value over-predicts it. Where the bound *is* enforced, a calibrated dilation angle above it is
   never realised, so the realised ratio $\Delta g_n^{p}/\Delta\gamma$ should be reported alongside
   the nominal angle.
7. Routing dilation kinematically, as a normal eigen-opening rather than as a contact-stress
   reduction, reverses the sign of its feedback on strength and is the only form that yields a
   normal displacement jump comparable with the reported LVDT record. Where it is used consistently
   — as it is on the two tensile fractures — the mechanical gap becomes the single source of the
   hydraulic aperture, and flow tracks opening with a correlation of 0.999 or better. Where a
   separate dilation feed is retained alongside it, as on the two saw cuts, that correlation falls
   to 0.562 and the flow channel ceases to report an opening at all.
8. Per-step increment caps on slip and dilation are not admissible limiters. In one calibration a
   slip cap bound on 14 time steps and supplied about 30 % of the accumulated slip, making a
   numerical parameter the author of a physical result. Time-step control, event-aware substepping
   and reported viscosity are the substitutes that converge under refinement.
9. A persistent residual attributed to a constitutive law should be checked against the channel that
   reports it before it is believed. On the most-scrutinised specimen here, an apparent post-slip
   sign reversal in shear stress survived several calibration generations and was a stress-frame
   mismatch in a postprocessor, not a model failure. Because every attempt is scored through the
   same channel, a reporting error fails consistently and therefore reads as a robust finding.

---

## Appendix A. Recovering Geometry and Compliance from the Published Table

### A.1 Fracture orientation

The authors resolve the applied stresses onto the fracture using

$$
\sigma'_n = (\sigma_3 - P_p) + \sigma_d \sin^2\theta, \qquad
\tau = \sigma_d \sin\theta\cos\theta .
$$

Dividing eliminates the unknown differential stress:

$$
\tan\theta = \frac{\sigma'_n - \sigma_3 + P_p}{\tau},
\qquad P_p = \tfrac{1}{2}(P_i + P_o).
$$

Every quantity on the right is tabulated, so $\theta$ follows at each of the eleven hold stages
with no free parameter. Taking the median across stages:

| Specimen | $\theta$ recovered | $\theta$ in mesh | difference |
|---|---|---|---|
| SW-T1 | 32.00° | 32.000° | 0.00° |
| SW-T2 | 30.00° | 30.000° | 0.00° |
| SW-S3 | 29.03° | 29.000° | 0.03° |
| SW-S4 | 30.02° | 30.000° | 0.02° |

For SW-T2 this resolves a discrepancy: Table 1 of the original paper gives 31°, while its own
Table 2 implies 30.00°. We adopt the value implied by the stress data, since that is the value
with which the reported $\sigma'_n$ and $\tau$ were computed.

### A.2 Series compliance of the loading column

The axial piston is held at constant displacement, so between any two hold stages the total
column shortening is unchanged. Writing $\Omega = L/E + A/k_{\rm machine}$ for the series
compliance per unit axial stress, and resolving the fracture displacements onto the axis,

$$
0 = \Omega\,\Delta\sigma_d + \cos\theta\,\Delta d_s + \sin\theta\,\Delta d_n ,
$$

where slip shortens the column by $d_s\cos\theta$ and dilation lengthens it by $d_n\sin\theta$
(with $d_n$ reported negative for opening). Since $\sigma_d = \tau/(\sin\theta\cos\theta)$ is
obtainable from the tabulated $\tau$ and the angle of A.1, every term is known, and regressing
$\Delta\sigma_d$ on the kinematic term gives $\Omega$.

| Specimen | $\Omega$ (all stages) | $\Omega$ (slip burst alone) | $L/E$ | machine share |
|---|---|---|---|---|
| SW-T1 | $4.4158\times10^{-12}$ | $4.4138\times10^{-12}$ | $1.922\times10^{-12}$ | 56 % |
| SW-T2 | $3.8952\times10^{-12}$ | $3.8951\times10^{-12}$ | $1.981\times10^{-12}$ | 49 % |
| SW-S3 | $1.6139\times10^{-12}$ | $1.6173\times10^{-12}$ | $1.659\times10^{-12}$ | negative |
| SW-S4 | $2.1804\times10^{-12}$ | $2.5044\times10^{-12}$ | $1.772\times10^{-12}$ | 19 % |

The two estimates — a weighted regression over all stage transitions, and the single dominant
slip burst alone — agree to four significant figures for the three burst specimens, which is
strong evidence that the relation is the right one. They differ by 15 % for SW-S4, consistent
with its progressive rather than burst-like slip.

The machine share column is the identifiability statement of §6.1.

### A.3 Flow geometry factor

The published reduction replaces the elliptical fracture with an equivalent rectangle of the same
area, so $W = A/L$, and

$$
L^2 = \frac{a_h^3 A \Delta P}{12\mu_f Q}, \qquad \frac{W}{L} = \frac{A}{L^2}.
$$

Applied to the pre-slip hold stages, this gives $W/L = 0.814, 0.816, 0.813, 0.817$ for the four
specimens — agreement to ±1 %, which indicates the inversion is correct rather than accidental.

A caveat that should be carried into any use of the published $a_h$: a purely geometric estimate
disagrees. The boreholes sit 6 mm inside the sidewall, so their separation measured in the
fracture plane is $2(D/2 - 6)/\sin\theta = 77.0$ mm for SW-S4, not the 70 mm the inversion
implies. The paper does not state whether $L$ was measured in-plane or as a projection. Using
77 mm would raise every reported $a_h$ by about 7 %. We use 0.81 for consistency with the
published table, and treat $a_h$ as carrying a ~7 % systematic.

### A.4 Preload gating

`[Cross-reference: doc/verification_axial_preload_gate.md, which documents the procedure and its
design rationale in full.]`

---

## Appendix B. Measuring Flow Rate in a Split-Node Interface Formulation

Recovering the injected mass rate from a finite-element solution with a Dirichlet pressure
condition is normally done by summing the residual contributions at the constrained nodes. On a
split interface this requires care, and getting it wrong is silent.

The injection node lies on the fracture and is therefore duplicated by the interface split, so the
"injection point" is two coincident nodes. Summing the residual contributions saved by individual
kernels across that pair does not reproduce the nodal reaction: the leak-off term between the two
faces enters with opposite signs and cancels, and any kernel whose contribution is not explicitly
saved is missing entirely. In our case the Biot volumetric-expansion term fell into the second
category. The resulting flow estimate was low by a factor of 132.

The reliable construction is to tag the residual contributions of all kernels acting on the
pressure variable into an auxiliary vector, and to read the reaction from that vector rather than
from per-kernel accumulation. A tagged vector cannot omit a contribution, because tagging happens
at assembly.

We verify this against a measure that uses no reaction at all. With $a_h$ the hydraulic aperture,
$\boldsymbol{v}$ the in-fracture Darcy velocity and $\boldsymbol{e}$ the unit vector from
injection to production separated by $L_{\rm path}$,

$$
Q = \frac{1}{L_{\rm path}} \int_\Gamma a_h \left(\boldsymbol{v}\cdot\boldsymbol{e}\right)\,\mathrm{d}A ,
$$

which is exact for one-dimensional flow, since $\int a_h v_x\,\mathrm{d}A / L = W a_h v_x$. On
SW-T1 at the first hold stage the two measures agree to 7 % (0.0257 against 0.0277 mL min⁻¹),
while the per-kernel accumulation gives 0.00021 mL min⁻¹.

A corollary: with the reaction correctly recovered, injected and produced fluxes carry opposite
signs and balance to 4.3 %, which is a usable global mass-balance diagnostic. With the incorrect
construction the same diagnostic reported an apparent imbalance of 2300 %, which had been
misinterpreted as a physics problem.

---

## Appendix C. Comparing the Meshed Fracture with a Tomographic Reconstruction

§4.1.1 verifies the meshed fracture area against a closed-form ellipse, and §4.1.2 bounds the
surface area the planar idealisation omits using a JRC correlation. Computed tomography can replace
both the geometric assumption and the correlation with measurements. Because the comparison is
frequently made loosely, we set out what is and is not comparable, and at what resolution.

### C.1 What "fracture area" means, and which meanings are comparable

Three distinct quantities are all called the fracture area:

- $A_{\rm proj}$, the **projected** area of the fracture on its mean plane. This is what the model
  meshes and what appears in Table 2.
- $A_{\rm true}$, the **true** area of the rough surface, $\int\sqrt{1+|\nabla h|^2}\,{\rm d}A$
  over the mean plane. This exceeds $A_{\rm proj}$ and is what a triangulated tomographic surface
  reports by default.
- $A_{\rm contact}$, the area actually in mechanical contact at a given $\sigma'_n$, a fraction of
  $A_{\rm proj}$ that rises with normal stress.

A planar zero-thickness interface represents $A_{\rm proj}$ exactly and $A_{\rm true}$ not at all;
$A_{\rm contact}$ is a state variable of the constitutive law, not a mesh property. **Comparing a
meshed area against a triangulated CT surface area is therefore a category error** unless the CT
surface is first projected onto its own mean plane. Doing so would report a four to five per cent
"mesh error" on the tensile specimens that is nothing of the kind.

### C.2 A three-level protocol

**Level 1 — trace geometry.** Requires only the specimen dimensions and a photograph or a single CT
projection. The fracture meets the cylindrical surface on an ellipse whose axial extent is
$2R/\tan\theta$; measuring that extent gives θ without any stress reduction, and $A_{\rm proj} =
\pi R^2/\sin\theta$ follows. This is an independent check on the θ recovered in Appendix A from the
stress data, and the two disagreeing would be significant. Level 1 is available for any specimen
that has been photographed.

**Level 2 — segmentation and plane fit.** Requires a CT stack at any resolution that *detects* the
fracture, which is a far weaker requirement than resolving its aperture. The fracture void is a
high-contrast, low-attenuation feature and segments reliably.

1. Segment the void in each slice and collect the voxel centroids.
2. Fit a plane by total least squares. Its normal gives θ **directly**, with no assumption about
   the stress state, and the fit residual gives the r.m.s. and maximum out-of-plane deviation.
3. Project the segmented voxels onto the fitted plane and take the area of their alpha-shape. That
   is $A_{\rm proj}$, measured.

Level 2 delivers the two numbers that matter for justifying the mesh: $A_{\rm proj}^{\rm CT}$
against $A_{\rm mesh}$, which is a like-for-like comparison, and the out-of-plane deviation, which
is the quantitative statement of how good the planar idealisation is. For a saw cut the latter
should be tens of micrometres; for a tensile fracture in a 50 mm core, several hundred micrometres
to a millimetre. That contrast is itself the evidence for the argument of §2.3.2, and it is
measurable at ordinary laboratory resolution.

**Level 3 — the aperture field.** Requires resolving the void, and this is where the method meets
its limit for this experiment. Calibrating the partial-volume signal against a known gap yields a
local aperture map $a(x,y)$, from which follow:

- the mean mechanical aperture $\langle a\rangle$, comparable to the model's;
- the contact area fraction, the fraction of the plane with $a = 0$, comparable to the model's
  contact-area state variable — a quantity the flow data cannot constrain at all;
- the hydraulic aperture, from a Reynolds (local cubic law) solve on $a(x,y)$, comparable both to
  the model's $a_h$ and to the values Ye and Ghassemi invert from flow rate. This last comparison
  would settle the geometry-factor question of Appendix A.3 independently, since it computes the
  transmissivity of the actual void rather than assuming a rectangle equivalent to it.

**The resolution caveat must be stated rather than discovered.** A laboratory µCT scan of a 50 mm
core gives voxels of roughly 25–50 µm. The hydraulic apertures in this experiment span 9–70 µm
(Table 2), so the aperture is between one fifth of a voxel and two voxels. Level 3 is therefore
semi-quantitative at that scale unless the scan is done on a sub-core, at higher energy resolution,
or with a calibrated partial-volume correction, and any aperture map produced without one of those
should be treated as an upper bound biased by the point-spread function. Levels 1 and 2 are
unaffected: they need the fracture to be detectable, not resolved.

### C.3 What this study claims without tomography

No CT data accompany the published dataset, and none were available to us. The claims made here are
chosen so as not to require them. Both rest on $A_{\rm proj}$, which is determined exactly by the
reported radius and the inclination, and is verified against the mesh to 0.05 % in Table 2. The
omitted surface area is bounded, not measured, by the JRC correlation of §4.1.2, and enters only as
a bound on how much of the SW-T residual could be geometric. Should tomography of these or
equivalent specimens become available, Level 2 would convert that bound into a measurement, and
Level 3 would test the contact-area evolution, which is at present the least constrained part of
the model.

---

## Open Research

`[PENDING — required by AGU. Must include: the ORCA source at a tagged release with a DOI; the
input decks, meshes and journal files for all runs reported; the digitised validation curves with
their provenance; and the analysis notebooks. Zenodo archive of the repository at the submission
commit.]`

---

## Notation

| Symbol | Meaning | Units |
|---|---|---|
| $\alpha$ | Biot coefficient of the matrix | – |
| $\alpha_f$, $\sigma_0$ | fracture pressure–area coefficient, $\sigma_0/(\sigma_0+\sigma'_n)$; its reference stress | –, Pa |
| $a_h$, $a_m$ | hydraulic, mechanical aperture | m |
| $a_{h0}$, $a_g$ | reference hydraulic aperture, saturated gouge fill | m |
| $C_n$, $\sigma_{\rm ref}$ | reversible normal compliance, its reference stress | m Pa⁻¹, Pa |
| $c$, $c_r$, $c_s$ | interface cohesion; rough and smooth end members | Pa |
| $c_0$ | pre-seating closure offset | m |
| $D_c$ | Barton–Bandis slip-weakening distance | m |
| $d_n$, $d_s$ | reported normal, shear displacement | m |
| $d_{\rm rev}$ | reversible (recoverable) part of $d_n$ | m |
| $E$, $\nu$ | Young's modulus, Poisson's ratio | Pa, – |
| $\epsilon_D$ | dissipation margin in the dilation bound | – |
| $\epsilon_g$ | contact active-set smoothing width | m |
| $\eta_t$ | tangential (Perzyna) viscosity | Pa s m⁻¹ |
| $F$ | yield function | Pa |
| $f$ | unload retention fraction | – |
| $\boldsymbol{g}$, $g_n$, $\boldsymbol{g}_t$ | displacement jump in the local frame; normal, tangential | m |
| $g_n^{p}$, $\boldsymbol{g}_t^{p}$ | plastic normal (dilational), plastic tangential jump | m |
| $\Delta\gamma$ | plastic multiplier (slip increment magnitude) | m |
| JRC, JCS | joint roughness coefficient, joint wall compressive strength | –, Pa |
| $K_{ni}$, $v_m$ | initial normal stiffness, maximum closure | Pa m⁻¹, m |
| $k_f$, $k_m$ | fracture, matrix permeability | m² |
| $k_n$, $k_t$ | normal, tangential penalty stiffness | Pa m⁻¹ |
| $k_{\rm sys}$ | system unloading stiffness resolved on the fracture | Pa m⁻¹ |
| $L$, $W$ | equivalent flow length, width | m |
| $L_R$, $L_\psi$ | roughness-decay, dilation-decay characteristic slip | m |
| $M$ | Biot modulus | Pa |
| $\boldsymbol{m}$ | flow direction, $\boldsymbol{t}_t / \lVert\boldsymbol{t}_t\rVert$ | – |
| $m_\mu$, $m_c$, $m_\psi$ | interpolation exponents for $\mu$, $c$, $\psi$ | – |
| $\mu$, $\mu_r$, $\mu_s$ | friction coefficient; rough and smooth end members | – |
| $\mu_f$ | fluid dynamic viscosity | Pa s |
| $\Omega$ | series compliance per unit axial stress | m Pa⁻¹ |
| $P_i$, $P_o$, $P_p$ | injection, production, mean pore pressure | Pa |
| $p_c$ | contact pressure (compression positive; $= \sigma'_n$) | Pa |
| $\phi$, $\phi_r$ | porosity; residual friction angle | –, ° |
| $\psi$, $\psi_p$, $\psi_r$ | dilation angle; peak and residual values | ° |
| $Q$ | volumetric flow rate | m³ s⁻¹ |
| $R$, $\bar R$, $R_0$, $R_r$ | roughness state; normalised, initial, residual | – |
| $s$, $s^{*}$, $s_c$ | cumulative plastic slip; gouge onset, gouge distance | m |
| $\sigma_1$, $\sigma_3$, $\sigma_d$ | axial, confining, differential stress | Pa |
| $\sigma_n$, $\sigma'_n$ | total, effective normal stress on the fracture | Pa |
| $T$ | fracture transmissivity | m³ Pa⁻¹ s⁻¹ |
| $\tau$, $\tau^{\rm trial}$, $\tau_{\min}$ | shear traction; elastic trial value; residual floor | Pa |
| $\theta$ | angle between fracture plane and core axis | ° |
| $\chi$ | dilation-propping coefficient | – |
| $Y$ | interface shear strength | Pa |

---

## References

`[PENDING — to be completed in AGU style. Core set:]`

- Barton, N., Bandis, S., & Bakhtar, K. (1985). Strength, deformation and conductivity coupling of
  rock joints. *International Journal of Rock Mechanics and Mining Sciences*, 22(3), 121–140.
- Ellsworth, W. L. (2013). Injection-induced earthquakes. *Science*, 341(6142), 1225942.
- Garipov, T. T., Karimi-Fard, M., & Tchelepi, H. A. (2016). Discrete fracture model for coupled
  flow and geomechanics. *Computational Geosciences*, 20, 149–160.
- Grigoli, F., et al. (2018). The November 2017 M_w 5.5 Pohang earthquake: A possible case of
  induced seismicity in South Korea. *Science*, 360(6392), 1003–1006.
- Jha, B., & Juanes, R. (2014). Coupled multiphase flow and poromechanics: A computational model of
  pore pressure effects on fault slip and earthquake triggering. *Water Resources Research*,
  50(5), 3776–3808.
- McClure, M. W., & Horne, R. N. (2011). Investigation of injection-induced seismicity using a
  coupled fluid flow and rate/state friction model. *Geophysics*, 76(6), WC181–WC198.
- Permann, C. J., et al. (2020). MOOSE: Enabling massively parallel multiphysics simulation.
  *SoftwareX*, 11, 100430.
- Tse, R., & Cruden, D. M. (1979). Estimating joint roughness coefficients. *International Journal
  of Rock Mechanics and Mining Sciences*, 16(5), 303–307.
- Ucar, E., Berre, I., & Keilegavlen, E. (2018). Three-dimensional numerical modeling of shear
  stimulation of fractured reservoirs. *JGR: Solid Earth*, 123(5), 3891–3908.
- Willis-Richards, J., Watanabe, K., & Takahashi, H. (1996). Progress toward a stochastic rock
  mechanics model of engineered geothermal systems. *JGR: Solid Earth*, 101(B8), 17481–17496.
- Wilson, Z. A., & Landis, C. M. (2016). Phase-field modeling of hydraulic fracture. *Journal of
  the Mechanics and Physics of Solids*, 96, 264–290.
- Ye, Z., & Ghassemi, A. (2018). Injection-induced shear slip and permeability enhancement in
  granite fractures. *JGR: Solid Earth*, 123, 9009–9032.
