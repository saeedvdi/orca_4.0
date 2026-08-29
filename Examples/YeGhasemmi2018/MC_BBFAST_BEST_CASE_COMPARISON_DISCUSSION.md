# Discussion: best-case BBFast versus matched Mohr–Coulomb baselines

> **Status (2026-08-28): historical baseline discussion.** The 94/102-series
> conclusions below remain useful as controlled model-form history, but they are
> superseded for final figures by the equal-budget winners: SWT1 `pb04`, SWT2
> `pb04`, SWS3 `pb06`, and SWS4 `center`. See
> `FINAL_AUDIT_2026-08-28.md` and `MC_EQUAL_BUDGET_SWEEP_AUG27.md`.

## Scope of the comparison

The 102-series simulations test whether the preference for the Barton–Bandis/BBFast formulation
persists when the Mohr–Coulomb (MC) baselines receive the same specimen-specific scalar refinements
as the best physical BBFast cases in the updated ranking. The comparison includes SW-T1 maximum
closure, SW-T2 hydraulic-aperture scale, SW-S3 residual cohesion, and the unchanged authoritative
SW-S4 case. Each MC deck retains the mesh, loading schedule, boundary conditions, hydraulic
properties, closure law, solver settings, and reporting definitions of its paired BBFast case. The
principal change is therefore the shear-contact formulation and its associated weakening and
dilation evolution.

All four 102-series runs are numerically complete. Each reaches all eleven ordered Table-2 stages,
and none contains non-finite values, duplicated times, or a truncated final stage. Their poorer
agreement is consequently a model result rather than a failed-run artefact. Accuracy is evaluated
with the same stage-1 displacement datum and range-normalised root-mean-square error (nRMSE) used
throughout the validation campaign. Only the five independent measured quantities are scored:
flow rate, effective normal stress, shear stress, normal displacement, and shear displacement.

## Downloaded-result and run-coverage audit (2026-08-25)

The downloaded files do not represent a result for every input deck in the four specimen
directories. There are 178 campaign `.i` files, of which 118 have at least one result CSV that
maps back to the deck and 60 have no mapped result. This literal count includes many retired
legacy variants that were never selected for a production campaign, so it is an inventory result,
not evidence that 60 current jobs failed.

The named submission batches are substantially more complete. The 94, 97/98, 101, 103, and 104
batches have 4/4, 8/8, 16/16, 3/3, and 5/5 result CSVs, respectively. The older rescoped 95/96
submission manifest has 8/11: the missing files are the three rate-and-state level-matched
controls `95_01` (SW-T1), `95_05` (SW-T2), and `95_09` (SW-S3). The project documentation already
states that only the SW-S4 rate-and-state bracket was run, so these are remaining simulations,
not missing copies of known completed HPC outputs.

This audit treats the result CSV as the required scientific output because the ranking and all
committed comparison readers consume CSV data. It does not show that every HPC artifact was
downloaded: the four `results_exodus_hpc_rorqual` directories contain only one Exodus file in
total (`94_03` for SW-T2), and current Slurm `.out`/`.err` files are generally absent. HPC
checkpoints were explicitly disabled by the launch scripts. Consequently, completion can be
established from schedule coverage and CSV end time, but scheduler exit codes and most solver-log
diagnostics cannot be independently audited from this checkout.

All 16 series-101 files reach their scheduled end times. Twelve are scientifically valid and the
four SW-S4 files are `qualified_failed_pre_injection_falsifier`: their outputs are complete, but
the registered pre-injection check fails. All five series-104 files also reach their scheduled end
times and reproduce the committed 104 metrics. Series 101 and 104 use cyclic or shut-in schedules,
so they must not be inserted into the monotonic Table-2 ranking.

