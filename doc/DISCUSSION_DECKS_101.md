# The 101-series discussion decks

**Built 2026-08-19 on branch `orca_v6`. Generator: `scripts/build_101_decks.py`.
Reader: `scripts/analyze_101.py`. Submit: `Examples/YeGhasemmi2018/submit_discussion_101.sh`.**

16 decks, all mesh 5, all built from the 93-series validated finals. They replace
the 97 (cyclic) and 98 (shut-in) pair.

> **None of these is scoreable against Table 2.** Every one of them replaces
> Ye & Ghassemi's monotonic injection history by design. Do not run
> `scripts/table2_gate.py` on them. The validation set is and remains the
> 93-series.

> **The 97 and 98 SLURM scripts are superseded. Do not resubmit them.** The four
> 97 scripts carry a resourcing bug (below) and the 98 runs are reproduced, with
> their confound removed, by 101_09–101_14.

---

## 1. Why there is a 101 series

The 97/98 batch answered its questions. Three things in it are not
publication-grade, and one question the results themselves raised was never
asked.

### 1.1 Three of the four cyclic runs were killed by their wall-clock allocation

Not a physics problem — a resourcing bug, and a wall-estimate error on top of it.

`submit_discussion_97_98.sh` and `doc/DISCUSSION_DECKS_97_98.md` both advertise
*8 jobs, 32 ranks / 32 G / 24 h*. The four **98** scripts do request that. The
four **97** scripts request **16 ranks / 12 h**, because
`scripts/make_hpc_nochk_jobs.py` rewrote `#SBATCH --time=` but inherited
`--ntasks` and the `srun -n` from its template. `git status` confirms the
scripts are as committed, so this was generation, not a hand edit.

The wall-time estimate was independently wrong by about 2.5×. It assumed
1.85 s of wall clock per simulated second, measured on SW-S3's 4802 s validation
run — but three of the four decks carry `dtmax = 0.75 s`, so a 15.8 ks cyclic
run is ~21 000 steps, not ~8500. **Wall time must be sized from the step count
(`end_time / dtmax`), never from the simulated duration.** The 101 SLURM scripts
do that and print the arithmetic in their own header.

Result: SW-S3 reached 1 cycle of 3 and contributed nothing — and SW-S3 happens
to be the sharpest remaining test of pre-registered outcome 3, since Table 10
leaves it with more unspent gouge capacity than SW-S4 (0.095 vs 0.039 µm).

### 1.2 SW-S4's three cycles did not see the same loading frame

SW-S4's parent carries two fitted, **absolute-time** loading-frame terms: an
axial piston relaxation (`relax_t0 = 1000`, `relax_dur = 800`) and a confinement
bleed (`side_unload_t0 = 1900`, `side_unload_dur = 1400`). Both are
`min(...,1)`-bounded, so they saturate and hold — nothing runs away. But in
97_04 the confinement bleed saturated at **t = 3300 s**, which falls *after*
cycle 1's peak hold (1821 s) and *before* cycle 2's (5209 s).

So cycle 1 ran at a different effective normal stress from cycles 2 and 3 —
precisely the variable a cyclic experiment exists to hold fixed. The measured
cost, priced against the closure law on cycle 3's own down-leg at frozen slip:
**+7.4 of the +13.1 % apparent cycle-2 permeability gain was the bleed, not the
cycling** (and +3.1 of +4.1 % at the floor). The bleed-free cycle 2 → cycle 3
comparison survived, but only because two clean cycles happened to exist.

### 1.3 The arrest test was run on an already-decelerating fault

98 ramps to peak, holds 200 s, then shuts in. The completed runs show the peak
slip **rate** occurring 262–491 s *before* the shut-in instant — during the
ramp. So "slip arrests after shut-in" was demonstrated starting from a state
that was already slowing down. And on SW-S4 the confinement bleed ran from 1900
to 3300 s, i.e. straight *through* the post-shut-in observation window, lowering
σ′ₙ while the test asked whether slip arrests. That made 98_04's result
conservative, not wrong — but it should not be conservative-by-accident.

### 1.4 The questions the 97 result raised were never asked

