# SW-S4 — final validation case and paper notes

## SUPERSEDING NOTE (2026-08-26) — deck of record unchanged, diagnosis corrected

**Deck of record:** `93_07_sw4_final_theta30_jrc5_ppfix.i`, **unchanged at mean nRMSE 6.139 %**.
Nothing on disk beats it. It is now the **worst of the four specimens** — the other three moved
and this one did not — and it carries the campaign's single worst channel, tau at 10.103 %.

**The 105-series arms all regressed:** `105_04` (D_c 74.5 -> 45 um) 13.93, `105_05`
(weakening floor 6.50 -> 3.15 deg) 9.10, `105_06` (both) 20.35, and the two MC transfer arms
`105_07`/`105_08` 8.84 / 11.46 against the 94_07 baseline's 7.07.

**Two earlier readings are corrected.**

1. *The residual is not delayed onset.* The tau error is one spike at hold stage 4 (+2.74 MPa),
   and there `limit_tau_pp` is 12.291 MPa against a model tau of 12.121 — the joint is **on its
   own yield surface**, having slipped just enough to reach it (0.0034 mm against Table 2's
   0.017). The lever is the *level* of the envelope, not whether the joint is allowed to reach it.
   Inverting Table 2 at its own stage-4 slip gives a required peak of 11.039 MPa, i.e.
   phi_peak = 25.717 deg where this deck gives 26.799 -- **1.083 deg too high**. `106_08`/`106_09`
   bracket that. phi_r is the only lever: the JRC that would lower phi at 22.92 MPa while holding
   it at 26.5 solves to -16.8, and JCS is algebraically identical to phi_r over a span this narrow.

2. *D_c and the unloading floor were already right.* Fitting Table 2's own tau / d_s pairs implies
   D_c = 55-98 um and this deck's 74.5 um is inside that bracket; the unloading tau error already
   decays to +0.05 MPa by stage 11. `105_04` and `105_05` tested both and both regressed. The
   earlier "residual floor too high" reading is withdrawn.

**One real hydraulic gain remains.** Unlike the mode-I specimens SW-S4's stress-aperture term is
live and roughly the right size, but its *shape* is wrong: at p = 2.0 it over-opens through the
loading stages and under-opens at the event, leaving Q 15 % low at stage 6. Refitting p to 3.28 and
sigma_0 to the deck's own mechanical K_ni*V_m predicts Q 5.005 -> 2.183 %. See `106_10`.

> This block was added on 2026-08-26 after the 105-series post-mortem. It **supersedes the
> "Final deck" line below it**; everything after it is left exactly as written so the earlier
> selection stays auditable. The authoritative ranking is
> `doc/independent_analysis/TABLE2_ERROR_ACCURACY_RANKING.csv`, regenerated the same day and now
> complete through series 105. The next campaign is
> `doc/independent_analysis/RUN_LIST_106_SERIES.md`.

---

**Status: FINAL. No further sweep — the remaining error is model-form, and it has been bracketed
in both directions.**
Deck of record (mesh 5): `93_07_sw4_final_theta30_jrc5_ppfix.i` — constitutively identical to
`90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6.i`, which is the run scored below; see §8.
Mesh-convergence run: `93_08_sw4_final_theta30_jrc5_ppfix_mesh3.i`
MC baseline: `94_07_sw4_mc_final.i` / `94_08_sw4_mc_final_mesh3.i`
Date: 2026-08-17. Branch `orca_v5`, repo `orca_4.0`.

---

## 1. Specimen and what the model has to reproduce

SW-S4 is a **polished saw cut** in Sierra White granite — the smoothest of the four specimens,
with no asperity interlock to lose. Its shear tractions are an order of magnitude below the two
tensile specimens (12.6 MPa peak against 74.9 MPa on SW-T2), its total slip is 79 µm against
552 µm, and its flow rates are three orders of magnitude smaller (0.005–0.113 mL/min against
0.115–11.1). Everything about it is small, which makes it the most demanding of the four in
relative terms.

**Fracture angle and mesh provenance.** The old SW-S4 journal was a copy of SW-S3's: its
fracture-plane z-span was bit-identical, which is how a 118.70 mm specimen ended up carrying a
123.40 mm specimen's plane offsets — 28.990° and 2.85 mm off centre. Recovering θ from Table 2
via `tan θ = (σ'ₙ − σ₃ + P_p)/τ` gives **30.020°**, so the mesh is now cut at 30.000° and centred.

## 2. Calibrated joint parameters