Recomputing the ranking against the downloaded sources changes the monotonic inventory from 71
complete and 15 partial cases to **74 complete and 12 partial cases**. Three replacement CSVs now
complete all eleven stages: `93_02` (SW-T1 mesh 3), `93_04` (SW-T2 mesh 3), and `93_06` (SW-S3
mesh 3). The downloaded `93_08` SW-S4 file also changes its score from 6.366967% to 6.288682%.
The selected mesh-5 BBFast and matched MC cases used in the headline comparison are unchanged.

The ranking arithmetic is internally consistent after this refresh: each mean is the average of
the five recorded nRMSE channels, accuracy is `100 − mean nRMSE`, complete runs alone receive a
rank, and ties use competition ranking on the published six-decimal score. The rank is a numerical
leaderboard, however, not a physical-selection list. It intentionally mixes model families,
meshes, controls, and historical cases; most notably, numerical rank 1 for SW-S3 is explicitly
marked `historical_unphysical`. Selection decisions must therefore use `selection_status` and the
notes together with `rank_within_sample`, rather than the rank column alone.

One superseded series-97 file, `97_03_sw3_cyclic3_hpc.csv`, has non-finite values in 50 channels
on its final row. Its time history is monotonic and the corrected series-101 campaign supersedes
it; it is neither a ranking source nor evidence against the current comparison. One local CSV,
`126_01_swt1_fluxfix_t320_local.csv`, has no matching input deck anywhere in this repository and
therefore cannot be independently reproduced from the files present here.

### Fresh mesh-3 comparison

The three newly completed 93-series files make the authoritative BBFast mesh comparison complete
for all four specimens:

| Specimen | mesh 5 mean nRMSE | mesh 3 mean nRMSE | mesh 3 − mesh 5 |
|---|---:|---:|---:|
| SW-T1 | 4.435159% | 5.527736% | +1.092577 pp |
| SW-T2 | 2.427821% | 2.258740% | −0.169081 pp |
| SW-S3 | 4.574322% | 4.759550% | +0.185228 pp |
| SW-S4 | 6.139187% | 6.288682% | +0.149495 pp |
| **Four-specimen mean** | **4.394122%** | **4.708677%** | **+0.314555 pp** |

Mesh 3 is 7.2% worse in the four-specimen mean, driven mainly by SW-T1, while SW-T2 improves
slightly. This is modest relative to the BBFast-versus-MC separation and does not change the model
comparison below. A corresponding four-specimen MC mesh comparison is still unavailable:
`94_02`, `94_04`, and `94_06` remain partial, while only SW-S4 `94_08` is complete.

## The transfer is verified, not merely asserted

The strongest single check on this comparison is that the paired arms are the *same model* until
they yield. Over Table-2 stages 1 to 4 the largest disagreement between each BBFast run and its
MC pair is 0.0003 MPa in shear stress for SW-T1, 0.0026 MPa for SW-T2, 0.00002 MPa for SW-S3 and
0.099 MPa for SW-S4.

The two envelopes also agree at the *other* end. Peak and residual $\tau_\mathrm{lim}$, taken
from each run's own limit-traction channel:

| Specimen | BBFast peak | MC peak | difference | BBFast residual | MC residual | difference |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 73.675 | 73.765 | +0.090 | 35.695 | 36.726 | +1.031 |
| SW-T2 | 80.108 | 80.223 | +0.114 | 36.371 | 35.896 | −0.475 |
| SW-S3 | 21.316 | 21.292 | −0.024 | 8.506 | 6.871 | −1.635 |
| SW-S4 | 15.735 | 15.758 | +0.024 | 6.096 | 6.722 | +0.626 |

Peak strength agrees to 0.12 MPa or better on every specimen, and the peak-to-residual *range*
agrees to within 2.5% on SW-T1, 1.3% on SW-T2 and 6.2% on SW-S4 (13% on SW-S3, the loosest).
The MC arm is therefore not a weaker model: it starts at the same strength and ends at the same
strength. Only the path between those endpoints differs. This forecloses the most obvious
objection to the comparison, and the manuscript should state it explicitly rather than leaving
the tangent match as a claim about how the decks were built.

