# Ye & Ghassemi 2018 — back-analysis of the completed campaign

**Written 2026-08-24**, after the HPC results were downloaded and the manuscript declared
finished. Method: `doc/back_analysis_method.md`. Re-runnable arithmetic:
`scripts/mesh3_convergence.py`, `scripts/check_axis_intervals.py`, `scripts/table2_gate.py`.

**Scope of the conclusion.** None of what follows changes Table 5. Every scored number in the
manuscript stands. What changes is the *verification* section (§5.1), one table in §5.4, and two
footnotes — plus one result the manuscript currently throws away and should not.

---

## 0. The completeness audit comes first

The standing rule from the Kalantar campaign is *guard the score, never the plot*: establish what
each run actually contains before reading anything off it. Applied to all 105 Ye2018 HPC CSVs
against their decks' own `end_time`:

**The belief that only SW-T1's mesh-3 run is outstanding is wrong.** Seven of the ten mesh-3 runs
are truncated, and four other runs are too:

| run | reached | of | % |
|---|---:|---:|---:|
| `93_06` SW-S3 BB mesh3 | 2833.5 | 4803.0 | 59.0 |
| `94_06` SW-S3 MC mesh3 | 2804.2 | 4803.0 | 58.4 |
| `93_02` SW-T1 BB mesh3 | 70.5 | 3500.0 | **2.0** |
| `94_02` SW-T1 MC mesh3 | 372.0 | 3500.0 | 10.6 |
| `92_05` SW-T2 BB mesh3 | 2217.0 | 2852.5 | 77.7 |
| `93_04` SW-T2 BB mesh3 | 1773.8 | 2852.5 | 62.2 |
| `94_04` SW-T2 MC mesh3 | 1806.0 | 2852.5 | 63.3 |
| `96_04`/`96_05` SW-S3 fpc | — | — | 51.5 / 52.3 |
| `96_07`/`96_08` SW-S4 fpc | — | — | 47.7 / 47.8 |
| `97_01`/`97_02`/`97_03` cyclic | — | — | 87.6 / 79.0 / 39.3 |

Only **SW-S4's** mesh-3 pair is complete. The `97`-series truncations are harmless — that series
was superseded by the `101` series, which is complete — but they must not be scored.

### 0.1 Wall-clock percentage is the wrong measure, and it misleads in both directions

Every protocol pressurises to a peak and then depressurises. A run that dies at 59 % of
`end_time` may hold the *entire* pressurisation branch; one that dies at 23 % may hold nothing but
the preload. Measuring the cut against peak injection instead:

| pair | cut | peak | % of pressurisation | P at cut | Q developed | verdict |
|---|---:|---:|---:|---:|---:|---|
| SW-S3 BB | 2833.5 | 2698.5 | **100 %** | 24.41 | 65.8 % | usable |
| SW-S3 MC | 2804.2 | 2698.9 | **100 %** | 25.76 | 75.4 % | usable |
| SW-S4 both | 3500.0 | 1722 | 100 % | — | — | complete |
| SW-T1 BB | 70.5 | 1640 | 4.3 % | 6.12 | **0.3 %** | nothing |
| SW-T1 MC | 372.0 | 1640 | 22.7 % | 8.12 | **0.9 %** | nothing |
| SW-T2 BB | 1773.8 | 2280 | 77.8 % | 20.79 | **6.6 %** | uninformative |
| SW-T2 MC | 1806.0 | 2280 | 79.2 % | 22.15 | **7.6 %** | uninformative |

The `Q developed` column is the decisive one for the two tensile specimens. SW-T2's refined run
covers 78 % of the pressurisation branch but only **6.6 %** of the flow range, because the
tensile fracture stays shut until it opens abruptly: the entire flow response lives in the last
fifth. A percentage of wall clock flatters that pair badly.

---

## 1. SW-S3's refined pair is usable, and the manuscript discards it

§5.1 currently reads *"SW-T2 reaches stage 4 of 11, SW-S3 stage 6, and SW-T1 terminates during the
preload"* and treats all three as equally unusable.

**But SW-S3's stage 6 is peak injection.** Table 2's schedule is six loading stages (8→28 MPa)
then five unloading. Reaching stage 6 means the refined run covers **every loading stage**, and
the gate confirms the slip event is inside that window — at stage 6 the model gives
$d_n = -0.0515$ mm against Table 2's $-0.044$ and $d_s = 0.0780$ against $0.071$. Only the
unloading branch is missing.

Matched-stage scores, both meshes re-scored over stages 1–6 with the Table-2 range renormalised
over the same stages:

| specimen | law | mesh 5 | mesh 3 | change |
|---|---|---:|---:|---:|
| SW-S3 | Barton–Bandis | 4.36 % | 5.26 % | **+0.90** |
| SW-S3 | Mohr–Coulomb | 24.39 % | 24.89 % | **+0.50** |

These are **not** comparable to Table 5 — different stage set, different normalising range. Quote
the change, never the level. Both changes are small against the 20-point BB/MC separation on those
same stages, in the same way §5.1 already argues for SW-S4's 2.83-point separation.