| parameter | value | note |
|---|---|---|
| θ | 30.000° | rebuilt mesh; recovered 30.020° from Table 2 |
| L × D | 118.70 × 50.51 mm | Table 1 |
| JRC | 5.0 | polished saw cut |
| JCS | 150 MPa | paper §2.1, intact UCS |
| φ_r | 22.72° | solved from φ_r + 5·log₁₀(150/24) = 26.70° |
| slip-weakening residual φ | 6.50° | |
| **D_c** | **74.5 µm** | bracketed 40 / 74.5 / 120 µm — see §4 |
| slip-weakening exponent `m` | 1.10 | |
| cohesion, residual cohesion | 0, 0 | a polished saw cut has no interlock to keep |
| roughness state, initial → residual | 0.45 → 0.10 over 80 µm | supplies the residual instead |
| Biot coefficient α | 0.6 | |
| E, ν | 67 GPa, 0.32 | shared by all four specimens |
| axial frame penalty | 1.2 × 10¹² Pa/m | |

SW-S4 is the specimen whose residual comes entirely from **roughness degradation**, not from a
residual cohesion. That is the physically right choice for a polished surface, and it is why
SW-S4 was the only one of the four whose residual state was already correct before the
91-series touched anything.


## 3. Comparison against Ye & Ghassemi (2018) Table 2

Scored with `scripts/table2_gate.py`; displacements zeroed at stage 1 as Table 2 is, so stage 1
is excluded from the d_n and d_s statistics. a_h and k are informational only — the paper
back-computes a_h from the measured Q and defines k = a_h²/12, so neither is independent of Q.


| stage | branch | P_i (MPa) | Q (mL/min) paper \| model \| err | sigma'_n (MPa) paper \| model \| err | tau (MPa) paper \| model \| err | d_n (mm) paper \| model \| err | d_s (mm) paper \| model \| err |
|---|---|---|---|---|---|---|---|
| 1 | loading | 8 | 0.0050 \| 0.0051 \| +0.0001 | 30.75 \| 30.59 \| -0.16 | 12.56 \| 12.35 \| -0.21 | 0.0000 \| 0.0000 \| +0.0000 | 0.0000 \| 0.0000 \| +0.0000 |
| 2 | loading | 12 | 0.0120 \| 0.0128 \| +0.0008 | 28.73 \| 28.50 \| -0.23 | 12.53 \| 12.35 \| -0.18 | 0.0000 \| -0.0004 \| -0.0004 | 0.0000 \| 0.0000 \| +0.0000 |
| 3 | loading | 16 | 0.0220 \| 0.0220 \| -0.0000 | 26.51 \| 26.48 \| -0.03 | 12.14 \| 12.38 \| +0.24 | -0.0010 \| -0.0009 \| +0.0001 | 0.0000 \| 0.0000 \| +0.0000 |
| 4 | loading | 20 | 0.0350 \| 0.0359 \| +0.0009 | 22.92 \| 24.33 \| +1.41 | 9.38 \| 12.09 \| +2.71 | -0.0080 \| -0.0033 \| +0.0047 | 0.0170 \| 0.0036 \| -0.0134 |
| 5 | loading | 24 | 0.0560 \| 0.0527 \| -0.0033 | 19.25 \| 19.80 \| +0.55 | 6.48 \| 7.54 \| +1.06 | -0.0210 \| -0.0240 \| -0.0030 | 0.0410 \| 0.0473 \| +0.0063 |
| 6 | loading | 28 | 0.1130 \| 0.0959 \| -0.0171 | 15.31 \| 16.05 \| +0.74 | 3.12 \| 4.38 \| +1.26 | -0.0410 \| -0.0427 \| -0.0017 | 0.0750 \| 0.0807 \| +0.0057 |
| 7 | unloading | 24 | 0.0640 \| 0.0631 \| -0.0009 | 17.13 \| 17.68 \| +0.55 | 2.82 \| 3.71 \| +0.89 | -0.0380 \| -0.0387 \| -0.0007 | 0.0770 \| 0.0816 \| +0.0046 |
| 8 | unloading | 20 | 0.0370 \| 0.0398 \| +0.0028 | 19.00 \| 19.51 \| +0.51 | 2.59 \| 3.22 \| +0.63 | -0.0360 \| -0.0357 \| +0.0003 | 0.0780 \| 0.0816 \| +0.0036 |
| 9 | unloading | 16 | 0.0240 \| 0.0248 \| +0.0008 | 20.89 \| 21.26 \| +0.37 | 2.41 \| 2.86 \| +0.45 | -0.0340 \| -0.0339 \| +0.0001 | 0.0790 \| 0.0816 \| +0.0026 |
| 10 | unloading | 12 | 0.0130 \| 0.0139 \| +0.0009 | 22.82 \| 23.03 \| +0.21 | 2.28 \| 2.57 \| +0.29 | -0.0330 \| -0.0327 \| +0.0003 | 0.0790 \| 0.0815 \| +0.0025 |
| 11 | unloading | 8 | 0.0050 \| 0.0053 \| +0.0003 | 24.81 \| 24.86 \| +0.05 | 2.27 \| 2.32 \| +0.05 | -0.0320 \| -0.0319 \| +0.0001 | 0.0790 \| 0.0815 \| +0.0025 |