## Aggregate performance

The best-case comparison strongly favours BBFast:

| Specimen | BBFast mean nRMSE | MC mean nRMSE | MC/BBFast error | BBFast reduction relative to MC |
|---|---:|---:|---:|---:|
| SW-T1 | 2.689% | 25.351% | 9.43× | 89.4% |
| SW-T2 | 2.132% | 23.365% | 10.96× | 90.9% |
| SW-S3 | 4.354% | 18.744% | 4.31× | 76.8% |
| SW-S4 | 6.139% | 8.969% | 1.46× | 31.5% |
| **Four-specimen mean** | **3.828%** | **19.107%** | **4.99×** | **80.0%** |

The improvement is not produced by one favourable observable. BBFast is more accurate in 19 of
the 20 specimen–observable comparisons. The one exception is SW-S4 shear displacement, for which
MC gives 6.178% nRMSE compared with 7.082% for BBFast. BBFast nevertheless remains more accurate
for the other four SW-S4 observables, including a large improvement in normal-displacement nRMSE
from 16.543% with MC to 4.633% with BBFast. The manuscript should therefore state that BBFast
improves 19 of 20 scored channels rather than claiming that every individual channel improves.

### Robustness to the normal-displacement channel

Normal displacement is the channel where the MC arm is most exposed to a capability gap rather
than to a constitutive difference (§"The normal-unloading gap" below). The aggregate result does
not depend on it. Recomputing the means over the remaining four observables only:

| Specimen | BBFast (no $d_n$) | MC (no $d_n$) | MC/BBFast |
|---|---:|---:|---:|
| SW-T1 | 2.215% | 23.859% | 10.77× |
| SW-T2 | 2.148% | 22.243% | 10.35× |
| SW-S3 | 3.899% | 16.520% | 4.24× |
| SW-S4 | 6.516% | 7.075% | 1.09× |
| **Four-specimen mean** | **3.694%** | **17.424%** | **4.72×** |

The headline moves from 4.99× to 4.72×, and the reduction from 80.0% to 78.8%. Reporting this
alongside the main table removes the objection before it is raised.

The exception is again SW-S4, which falls from 1.46× to 1.09×. Outside the $d_n$ channel SW-S4
does not separate the two formulations at all, and §"Why SW-S4 is different" is corrected below
accordingly.

### The best-case selections are not all resolved

Two of the four selections sit inside the campaign's cross-machine reproducibility floor of
0.1 percentage points of mean nRMSE:

| Specimen | selected best | runner-up | margin | resolved? |
|---|---|---|---:|---|
| SW-T1 | 100_01 (2.689%) | 100_02 (3.259%) | 0.570 pp | yes |
| SW-T2 | 100_04 (2.132%) | 100_03 (2.136%) | **0.004 pp** | **no** |
| SW-S3 | 100_06 (4.354%) | 100_05 (4.436%) | **0.082 pp** | **no** |
| SW-S4 | 93_07 (6.139%) | 99_07 (6.245%) | 0.106 pp | marginal |

SW-T2's hydraulic-aperture scale of 0.0177 is indistinguishable from 0.0175, and SW-S3's three
candidates (100_06 at 4.354%, 100_05 at 4.436%, 99_06 at 4.451%) are one result. The manuscript
must not report these as identified values. Report a bracket — SW-T2 aperture scale in
0.0175–0.0177, SW-S3 residual cohesion in 1.25–1.30 MPa — and say that the selection within each
bracket is below the resolution of the metric. Nothing in the MC comparison depends on the choice:
the smallest gap to any MC arm is a factor of 4.3.

