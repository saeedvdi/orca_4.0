# What needs re-running — the 105-series run list

**2026-08-25.** Written after the `d_n` channel correction and the recovery of the
`orca_3.0_full` Mohr–Coulomb archive.

---

## 0. First, the short answer: nothing already run needs re-running

The `d_n` correction was a **scoring** change, not a model change. The gate now
reads `frac_normal_dilation_paper_mm` (the global kinematic jump) instead of
`czm_normal_dilation_paper_mm_pp` (each material's own `normal_opening_total`
decomposition, which the Mohr–Coulomb law builds without the elastic term).

Both columns are already written by every finished run. Verified:

```
result CSVs scanned:                        128
missing the kinematic d_n column:             4
```

and all four are derived summaries (`*_table2.csv`, `sws3_final_ab.csv`,
`sws3_stage6_ab.csv`), not simulations. **Every one of the 124 simulation CSVs
can be re-scored from disk.** `scripts/table2_gate.py` and the regenerated
`TABLE2_ERROR_ACCURACY_RANKING.csv` already have been.

### One thing that is stale but does not need a re-run either

Decks **99 through 104 — all 34 of them — predate the 2026-08-24
flow-measurement fix** (task #123) and still sum `inj_flux_aux` rather than
`react_pore_pressure`. Grepping for the *variable* is misleading — every deck
declares `react_pore_pressure` as an AuxVariable — so the test has to read what
`inj_reaction_sum_pp` actually sums:

```
for f in Examples/YeGhasemmi2018/*/[0-9]*.i; do
  awk '/^  \[inj_reaction_sum_pp\]/{g=1} g&&/variable =/{print $3; exit}' "$f"
done | sort | uniq -c
    146 inj_flux_aux
     26 react_pore_pressure
```

The fix never left the 93/94-series finals: those 16 decks plus the 10 new ones
below are the entire set that carries it. Series 99–104 accounts for 34 of the
146; the rest are older and already superseded.

This is **output-only and touches no scored channel.** The scored `Q` is
`flow_rate_validation_ml_min_pp`, a cubic-law reconstruction from
`hydraulic_aperture_pp` and `pp_drop_pp`:

```
expression = '(W/L / (12 mu)) * hydraulic_aperture_pp^3 * pp_drop_pp * ml_per_m3_per_min'
```

It never reads `inj_flux_aux`. Only `inj_reaction_sum_pp` / `prod_reaction_sum_pp`
— diagnostics quoted nowhere — are affected. The ten new decks below all descend
from 93/94-series parents and therefore carry the fix.

---

## 1. Why these ten, and not others

### A. SW-T1: the maximum-closure bracket never turned around

Scored on the corrected channel:

| deck | V_m (µm) | mean | Q | σ'ₙ | τ | d_n | d_s |
|---|---:|---:|---:|---:|---:|---:|---:|
| 93_01 (published final) | 45.91 | 4.44 | 7.38 | 1.98 | 2.73 | 9.06 | 1.02 |
| 99_01 | 50.00 | 3.68 | 6.15 | 1.69 | 2.32 | 7.28 | 0.96 |
| 100_01 | 55.00 | **2.69** | 4.51 | 1.44 | 1.98 | 4.58 | 0.93 |

Every channel improves, monotonically, and the arm has no interior minimum. A
bracket with no minimum is not a result — it is an unfinished search, and it
means **the published SW-T1 final is not the best this model reaches.** 105_01–03
run 70/90/110 µm until the trend turns. At 110 µm σ₀ = K_ni·V_m = 26.87 MPa
against the 31 MPa preload, so that arm is *expected* to overshoot. That is what
closes the bracket.

### B. SW-S4: the τ residual is two defects, and the 99-series probed neither

93_07 against Table 2, model − paper:

| stage | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| τ (MPa) | **+2.74** | +1.06 | +1.26 | +0.89 | +0.65 | +0.45 | +0.29 | +0.05 |
| d_s | **−80 %** | +15 % | +7.7 % | +6.0 % | +4.6 % | +3.2 % | +3.2 % | +3.2 % |

1. **Onset is late.** At stage 3 the measured τ has already fallen 12.14 → 9.38 MPa
   while the model sits at 12.12 and has slipped 3.4 µm against a measured 17 µm.
   Weakening has not begun.
2. **The floor is high.** From stage 5 on the model has the right shape but sits
   0.3–1.3 MPa above the data, converging only at the last stage.

This is why the 99-series failed. 99_07 (exponent 1.10 → 1.05) and 99_08
(viscosity 3.5 → 3.0e12) each bought ≈0.5 MPa at stage 4, nothing at stage 3, and
both **lost** mean accuracy (6.14 → 6.25, 6.35) by paying for it in d_n and d_s.
The exponent reshapes a curve that has not started; it cannot move its start.

The archive is the existence proof that the headroom is real: on this same
specimen a calibrated MC envelope — cohesionless, µ 1.17 → 0.055 over 115 µm —
reached τ = 5.6 % where 93_07 sits at 10.1 %. **This corrects my earlier note that
SW-S4's τ was frame-limited. It is not.**

105_04 moves the onset knob, 105_05 the floor knob, 105_06 both.

### C. The calibrated Mohr–Coulomb upper bound

Best archived runs on today's metric, corrected channel:

| | best archived MC | 94-series transfer | BBFast final |
|---|---:|---:|---:|
| SW-S4 | **4.40 %** (`65_11`) | 7.07 % | 6.14 % |
| SW-S3 | **6.07 %** (`83_11`) | 18.23 % | 4.57 % |

On SW-S4 a freely calibrated Mohr–Coulomb beats our own Barton–Bandis final.
That number cannot be quoted as it stands — superseded meshes, pre-`ppfix` frame,
and on SW-S3 `biot = 1e-12`. It also cannot be ignored: it is the obvious attack
on the manuscript's central comparison, and a fair one. 105_07–10 re-run the
calibrated envelopes on the corrected mesh, the corrected frame and `biot = 0.6`,
so Table 6 can carry a *stated upper bound* instead of an implied claim that
Mohr–Coulomb "fails".

Deliberate deviations from the archived decks, all documented in each header:
the power-law BB normal closure is **kept** (83_11's flat `penalty_normal = 2e13`
is ~19× too stiff on unload and would suppress the recovery the corrected `d_n`
channel now measures — keeping the better normal law can only help MC, so the
bound stays an upper bound); the output-only `reversible_normal_*` reconstruction
is **not** ported; and `roughness_decay_distance` is the archive's, which means
these decks are deliberately *not* hydraulically matched to their BBFast siblings.

> **The tensile slots stay blocked.** SW-T1 MC and SW-T2 MC are recorded
> `blocked` in the 3.0 `SelectionReview_2026-08-03`: two decks were written and
> neither produced a result. **No calibrated Mohr–Coulomb tensile run has ever
> existed in this project.** That is itself reportable, and it is why C is four
> decks and not six.

---

## 2. The list

All ten keep the paper injection schedule and are scoreable against Table 2.

| # | deck | specimen | parent | one change from parent |
|---|---|---|---|---|
| 1 | `105_01_swt1_vm70um_ppfix` | SW-T1 | 93_01 | V_m 45.91 → 70 µm, offset re-solved at 31 MPa |
| 2 | `105_02_swt1_vm90um_ppfix` | SW-T1 | 93_01 | V_m → 90 µm |
| 3 | `105_03_swt1_vm110um_ppfix` | SW-T1 | 93_01 | V_m → 110 µm |
| 4 | `105_04_sw4_dc4p5em5_ppfix` | SW-S4 | 93_07 | Dc 74.5 → 45.0 µm (**onset**) |
| 5 | `105_05_sw4_swfloor3p15_ppfix` | SW-S4 | 93_07 | φ_res 6.50 → 3.15° i.e. µ 0.114 → 0.055 (**floor**) |
| 6 | `105_06_sw4_dc4p5em5_swfloor3p15_ppfix` | SW-S4 | 93_07 | both |
| 7 | `105_07_sw4_mc_calib_ppfix` | SW-S4 | 94_07 | `67_11` envelope, RSF off |
| 8 | `105_08_sw4_mc_calib_rsf_ppfix` | SW-S4 | 94_07 | `67_11` envelope + RSF (full port) |
| 9 | `105_09_sw3_mc_calib_ppfix` | SW-S3 | 94_05 | `83_11` envelope, RSF off |
| 10 | `105_10_sw3_mc_calib_rsf_ppfix` | SW-S3 | 94_05 | `83_11` envelope + RSF (full port) |

Pairs 7/8 and 9/10 exist to separate the calibrated **envelope** from the
rate-and-state **regulariser**; the 94-series baseline deliberately runs without
RSF, so without the pair the two are confounded.

---

## 3. How they were built, and how they were checked

`scripts/make_105_series.py` derives every deck mechanically from its 93/94-series
parent — no deck was hand-edited — so each one is auditable as a diff against a
run that is already in the ranking. Re-running the script is idempotent.

All ten pass MOOSE's own input checker, which validates every parameter name,
type, range check and material dependency against the compiled app:

```
OK    SWT1/105_01_swt1_vm70um_ppfix          OK    SWS4/105_06_sw4_dc4p5em5_swfloor3p15_ppfix
OK    SWT1/105_02_swt1_vm90um_ppfix          OK    SWS4/105_07_sw4_mc_calib_ppfix
OK    SWT1/105_03_swt1_vm110um_ppfix         OK    SWS4/105_08_sw4_mc_calib_rsf_ppfix
OK    SWS4/105_04_sw4_dc4p5em5_ppfix         OK    SWS3/105_09_sw3_mc_calib_ppfix
OK    SWS4/105_05_sw4_swfloor3p15_ppfix      OK    SWS3/105_10_sw3_mc_calib_rsf_ppfix
```

One real error was caught this way and fixed: 94_07 routes five of the ported
parameters through top-level variables, and writing literals into `[czm_contact]`
left those variables unused — which MOOSE treats as an error. The SW-S4 decks now
move the variables and keep the `${...}` references.

`doc/independent_analysis/INPUT_DECK_ANALYSIS_COVERAGE.csv` has been regenerated;
the ten appear as `no_result_available`.

---

## 4. Submitting

```
bash Examples/YeGhasemmi2018/submit_recovery_105.sh
```

32 ranks / 32 GB / 24 h each, copied from each deck's own parent submission
script. Per-deck scripts are `<spec>/<stem>_hpc_nochk.sh` if you want to submit
selectively.

**Do not run these locally.** The workstation has 16 physical cores and 30 GB;
the OOM killer has already taken a 16-rank job on this campaign.

---

## 5. What to look at when they land

```
python scripts/table2_gate.py <csv> --dn-channel kinematic
```

- **105_01–03** — has the mean turned? If 70 µm is still improving and 90 µm is
  worse, the minimum is between them and the bracket is closed. Report the
  minimum; do not adopt it silently — moving the SW-T1 final after the fact is a
  calibration decision and belongs in the manuscript's methods, not its results.
- **105_04–06** — read τ **with** d_s and d_n. Both 99-series probes improved τ
  and lost overall accuracy. A τ gain that costs more than it returns is not an
  improvement, and this bracket is not exempt from that.
- **105_07–10** — the number that matters is the mean against 7.07 % (SW-S4) and
  18.23 % (SW-S3), and against the BBFast finals 6.14 % and 4.57 %. If the
  calibrated SW-S4 MC still beats 6.14 % on the corrected mesh, say so in §5.5.1
  and lean harder on parameter economy; that argument survives the result, and
  the alternative — discovering it in review — does not.