| observable | n | MAE | RMSE | max abs err | mean abs % | nRMSE (% of measured range) |
|---|---|---|---|---|---|---|
| Q (mL/min) | 11 | 0.002527 | 0.00534 | 0.01706 | 5.1% | **4.94%** |
| sigma'_n (MPa) | 11 | 0.44 | 0.58 | 1.4 | 2.2% | **3.74%** |
| tau (MPa) | 11 | 0.73 | 1 | 2.7 | 16.4% | **10.01%** |
| d_n (mm) | 10 | 0.001137 | 0.001859 | 0.004687 | 10.7% | **4.53%** |
| d_s (mm) | 10 | 0.004133 | 0.005538 | 0.01342 | 15.3% | **7.01%** |
| **mean** |  |  |  |  |  | **6.05%** |

**Mean normalised RMSE 6.05%.** Ten of the eleven stages are tight. Q has a mean absolute error
of 0.0025 mL/min — 5.1% in relative terms on numbers as small as 0.005 — and d_n is inside the
3 µm acceptance gate on 9 of 10 scored stages. **The entire residual is stage 4.**

## 4. Why this is final: the D_c bracket failed in both directions

`D_c` is the slip-weakening length, and it is the regularisation parameter for the transition.
The 91-series bracketed it deliberately, one arm each side of the calibrated 74.5 µm:

| case | D_c | Q | σ'ₙ | τ | d_n | d_s | **mean nRMSE** | final slip |
|---|---|---|---|---|---|---|---|---|
| `91_08` | 40 µm | 4.77 | 6.49 | 16.70 | 24.46 | 32.02 | 16.89% | 0.1001 mm |
| **`90_08`** | **74.5 µm** | 4.94 | 3.74 | 10.01 | 4.53 | 7.01 | **6.05%** | 0.0828 mm |
| `91_07` | 120 µm | 9.43 | 11.23 | 28.86 | 20.57 | 24.26 | 18.87% | 0.0568 mm |
| `90_07` | 74.5 µm, JRC 9 | 5.22 | 4.00 | 10.61 | 4.30 | 6.27 | 6.08% | 0.0814 mm |

Measured final slip is 0.0795 mm. **Both arms are roughly three times worse than the centre**, and
they fail in opposite ways: 120 µm under-slips by 29%, 40 µm overshoots by 26%. D_c = 74.5 µm is
at an optimum, and the remaining error is not a regularisation artefact.

`90_07` (JRC 9) and `90_08` (JRC 5) are a dead heat at 6.08 vs 6.05. `90_08` is preferred: it
wins on four of the five observables and it is the arm that keeps the paper's physically
defensible low JRC for a polished surface. (Note that an earlier preference for `90_07` rested
on `differential_stress_mpa_pp`, which subtracts a *total* confining stress from a *skeleton*
axial stress and reads α·p ≈ 3.5 MPa low for the whole run; on the load-cell channel the verdict
reverses. That postprocessor is referenced nowhere outside `[Postprocessors]`, so no physics was
affected — but it should not be plotted.)

## 5. The one remaining error, and how to justify it in the paper

**Stage 4 (the 20 MPa loading hold) carries τ +2.71 MPa and d_s −0.0134 mm, and nothing else in
the table is close.** The model misses the experiment's *first* slip burst.

The measurement slips in **three discrete bursts, and every one of them sits on a pressure ramp,
not on a hold**:

| window | injection | measured Δd_s | `90_08` Δd_s |
|---|---|---|---|
| 1015–1120 s | ramp 16 → 20 MPa | **15.8 µm** | 2.3 µm |
| 1120–1310 s | **hold at 20 MPa** | 2.1 µm | 2.9 µm |
| 1310–1415 s | ramp 20 → 24 MPa | **21.2 µm** | 17.8 µm |
| 1415–1600 s | **hold at 24 MPa** | 1.3 µm | **34.1 µm** |
| 1600–1710 s | ramp 24 → 28 MPa | **32.2 µm** | 17.2 µm |
| total | | 79.5 µm | 82.8 µm |