The later scalar refinements do not materially improve MC relative to the audited 94-series
baseline. The change in mean MC nRMSE is +0.078 percentage points for SW-T1, +0.220 for SW-T2,
+0.273 for SW-S3, and −0.004 for SW-S4. The SW-T1 and SW-S4 changes fall below the campaign's
0.1-percentage-point reproducibility floor. The resolved SW-T2 and SW-S3 changes make MC slightly
worse. Thus, carrying the updated closure, aperture, and residual-strength selections into MC
strengthens rather than weakens the original conclusion: the performance gap cannot be removed by
these scalar adjustments.

## Where the models separate

The aggregate error is created mainly by the timing and path of weakening, not by the final
post-slip displacement alone. This distinction is clearest on SW-T1, SW-T2, and SW-S3. At loading
stage 5, one pressure stage before the peak hold, the measured, BBFast, and MC shear displacements
are:

| Specimen | Experiment | BBFast | MC |
|---|---:|---:|---:|
| SW-T1 | 0.008 mm | 0.001 mm | 0.483 mm |
| SW-T2 | 0.015 mm | 0.003 mm | 0.517 mm |
| SW-S3 | 0.001 mm | 0.001 mm | 0.064 mm |

At the same stage, MC has already shed most of the shear resistance. Its predicted shear stresses
are 33.65 MPa for SW-T1, 32.41 MPa for SW-T2, and 6.29 MPa for SW-S3, whereas the measured values
are 66.32, 73.40, and 14.26 MPa. BBFast predicts 67.73, 74.01, and 14.72 MPa, respectively. The
BBFast response therefore remains on the measured high-strength branch through stage 5, while MC
transitions prematurely to its weakened branch.

By the peak hold at stage 6, the MC displacement endpoints appear much less problematic. MC gives
0.514 mm against 0.532 mm for SW-T1, 0.548 mm against 0.571 mm for SW-T2, and 0.079 mm against
0.071 mm for SW-S3. Judging only the final displacement would consequently hide the failure: MC
arrives near the final state through an incorrect path, producing almost the full slip event one
stage too early. The ordered-stage nRMSE correctly penalises this premature transition.

## What actually places the transition: the weakening exponent

Because the two envelopes are matched at both endpoints, the premature MC failure cannot be a
matter of the MC arm being weaker. It is a matter of how fast each law travels from peak to
residual as plastic slip accumulates. The two forms are

$$W_{\mathrm{BBFast}} = \exp\!\left[-(\gamma/D_c)^{m}\right],\qquad
  \bar R_{\mathrm{MC}} = \exp\!\left[-\gamma/L\right],$$

with $m = 1.4$ on SW-T1, SW-T2 and SW-S3 ($1.10$ on SW-S4). The Mohr–Coulomb material carries a
single roughness state whose decay is exponential in slip, so its effective exponent is fixed at
1. For $\gamma \ll D_c$ — which is precisely where the yield decision is made — the two are far
apart. Measured on SW-T1, strength shed per unit cumulative plastic slip:

| $\gamma$ | BBFast | MC | ratio |
|---:|---:|---:|---:|
| 1 µm | 0.016 MPa | 0.185 MPa | **11.7×** |
| 5 µm | 0.151 MPa | 0.913 MPa | 6.1× |
| 20 µm | 1.023 MPa | 3.476 MPa | 3.4× |

Both laws were verified against their own `cumulative_plastic_slip` channel before this table was
computed. The pre-yield strength margin is only 1–2 MPa, so a difference of this size decides the
outcome. Tracing SW-T1 through the event: at $t = 1350$ s the BBFast margin is $+1.043$ MPa and
the MC margin is $-0.068$ MPa, and the entire difference is in cohesion already shed at
comparable plastic slip — 0.036 MPa for BBFast against 0.885 MPa for MC.

Solving for the decay length that would make each MC arm shed strength at its BBFast pair's rate,
evaluated at the plastic slip that pair has reached at its last pre-event stage:

| Specimen | $\gamma$ at stage 5 | $D_c$ | $m$ | $L$ needed | $L$ used | factor |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | 1.50 µm | 150 µm | 1.40 | 9.46 × 10⁻⁴ | 1.5 × 10⁻⁴ | 6.3× |
| SW-T2 | 2.95 µm | 150 µm | 1.40 | 7.22 × 10⁻⁴ | 1.5 × 10⁻⁴ | 4.8× |
| SW-S3 | 0.70 µm | 60 µm | 1.40 | 3.56 × 10⁻⁴ | 4.0 × 10⁻⁵ | 8.9× |
| SW-S4 | 47.64 µm | 74.5 µm | 1.10 | 7.79 × 10⁻⁵ | 8.0 × 10⁻⁵ | **1.0×** |

SW-S4 needs no correction at all: its exponent is already 1.10, so its MC transfer is
rate-matched by construction. And SW-S4 is exactly the specimen where MC nearly matches BBFast —
1.46× overall, 1.09× once $d_n$ is set aside. The three specimens carrying $m = 1.4$ are the
three where MC collapses. That correlation is already present in the completed data and requires
no new runs, but it is correlational, which is why the 103-series control described below exists.

Note also that on SW-S3 the MC decay length (4.0 × 10⁻⁵ m) is *shorter* than its BBFast pair's
characteristic slip distance (6.0 × 10⁻⁵ m), which compounds the exponent effect in the same
direction. SW-S3 is the specimen where the transfer is furthest from rate-matched.

## The normal-unloading gap

The unloading branches expose a second, independent asymmetry, and it is not a shear-law
difference. On the unloading branch SW-T1's MC arm closes **2.0 nm** while its effective normal
stress rises 9.6 MPa; its BBFast pair closes 36.4 µm and the measurement shows about 44 µm. The
same holds on every specimen — the MC normal-displacement recovery is exactly zero to four
figures on all four, against 0.036, 0.011, 0.011 and 0.011 mm for the BBFast arms. This is a
capability limit of the transferred material, not a consequence of its shear law, and it accounts
for the largest single MC error channel on three of the four specimens.

The correct framing is therefore that the transfer changes **two** things, not one: the shear
formulation, and the availability of a normal-unloading path. The robustness check above shows
the aggregate conclusion survives the loss of the $d_n$ channel entirely, which is what licenses
continuing to report the five-channel mean as the headline. Both facts belong in the manuscript.

The scalar hydraulic-aperture and maximum-closure refinements can alter the magnitude of flow or
closure, but they cannot correct either the stage at which the MC shear law loses strength or the
absence of a reclosure branch.

## Why SW-S4 is different

SW-S4 is the least decisive specimen in the aggregate comparison and the only case in which MC is
better for one scored channel. Unlike the three abrupt-slip specimens, SW-S4 develops slip
progressively over several pressure stages. MC predicts a final shear displacement near 0.077 mm,
close to the measured 0.079 mm, while BBFast ends near 0.082 mm. This explains the modest MC
advantage in shear-displacement nRMSE.

That agreement does not extend to the coupled normal response. At the peak stage, measured normal
displacement is −0.041 mm; BBFast gives −0.043 mm, while MC gives only −0.028 mm. During unloading,
BBFast recovers toward the measured −0.032 mm endpoint, whereas MC remains close to −0.028 mm.

The earlier draft of this section then claimed that BBFast is also clearly closer in flow,
effective normal stress and shear stress. It is closer, but not by a margin that carries any
weight. Excluding $d_n$, SW-S4's four remaining channels give 6.516% for BBFast against 7.075%
for MC — a ratio of 1.09×, against a four-specimen mean of 4.72×. **Outside the normal-displacement
channel, SW-S4 does not separate the two formulations.** Since $d_n$ is exactly the channel
carrying the normal-unloading capability gap, SW-S4 should be reported as a specimen on which
this comparison is inconclusive, not as weak support.