97 landed on outcome 1, but **not for the pre-registered reason**. §6.6.5 guessed
the joint would end each cycle below residual strength and re-pressurise
elastically. It does not. It sits *exactly on* the yield surface —
τ − τ_lim = 0.0000 MPa to five figures at every peak hold on SW-T1 and SW-T2 —
in neutral **plastic** equilibrium. W is spent, so τ_lim no longer moves, and
what stops slip from accumulating is the **series compliance of the loading
column**, which sheds shear stress the instant slip resumes.

That makes the null result a statement about the loading system rather than
about the aperture law. A lab loading frame is not a reservoir, so as it stands
the result does not transfer to the field — which is the only place anyone
cares about cyclic stimulation. Two new groups close that:

* **Group B, escalating peaks.** Equal-peak cycling breaks no new ground *by
  construction*: the joint re-treads a path it has already taken, so group A
  cannot see outcome 2 (continued growth) or outcome 3 (gouge outrunning
  dilation) even if they are real. Escalating cycles can, and escalation is what
  a field stimulation actually does.
* **Group E, a loading-frame stiffness bracket.** If the frame sets the
  saturation, the retained enhancement per cycle must move with the frame
  stiffness. If the aperture law sets it, it must not. This is the direct test
  of the claim, and the answer decides whether the null result generalises.

---

## 2. What changed from the 93-series parent, and what did not

**Changed, every deck:** the `[injection_pressure]` function, `end_time`, the
three output file bases, the Exodus write interval (10 → 50 steps), and two
added output-only postprocessors.

**Changed, SW-S4 only:** five loading-frame time anchors, retimed (§3.1).

**Changed, group E only:** `axial_bc_penalty` and, by its inverse, the two
commanded piston displacements (§3.5).

**Not changed anywhere:** the mesh, the source nodesets, every constitutive
parameter, the paper-frame constants, the flow constants, the solver, its
tolerances, and `dtmax`.

### `dtmax` is deliberately left alone

It is the obvious wall-time lever. About 60 % of a cyclic run sits below any
pressure at which anything happens (the floor holds and the low legs of the
inter-cycle ramps), so a pressure-gated dt cap would cut these runs by more than
half. It is not used, because it changes how the slip-weakening integral
W = exp(−(s/D_c)^m) is integrated through the active window, and an unverified
speedup is not worth buying when wall clock is free. **If a 101 run still times
out, that is the lever to reach for — and not before.** MOOSE supports it
directly: a `[TimeSteppers]` block composing the existing `IterationAdaptiveDT`
with a `FunctionDT` takes the minimum of the two.

### The Exodus interval

`time_step_interval = 10` on a 21 000-step job writes 2100 full-mesh frames.
Nothing reads Exodus for these runs — the analysis reads CSV — and the cluster
caps file count, which is the whole reason the `_hpc_nochk` scripts exist. 50 is
a pure win: no physics change, less I/O, fewer files.

### The two added postprocessors

Both are postprocessors of already-computed quantities, consumed by nothing, so
neither can affect the solve.

```
strength_margin_mpa_pp   (limit_tau_pp - shear_traction_magnitude_pa) * 1e-6
slip_rate_mm_per_s_pp    ChangeOverTimePostprocessor, divide_by_dt = true
```

`strength_margin_mpa_pp` exists because the 97/98 analysis had to reconstruct it
by hand and **got it wrong the first time**: it differenced the *paper-frame*
shear stress against the *interface-frame* limit and reported a spurious
overstress (τ > τ_lim). Computed in the deck it is unambiguous — `limit_tau_pp`
and `shear_traction_magnitude_pa` are the same pair the constitutive law itself
compares, in the same frame. It is also the sharpest single number in the cyclic
result, so it has no business being a notebook-derived quantity.

`slip_rate_mm_per_s_pp` is the shut-in test's primary observable. Finite-
differencing the CSV works but is noisy across adaptive steps, and *"where is
the slip-rate maximum"* is exactly the question.

---

## 3. The five groups