The specimen slides only while σ'ₙ is *falling* and arrests the moment it stops falling. A
slip-weakening law has no dependence on dσ'ₙ/dt: once weakening starts it continues, so `90_08`
puts 34 µm into the 24 MPa hold where the experiment puts 1.3. **The total slip budget is
correct to 4%; only its distribution in time is wrong.**

Three consequences, all worth stating explicitly in the paper:

1. **Lowering the regularisation makes it worse, and this was measured, not assumed.** `91_08`
   at D_c = 40 µm dumps **66.9 µm — 73% of its total slip — into the 20 MPa hold** as a single
   runaway, and overshoots to 0.100 mm. A sharper weakening law does not produce more steps; it
   produces one bigger step.
2. **Moving the peak envelope cannot buy the missing burst either.** The strength margin
   `m = (τ_lim − τ)/τ_lim` reads +7.16% in the 16–18 MPa bin and +1.40% in 18–20, against a
   measured first burst beginning at P_i = 17.9 MPa. Shaving ~1.7 percentage points of margin
   (≈ 0.2 MPa of strength, or −0.39° of φ_r) would start the burst on time — but the model would
   then keep sliding through the 20 MPa hold exactly as it now does through the 24 MPa hold, and
   stage 5 would go from +6 µm to roughly +20 µm. It buys stage 4 and loses stage 5.
3. **What would actually fix it is a constitutive addition, not a parameter.** Arresting slip
   when the driving rate vanishes requires rate- or state-dependence in τ_lim (a
   velocity-strengthening term, or full rate-and-state). That is a modelling extension and is
   out of scope for this validation. It is the honest limit of a Barton–Bandis slip-weakening
   law on a staged-injection path, and it is worth reporting as such — it is a *transferable*
   finding, not an SW-S4 quirk. SW-T1 shows the same signature at a different scale: the
   experiment takes ~70 s between first slip and the stress drop, the model takes ~10 s.

**Secondary residuals.** τ runs +0.05 to +1.26 MPa strong on stages 5–11, decaying monotonically
to essentially zero at stage 11 (+0.05 on 2.27) — the residual envelope is right and only the
approach to it is early-strong. σ'ₙ mirrors τ through eq (3) and is not independent evidence.

## 6. Mesh convergence

`92_06_sw4_final_theta30_jrc5_mesh3.i` — identical physics on the size-3 mesh (104 781 nodes,
1977 on the interface, against 10 225 / 409 at size 5). **No constitutive parameter differs.**
The injection/production coordinates are replaced with the exact size-3 interface-node values
(`∓0.018183600, 0, 0.027855081 / 0.090844919`; the borehole moves 184 µm, well inside one
element). Unlike SW-T2, the size-5 coordinates do *not* fall into the bulk-node trap here — they
already snap to a genuine interface node 367 µm away — but they are pinned exactly anyway so the
deck states where the borehole is rather than where it was asked to be. Verified with
`scripts/check_source_nodes.py`, which must be re-run after any mesh change.

`injection_pressure_pp` and `pp_outlet_pp` are `AverageNodalVariableValue` over the two nodesets.
This matters on SW-S4 specifically: they used to be `PointValue` at the *old* 28.99°/off-centre
borehole coordinates, which after the mesh swap sampled 5.86 mm and 0.89 mm off-node and made the
injection pressure read 1.90 MPa low while the outlet read ~2 MPa high against its own 5 MPa
Dirichlet. That was fixed on 2026-08-17 and is why SW-S4's Q now scores 5.1% instead of ~27%.

**What to expect from the mesh-3 run.** `flow_rate_validation_ml_min_pp` (the paper's eq (9)
value, and the only flow channel used above) is built from boundary averages and should be
mesh-insensitive. `flow_rate_pp` and `flow_rate_mesh_geometry_ml_min_pp` are not
mesh-independent by construction and are diagnostics only.

## 7. Reproduce

```bash
sbatch SWS4/92_06_sw4_final_theta30_jrc5_mesh3_hpc_nochk.sh
python3 scripts/table2_gate.py --tag hpc \
  SWS4/results_csv_hpc_rorqual/90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6_hpc.csv \
  SWS4/results_csv_hpc_rorqual/92_06_sw4_final_theta30_jrc5_mesh3_hpc.csv
```


---

## 8. The 93/94 series — audit fixes and the Mohr-Coulomb baseline