That is not a defect in the run; it is the expected result, and it is the most informative thing
SW-S4 contributes. SW-S4 is the one specimen whose slip-weakening exponent (1.10) is already
close to the exponent of 1 that the Mohr–Coulomb transfer is forced into, so its two arms should
behave alike — and they do. SW-S4 is the internal control for the mechanism identified above,
not a fourth vote for BBFast.

This specimen also limits the interpretation of the average result. The MC and BBFast strength
envelopes were tangent-matched at onset and differ only modestly in slope over the stress interval
sampled by the experiment. The comparison should not be presented as direct proof that the
curvature of the Barton–Bandis envelope has been uniquely identified. Instead, it demonstrates
that the complete BBFast formulation—with separate controls on peak-to-residual weakening,
dilation evolution, and hydraulic response—organises these measured paths substantially better
than the transferred linear MC formulation.

## The 103-series control

The mechanism identified above is, on the completed data, a correlation: the three specimens with
$m = 1.4$ fail early and the one with $m = 1.10$ does not. Three decks make it causal, and they
are controls rather than tuning runs.

`103_01`, `103_02` and `103_03` are the SW-T1, SW-T2 and SW-S3 best-case BBFast decks with
**one** parameter changed — `slip_weakening_exponent` from 1.4 to 1.0 — which turns BBFast's
strength weakening into exactly the exponential form the Mohr–Coulomb material is stuck with. The
peak and residual envelopes, the hydraulic aperture, the dilation, the normal-unload retention,
the mesh, the schedule and the solver are untouched.

The test has to be run on the BBFast side. The obvious alternative — lengthening the MC roughness
decay until it matches — is not clean, and `102_01`'s own header says why: in the MC material one
roughness state drives both the strength *and* the hydraulic aperture, so any change to its decay
moves $Q$ for a reason unrelated to the shear law. The exponent parameters cannot compensate
either, since `friction_roughness_exponent` and `cohesion_roughness_exponent` are range-checked
$\geq 1$ and only ever make the strength decay faster. BBFast has no such coupling: its aperture
runs off a separate `roughness_characteristic_slip`.

**Prediction, recorded before the runs.** 103 should reproduce the MC failure mode on all three
specimens — yield at stage 5 rather than stage 6, roughly 0.5 mm of slip one stage early, shear
stress collapsing toward residual while the measurement is still on the high-strength branch —
and its mean nRMSE should move a large fraction of the way from its BBFast parent toward its MC
pair.

**Falsifier.** If 103 still holds through stage 5, the exponent is not the mechanism, and the
next suspect is the normal-unloading path documented above.

If the prediction holds, the manuscript's claim changes from "MC weakens one stage too early" to
"the weakening exponent is what places the transition, and a single-state Coulomb law has no way
to represent it" — a statement about constitutive form, which is what this comparison is supposed
to be about. If the prediction fails, the 102 result still stands as a performance claim but its
mechanism is unexplained, and that should be said.

### Result (2026-08-22): confirmed on the tensile pair, falsified on SW-S3

All three controls ran to their full end times on the cluster. Read with
`scripts/score_103_control.py`. Stage 5 is the deciding stage — the one where the MC arms yield
and the measurement does not.

| specimen | stage-5 slip: parent → control → pair (mm) | measured | mean nRMSE: parent / control / pair |
|---|---|---:|---|
| SW-T1 | 0.0082 → **0.4901** → 0.4894 | 0.0080 | 2.689% / **24.355%** / 25.351% |
| SW-T2 | 0.0106 → **0.5243** → 0.5240 | 0.0150 | 2.132% / **23.339%** / 23.365% |
| SW-S3 | 0.0021 → **0.0039** → 0.0651 | 0.0010 | 4.354% / **5.267%** / 18.744% |