**Why this matters more than an extra row.** §5.1's own stated gap is that *"no matched
full-schedule comparison exists for the three burst specimens"* — SW-S4, the one complete pair, is
explicitly the specimen whose slip is progressive rather than a burst. SW-S3 **is** a burst
specimen, and its refined pair spans the burst. The claim available is therefore stronger than the
one written: mesh-insensitivity holds on the progressive specimen over the full schedule *and* on
a burst specimen over the full loading branch.

The script reproduces the manuscript's SW-S4 numbers (6.14 / 6.37 and 8.98 / 8.84) exactly, which
is what licenses the SW-S3 rows.

### 1.1 The two tensile pairs stay unusable, and one of them for a second reason

SW-T1 reaches 0 and 1 scored stages. SW-T2 reaches 4, all pre-burst — and there the Barton–Bandis
and Mohr–Coulomb runs agree to 0.00 % in $Q$ and within 0.02 points on every other channel,
because nothing constitutive has engaged yet. A comparison over a window where the two laws are
indistinguishable cannot say anything about either.

---

## 2. The Ye2018 mesh estate has the Kalantar integer-pinning defect, on all four specimens

`scripts/check_axis_intervals.py`, written for Kalantar, transfers unchanged. Every borehole node
lands at $\mathrm{round}(0.802\,N)/N$ along the fracture major axis:

| specimen | mesh | $N$ | separation (mm) | vs design |
|---|---|---:|---:|---:|
| SW-S3 | 5 | 12 | 86.8554 | **+3.894 %** |
| SW-S3 | 3 | 25 | 83.3812 | −0.262 % |
| SW-S4 | 5 | 11 | 82.6527 | **+2.015 %** |
| SW-S4 | 3 | 25 | 80.8160 | −0.252 % |
| SW-T1 | 5 | 11 | 78.0016 | **+2.010 %** |
| SW-T1 | 3 | 24 | 75.4738 | −1.296 % |
| SW-T2 | 5 | 11 | 80.2553 | **+2.010 %** |
| SW-T2 | 3 | 23 | 76.7660 | −2.425 % |

Two consequences the manuscript does not currently state:

1. **Every mesh-5 run — every reported result — has its boreholes 2.0–3.9 % too far apart.** The
   coarse meshes all have $N \in \{11, 12\}$, neither divisible by 5, so none can place a node at
   $0.802\,r$. The refined meshes land on $N = 23$–25 and do much better.
2. **The pair difference is not 3.1 % on SW-T1 alone.** It is −4.00 % on SW-S3, −2.22 % on SW-S4,
   −3.24 % on SW-T1 and −4.35 % on SW-T2. Footnote 14 singles out SW-T1 and treats SW-S4's pair as
   clean; SW-S4's is 2.22 %.

### 2.1 …and it does not reach the scored channels. This is the finding that rescues §5.1

The manuscript worries, correctly in principle, that a pair differing in source separation "would
not be a pure discretisation comparison". Measured, the worry does not cash out.

**$Q$ is an exact algebraic function of the aperture.** Fitting a single constant to
$Q$ against $a_h^3\,\Delta p$ over every output row:

| specimen | $n$ | $r(Q,\ a_h^3\Delta p)$ | max deviation from one constant |
|---|---:|---:|---:|
| SW-S3 | 6403 | 1.00000000 | 0.0000 % |
| SW-S4 | 2334 | 1.00000000 | 0.0000 % |
| SW-T1 | 7456 | 1.00000000 | 0.0000 % |
| SW-T2 | 3724 | 1.00000000 | 0.0000 % |

The reason is structural: $W/L$ is a constant fitted from Table 2 and identical in both meshes,
and $\Delta p = P_{\rm inj}(t) - P_{\rm out}$ where the outlet is a `DirichletBC` at 5 MPa — so
`pp_drop_pp` is bit-identical between the two meshes. The separation cannot enter $Q$ directly at
all. It can only enter through the mechanics, into $a_h$:

| specimen | Δ separation | Δ $a_h$ | Δ $Q$ |
|---|---:|---:|---:|
| SW-S3 | −4.00 % | +1.10 % | +6.02 % |
| SW-S4 | −2.22 % | +0.51 % | +1.36 % |
| SW-T2 | −4.35 % | **0.00 %** | 0.00 % |

The specimen with the **largest** separation change shows **zero** aperture response. There is no
ordering, so the separation is not what drives the difference between the meshes. That is a clean
null and it should be reported as one — it is what makes the mesh comparison legitimate despite
the geometry defect.

**Do not rebuild the Ye2018 meshes for this.** The runs are final and the null above prices the
fix at approximately nothing. The lesson belongs in the method, not in a remesh.

---

## 3. The 2026-08-06 flow-measurement fix was never ported into the final decks

This is the one real defect.