Everything above was scored on the deck named in the "Final deck" line's parenthetical. A
mesh-and-postprocessor audit of all eight BBFast decks (four specimens x two mesh sizes) then
found the items below. **No constitutive parameter moved.** The corrected decks are the
**93-series**; each has a **94-series** Mohr-Coulomb sibling that differs from it in one block.

### What the audit confirmed

All eight meshes are correct and current: L and D match Table 1, the fracture angle is exact to
four decimals (SW-T1 32.0000, SW-T2 30.0000, SW-S3 29.0000, SW-S4 30.0000 deg), the fracture plane
is centred to 0.0000 mm on every one, and the mesh-3 meshes are about 2.2x finer in edge length and
10x in element count. Critically, **each deck's paper-frame trig constants match its own mesh's
angle**, checked by an SVD plane fit on the `fracture_interface` nodeset — there is no frame/mesh
mismatch anywhere in the BBFast set.

### What the audit fixed

**1. `d_n` is now read from the same channel as the other three specimens.**
`czm_normal_dilation_paper_mm_pp` was built on `czm_dn_pp` (the raw kinematic jump) here and on
`czm_dn_total_pp` (`normal_opening_total`) on SW-T1, SW-T2 and SW-S3. With the reporting knobs at
their defaults — which is the case on this deck — the two channels are numerically identical, so
**this changes no number**; it removes a cross-specimen inconsistency that would otherwise have to
be explained in the paper. (On SW-S3, where the knobs were *not* at defaults, the same difference
is worth 4.96 nRMSE points — see `SWS3_FINAL.md` §9.)

**2. Three missing channels added**: `czm_dn_total_pp`, `flow_rate_mesh_geometry_ml_min_pp` and
`reported_czm_shear_slip_mm_pp`, which the other three specimens carried and this one did not.
SW-S4 also had no `mesh_flow_width_over_length` constant at all; it is now set equal to the paper
constant, as on SW-T1 and SW-T2.

**3. The bulk probe points were put on the common rule**, `z = L/2 +- 50 mm` (a 100 mm gauge on
every specimen) instead of the ad-hoc `z = 0.115 / 0.010`, which straddled this specimen's
fracture asymmetrically (55.65 mm above against 49.35 below). Diagnostic channels only.

**4. Nothing else.** Both source coordinates are exact interface nodes on both meshes, the
theta30 / centred mesh is the one in use, and the paper-frame constants match its 30.0000 deg.

### The 94-series MC baseline

`94_07_sw4_mc_final.i` / `94_08_sw4_mc_final_mesh3.i` are the 93-series decks with **one block replaced**: `[czm_contact]` becomes
`ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`. Mesh, source nodesets and
their coordinates, boundary conditions, injection schedule, paper-frame constants, flow constants,
solver, and 84 of the 91 postprocessors are byte-identical to the BBFast sibling. The seven `bb_*`
envelope channels become seven `mc_*` analogues because the Barton-Bandis properties they read do
not exist under the other law.

The MC parameters are a **transfer of this specimen's already-calibrated Barton-Bandis envelope**,
not a fresh fit, so the pair differs in constitutive form rather than in fitted strength:

* `mu_smooth` / `c_smooth` are an **exact** transfer — the BB slip-weakened envelope
  `tau = c_res + sigma'_n*tan(phi_r,sw)` is already a Coulomb line.
* `mu_rough` / `c_rough` **tangent-match** the BB peak envelope at the onset normal stress, then
  are divided by `Rbar_0` so MC's strength at zero slip equals the BB peak on a deck that starts
  at `R_0 < 1`.
* `initial_roughness`, `residual_roughness` and `roughness_decay_distance` are copied verbatim,
  because `roughness_state` drives the aperture material and therefore the scored `Q`.

Agreement between the two envelopes is within 0.02 MPa at every stick stage and the MC strength
margin over the measured `tau` is identical to BB's, so **slip onset is inherited, not refitted**.
Rate-and-state is off: the baseline is a plain Coulomb model.

None of the four pre-existing MC decks was reusable. SW-S3's `83_11` sits on the superseded
124.40 mm mesh at `biot = 1e-12`; SW-S4's `67_11` sits on the buggy 28.9904 deg / 2.85 mm
off-centre mesh and emits no paper-frame stress channel at all; and the SW-T1 and SW-T2 MC decks
**carry each other's fracture angle** in their paper-frame constants (32 deg mesh with 31 deg
constants and vice versa) — about 2.3 MPa on `sigma'_n` at this campaign's differential stress,
roughly 3x SW-T1's entire `sigma'_n` RMSE, which invalidates the cohesions fitted in them.