| Group | Decks | Design | Question |
|---|---|---|---|
| **A** | 101_01–04 | 3 equal-peak cycles | the 97 experiment, resourced to finish |
| **B** | 101_05–08 | 3 escalating peaks, equal 2 MPa steps | outcome 2/3, which A cannot see |
| **C** | 101_09–12 | shut-in, **no** pre-shut-in hold | isolates the hold |
| **D** | 101_13,14 | shut-in, τ = 1500 s | isolates the bleed-off rate |
| **E** | 101_15,16 | SW-T1, 2 cycles, frame ×2 / ×0.5 | tests the saturating mechanism |

Common to every cyclic deck: each specimen ramps at **its own** rate
R = (P_peak − P_amb)/(t_peak − 2), measured from its digitized schedule, because
the model has a genuine rate dependence (`tangential_viscosity` — see the memory
note *tangential-viscosity-is-the-hidden-rate-law*). Floor 8.00 MPa, the level
all four schedules bleed back to. Every peak and floor held 200 s, and **every
comparison is read at mid-hold**, where the pressure is identical from cycle to
cycle and the slip velocity has relaxed, so the reading carries no Perzyna η·V
overstress.

### 3.1 SW-S4's frame retiming (groups A, B, C, D)

| scalar | was | now | completes at |
|---|---:|---:|---:|
| `poro_dur` | 945 | 300 | t = 355 s |
| `relax_t0` | 1000 | 100 | — |
| `relax_dur` | 800 | 400 | t = 500 s |
| `side_unload_t0` | 1900 | 100 | — |
| `side_unload_dur` | 1400 | 600 | t = 700 s |

Magnitudes are untouched; only the anchors move, and because every term is
`min(...,1)`-bounded the **saturated end state is bit-identical** to the parent's.
Injection then starts at **t = 800 s** instead of t = 2 s, so all three cycles
see one frozen frame.

This is a real change to SW-S4's loading path and it means 101_04's cycle 1 is
not directly comparable to 93_07's stage history. That is acceptable: these
decks were never scoreable, and the comparison they exist to make is
cycle-to-cycle.

**Will the specimen stay quiescent through the settling window?** Checked
against 97_04's own CSV before building. At t = 500 s (p_inj = 11.65 MPa) the
strength margin is 2.27 MPa on the *peak* envelope. Backing the injection
pressure down to ambient raises σ′ₙ by roughly α_f·(11.65 − 5) ≈ 5.7 MPa, which
lifts τ_lim to ≈ 17.7 MPa against a τ of ≈ 12.5 MPa, i.e. a margin near 5 MPa.
The retimed bleed costs at most ~1.0 MPa of that (σ₃ down 1.2 MPa raises τ by
0.52 MPa and lowers τ_lim by ~0.45 MPa; the axial relaxation pushes the other
way). So the margin should stay around 4 MPa.

> **FALSIFIER, check this first on every SW-S4 101 run:**
> `reported_czm_shear_slip_mm_pp` at t = 800 s must still be ≈ 0. If it is not,
> the confinement bleed alone reactivated the fault at ambient pore pressure —
> a result in its own right, but one that means the settling window must shrink
> and the estimate above is wrong.

### 3.2 Group A — equal-peak, the 97 experiment repeated

Identical in design to 97, and for SW-T1/T2/S3 identical in every parameter too:
these three specimens have no absolute-time frame terms (their axial ramp is
complete by t = 55 s), so nothing needed retiming. The only differences are
resources, the Exodus interval and the two new postprocessors.

**Expected**: outcome 1 reproduced on all four, now including SW-S3, and SW-S4's
cycle 1 → cycle 2 comparison finally clean.

### 3.3 Group B — escalating peaks

Peaks at **P_peak − 4, P_peak − 2, P_peak** MPa. Equal 2 MPa increments, so
*"does the enhancement per increment shrink?"* is read straight off the
peak-hold rows with no normalisation and no model. A shrinking increment is
saturation; a constant one is not. Same floor, same holds, same rate.

The 68-series prototype escalated 15/20/24/28 MPa, which confounded "enhancement
from cycling" with "enhancement from reaching a higher pressure than before".
Group B is not that mistake repeated — group A already isolates the first
effect; group B deliberately measures the second, and the pair together is the
decomposition.

### 3.4 Groups C and D — the two shut-in controls