**SW-T1 and SW-T2 confirm the prediction completely.** Changing one parameter — the slip-weakening
exponent, 1.4 → 1.0 — moves the control onto its Mohr–Coulomb pair to three decimal places in
stage-5 slip (0.4901 vs 0.4894; 0.5243 vs 0.5240) and reproduces essentially all of the accuracy
gap: 24.355% against the pair's 25.351%, from a parent at 2.689%. On the tensile fractures the
entire Barton–Bandis advantage in this comparison is carried by the weakening exponent, and none
of it by the shape of the strength envelope.

**SW-S3 triggers the registered falsifier.** Its control holds through stage 5 — 0.0039 mm against
the parent's 0.0021 and the pair's 0.0651 — and its mean nRMSE moves only 4.354% → 5.267%, a fifth
of the way to the pair's 18.744%. The exponent is *not* the mechanism on SW-S3. The falsifier named
the next suspect in advance, and it is the one this document already flags: SW-S3's best case is
the zero-normal-unloading-retention deck, and the MC material has no normal-unloading path at all
(see "The normal-unloading gap" and the SW-S3 matching qualification above). That gap, not the
weakening exponent, is what the SW-S3 comparison is measuring.

The honest summary is therefore **specimen-dependent rather than general**: the same 5× aggregate
performance gap has two different causes in two different specimens. This is a weaker claim than
the prediction anticipated, and it is the one the manuscript should make. It also means SW-S3
should not be pooled with the tensile pair as evidence for the exponent.

## SW-S3 matching qualification

The nominal best SW-S3 BBFast case, `100_06_sw3_resc1p30_unld0p00_ppfix`, combines a residual
cohesion of 1.30 MPa with zero normal-unloading retention. The MC material has no corresponding
unloading-retention parameter, so `102_03_sw3_mc_resc1p30_ppfix` can inherit the residual cohesion
but cannot reproduce that additional mechanism. This makes the nominal best-case comparison a
comparison of available model capability rather than a literal one-parameter-block substitution.

An earlier draft of this section limited that qualification to SW-S3. It applies to all four. No
MC arm has a normal-unloading path at all — see §"The normal-unloading gap" — and the retention
fractions the BBFast arms carry are 0.94 for SW-T1 and 0.84 for SW-T2, far larger than SW-S3's
0.00. SW-S3 is simply the specimen where the gap is smallest, not the only one where it exists.

The existing `99_06_sw3_resc1p30_ppfix` BBFast result provides the strictest available control: it
uses the same 1.30 MPa residual cohesion without the zero-retention refinement. Its mean nRMSE is
4.451%, compared with 4.354% for the nominal best BBFast case and 18.744% for MC. The scientific
conclusion is therefore insensitive to the qualification, and no additional monotonic SW-S3 run
is required. For maximum transparency, the nominal best comparison can be reported in the main
table and the `99_06` sensitivity stated in the text or a footnote.

## Constitutive interpretation

The paired decks deliberately share the nonlinear normal-closure law. Their separation cannot be
used as evidence that Barton-type closure is superior to an MC closure model, because no such
closure comparison was performed. The result instead concerns the representation of shear
strength and its coupling to dilation and hydraulic aperture.

The tangent match makes the pre-yield MC and BBFast responses nearly identical. After yield,
however, the transferred MC formulation evolves strength and dilation through a single
roughness-dependent path, while BBFast carries separate characteristic scales for strength loss
and dilation evolution. The abrupt specimens expose this difference as premature MC failure at
stage 5. SW-S4 exposes it through the normal-dilation history even though its final shear
displacement is reproduced reasonably well. Across the four specimens, the repeated pattern is
therefore not simply that MC predicts too much or too little final slip; it is that MC cannot place
the transition and the coupled post-yield path correctly with the transferred parameterisation.

This conclusion should be phrased as a performance result under a matched transfer procedure, not
as universal model selection. BBFast has greater constitutive flexibility, and the parameters were
selected with knowledge of the experimental results. The data demonstrate that this additional
structure is useful for these four laboratory histories. They do not prove that every rough joint
requires the same formulation, nor do they independently identify every BBFast internal parameter.