The 2026-08-06 back-analysis found that `inj_flux_aux`, filled by `save_in`, under-reports the
injection flux, and that the decks already build the correct quantity — `react_pore_pressure`, a
`TagVectorAux` on the `mass_reaction` tag with `remove_variable_scaling = true` — and never use
it. The fix was to repoint the two `NodalSum` postprocessors at it.

**All sixteen finalized decks still sum `inj_flux_aux`:**

```
[inj_reaction_sum_pp]      [react_pore_pressure_aux]        <- built, correct, never summed
  type = NodalSum            type = TagVectorAux
  variable = inj_flux_aux    vector_tag = mass_reaction
  boundary = source_in       v = pore_pressure
[]                           remove_variable_scaling = true
```

Verified across `93_01`–`93_08` and `94_01`–`94_08`, both laws, both meshes, all four specimens.

**What it costs.** At SW-T1's first hold stage, with the pressure drop at exactly 3.000 MPa —
the point the manuscript's §5.4 table is quoted at:

| quantity | manuscript §5.4 | current `93_01` |
|---|---:|---:|
| solved injection flux | 0.0277 | **0.000191** |
| independent flux integral | 0.0257 | 0.000223 (outlet) |
| cubic law on simulated aperture | 0.0508 | 0.0528 |
| Ye & Ghassemi Table 2 | 0.053 | 0.053 |

The cubic-law row reproduces. The solved-flux row is **145× lower**. And it is 0.00019–0.00022 in
*every* SW-T1 run in the repository — `87_01` through `104` — so the manuscript's 0.0277 is not
recoverable from any finished run.

§5.1's mass-balance sentence is affected the same way: it claims 4.3 % "measured on SW-T1", and
the final SW-T1 run `93_01` gives **16.8 %**.

**What it does not cost.** Nothing in Table 5. The scored flow channel is
`flow_rate_validation_ml_min_pp`, the cubic-law evaluation, which never touches the reaction
vector. Every score, every ranking, and the whole of §5.5 are unaffected.

**Fix.** Repoint the two `NodalSum`s, add a `react_pore_pressure` sum, and re-run **only to the
first hold stage** — SW-T1 to $t = 300$ s is enough to regenerate both numbers. No exodus exists
locally for `93_01`, so this cannot be recovered by post-processing.

### 3.1 A second, smaller wiring issue in the same family

`flow_rate_mesh_geometry_ml_min_pp` is meant to be the mesh-derived counterpart of the fitted
channel. On SW-S4, SW-T1 and SW-T2 it returns **exactly** the validation value (ratio 1.000),
because those decks set `mesh_flow_width_over_length = paper_flow_width_over_length` — the same
fitted number copied across, with a comment in `93_07` admitting SW-S4 "had no mesh-geometry flow
channel at all". Only SW-S3 carries a genuinely independent value (0.830× the fitted channel).
This is task #13 and it is not a new finding, but three of the four decks currently make the
diagnostic look like it agrees when it is not computing anything.

---

## 4. What §5.4 already gets right, stated more sharply

§5.4 argues that the flow disagreement is a geometry factor and should be reported rather than
fitted. §2.1 above turns that from an interpretation into an identity: the scored $Q$ is
$C\,a_h^3\,\Delta p$ with $C$ fitted and $\Delta p$ prescribed, so **the flow score is an aperture
score wearing different units, and the transport the model actually solves is never scored at
all.** That is worth one sentence in §5.4, because it tells a reader exactly what the $Q$ column
of Table 5 does and does not test.

---

## 5. How to move forward

**Do first, because the manuscript is otherwise finished:**

1. **Task #123** — port the flow fix, re-run SW-T1 to $t = 300$ s locally, regenerate the §5.1 and
   §5.4 numbers. Cheap, and it is the only item that changes a stated result.
2. **Task #124** — rewrite §5.1's mesh paragraph and footnote 14 to promote SW-S3. This *adds* a
   result; it does not retract one.
3. **Task #125** — correct the separation claim to all four specimens and add the §2.1 null.

**Do not do:**

* **Do not rebuild the Ye2018 meshes.** §2.1 prices the separation defect at approximately zero on
  the scored channels.
* **Do not re-run the SW-T2 or SW-S3 mesh-3 pairs to completion.** SW-S3 already answers the
  question over the loading branch; SW-T2's window is pre-burst and would need the full run to say
  anything, at burst-specimen cost.
* **Do not score the `97`-series.** Truncated and superseded by the complete `101` series.
* **Do not re-rank anything on a change below 0.1 points** — the cross-machine floor.

**On the SW-T1 mesh-3 run currently in flight.** Two things are worth knowing before it lands.
Its predecessor reached 2.0 % of the schedule; and SW-T1's flow response is 99.7 % concentrated
after the point that run reached, so a partial result will again say nothing. If it does not reach
stage 6 — peak injection — it adds no evidence, and §5.1 should be written on SW-S4 + SW-S3
regardless of its outcome rather than waiting on it.

**Then, and only then, back to Kalantar.** Nothing in this document blocks that: the highest-
leverage open item across both campaigns remains task #121, `bb_jrc_mobilized` never moving in any
deck of either campaign.
