# SW-S4 — final validation case and paper notes

**Status: FINAL. No further sweep — the remaining error is model-form, and it has been bracketed
in both directions.**
Deck of record (mesh 5): `90_08_sw4_bbfast_theta30_jrc5_kernel_SV_biot0p6.i`
Mesh-convergence run: `92_06_sw4_final_theta30_jrc5_mesh3.i`
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