## Implications for additional simulations

The 102-series results do not justify another monotonic MC tuning case. The SW-T1 and SW-S4 changes
relative to the old MC baselines are below the reproducibility floor, while the resolved SW-T2 and
SW-S3 changes worsen the score. More adjustment of maximum closure, aperture scale, or residual
cohesion would optimise secondary consequences without addressing the premature weakening that
dominates the MC error. Such tuning would also weaken the interpretation of MC as a transferred,
non-recalibrated baseline.

The 103-series is not an exception to this. It is not an MC tuning case at all — it changes a
BBFast deck, in the direction that makes it *worse*, to test a stated mechanism. The distinction
matters for how the manuscript presents it: 103 is a control, and controls that are predicted to
degrade the fit are the only kind that carry information here.

Nor does the ranking justify further BBFast refinement. Two of the four selections (SW-T2, SW-S3)
are already inside the reproducibility floor, so additional scalar cases would produce differences
the metric cannot resolve.

The conclusion applies only to the monotonic Table-2 histories. The completed 101-series cyclic
and shut-in simulations use BBFast, so this comparison cannot establish whether MC and BBFast
predict different cycle-to-cycle retention or post-shut-in arrest. If the paper is to make a
direct constitutive comparison for those loading histories, matched MC versions of the equal-peak
cyclic and no-hold shut-in schedules are still required for all four specimens. Those simulations
would answer a different question and should be analysed separately from the monotonic accuracy
ranking.

## Recommended manuscript conclusion

Under a matched transfer from the selected specimen-specific calibrations, the BBFast formulation
reduced the four-specimen mean nRMSE from 19.107% for linear Mohr–Coulomb to 3.828%, corresponding
to an 80.0% reduction; excluding the normal-displacement channel, which is subject to a capability
asymmetry rather than a constitutive difference, the reduction is 78.8%. BBFast improved 19 of 20
specimen–observable combinations.

The transfer is verified rather than assumed: the paired runs agree to better than 0.003 MPa in
shear stress through Table-2 stage 4 on the three tensile and saw-cut specimens, and their peak
strength envelopes agree to 0.12 MPa or better. The arms begin at the same strength and end at the
same residual, so the error is generated entirely by the path between them.

The largest MC errors arose because SW-T1, SW-T2 and SW-S3 weakened one injection stage before the
measured slip event; near agreement in their final displacements therefore masked an incorrect
loading path. **On the two tensile fractures the mechanism is the weakening exponent**, and the
103-series controls demonstrate this causally rather than by correlation. A single-state Coulomb
law decays exponentially in slip, whereas the calibrated Barton–Bandis weakening carries an
exponent of 1.4, and at the sub-micrometre plastic slips where the yield decision is made the two
differ by an order of magnitude in strength shed per unit slip — against a pre-yield margin of only
1 to 2 MPa. SW-S4, whose calibrated exponent is already 1.10, is correspondingly the one specimen
on which the two formulations do not separate outside the normal-displacement channel (1.09×), and
should be reported as an internal control rather than as a fourth vote.

**On SW-S3 the mechanism is different, and the control proves it is not the exponent**: setting the
exponent to 1 leaves SW-S3 holding through stage 5 and recovers only a fifth of the accuracy gap.
What separates the arms there is the normal-unloading path, which the MC material does not
implement at all. The aggregate 5× performance gap is therefore real but not monocausal, and the
manuscript should attribute it per specimen rather than to a single constitutive term.

Because the models share the same normal-closure law and their strength envelopes agree at both
endpoints, this result supports the BBFast weakening formulation — on the tensile pair specifically
its exponent — rather than uniquely identifying envelope curvature. The completed scalar
refinements did not improve MC, so no further monotonic tuning run is warranted; the 103-series
exponent control is a control, not a tuning case.