**C** shuts in at the instant peak pressure is reached (`hold = 0`). Same peak,
same ramp rate, same everything else as 98 — the hold is the only variable, so
the 98 ↔ 101 pair answers *"how long must you hold before shut-in arrests the
fault?"*

**D** replaces τ = 150 s with **τ = 1500 s** on SW-T1 and SW-S4, with 6000 s of
observation instead of 3000 (≥ 4τ). A fast shut-in makes arrest easy — the
pressure is gone before the fault can respond — and the field-relevant case is a
well that bleeds off over hours. If slip still arrests at τ = 1500 s, arrest is
not a race between the wellbore fall-off and diffusion into the fault, and the
negative result generalises. If it does not, the 98 result is an artefact of
τ = 150 s, and *that* is the more important finding.

### 3.5 Group E — the loading-frame bracket

SW-T1, two equal-peak cycles, `axial_bc_penalty` × 2 and × 0.5.

`axial_pres_initial` and `axial_pres_final` are **commanded displacements** equal
to −σ/penalty, so scaling the penalty by *g* and the displacements by 1/*g*
holds the commanded **stress** fixed and moves only the series stiffness.
Arithmetic check on the parent: 7.5188e-5 × 4.123e11 = 31.0 MPa = σ_zz0. ✔

Two cycles suffice — the question is whether cycle 2 reproduces cycle 1.

| deck | `axial_bc_penalty` | `axial_pres_initial` | `axial_pres_final` |
|---|---:|---:|---:|
| 101_01 (reference) | 4.123e11 | −7.5188e-5 | −7.31214e-4 |
| 101_15 (×2, stiffer) | 8.246e11 | −3.75940e-5 | −3.65607e-4 |
| 101_16 (×0.5, softer) | 2.0615e11 | −1.50376e-4 | −1.46243e-3 |

**Prediction to write down before reading the result:** if the frame sets the
saturation, the cycle-2 / cycle-1 aperture ratio moves with stiffness — a softer
frame sheds less stress per unit slip, so it should permit more accumulation. If
the aperture law sets it, all three arms give 1.000.

---

## 4. Resources

Wall time is sized from `end_time / dtmax`, at the measured 5.3 s/step on 16
ranks scaled by an assumed 1.6× for 32 ranks (the solve is LU/MUMPS-bound and
does not scale linearly). 24 h unless that exceeds 14 h, else 48 h. All 16 jobs
are 32 ranks / 32 G / 1 node.

| deck | grp | end_time (s) | dtmax | steps | est. h | `--time` |
|---|---|---:|---:|---:|---:|---|
| 101_01_swt1_cyclic3_eq | A | 10375.4 | 0.75 | 13834 | 12.7 | 24:00:00 |
| 101_02_swt2_cyclic3_eq | A | 13881.5 | 0.75 | 18509 | 17.0 | 48:00:00 |
| 101_03_sw3_cyclic3_eq | A | 15792.7 | 0.75 | 21057 | 19.3 | 48:00:00 |
| 101_04_sw4_cyclic3_eq | A | 11613.9 | 1.50 | 7743 | 7.1 | 24:00:00 |
| 101_05_swt1_cyclic3_esc | B | 9520.8 | 0.75 | 12695 | 11.6 | 24:00:00 |
| 101_06_swt2_cyclic3_esc | B | 12693.0 | 0.75 | 16924 | 15.5 | 48:00:00 |
| 101_07_sw3_cyclic3_esc | B | 14442.7 | 0.75 | 19257 | 17.7 | 48:00:00 |
| 101_08_sw4_cyclic3_esc | B | 10715.6 | 1.50 | 7144 | 6.5 | 24:00:00 |
| 101_09_swt1_shutin_nohold | C | 4640.0 | 0.75 | 6187 | 5.7 | 24:00:00 |
| 101_10_swt2_shutin_nohold | C | 5280.0 | 0.75 | 7041 | 6.5 | 24:00:00 |
| 101_11_sw3_shutin_nohold | C | 5569.2 | 0.75 | 7426 | 6.8 | 24:00:00 |
| 101_12_sw4_shutin_nohold | C | 5518.7 | 1.50 | 3680 | 3.4 | 24:00:00 |
| 101_13_swt1_shutin_slowtau | D | 7840.0 | 0.75 | 10454 | 9.6 | 24:00:00 |
| 101_14_sw4_shutin_slowtau | D | 8718.7 | 1.50 | 5813 | 5.3 | 24:00:00 |
| 101_15_swt1_cyclic2_frame2x | E | 7126.7 | 0.75 | 9503 | 8.7 | 24:00:00 |
| 101_16_swt1_cyclic2_frame0p5x | E | 7126.7 | 0.75 | 9503 | 8.7 | 24:00:00 |

**Run order if the allocation is tight:** A (must exist) → C (cheap, sharp) →
B (turns the null into an argument) → D, E.

All 16 pass `--check-input` against the current `orca-opt`.

---

## 5. What to measure

`scripts/analyze_101.py` reads every finished run and emits the tables below. It
imports the probe times from `build_101_decks.py` rather than hard-coding them,
so the reader cannot drift from the generator.

**Cyclic (A, B, E)** — at each mid-hold instant: `hydraulic_aperture_um_pp`,
`flow_rate_validation_ml_min_pp`, `fracture_permeability_1e13_m2_pp`,
`reported_czm_shear_slip_mm_pp`, `czm_normal_dilation_paper_mm_pp`,
`effective_normal_paper_frame_mpa_pp`, `bb_dilation_angle_pp`,
`slip_damage_aperture_um_pp`, `cumulative_plastic_slip_pp`,
`strength_margin_mpa_pp`, and W = exp(−(s/D_c)^m) computed from the deck's own
D_c and exponent. Then cycle-*k* / cycle-1 ratios at matched holds, and the
within-cycle peak/floor ratio (the reversible part).

**Shut-in (C, D)** — slip at the shut-in instant, maximum slip afterwards, the
growth between them, the lag from shut-in to the slip-rate maximum (**negative
means the maximum preceded shut-in**), and the retained permeability *at matched
σ′ₙ* — the point on the initial loading ramp carrying the same effective normal
stress as the end state. Matching on σ′ₙ, not on time, is what makes "retained
enhancement" a real number: at t = 2 s the fracture pressure has not equilibrated
(3.789 vs 5.000 MPa), so a t = 2 s baseline reports a confounded ratio.

**Group E** — the cycle-2 / cycle-1 ratios from 101_15, 101_16 and 101_01 side by
side against the frame stiffness.

### D_c and the weakening exponent, per specimen

| specimen | D_c (m) | m |
|---|---:|---:|
| SW-T1 | 1.50e-4 | 1.40 |
| SW-T2 | 1.50e-4 | 1.40 |
| SW-S3 | 6.0e-5 | 1.40 |
| SW-S4 | 7.45e-5 | 1.10 |

### Reproducibility floor

Do not rank two runs on a mean-nRMSE difference below **0.1 pp**, and do not
read `d_n` differences below ~10 % as physics. The same deck run on two machines
gives Q, σ′ₙ and τ identical to 7 digits but a `d_n` MAE 10.8 % apart. See the
memory note *orca-cross-machine-reproducibility-floor*.

---

## 6. Known limits of this batch

* **`fault_pressure_coefficient` is redundant with the Biot coefficient.**
  α = 0.6 with E = 67 GPa / ν = 0.32 implies K_s = 155 GPa, which is not a rock
  modulus. Only the two saw-cuts attenuate it. Unchanged here because changing
  it would invalidate the 93-series calibration these decks inherit.
* **SW-S4's cohesion channel is inert** (`cohesion_effective ≡ 0`), and JRC
  mobilization is inert in all four. Any cyclic result on the cohesion channel
  is therefore a null by construction, not by measurement. Task #91.
* **Group E perturbs a calibrated constant.** It is a mechanism probe, not a
  validation run, and must be presented as one. Its two arms are comparable to
  each other and to 101_01; they are comparable to nothing else.
* **The flow measurement is still not mesh-independent** (task #13), so
  cross-specimen absolute Q comparisons carry that caveat. All the ratios above
  are within-specimen and unaffected.
